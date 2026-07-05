# CDC Partner Portal

Streamlit Community Cloud external sharing package for CDC Distributors / Permagrain Collection.

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
- `logo_white_t.png`
- `kcc_certification_badges.png`
- `kcc_4re_solution.png`
- `kcc_lvt_blue_brochure_2026.pdf`

## Streamlit Secrets

Before sharing the public Streamlit URL, add a portal password in Streamlit Cloud > App settings > Secrets:

```toml
CDC_PORTAL_PASSWORD = "choose_a_private_password"
```

To activate live FRED charts, also add:

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

5. Add `CDC_PORTAL_PASSWORD` in Secrets before sharing the URL.
6. Add `FRED_API_KEY` in Secrets if available.
7. Deploy and copy the generated external URL.

## External Sharing Note

This version is set to customer review mode. It uses a password gate, hides upload controls, removes decorative animation, and avoids internal credit, cost, margin, or strategy-note wording.
