# Portfolio Data Schema

This document describes the CSV schema expected by the LeanIX GenAI Portfolio Analyzer.
It maps directly to LeanIX Application Fact Sheet fields.

## How to export from LeanIX

1. Go to **Inventory → Applications**
2. Click **Export → Excel/CSV**
3. Select the columns below
4. Rename columns to match the field names below (lowercase, underscores)

## Required columns

| Field | Type | Allowed values | LeanIX mapping |
|---|---|---|---|
| `app_name` | string | Any | Application > Name |
| `business_capability` | string | Any | Application > Business Capability (tag) |
| `lifecycle_stage` | string | Plan, Phase In, Active, Phase Out, End of Life | Application > Lifecycle > Phase |
| `tech_debt_score` | integer | 0–10 | Application > Technical Fit score |
| `business_value_score` | integer | 0–10 | Application > Functional Fit score |
| `annual_cost_usd` | integer | Any positive number | Application > Annual cost (IT Native) |
| `hosting_type` | string | On-Premise, SaaS, Cloud | Application > Technical Stack > Deployment |
| `last_updated_year` | integer | e.g. 2019 | Application > Last major update |
| `owner_team` | string | Any | Application > IT Owner |

## Derived columns (added automatically)

| Field | Description |
|---|---|
| `age_years` | Years since last_updated_year |
| `rationalization_quadrant` | Invest / Modernize / Monitor / Retire |
| `cost_per_value_point` | annual_cost_usd / business_value_score |
| `risk_score` | Weighted score: tech debt + age + inverse business value |

## Notes

- `tech_debt_score` maps to LeanIX **Technical Fit**: Poor=8–10, Fair=5–7, Good=0–4
- `business_value_score` maps to LeanIX **Functional Fit**: Poor=0–4, Fair=5–7, Good=8–10
- Scores should be inverted if exporting directly from LeanIX (LeanIX uses 1=poor, 4=good)
- The sample dataset in `data/sample_portfolio.csv` shows the expected format