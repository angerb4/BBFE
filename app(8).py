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
    "Vaccinated but response unknown (anti-HBs unknown or not documented)",
    "Unvaccinated or incompletely vaccinated"
])
anti_hbs = None
if "response unknown" in hcp_hbv or "Vaccinated but response unknown" in hcp_hbv:
    anti_hbs = st.radio("Current anti-HBs result", [
        "≥10 mIU/mL (immune)",
        "<10 mIU/mL (not immune)",
        "Not yet available — obtain ASAP and re-evaluate"
    ])

pregnant = st.radio("Pregnant?", ["No", "Yes", "Possibly / unknown"])
breastfeeding = st.radio("Breastfeeding?", ["No", "Yes"])
immunosuppressed = st.radio("Significant immunosuppression?", ["No", "Yes"])
renal = st.radio("Renal function", ["Normal (CrCl ≥50)", "Moderate impairment (CrCl 30–49)", "Severe impairment (CrCl <30)"])
on_prep = st.radio("Currently taking HIV PrEP?", ["No", "Yes"])
tetanus = st.radio("Tetanus immunization up to date? (typically within last 10 years; 5 years if dirty/tetanus-prone wound)", [
    "Yes — up to date",
    "No / unknown — tetanus booster indicated",
    "Not applicable (no percutaneous injury)"
])

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
hbv_followup_needed = False

if hcp_hbv.startswith("Documented responder"):
    show_box("ok", "HBV: Immune — no further action",
             "Documented vaccine responder (anti-HBs ≥10 mIU/mL). **No HBV PEP, no further HBV monitoring or follow-up testing needed** related to this exposure. Source HBsAg testing is not required for the exposed person’s management.")
elif hcp_hbv.startswith("Documented non-responder"):
    if source_hbv in ["HBsAg-positive", "Unknown / cannot be tested"]:
        show_box("bad", "HBV PEP indicated (documented non-responder)",
                 "Give **HBIG 0.06 mL/kg IM as soon as possible** (preferably ≤24 h; efficacy uncertain >7 days). Repeat HBIG in 1 month. Vaccination generally not repeated if true non-responder after two complete series.")
        hbv_action.append("HBIG now + HBIG in 1 month")
        hbv_followup_needed = True
    else:
        show_box("ok", "Source HBsAg-negative", "No HBIG needed for non-responder if source is documented HBsAg-negative.")
elif anti_hbs is not None:  # response unknown path
    if anti_hbs.startswith("≥10") or "immune" in anti_hbs.lower():
        show_box("ok", "Anti-HBs ≥10 mIU/mL — immune",
                 "**No HBV PEP and no further HBV monitoring or follow-up testing needed** related to this exposure. Treat as documented responder.")
    elif "Not yet available" in anti_hbs:
        show_box("warn", "Anti-HBs not yet available — obtain ASAP and re-evaluate",
                 "**Order anti-HBs immediately.** Do not delay other indicated PEP (HIV, HBIG if clearly indicated by other factors). Once anti-HBs result returns: if ≥10 mIU/mL → no further HBV action; if <10 mIU/mL → re-evaluate for HBIG ± vaccine per CDC table based on source HBsAg status.")
        hbv_action.append("Obtain anti-HBs ASAP and re-evaluate HBV PEP")
    else:  # <10
        if source_hbv in ["HBsAg-positive", "Unknown / cannot be tested"]:
            show_box("bad", "HBV PEP + revaccination (anti-HBs <10)",
                     "Give **HBIG 0.06 mL/kg IM once ASAP** + initiate hepatitis B vaccine series (or revaccination) at a separate anatomic site. Complete series and check anti-HBs 1–2 months after last dose.")
            hbv_action.append("HBIG ×1 + start/complete HepB vaccine")
            hbv_followup_needed = True
        else:
            show_box("info", "Source HBsAg-negative — vaccinate (anti-HBs <10)",
                     "Initiate/complete vaccine series; check anti-HBs 1–2 months after final dose. No HBIG needed.")
            hbv_action.append("Complete HepB vaccine series")
else:  # unvaccinated / incomplete
    if source_hbv in ["HBsAg-positive", "Unknown / cannot be tested"]:
        show_box("bad", "HBV PEP + vaccination",
                 "Give **HBIG 0.06 mL/kg IM once ASAP** (≤24 h preferred) **and** hepatitis B vaccine dose #1 at a separate anatomic site. Complete the vaccine series on schedule. Check anti-HBs 1–2 months after the last dose.")
        hbv_action.append("HBIG ×1 + HepB vaccine series")
        hbv_followup_needed = True
    else:
        show_box("info", "Source HBsAg-negative — vaccinate",
                 "Complete hepatitis B vaccine series; post-vaccination serology 1–2 months after final dose.")
        hbv_action.append("Complete HepB vaccine series")

if hbv_followup_needed:
    st.markdown(f"""
**HBV follow-up testing (susceptible + source positive/unknown):**  
- Baseline: total anti-HBc (and other HBV markers as indicated)  
- ~6 months: HBsAg + total anti-HBc  
- Target 6-month date: **{d(180)}**
""")
else:
    st.caption("No routine HBV post-exposure serologic follow-up required based on current selections (immune or source negative).")

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

# ---------- SUMMARY (clinical note–ready) ----------
st.header("10. Assessment / Plan Summary (copy-paste ready)")

# Build dynamic pieces
hiv_plan = "HIV PEP indicated — start ASAP (within 72 h of exposure), 28-day course per 2025 USPHS preferred regimen (BIC/FTC/TAF or DTG + TAF/TDF + FTC/3TC). Expert consult (PEPline 1-888-448-4911) for pregnancy, renal impairment, resistance concerns, or source with undetectable VL." if (hiv_pep_indicated and hcp_hiv.startswith("Negative")) else "HIV PEP not indicated based on current information (source HIV-negative or exposed person already HIV-positive)."
hbv_plan = "; ".join(hbv_action) if hbv_action else "HBV: no PEP required (documented immune / anti-HBs ≥10 or source HBsAg-negative)."
hcv_needed = source_hcv in ["HCV RNA-positive (or anti-HCV+ with unknown RNA)", "Unknown / cannot be tested"]
tetanus_plan = ""
if "tetanus" in dir() or "tetanus" in locals():
    pass
# tetanus variable from earlier
try:
    if tetanus.startswith("No"):
        tetanus_plan = "Tetanus booster indicated (immunization not up to date or unknown)."
    elif tetanus.startswith("Yes"):
        tetanus_plan = "Tetanus: up to date — no booster needed."
    else:
        tetanus_plan = "Tetanus: not applicable (no percutaneous injury)."
except NameError:
    tetanus_plan = "Tetanus status: not assessed."

# Prefer combined dates: use later end of ranges for single appointments
hiv_interim = d(42)          # later end of 4–6 wk
hiv_final = d(84)            # 12 weeks
hcv_rna = d(42)              # later end of 3–6 wk — can combine with HIV interim
hcv_final = d(180)           # later end of 4–6 mo
hbv_6mo = d(180)

labs_today = ["HIV Ag/Ab (lab or rapid) ± HIV NAT", "Pregnancy test if applicable"]
if hcv_needed or True:
    labs_today.append("HCV antibody with reflex to RNA if positive")
labs_today.append("HBV serology as indicated (anti-HBs if unknown; consider total anti-HBc / HBsAg if susceptible)")
labs_today.append("Creatinine, AST, ALT if starting HIV PEP")
if any("Not yet available" in str(x) for x in [anti_hbs]):
    labs_today.insert(0, "**Anti-HBs ASAP (result needed to finalize HBV PEP decision)**")

followup_lines = []
if hiv_pep_indicated and hcp_hiv.startswith("Negative"):
    followup_lines.append(f"- **{hiv_interim}** (≈6 weeks): HIV Ag/Ab ± NAT" + (" + HCV RNA" if hcv_needed else ""))
    followup_lines.append(f"- **{hiv_final}** (12 weeks): Final HIV Ag/Ab (lab-based) + diagnostic HIV NAT")
elif hcv_needed:
    followup_lines.append(f"- **{hcv_rna}** (≈6 weeks): HCV RNA (NAT)")
if hcv_needed:
    followup_lines.append(f"- **{hcv_final}** (6 months): HCV antibody (reflex RNA if positive)" + ("; HBV HBsAg + total anti-HBc if HBV follow-up indicated" if hbv_followup_needed else ""))
elif hbv_followup_needed:
    followup_lines.append(f"- **{hbv_6mo}** (6 months): HBsAg + total anti-HBc")
if not followup_lines:
    followup_lines.append("- No pathogen-specific post-exposure serologic follow-up required based on current risk assessment.")

summary_text = f"""
**Occupational bloodborne pathogen exposure — Assessment & Plan**

**Exposure:** {exp_date}, approximately {hours_since} hours prior. Type: {exposure_type}. Fluid: {fluid}.

**Source status:** HIV — {source_hiv}" + (f" (VL: {source_vl})" if source_vl else "") + f"; HBsAg — {source_hbv}; HCV — {source_hcv}.

**Exposed person:** Baseline HIV — {hcp_hiv}; HBV status — {hcp_hbv}" + (f" (anti-HBs: {anti_hbs})" if anti_hbs else "") + f". Pregnant: {pregnant}. Breastfeeding: {breastfeeding}. Immunosuppressed: {immunosuppressed}. Renal: {renal}. PrEP: {on_prep}.

**Plan**

1. **HIV:** {hiv_plan}

2. **HBV:** {hbv_plan}

3. **HCV:** No post-exposure prophylaxis recommended. {"Follow testing schedule below (source positive or unknown)." if hcv_needed else "Source HCV-negative — no routine HCV follow-up testing required beyond baseline."}

4. **Tetanus:** {tetanus_plan}

5. **Labs to collect today:**
""" + "\n".join(f"   - {x}" for x in labs_today) + f"""

6. **Follow-up laboratory monitoring** (dates calculated from today; later date of any range used to allow combined visits when possible):
""" + "\n".join(followup_lines) + f"""

7. **Precautions until final testing is negative:**
   - Do not donate blood, plasma, organs, tissue, or semen.
   - Use barrier protection for sexual contact.
   - Avoid pregnancy if possible; discuss contraception.
   - If breastfeeding and on HIV PEP, discuss temporary interruption vs continuation with expert input.
   - Report any acute illness promptly.

8. **Seek immediate medical care** for fever, rash, lymphadenopathy, jaundice, dark urine, pale stools, severe fatigue, flu-like symptoms, or any other concerns for acute HIV, hepatitis B, or hepatitis C infection.

9. **Expert consultation:** PEPline 1-888-448-4911 for complex cases (pregnancy, resistance, renal/hepatic impairment, source with undetectable viral load, etc.).

Occupational health / employee health notified per institutional policy. Patient educated on the above plan and warning signs.
"""

# Fix the f-string construction that got messy — rebuild cleanly
summary_text = f"""**Occupational bloodborne pathogen exposure — Assessment & Plan**

**Exposure:** {exp_date}, approximately {hours_since} hours prior. Type: {exposure_type}. Fluid: {fluid}.

**Source status:** HIV — {source_hiv}"""
if source_vl:
    summary_text += f" (VL: {source_vl})"
summary_text += f"""; HBsAg — {source_hbv}; HCV — {source_hcv}.

**Exposed person:** Baseline HIV — {hcp_hiv}; HBV status — {hcp_hbv}"""
if anti_hbs:
    summary_text += f" (anti-HBs: {anti_hbs})"
summary_text += f""". Pregnant: {pregnant}. Breastfeeding: {breastfeeding}. Immunosuppressed: {immunosuppressed}. Renal: {renal}. PrEP: {on_prep}.

**Plan**

1. **HIV:** {hiv_plan}

2. **HBV:** {hbv_plan}

3. **HCV:** No post-exposure prophylaxis recommended. {"Follow testing schedule below (source positive or unknown)." if hcv_needed else "Source HCV-negative — no routine HCV follow-up testing required beyond baseline."}

4. **Tetanus:** {tetanus_plan}

5. **Labs to collect today:**
"""
for x in labs_today:
    summary_text += f"   - {x}\n"
summary_text += f"""
6. **Follow-up laboratory monitoring** (dates from today; later end of ranges used so HIV and HCV can be drawn together when both apply):
"""
for line in followup_lines:
    summary_text += line + "\n"
summary_text += f"""
7. **Precautions until final testing is negative:**
   - Do not donate blood, plasma, organs, tissue, or semen.
   - Use barrier protection for sexual contact.
   - Avoid pregnancy if possible; discuss contraception.
   - If breastfeeding and on HIV PEP, discuss temporary interruption vs continuation with expert input.
   - Report any acute illness promptly.

8. **Seek immediate medical care** for fever, rash, lymphadenopathy, jaundice, dark urine, pale stools, severe fatigue, flu-like symptoms, or any other concerns for acute HIV, hepatitis B, or hepatitis C infection.

9. **Expert consultation:** PEPline 1-888-448-4911 for complex cases (pregnancy, resistance, renal/hepatic impairment, source with undetectable viral load, etc.).

Occupational health / employee health notified per institutional policy. Patient educated on the above plan and warning signs.
"""

st.code(summary_text, language=None)
st.success("Copy the text above and paste directly into the Assessment/Plan section of the clinical note. Use browser Print (Ctrl/Cmd+P) if a PDF copy is needed.")

st.divider()
st.caption("""
Sources: 2025 USPHS Guidelines for the Management of Occupational Exposures to HIV; CDC Hepatitis B occupational exposure guidance; CDC HCV HCP exposure testing guidance.  
This tool is an educational/clinical reference aid only and does not replace official guidelines or clinical judgment.
""")
