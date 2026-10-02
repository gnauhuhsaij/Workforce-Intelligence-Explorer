# CDKCanvas - Visual AWS CDK Builder

An interactive Tableau dashboard for researching U.S. industries, occupations, skills, wages, and regional employment patterns.

## Purpose

Labor market data is often spread across large tables that are difficult to compare. This project brings selected Bureau of Labor Statistics datasets into one research tool for people evaluating industries, occupations, or career directions.

The dashboard is intended to support exploration rather than prescribe a single "best" career.

## Intended audience

- Job seekers and career changers researching unfamiliar fields
- Students comparing career and education options
- Analysts exploring workforce and industry trends

## Planned dashboard

### 1. Workforce Overview

A high-level view of employment and wage changes from May 2024 to May 2025. The main visual will compare wage and employment change while preserving occupation size and group.

### 2. Industry Deep Dive

An industry research view showing changes in employment estimates and occupational composition. Users will be able to select an industry and inspect the occupations that contribute most to its workforce.

### 3. Occupation & Skills Explorer

An occupation-level view combining skill profiles with a state map. Users will be able to compare skills, wages, employment concentration, and geographic differences for a selected occupation.

## Data sources

The project uses May 2024 and May 2025 OEWS estimates with the latest BLS occupational skills and education data.

The four prepared tables connect on `occupation_code`: occupations, industry occupations, occupation skills, and state occupations. Employment changes describe changes in published OEWS estimates rather than exact job creation; wages are nominal.

## Rebuild the data

Download the 2024 OEWS [national](https://www.bls.gov/oes/special-requests/oesm24nat.zip), [state](https://www.bls.gov/oes/special-requests/oesm24st.zip), and [industry](https://www.bls.gov/oes/special-requests/oesm24in4.zip) files; the matching 2025 [national](https://www.bls.gov/oes/special-requests/oesm25nat.zip), [state](https://www.bls.gov/oes/special-requests/oesm25st.zip), and [industry](https://www.bls.gov/oes/special-requests/oesm25in4.zip) files; plus [occupation data](https://www.bls.gov/emp/ind-occ-matrix/occupation.xlsx) and [skills data](https://www.bls.gov/emp/skills/public-skills-data.xlsx). Save all eight files in `data/raw/`, then run:

```bash
pip install -r requirements.txt
python src/prepare_data.py
```
