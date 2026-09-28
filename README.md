# U.S. Workforce Intelligence Explorer

An interactive Tableau dashboard for researching U.S. industries, occupations, skills, wages, and regional employment patterns.

## Purpose

Labor market data is often spread across large tables that are difficult to compare. This project brings selected Bureau of Labor Statistics datasets into one research tool for people evaluating industries, occupations, or career directions.

The dashboard is intended to support exploration rather than prescribe a single "best" career.

## Intended audience

- Job seekers and career changers researching unfamiliar fields
- Students comparing career and education options
- Analysts exploring workforce and industry trends

## Research questions

1. Which occupations combine strong projected growth, meaningful job openings, and competitive wages?
2. Which industries are expected to grow or contract, and what occupations make up their workforce?
3. Which skills are most important across different occupations?
4. Where are selected occupations concentrated, and how do wages differ by state?

## Planned dashboard

### 1. Workforce Overview

A high-level view of employment, projected growth, annual openings, and wages. The main visual will compare wage and growth while preserving occupation size and group.

### 2. Industry Deep Dive

An industry research view showing projected employment change and occupational composition. Users will be able to select an industry and inspect the occupations that contribute most to its workforce.

### 3. Occupation & Skills Explorer

An occupation-level view combining skill profiles with a state map. Users will be able to compare skills, wages, employment concentration, and geographic differences for a selected occupation.

## Planned data sources

The project will use public data from the U.S. Bureau of Labor Statistics. Exact files and fields will be confirmed during the data audit.

- Employment Projections and National Employment Matrix
- Occupational Skills Data
- Occupational Employment and Wage Statistics by state

## Design principles

- Keep the scope to three focused dashboard pages
- Use normalized measures when raw totals could be misleading
- Make filters and calculations understandable to a general audience
- Separate current employment estimates from future projections
- Prefer clear, familiar charts over decorative or custom visuals
- Document important assumptions without overloading the dashboard

## Repository structure

```text
.
├── assets/          # Dashboard screenshots and demo media
├── dashboard/       # Tableau workbook
├── data/
│   ├── raw/         # Source files retained in their original form
│   └── processed/   # Analysis-ready tables used by Tableau
├── src/              # Data preparation script
└── README.md
```

## Project roadmap

- [x] Define the audience, research questions, and dashboard scope
- [ ] Audit source data, fields, join keys, and limitations
- [ ] Prepare and validate analysis-ready data
- [ ] Build the Workforce Overview
- [ ] Build the Industry Deep Dive
- [ ] Build the Occupation & Skills Explorer
- [ ] Publish to Tableau Public and complete the portfolio documentation

## Tools

- Tableau Public
- Python and pandas for lightweight data preparation
- GitHub for documentation and version history

