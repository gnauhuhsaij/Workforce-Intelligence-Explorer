from io import BytesIO
from pathlib import Path
from zipfile import ZipFile

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
OUTPUT = ROOT / "data" / "processed"


def read_zip_xlsx(filename, token):
    with ZipFile(RAW / filename) as archive:
        member = next(
            name for name in archive.namelist()
            if token in name and name.endswith(".xlsx")
        )
        return pd.read_excel(BytesIO(archive.read(member)))


def number(series):
    return pd.to_numeric(series, errors="coerce")


def add_change_columns(data, metric):
    start = data[f"{metric}_2024"]
    end = data[f"{metric}_2025"]
    data[f"{metric}_change"] = end - start
    data[f"{metric}_change_pct"] = ((end - start) / start.replace(0, pd.NA)).round(4)


def build_occupations(national_2024, national_2025):
    source = pd.read_excel(RAW / "occupation.xlsx", sheet_name="Table 1.2", header=1)
    columns = {
        "2025 National Employment Matrix code": "occupation_code",
        "2025 National Employment Matrix title": "occupation_title",
        "Typical education needed for entry": "typical_education",
        "Work experience in a related occupation": "related_work_experience",
        "Typical on-the-job training needed to attain competency in the occupation": "on_the_job_training",
    }
    occupations = source.loc[source["Occupation type"].eq("Line item"), list(columns)].rename(columns=columns)
    occupations["occupation_code"] = occupations["occupation_code"].str.strip()
    occupations["occupation_title"] = occupations["occupation_title"].str.strip()
    occupations["major_group_code"] = occupations["occupation_code"].str[:2] + "-0000"
    occupations["related_work_experience"] = occupations["related_work_experience"].fillna("None")
    occupations["on_the_job_training"] = occupations["on_the_job_training"].fillna("None")

    major_groups = national_2025.loc[
        national_2025["O_GROUP"].eq("major"), ["OCC_CODE", "OCC_TITLE"]
    ].rename(columns={"OCC_CODE": "major_group_code", "OCC_TITLE": "major_group_title"})
    occupations = occupations.merge(major_groups, on="major_group_code", how="left")

    for year, data in [(2024, national_2024), (2025, national_2025)]:
        values = data.loc[data["O_GROUP"].eq("detailed"), ["OCC_CODE", "TOT_EMP", "A_MEDIAN"]].copy()
        values = values.rename(columns={
            "OCC_CODE": "occupation_code",
            "TOT_EMP": f"employment_{year}",
            "A_MEDIAN": f"median_wage_{year}",
        })
        values[f"employment_{year}"] = number(values[f"employment_{year}"]).astype("Int64")
        values[f"median_wage_{year}"] = number(values[f"median_wage_{year}"]).astype("Int64")
        occupations = occupations.merge(values, on="occupation_code", how="left")

    add_change_columns(occupations, "employment")
    add_change_columns(occupations, "median_wage")
    occupations["employment_change"] = occupations["employment_change"].astype("Int64")
    occupations["median_wage_change"] = occupations["median_wage_change"].astype("Int64")

    order = [
        "occupation_code", "occupation_title", "major_group_code", "major_group_title",
        "employment_2024", "employment_2025", "employment_change", "employment_change_pct",
        "median_wage_2024", "median_wage_2025", "median_wage_change", "median_wage_change_pct",
        "typical_education", "related_work_experience", "on_the_job_training",
    ]
    return occupations[order].sort_values("occupation_code")


def build_industries(industry_2024, industry_2025, occupations):
    occupation_codes = set(occupations["occupation_code"])
    yearly = []
    for year, data in [(2024, industry_2024), (2025, industry_2025)]:
        keep = data["O_GROUP"].isin(["total", "detailed"])
        values = data.loc[keep, [
            "NAICS", "NAICS_TITLE", "OCC_CODE", "OCC_TITLE", "O_GROUP",
            "TOT_EMP", "PCT_TOTAL", "A_MEDIAN",
        ]].copy()
        values = values[values["OCC_CODE"].isin(occupation_codes | {"00-0000"})]
        values["TOT_EMP"] = number(values["TOT_EMP"]).astype("Int64")
        values["PCT_TOTAL"] = (number(values["PCT_TOTAL"]) / 100).round(4)
        values["A_MEDIAN"] = number(values["A_MEDIAN"]).astype("Int64")
        values = values.rename(columns={
            "NAICS": "industry_code",
            "NAICS_TITLE": f"industry_title_{year}",
            "OCC_CODE": "occupation_code",
            "OCC_TITLE": f"occupation_title_{year}",
            "O_GROUP": f"record_type_{year}",
            "TOT_EMP": f"employment_{year}",
            "PCT_TOTAL": f"industry_share_{year}",
            "A_MEDIAN": f"median_wage_{year}",
        })
        yearly.append(values)

    industries = yearly[0].merge(yearly[1], on=["industry_code", "occupation_code"], how="outer")
    industries["industry_title"] = industries["industry_title_2025"].combine_first(industries["industry_title_2024"])
    industries["occupation_title"] = industries["occupation_title_2025"].combine_first(industries["occupation_title_2024"])
    industries["record_type"] = industries["record_type_2025"].combine_first(industries["record_type_2024"])
    title_map = occupations.set_index("occupation_code")["occupation_title"]
    detailed = industries["record_type"].eq("detailed")
    industries.loc[detailed, "occupation_title"] = industries.loc[detailed, "occupation_code"].map(title_map)
    add_change_columns(industries, "employment")
    add_change_columns(industries, "median_wage")
    industries["employment_change"] = industries["employment_change"].astype("Int64")
    industries["median_wage_change"] = industries["median_wage_change"].astype("Int64")

    order = [
        "industry_code", "industry_title", "occupation_code", "occupation_title", "record_type",
        "employment_2024", "employment_2025", "employment_change", "employment_change_pct",
        "industry_share_2024", "industry_share_2025", "median_wage_2024", "median_wage_2025",
        "median_wage_change", "median_wage_change_pct",
    ]
    return industries[order].sort_values(["industry_code", "record_type", "occupation_code"])


def build_skills(occupations):
    source = pd.read_excel(RAW / "public-skills-data.xlsx", sheet_name="EP Skills Data", header=1)
    columns = {
        "2025 National Employment Matrix code": "occupation_code",
        "EP skill category ID": "skill_id",
        "EP skill category": "skill_name",
        "EP skill score": "skill_score",
    }
    skills = source[list(columns)].rename(columns=columns).drop_duplicates()
    skills = skills.merge(occupations[["occupation_code", "occupation_title"]], on="occupation_code", how="inner")
    skills = skills[["occupation_code", "occupation_title", "skill_id", "skill_name", "skill_score"]]
    return skills.sort_values(["occupation_code", "skill_id"])


def build_states(state_2024, state_2025, occupations):
    yearly = []
    for year, data in [(2024, state_2024), (2025, state_2025)]:
        keep = data["O_GROUP"].eq("detailed") & ~data["PRIM_STATE"].isin(["GU", "PR", "VI"])
        values = data.loc[keep, [
            "PRIM_STATE", "AREA_TITLE", "OCC_CODE", "TOT_EMP",
            "JOBS_1000", "LOC_QUOTIENT", "A_MEDIAN",
        ]].copy()
        values["TOT_EMP"] = number(values["TOT_EMP"]).astype("Int64")
        values["JOBS_1000"] = number(values["JOBS_1000"]).round(3)
        values["LOC_QUOTIENT"] = number(values["LOC_QUOTIENT"]).round(3)
        values["A_MEDIAN"] = number(values["A_MEDIAN"]).astype("Int64")
        values = values.rename(columns={
            "PRIM_STATE": "state_code",
            "AREA_TITLE": f"state_name_{year}",
            "OCC_CODE": "occupation_code",
            "TOT_EMP": f"employment_{year}",
            "JOBS_1000": f"jobs_per_1000_{year}",
            "LOC_QUOTIENT": f"location_quotient_{year}",
            "A_MEDIAN": f"median_wage_{year}",
        })
        yearly.append(values)

    states = yearly[0].merge(yearly[1], on=["state_code", "occupation_code"], how="outer")
    states["state_name"] = states["state_name_2025"].combine_first(states["state_name_2024"])
    states = states.merge(occupations[["occupation_code", "occupation_title"]], on="occupation_code", how="inner")
    add_change_columns(states, "employment")
    add_change_columns(states, "median_wage")
    states["employment_change"] = states["employment_change"].astype("Int64")
    states["median_wage_change"] = states["median_wage_change"].astype("Int64")

    order = [
        "state_code", "state_name", "occupation_code", "occupation_title",
        "employment_2024", "employment_2025", "employment_change", "employment_change_pct",
        "jobs_per_1000_2024", "jobs_per_1000_2025", "location_quotient_2024", "location_quotient_2025",
        "median_wage_2024", "median_wage_2025", "median_wage_change", "median_wage_change_pct",
    ]
    return states[order].sort_values(["state_code", "occupation_code"])


def validate(occupations, industries, skills, states):
    assert len(occupations) == 831 and occupations["occupation_code"].is_unique
    assert not industries.duplicated(["industry_code", "occupation_code"]).any()
    assert industries["industry_code"].nunique() == 20
    assert not skills.duplicated(["occupation_code", "skill_id"]).any()
    assert skills.groupby("occupation_code")["skill_id"].nunique().eq(17).all()
    assert not states.duplicated(["state_code", "occupation_code"]).any()
    assert states["state_code"].nunique() == 51


def main():
    national_2024 = read_zip_xlsx("oesm24nat.zip", "national_")
    national_2025 = read_zip_xlsx("oesm25nat.zip", "national_")
    industry_2024 = read_zip_xlsx("oesm24in4.zip", "natsector_")
    industry_2025 = read_zip_xlsx("oesm25in4.zip", "natsector_")
    state_2024 = read_zip_xlsx("oesm24st.zip", "state_")
    state_2025 = read_zip_xlsx("oesm25st.zip", "state_")

    occupations = build_occupations(national_2024, national_2025)
    industries = build_industries(industry_2024, industry_2025, occupations)
    skills = build_skills(occupations)
    states = build_states(state_2024, state_2025, occupations)
    validate(occupations, industries, skills, states)

    OUTPUT.mkdir(parents=True, exist_ok=True)
    tables = {
        "occupations.csv": occupations,
        "industry_occupations.csv": industries,
        "occupation_skills.csv": skills,
        "state_occupations.csv": states,
    }
    for filename, table in tables.items():
        table.to_csv(OUTPUT / filename, index=False)
        print(f"{filename}: {len(table):,} rows")


if __name__ == "__main__":
    main()
