import streamlit as st
from datetime import datetime, timedelta
import pandas as pd

st.set_page_config(
    page_title="BBP Occupational Exposure Decision Tool",
    page_icon="🩸",
    layout="wide",
    initial_sidebar_state="expanded"
)

LAST_VERIFIED = "September 2025 (2025 USPHS Occupational HIV PEP Guidelines + current CDC HBV/HCV guidance)"

st.markdown("""
<style>
.main-header {font-size: 1.7rem; font-weight: 700; color: #1a365d;}
.issue-box {background:#C6EFCE; padding:1rem; border-radius:8px; border-left:5px solid #006100; margin:0.6rem 0;}
.defer-box {background:#FFC7CE; padding:1rem; border-radius:8px; border-left:5px solid #9C0006; margin:0.6rem 0;}
.warn-box {background:#FFF2CC; padding:1rem; border-radius:8px; border-left:5px solid #BF8F00; margin:0.6rem 0;}
.info-box {background:#DDEBF7; padding:1rem; border-radius:8px; border-left:5px solid #1F4E79; margin:0.6rem 0;}
.stRadio > label {font-weight: 500;}
</style>
""", unsafe_allow_html=True)

st.markdown('<p class="main-header">🩸 Occupational Bloodborne Pathogen Exposure Decision Tool</p>', unsafe_allow_html=True)
st.caption(f"Based on 2025 USPHS Occupational HIV PEP Guidelines and current CDC HBV/HCV guidance. Last verified: {LAST_VERIFIED}")

st.error("""
**IMPORTANT DISCLAIMER**  
This is an **unofficial clinical decision-support aid only**. It does **not** replace the official CDC / USPHS guidelines, institutional protocols, or expert consultation (PEPline 1-888-448-4911).  
The clinician remains fully responsible for all management decisions. Always verify current guidelines and consult an expert for complex cases (pregnancy, resistance, renal/hepatic impairment, source with undetectable viral load, etc.).
""")

# ---------- SIDEBAR ----------
with st.sidebar:
    st.header("Quick Links")
    st.markdown("""
    - [2025 USPHS Occupational HIV PEP](https://www.cambridge.org/core/journals/infection-control-and-hospital-epidemiology)
    - [CDC HBV Occupational Exposure](https://www.cdc.gov/hepatitis-b/hcp/infection-control/index.html)
    - [CDC HCV HCP Exposure](https://www.cdc.gov/hepatitis-c/hcp/infection-control/index.html)
    - **PEPline (expert consult):** 1-888-448-4911

    **Free interaction checkers**
    - [Liverpool HIV Drug Interactions](https://www.hiv-druginteractions.org/)
    - [Liverpool HEP Drug Interactions](https://www.hep-druginteractions.org/)
    - [Drugs.com Interaction Checker](https://www.drugs.com/drug_interactions.html)
    """)
    st.divider()
    st.header("How to use")
    st.markdown("""
    1. Enter exposure date/time and details  
    2. Answer source & exposed-person questions  
    3. Review pathogen-specific recommendations  
    4. Note follow-up dates (calculated from today)  
    5. Check drug interactions if HIV PEP is recommended  
    """)

# ---------- HELPERS ----------
def d(days):
    return (datetime.now() + timedelta(days=days)).strftime("%b %d, %Y")

def show_box(kind, title, body):
    cls = {"ok": "issue-box", "warn": "warn-box", "bad": "defer-box", "info": "info-box"}.get(kind, "info-box")
    st.markdown(f'<div class="{cls}"><strong>{title}</strong><br>{body}</div>', unsafe_allow_html=True)

# ---------- 1. EXPOSURE DETAILS ----------
st.header("1. Exposure Details")
col1, col2 = st.columns(2)
with col1:
    exp_date = st.date_input("Date of exposure", value=datetime.now().date())
    exp_time = st.time_input("Approximate time of exposure (if known)")
with col2:
    hours_since = st.number_input("Hours since exposure (approximate)", min_value=0.0, max_value=168.0, value=2.0, step=0.5)
    exposure_type = st.radio("Type of exposure", [
        "Percutaneous (needlestick / sharps)",
        "Mucous membrane (eyes, nose, mouth)",
        "Non-intact skin",
        "Intact skin only (usually no risk)"
    ])

fluid = st.radio("Fluid involved", [
    "Blood or visibly bloody fluid",
    "Other potentially infectious material (semen, vaginal secretions, CSF, synovial, pleural, peritoneal, pericardial, amniotic)",
    "Urine, feces, saliva, sputum, sweat, tears, vomitus — NOT visibly bloody (generally not infectious for BBP)"
])

# ---------- 2. SOURCE ----------
st.header("2. Source Patient Status")
source_hiv = st.radio("Source HIV status", [
    "Known HIV-positive",
    "HIV-negative (documented recent test)",
    "Unknown / cannot be tested"
])
source_vl = None
if source_hiv == "Known HIV-positive":
    source_vl = st.radio("Source HIV viral load (if known)", [
        "Detectable / unknown",
        "Undetectable (documented)"
    ])

source_hbv = st.radio("Source HBsAg status", [
    "HBsAg-positive",
    "HBsAg-negative",
    "Unknown / cannot be tested"
])
source_hcv = st.radio("Source HCV status", [
    "HCV RNA-positive (or anti-HCV+ with unknown RNA)",
    "HCV RNA-negative / anti-HCV-negative",
    "Unknown / cannot be tested"
])

# ---------- 3. EXPOSED PERSON ----------
st.header("3. Exposed Person (HCP)")
hcp_hiv = st.radio("Exposed person’s baseline HIV status", ["Negative / unknown (test now)", "Known HIV-positive"])
hcp_hbv = st.radio("Exposed person’s HBV vaccine / immunity status", [
    "Documented responder (complete series + anti-HBs ≥10 mIU/mL)",
    "Documented non-responder (anti-HBs <10 after two complete series)",
    "Vaccinated but response unknown (anti-HBs unknown)",
    "Unvaccinated or incompletely vaccinated"
])
if "response unknown" in hcp_hbv:
    anti_hbs = st.radio("Current anti-HBs result (obtain ASAP)", ["≥10 mIU/mL", "<10 mIU/mL", "Not yet available"])
else:
    anti_hbs = None

pregnant = st.radio("Pregnant?", ["No", "Yes", "Possibly / unknown"])
breastfeeding = st.radio("Breastfeeding?", ["No", "Yes"])
immunosuppressed = st.radio("Significant immunosuppression?", ["No", "Yes"])
renal = st.radio("Renal function", ["Normal (CrCl ≥50)", "Moderate impairment (CrCl 30–49)", "Severe impairment (CrCl <30)"])
on_prep = st.radio("Currently taking HIV PrEP?", ["No", "Yes"])

# ---------- RISK SCREEN ----------
st.header("4. Initial Risk Assessment")
low_risk_fluid = "Urine, feces" in fluid or "Intact skin" in exposure_type
if low_risk_fluid:
    show_box("ok", "Generally no BBP transmission risk",
             "Intact skin or non-bloody urine/feces/saliva/etc. does not pose a meaningful risk for HIV, HBV, or HCV. No PEP or specific follow-up testing is usually required. Document the exposure.")
    st.stop()

hiv_pep_indicated = False
if source_hiv == "Known HIV-positive" and hcp_hiv.startswith("Negative"):
    hiv_pep_indicated = True
elif source_hiv == "Unknown / cannot be tested" and hcp_hiv.startswith("Negative"):
    # Case-by-case; still offer discussion
    hiv_pep_indicated = True  # default to considering PEP for unknown source in occupational setting with significant exposure

if hours_since > 72 and hiv_pep_indicated:
    show_box("warn", "PEP window may have closed",
             f"More than 72 hours have elapsed. Expert consultation (PEPline 1-888-448-4911) is strongly recommended before starting or withholding PEP. Do not automatically start PEP after 72 h except in very high-risk cases after expert input.")

# ---------- HIV SECTION ----------
st.header("5. HIV Management")
if hcp_hiv == "Known HIV-positive":
    show_box("info", "Exposed person already HIV-positive", "HIV PEP is not indicated. Continue/optimize HIV care. Still address HBV/HCV risk.")
elif not hiv_pep_indicated and source_hiv == "HIV-negative (documented recent test)":
    show_box("ok", "HIV PEP not indicated", "Source is documented HIV-negative. Baseline HIV test of exposed person still recommended; further HIV follow-up usually not needed unless new information arises.")
else:
    if source_vl == "Undetectable (documented)":
        show_box("warn", "Source has undetectable viral load",
                 "2025 guidelines support shared decision-making. Risk is very low but not zero. Discuss with exposed HCP and consider expert consultation. PEP may be foregone or stopped early after shared decision.")
    if hours_since <= 72:
        show_box("info", "HIV PEP is recommended / strongly consider",
                 "Start PEP **as soon as possible** (ideally within hours; up to 72 h). Do not delay for source lab results.")
    st.subheader("Preferred HIV PEP regimens (2025 USPHS) — 28 days")
    st.markdown("""
**Preferred (most HCP without contraindications):**
- **Bictegravir / emtricitabine / tenofovir alafenamide** (BIC/FTC/TAF – Biktarvy) **one tablet once daily**, **or**
- **Dolutegravir** 50 mg daily **PLUS** (tenofovir alafenamide 25 mg **or** tenofovir DF 300 mg) **PLUS** (emtricitabine 200 mg **or** lamivudine 300 mg)

**Alternative:**
- Darunavir 800 mg + cobicistat 150 mg (or ritonavir 100 mg) daily **PLUS** (TAF or TDF) **PLUS** (FTC or 3TC)

**Duration:** 28 days if tolerated.
""")
    if pregnant == "Yes" or pregnant.startswith("Possibly"):
        show_box("warn", "Pregnancy",
                 "Expert consultation recommended. Dolutegravir-based regimens are generally preferred in pregnancy in current guidance; avoid agents with pregnancy concerns. PEPline consultation advised.")
    if breastfeeding == "Yes":
        show_box("warn", "Breastfeeding",
                 "Discuss risks/benefits. Some ARVs pass into breast milk. Expert consultation recommended. Temporary interruption of breastfeeding may be considered while on PEP.")
    if renal.startswith("Moderate") or renal.startswith("Severe"):
        show_box("warn", "Renal impairment",
                 "Adjust tenofovir formulation/dose or avoid TDF if CrCl low. Prefer TAF when appropriate; expert consultation recommended for CrCl <50.")
    if on_prep == "Yes":
        show_box("info", "Exposed person on PrEP",
                 "Shared decision-making applies. Breakthrough risk is low if adherent; expert input may help decide whether to continue/ intensify or use full PEP.")

    st.subheader("HIV baseline & follow-up testing (dates calculated from today)")
    st.markdown(f"""
| Time point | Tests | Target date (from today) |
|------------|-------|---------------------------|
| **Baseline (now)** | HIV Ag/Ab (lab or rapid) ± HIV NAT; pregnancy test if applicable; HBV serology if not known; HCV Ab; creatinine, AST/ALT | **Today** |
| **4–6 weeks** | HIV Ag/Ab ± NAT (especially if any missed PEP doses or recent PrEP start) | **{d(28)} – {d(42)}** |
| **12 weeks (final)** | Lab-based HIV Ag/Ab **and** diagnostic HIV NAT | **{d(84)}** |
""")
    st.caption("2025 guidelines shortened routine follow-up; final testing by 12 weeks is the key endpoint for most HCP. Additional interim testing if adherence incomplete or high concern.")

# ---------- HBV SECTION ----------
st.header("6. Hepatitis B Management")
hbv_action = []
if hcp_hbv.startswith("Documented responder"):
    show_box("ok", "HBV: No action needed", "Documented vaccine responder (anti-HBs ≥10). Source HBsAg testing not required for the exposed person’s management.")
elif hcp_hbv.startswith("Documented non-responder"):
    if source_hbv in ["HBsAg-positive", "Unknown / cannot be tested"]:
        show_box("bad", "HBV PEP indicated (non-responder)",
                 "Give **HBIG 0.06 mL/kg IM as soon as possible** (preferably ≤24 h; efficacy uncertain >7 days). Repeat HBIG in 1 month. Vaccination generally not repeated if true non-responder after two series.")
        hbv_action.append("HBIG now + HBIG in 1 month")
    else:
        show_box("ok", "Source HBsAg-negative", "No HBIG needed for non-responder if source is documented HBsAg-negative.")
elif "response unknown" in hcp_hbv:
    if anti_hbs == "≥10 mIU/mL":
        show_box("ok", "Anti-HBs ≥10 — treat as responder", "No further HBV PEP needed.")
    else:
        if source_hbv in ["HBsAg-positive", "Unknown / cannot be tested"]:
            show_box("bad", "HBV PEP + revaccination",
                     "Give **HBIG 0.06 mL/kg IM once ASAP** + initiate hepatitis B vaccine series (or revaccination) at a separate site. Complete series and check anti-HBs 1–2 months after last dose.")
            hbv_action.append("HBIG ×1 + start/complete HepB vaccine")
        else:
            show_box("info", "Source negative — vaccinate if anti-HBs <10", "Initiate/complete vaccine series; check anti-HBs 1–2 mo after final dose.")
else:  # unvaccinated / incomplete
    if source_hbv in ["HBsAg-positive", "Unknown / cannot be tested"]:
        show_box("bad", "HBV PEP + vaccination",
                 "Give **HBIG 0.06 mL/kg IM once ASAP** (≤24 h preferred) **and** hepatitis B vaccine dose #1 at a separate anatomic site. Complete the vaccine series on schedule. Check anti-HBs 1–2 months after the last dose.")
        hbv_action.append("HBIG ×1 + HepB vaccine series")
    else:
        show_box("info", "Source HBsAg-negative — vaccinate", "Complete hepatitis B vaccine series; post-vaccination serology 1–2 months after final dose.")

st.markdown(f"""
**HBV follow-up testing (if susceptible and source positive/unknown):**  
- Baseline: total anti-HBc (and other HBV markers as indicated)  
- ~6 months: HBsAg + total anti-HBc  
- Target ~6-month date: **{d(180)}**
""")

# ---------- HCV SECTION ----------
st.header("7. Hepatitis C Management")
show_box("info", "No HCV PEP recommended",
         "CDC does **not** recommend post-exposure prophylaxis (including DAAs) for HCV after occupational exposure. Transmission risk is low (~0.2% percutaneous). Early testing and treatment if infection occurs is the strategy.")

if source_hcv in ["HCV RNA-positive (or anti-HCV+ with unknown RNA)", "Unknown / cannot be tested"]:
    st.markdown(f"""
**HCV testing schedule for exposed HCP (source positive or unknown):**

| Time point | Test | Target date |
|------------|------|-------------|
| **Baseline (≤48 h)** | Anti-HCV with reflex to HCV RNA if positive | **Today** |
| **3–6 weeks** | HCV RNA (NAT) | **{d(21)} – {d(42)}** |
| **4–6 months** | Anti-HCV (reflex RNA if positive). If already Ab+ at baseline, use RNA. | **{d(120)} – {d(180)}** |

If HCV RNA is detected at any time → refer for evaluation and treatment.
""")
    if immunosuppressed == "Yes":
        show_box("warn", "Immunosuppressed HCP", "Consider HCV RNA testing at the final time point even if antibody remains negative.")
else:
    show_box("ok", "Source HCV-negative", "No routine HCV follow-up testing required for the exposed person beyond baseline documentation.")

# ---------- PRECAUTIONS ----------
st.header("8. Precautions While Awaiting Follow-up / On PEP")
st.markdown("""
- **Do not donate** blood, plasma, organs, tissue, or semen during the follow-up period.
- Use **barrier protection** for sexual contact until final HIV (and if applicable HBV/HCV) testing is negative.
- Avoid pregnancy if possible until final HIV testing is complete; discuss contraception.
- If breastfeeding and on HIV PEP, discuss temporary interruption vs. continuation with expert input.
- Report any acute illness (fever, rash, lymphadenopathy, jaundice, flu-like symptoms) promptly.
- For HIV PEP: take every dose; set reminders; report side effects early (nausea, headache, fatigue are common).
- Occupational health / employee health should be notified per institutional policy.
""")

# ---------- SIMPLE INTERACTION CHECKER ----------
st.header("9. HIV PEP Medication Interaction Checker (basic)")
st.caption("This is a simplified checker for common issues only. Always use a full drug-interaction database and pharmacist review before prescribing.")
st.markdown("""
**Free full interaction databases (recommended):**
- **[Liverpool HIV Drug Interactions](https://www.hiv-druginteractions.org/)** — gold-standard free tool for ARV interactions (search by drug name or regimen)
- **[Liverpool HEP Drug Interactions](https://www.hep-druginteractions.org/)** — free tool for hepatitis drug interactions
- **[Drugs.com Interaction Checker](https://www.drugs.com/drug_interactions.html)** — free general interaction checker (useful for non-ARV meds)
""")

pep_choice = st.multiselect("Select the PEP agents you plan to use", [
    "Bictegravir (in Biktarvy)",
    "Dolutegravir",
    "Tenofovir alafenamide (TAF)",
    "Tenofovir DF (TDF)",
    "Emtricitabine (FTC)",
    "Lamivudine (3TC)",
    "Darunavir + cobicistat or ritonavir"
])
other_meds = st.text_input("List other current medications (comma-separated)", placeholder="e.g., metformin, omeprazole, atorvastatin, rifampin, St John’s wort")

if pep_choice or other_meds:
    st.subheader("Potential interaction notes")
    notes = []
    meds_lower = (other_meds or "").lower()
    if "Bictegravir" in str(pep_choice) or "Dolutegravir" in str(pep_choice):
        if any(x in meds_lower for x in ["rifampin", "rifampicin", "carbamazepine", "phenytoin", "st john", "st. john"]):
            notes.append("**Strong inducers** (rifampin, carbamazepine, phenytoin, St John’s wort) can significantly lower INSTI levels — avoid or use alternative PEP / expert consult.")
        if any(x in meds_lower for x in ["metformin"]):
            notes.append("Dolutegravir / bictegravir can increase metformin levels — monitor and consider metformin dose adjustment.")
        if any(x in meds_lower for x in ["aluminum", "magnesium", "calcium", "iron", "sucralfate", "antacid"]):
            notes.append("Polyvalent cations (antacids, Ca, Fe, Mg) can reduce INSTI absorption — separate dosing by several hours.")
    if "Darunavir" in str(pep_choice) or "cobicistat" in str(pep_choice).lower() or "ritonavir" in meds_lower:
        notes.append("Boosted darunavir has **many** interactions (statins, corticosteroids, certain antipsychotics, anticoagulants, etc.). Full interaction check mandatory.")
        if any(x in meds_lower for x in ["simvastatin", "lovastatin"]):
            notes.append("Simvastatin / lovastatin are contraindicated with boosted PIs.")
    if "Tenofovir DF" in str(pep_choice) or "TDF" in str(pep_choice):
        if any(x in meds_lower for x in ["nsaid", "ibuprofen", "naproxen", "aminoglycoside"]):
            notes.append("TDF + nephrotoxic agents (NSAIDs, aminoglycosides) increases renal risk — prefer TAF or monitor closely.")
    if renal.startswith("Moderate") or renal.startswith("Severe"):
        notes.append("Renal impairment: prefer TAF over TDF; adjust doses or avoid certain agents; expert/pharmacy input recommended.")
    if not notes:
        notes.append("No high-priority interactions flagged from the limited list entered. Still perform a complete interaction check before prescribing.")
    for n in notes:
        st.markdown(f"- {n}")

# ---------- SUMMARY ----------
st.header("10. Summary & Printable Plan")
st.markdown(f"""
**Exposure date:** {exp_date} (~{hours_since} h ago)  
**Exposure type:** {exposure_type} | Fluid: {fluid}

**HIV:** {"PEP indicated / strongly consider — start ASAP, 28-day course" if hiv_pep_indicated and hcp_hiv.startswith("Negative") else "PEP not indicated or already HIV+"}  
**HBV:** {"; ".join(hbv_action) if hbv_action else "See section 6 — often no PEP if documented responder"}  
**HCV:** No PEP; follow testing schedule if source positive/unknown

**Key follow-up dates (from today):**
- HIV interim (if needed): {d(28)}–{d(42)}
- HIV final (Ag/Ab + NAT): **{d(84)}**
- HCV RNA: {d(21)}–{d(42)}
- HCV final Ab/RNA: {d(120)}–{d(180)}
- HBV serology (~6 mo if indicated): **{d(180)}**

**Expert help:** PEPline **1-888-448-4911**
""")

st.success("Use browser Print (Ctrl/Cmd + P) to save this page as the exposure plan record.")

st.divider()
st.caption("""
Sources: 2025 USPHS Guidelines for the Management of Occupational Exposures to HIV (Infect Control Hosp Epidemiol 2025);  
CDC Hepatitis B occupational exposure guidance; CDC 2020/updated Hepatitis C HCP exposure testing guidance.  
This tool is educational only and must be used with official guidelines and clinical judgment.
""")
