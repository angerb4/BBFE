# Occupational Bloodborne Pathogen Exposure Decision Tool

Interactive Streamlit decision-support tool for management of occupational exposures to **HIV, Hepatitis B, and Hepatitis C**, based on:

- **2025 USPHS Guidelines** for Occupational Exposures to HIV and Recommendations for PEP
- Current **CDC HBV** occupational exposure / post-exposure prophylaxis guidance
- Current **CDC HCV** testing and follow-up guidance for healthcare personnel (no PEP recommended)

## Features

- Radio-button guided risk assessment (exposure type, fluid, source status, exposed person status)
- HIV PEP regimens (preferred and alternative) with 28-day course
- Special population considerations: pregnancy, breastfeeding, renal impairment, immunosuppression, current PrEP use
- HBV management by vaccine/responder status (HBIG ± vaccine)
- HCV: no PEP; structured testing schedule
- **Follow-up testing dates calculated from today**
- Basic HIV PEP drug-interaction checker
- Precautions while awaiting results / on PEP
- Printable summary plan
- Links to PEPline (1-888-448-4911) and official CDC pages

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Deploy free on Streamlit Community Cloud

1. Create a GitHub repository and upload `app.py` + `requirements.txt` + `README.md`
2. Go to https://share.streamlit.io → New app → select the repo → Deploy
3. You get a permanent public URL

## Disclaimer

This is an **unofficial educational and clinical reference aid only**.  
It does **not** replace official CDC/USPHS guidelines, institutional protocols, or expert consultation.  
The treating clinician remains solely responsible for all decisions.  
Always verify the latest guidelines and consult PEPline or an HIV/hepatitis expert for complex cases.

## Update cadence

Re-check CDC / USPHS occupational exposure pages periodically (especially after major guideline releases) and update regimens, testing windows, and special-population notes as needed.
