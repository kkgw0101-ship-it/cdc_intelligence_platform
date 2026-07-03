# CDC Permagrain Intelligence Platform

Streamlit Community Cloud external sharing package for CDC Distributors / Timeless Designs / Permagrain Collection.

## Main App

Use this file as the Streamlit main file path:

```text
cdc_intelligence_platform.py
```

## Required Files

Upload or commit these files together:

- `cdc_intelligence_platform.py`
- `requirements.txt`
- `freight_index_records.json`
- `cdc_distributors_logo.png`
- `cdc_distributors_logo_crop.png`
- `cdc_logo_horizontal.png`
- `cdc_logo_tagline_mark.png`
- `cdc_hero_facility_aerial.png`
- `cdc_hero_facility_parking.png`
- `cdc_hero_facility_exterior.png`
- `cdc_hero_team_event.png`
- `timeless_designs_logo.png`
- `timeless_designs_logo_crop.png`
- `logo_white_t.png`

## Streamlit Secrets

The app can open without secrets. To activate live FRED charts, add this in Streamlit Cloud > App settings > Secrets:

```toml
FRED_API_KEY = "your_fred_api_key"
```

## Streamlit Cloud Setup

1. Push the required files to a GitHub repository.
2. Go to Streamlit Community Cloud.
3. Create a new app from the GitHub repository.
4. Set main file path to:

```text
cdc_intelligence_platform.py
```

5. Add `FRED_API_KEY` in Secrets if available.
6. Deploy and copy the generated external URL.

## External Sharing Note

This version is set to customer review mode. It hides upload controls and avoids internal credit, cost, margin, or preview wording.
