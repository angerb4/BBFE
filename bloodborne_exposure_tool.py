import streamlit as st
from datetime import date, timedelta

st.set_page_config(page_title="Occupational Bloodborne Pathogen Exposure Tool", page_icon="🧪", layout="wide")

# Clinical decision support only. Verify local policy, current CDC/USPHS guidance,
# product labeling, and expert consultation before acting.

SOURCES = {
    "CDC 2025 occupational HIV PEP guideline": "https://stacks.cdc.gov/view/cdc/183609",
    "CDC 2025 HIV PEP recommendations": "https://www.cdc.gov/mmwr/volumes/74/rr/rr7401a1.htm",
    "CDC HBV occupational exposure guidance": "https://www.cdc.gov/hepatitis-b/hcp/infection-control/index.html",
    "CDC HBV treatment table": "https://www.cdc.gov/hepatitis-b/hcp/infection-control/table-1.html",
    "CDC HCV occupational exposure guidance": "https://www.cdc.gov/hepatitis-c/hcp/infection-control/index.html",
    "CDC HCV MMWR 2020": "https://www.cdc.gov/mmwr/volumes/69/rr/rr6906a1.htm",
    "NCCC PEPline": "https://nccc.ucsf.edu/clinician-consultation/pep-post-exposure-prophylaxis/",
    "Liverpool HIV interaction checker": "https://www.hiv-druginteractions.org/",
    "NIH HIV drug interaction guidance": "https://clinicalinfo.hiv.gov/en/guidelines/hiv-clinical-guidelines-adult-adolescent-arv/drug-interactions-overview",
}

# ---------------------------- helpers ----------------------------
def yes_no(label, key, help_text=None):
    return st.radio(label, ["Yes", "No", "Unknown / not available"], horizontal=True, key=key, help=help_text)

def add_days(d, n):
    return d + timedelta(days=n)

def fmt(d):
    return d.strftime("%B %-d, %Y") if hasattr(d, "strftime") else str(d)

def later_date(exposure_date, days):
    return fmt(add_days(exposure_date, days))

def status_is_yes(x):
    return x == "Yes"

def bullet(items):
    return "\n".join(f"- {x}" for x in items if x)

# ---------------------------- header ----------------------------
st.title("Occupational Bloodborne Pathogen Exposure Decision Tool")
st.warning(
    "Urgent clinical decision support for occupational exposure to blood or potentially infectious body fluids. "
    "This tool does not replace occupational-health protocols, infectious-disease consultation, product labeling, or current CDC/USPHS guidance."
)

with st.sidebar:
    st.header("Direct references")
    for label, url in SOURCES.items():
        st.markdown(f"[{label}]({url})")
    st.divider()
    st.caption("CDC-based embedded logic: HIV occupational PEP (2025), HBV occupational exposure guidance, and HCV occupational exposure guidance (2020; CDC page updated 2024).")

# ---------------------------- 1. encounter ----------------------------
st.header("1. Exposure and encounter")
col1, col2, col3 = st.columns(3)
with col1:
    exposure_date = st.date_input("Exposure date", value=date.today(), key="exposure_date")
with col2:
    exposure_time_known = yes_no("Is the exposure time known?", "exposure_time_known")
with col3:
    hours_since = st.number_input("Hours since exposure (best estimate)", min_value=0.0, max_value=10000.0, value=0.0, step=1.0, key="hours_since")

evaluation_date = date.today()
st.caption(f"Assessment/laboratory collection date: **{fmt(evaluation_date)}**. Follow-up dates are calculated from the exposure date unless otherwise specified.")

if hours_since <= 24:
    timing_label = "≤24 hours"
elif hours_since <= 72:
    timing_label = ">24 to 72 hours"
else:
    timing_label = ">72 hours"
st.info(f"Timing category: **{timing_label}**. HIV PEP, when indicated, should begin as soon as possible and no later than 72 hours; expert consultation is required for decisions beyond 72 hours.")

exposure_type = st.radio(
    "Primary exposure type",
    ["Percutaneous injury", "Mucous membrane exposure", "Nonintact skin exposure", "Intact skin only", "No true exposure / uncertain"],
    key="exposure_type",
)
fluid = st.radio(
    "Source material involved",
    [
        "Blood or visibly bloody fluid",
        "Potentially infectious sterile-site fluid (CSF, synovial, pleural, peritoneal, pericardial, amniotic)",
        "Semen or vaginal/rectal fluid",
        "Saliva, tears, sweat, urine, feces, vomitus, sputum, or nasal secretions without visible blood",
        "Unknown",
    ],
    key="fluid",
)

device_high_risk = "No"
if exposure_type == "Percutaneous injury":
    device_high_risk = yes_no("Was this a deep injury, hollow-bore needle, needle in a vein/artery, or device visibly contaminated with blood?", "device_high_risk")

st.subheader("Immediate first aid")
st.markdown(
    "Wash skin or wounds with soap and water; flush mucous membranes/eyes with water or saline; do not squeeze, milk, scrub, or apply bleach/caustic agents. Report the exposure immediately to occupational health and follow the facility exposure protocol."
)

# ---------------------------- 2. source ----------------------------
st.header("2. Source-patient evaluation")
source_hiv = st.radio("Source HIV status", ["Positive", "Negative", "Unknown / pending"], key="source_hiv")
source_hiv_viral = st.radio("If source is HIV-positive, viral load status", ["Detectable / unknown", "Sustained undetectable", "Not applicable / unknown"], key="source_hiv_viral")
source_hiv_resistance = yes_no("Known or suspected HIV drug resistance in the source?", "source_hiv_resistance")
source_hiv_acute = yes_no("Concern for acute HIV infection in the source despite a negative/unknown test?", "source_hiv_acute")

source_hbv = st.radio("Source HBsAg status", ["Positive", "Negative", "Unknown / pending"], key="source_hbv")
source_hcv = st.radio("Source HCV status", ["HCV RNA positive", "Anti-HCV positive; RNA unknown", "HCV RNA negative", "Negative / no evidence of infection", "Unknown / cannot test"], key="source_hcv")

st.caption("Source testing: obtain HIV testing promptly when indicated; for HCV, HCV RNA is preferred, or anti-HCV with reflex RNA; for HBV, HBsAg is the key source test for postexposure decisions.")

# ---------------------------- 3. exposed person ----------------------------
st.header("3. Exposed-person circumstances")
pregnancy = st.radio("Pregnancy status", ["Not pregnant", "Pregnant", "Possible / test pending", "Not applicable"], key="pregnancy")
breastfeeding = st.radio("Breastfeeding", ["No", "Yes", "Not applicable"], key="breastfeeding")
immunosuppression = yes_no("Immunosuppression, HIV infection, transplant, chemotherapy, biologic therapy, or high-dose steroids?", "immunosuppression")
liver_disease = yes_no("Known liver disease or abnormal baseline liver tests?", "liver_disease")
renal_disease = yes_no("Known kidney disease, dialysis, or abnormal baseline creatinine?", "renal_disease")
pr_ep = yes_no("Taking HIV PrEP or recently received long-acting injectable HIV prevention/treatment?", "prep")
allergies = st.text_input("Medication allergies", key="allergies")
current_meds = st.text_area("Current prescription medications, OTC medications, vitamins, minerals, and herbal products", key="current_meds")

# ---------------------------- 4. baseline labs ----------------------------
st.header("4. Baseline laboratory collection today")
needs_hiv_evaluation = not (exposure_type in ["Intact skin only", "No true exposure / uncertain"] and fluid.startswith("Saliva"))

baseline_labs = [
    "HIV laboratory-based 4th-generation Ag/Ab test (do not delay indicated PEP while awaiting result)",
    "Serum creatinine/eGFR or calculated creatinine clearance",
    "AST and ALT",
    "HBV triple panel: HBsAg, anti-HBs, total anti-HBc",
    "HCV antibody with reflex HCV RNA if positive",
]
if pregnancy in ["Pregnant", "Possible / test pending"]:
    baseline_labs.append("Pregnancy test if not already confirmed")
if pr_ep == "Yes":
    baseline_labs.append("HIV-1 diagnostic NAT; strongly consider/obtain if recent injectable ARV exposure or recent oral PrEP use")
if source_hiv == "Positive" or source_hiv == "Unknown / pending":
    baseline_labs.append("Consider baseline HIV-1 diagnostic NAT when clinically indicated, especially with recent ARV exposure or concern for acute infection")

st.markdown(bullet(baseline_labs))
st.caption("Baseline HCV testing is preferably obtained within 48 hours. Baseline HBV testing is especially important when vaccination or anti-HBs status is incomplete or unknown.")

# ---------------------------- 5. HBV ----------------------------
st.header("5. Hepatitis B decision pathway")
hbv_status = st.radio(
    "Exposed person's HepB vaccination/immune status",
    [
        "Documented responder: complete series and documented anti-HBs ≥10 mIU/mL",
        "Complete series; anti-HBs not previously documented",
        "Documented nonresponder after two complete vaccine series",
        "Unvaccinated or incompletely vaccinated",
        "Vaccination status unknown",
    ],
    key="hbv_status",
)
anti_hbs_available = "Not applicable"
anti_hbs_value = None
if hbv_status == "Complete series; anti-HBs not previously documented":
    anti_hbs_available = st.radio("Is current anti-HBs available now?", ["Yes", "No"], key="anti_hbs_available")
    if anti_hbs_available == "Yes":
        anti_hbs_value = st.number_input("Anti-HBs result (mIU/mL)", min_value=0.0, value=0.0, step=1.0, key="anti_hbs_value")
    else:
        st.info("Obtain anti-HBs as quickly as possible and re-evaluate the HBV pathway when the result is available.")

hbv_actions = []
hbv_followup = []
hbv_decision = ""
final_hbv_vaccine_date = None
if hbv_status in ["Unvaccinated or incompletely vaccinated", "Vaccination status unknown"] or (hbv_status == "Complete series; anti-HBs not previously documented" and anti_hbs_available == "Yes" and anti_hbs_value < 10):
    final_hbv_vaccine_date = st.date_input("Actual or planned date of final HepB vaccine dose", value=add_days(exposure_date, 180), min_value=exposure_date, key="final_hbv_vaccine_date")

if hbv_status == "Documented responder: complete series and documented anti-HBs ≥10 mIU/mL":
    hbv_decision = "Immune: no HBV postexposure prophylaxis, monitoring, or follow-up is needed."
    hbv_actions.append(hbv_decision)
elif hbv_status == "Complete series; anti-HBs not previously documented" and anti_hbs_available == "No":
    hbv_decision = "Anti-HBs unavailable: obtain anti-HBs as quickly as possible and re-evaluate. Do not assume immunity from vaccination history alone."
    hbv_actions.append(hbv_decision)
elif hbv_status == "Complete series; anti-HBs not previously documented" and anti_hbs_available == "Yes":
    if anti_hbs_value >= 10:
        hbv_decision = "Anti-HBs >10 mIU/mL: immune; no further HBV monitoring or follow-up is needed."
        hbv_actions.append(hbv_decision)
    else:
        if source_hbv in ["Positive", "Unknown / pending"]:
            hbv_decision = "Anti-HBs <10 with HBsAg-positive/unknown source: give HBIG once and initiate revaccination as soon as possible; complete the second vaccine series."
            hbv_actions.append(hbv_decision)
        else:
            hbv_decision = "Anti-HBs <10 with HBsAg-negative source: give one HepB vaccine dose now; repeat anti-HBs 1–2 months after the final vaccine dose."
            hbv_actions.append(hbv_decision)
elif hbv_status == "Documented nonresponder after two complete vaccine series":
    if source_hbv in ["Positive", "Unknown / pending"]:
        hbv_decision = "Give HBIG now and a second HBIG dose 1 month later; no additional HepB vaccine is routinely indicated after two complete series."
        hbv_actions.append(hbv_decision)
        hbv_followup.append(f"HBIG dose 2: {later_date(exposure_date, 30)} (approximately 1 month after dose 1)")
    else:
        hbv_decision = "Source HBsAg negative: no HBV postexposure prophylaxis is needed."
        hbv_actions.append(hbv_decision)
elif hbv_status in ["Unvaccinated or incompletely vaccinated", "Vaccination status unknown"]:
    if source_hbv in ["Positive", "Unknown / pending"]:
        hbv_decision = "Give HBIG once and HepB vaccine as soon as possible at separate injection sites; complete the vaccine series."
        hbv_actions.append(hbv_decision)
    else:
        hbv_decision = "Start or complete the HepB vaccine series as soon as possible; HBIG is not indicated when the source is HBsAg negative."
        hbv_actions.append(hbv_decision)

susceptible_or_uncertain = hbv_status != "Documented responder: complete series and documented anti-HBs ≥10 mIU/mL" and not (hbv_status == "Complete series; anti-HBs not previously documented" and anti_hbs_available == "Yes" and anti_hbs_value >= 10)
if susceptible_or_uncertain and source_hbv in ["Positive", "Unknown / pending"]:
    hbv_followup.insert(0, f"{fmt(evaluation_date)}: total anti-HBc baseline testing if not already collected")
    hbv_followup.append(f"6-month HBV follow-up: HBsAg and total anti-HBc on {later_date(exposure_date, 183)}")
if final_hbv_vaccine_date:
    hbv_followup.append(f"Anti-HBs: {fmt(add_days(final_hbv_vaccine_date, 60))} (1–2 months after final vaccine dose; use the later date if a range is needed, and delay until at least 6 months after HBIG if HBIG was given)")

st.success(hbv_decision or "HBV pathway requires completion of the questions above.")
if hbv_followup:
    st.markdown("**HBV testing/treatment schedule:**\n" + bullet(hbv_followup))

# ---------------------------- 6. HIV ----------------------------
st.header("6. HIV occupational PEP decision pathway")
true_exposure = exposure_type in ["Percutaneous injury", "Mucous membrane exposure", "Nonintact skin exposure"]
potentially_infectious_fluid = fluid in ["Blood or visibly bloody fluid", "Potentially infectious sterile-site fluid (CSF, synovial, pleural, peritoneal, pericardial, amniotic)", "Semen or vaginal/rectal fluid"]

hiv_pep_indicated = False
hiv_reason = ""
expert_flags = []

if not true_exposure or not potentially_infectious_fluid:
    hiv_reason = "No HIV PEP is generally indicated for intact-skin contact, noninfectious fluids without blood, or no true exposure. Document the event and follow local occupational-health protocol."
elif hours_since > 72:
    hiv_reason = "Exposure is beyond 72 hours: HIV PEP benefit is uncertain; obtain urgent HIV/ID expert consultation, especially if the exposure was high risk."
    expert_flags.append(">72 hours since exposure")
elif source_hiv == "Positive" and source_hiv_viral == "Sustained undetectable":
    hiv_reason = "Source has sustained undetectable HIV RNA: transmission risk is likely very low, but occupational PEP is a case-by-case shared decision based on exposure severity; consult an HIV expert."
    expert_flags.append("Source HIV RNA sustained undetectable")
    if device_high_risk == "Yes" or exposure_type == "Percutaneous injury":
        hiv_pep_indicated = True
elif source_hiv == "Positive":
    hiv_pep_indicated = True
    hiv_reason = "Source is HIV-positive and the exposure involves potentially infectious material contacting percutaneous tissue, mucosa, or nonintact skin: start PEP immediately."
elif source_hiv == "Unknown / pending":
    hiv_pep_indicated = True
    hiv_reason = "Source HIV status is unknown/pending and the exposure is potentially substantial risk: start PEP immediately while obtaining source testing; stop PEP if the source is confirmed HIV-negative."
    expert_flags.append("Source HIV status unknown/pending")
else:
    hiv_reason = "Source HIV test is negative; HIV PEP is not indicated unless there is a specific concern for acute HIV infection/window-period infection, in which case obtain expert consultation."
    if source_hiv_acute == "Yes":
        hiv_pep_indicated = True
        expert_flags.append("Concern for acute HIV infection in source")

if source_hiv_resistance == "Yes":
    expert_flags.append("Known/suspected source drug resistance")
if pregnancy in ["Pregnant", "Possible / test pending"]:
    expert_flags.append("Pregnancy or possible pregnancy")
if breastfeeding == "Yes":
    expert_flags.append("Breastfeeding")
if immunosuppression == "Yes":
    expert_flags.append("Immunosuppression")
if renal_disease == "Yes":
    expert_flags.append("Renal disease/abnormal creatinine")
if liver_disease == "Yes":
    expert_flags.append("Liver disease/abnormal AST or ALT")
if pr_ep == "Yes":
    expert_flags.append("PrEP or recent injectable ARV exposure")

st.write(f"**HIV pathway:** {hiv_reason}")
if expert_flags:
    st.warning("Expert consultation recommended for: " + ", ".join(expert_flags) + ". Do not delay the first indicated dose while arranging consultation.")

hiv_regimen = ""
interim_hiv_needed = False
if hiv_pep_indicated:
    regimen_group = st.radio(
        "Select the initial HIV PEP regimen pathway",
        [
            "Preferred: BIC/FTC/TAF (Biktarvy) once daily for 28 days",
            "Preferred: DTG plus TAF or TDF plus FTC or 3TC once daily for 28 days",
            "Alternative: boosted darunavir plus TAF or TDF plus FTC or 3TC for 28 days",
            "Need specialist-directed regimen",
        ],
        key="regimen_group",
    )
    if regimen_group.startswith("Preferred: BIC"):
        hiv_regimen = "Bictegravir/emtricitabine/tenofovir alafenamide (BIC/FTC/TAF; Biktarvy) 50/200/25 mg PO once daily for 28 days."
    elif regimen_group.startswith("Preferred: DTG"):
        hiv_regimen = "Dolutegravir 50 mg PO once daily PLUS tenofovir alafenamide 25 mg or tenofovir disoproxil fumarate 300 mg PLUS emtricitabine 200 mg or lamivudine 300 mg PO once daily for 28 days; renal/hepatic dosing must be verified."
    elif regimen_group.startswith("Alternative"):
        hiv_regimen = "Darunavir plus ritonavir or cobicistat PLUS tenofovir alafenamide or tenofovir disoproxil fumarate PLUS emtricitabine or lamivudine for 28 days; use ritonavir rather than cobicistat in pregnancy and consult an expert."
    else:
        hiv_regimen = "Specialist-directed 3-drug regimen; consult the NCCC PEPline/ID specialist immediately."
    st.error(f"**START HIV PEP NOW:** {hiv_regimen}")
    st.markdown("PEP administration: first dose as soon as possible; do not delay for pending laboratory results. Complete 28 days unless an HIV expert directs otherwise or the source is confirmed HIV-negative.")

hiv_followup = []
if hiv_pep_indicated or source_hiv in ["Positive", "Unknown / pending"] or true_exposure:
    hiv_followup.append(f"{fmt(evaluation_date)}: HIV laboratory-based 4th-generation Ag/Ab test; HIV-1 diagnostic NAT when indicated (especially recent injectable ARV/PrEP exposure or acute HIV concern)")
    interim_hiv_needed = hiv_pep_indicated and (hours_since > 24 or pr_ep == "Yes" or source_hiv_resistance == "Yes" or immunosuppression == "Yes")
    if interim_hiv_needed:
        hiv_followup.append(f"Interim HIV testing: laboratory HIV Ag/Ab plus diagnostic HIV NAT on {later_date(exposure_date, 42)} (6 weeks; later date selected from the CDC 4–6-week range)")
    hiv_followup.append(f"Final HIV testing: laboratory HIV Ag/Ab plus diagnostic HIV NAT on {later_date(exposure_date, 84)} (12 weeks)")
    hiv_followup.append(f"Clinical/medication access check within 24 hours: {later_date(exposure_date, 1)}")
    hiv_followup.append(f"Clinical reassessment by 72 hours after exposure: {later_date(exposure_date, 3)}")

# ---------------------------- 7. HCV ----------------------------
st.header("7. Hepatitis C pathway")
hcv_followup = []
if source_hcv in ["HCV RNA positive", "Anti-HCV positive; RNA unknown", "Unknown / cannot test"]:
    hcv_followup.append(f"{fmt(evaluation_date)} (within 48 hours): exposed-person anti-HCV with reflex HCV RNA if positive")
    hcv_followup.append(f"HCV RNA NAT at 6 weeks: {later_date(exposure_date, 42)}")
    hcv_followup.append(f"Final HCV anti-HCV with reflex HCV RNA if positive at 6 months: {later_date(exposure_date, 183)}")
    if immunosuppression == "Yes" or liver_disease == "Yes":
        hcv_followup.append("Because of immunosuppression or liver disease, consider HCV RNA at the final follow-up even if anti-HCV remains negative.")
    hcv_decision = "HCV PEP with direct-acting antivirals is not recommended. Use testing and prompt treatment if infection is detected."
elif source_hcv == "HCV RNA negative":
    hcv_decision = "No routine HCV follow-up is needed if the source is confirmed HCV RNA negative and specimen integrity is reliable; test sooner if symptoms develop."
else:
    hcv_decision = "Source HCV testing is pending/uncertain; arrange source HCV RNA testing if possible and use the follow-up schedule above when source status cannot be established."

st.write(hcv_decision)
if hcv_followup:
    st.markdown("**HCV schedule:**\n" + bullet(hcv_followup))
st.caption("If acute hepatitis symptoms develop at any point, obtain HCV RNA immediately. Any detectable HCV RNA requires referral for evaluation and treatment.")

# ---------------------------- 8. precautions ----------------------------
st.header("8. Precautions and counseling")
tetanus = st.radio("Is tetanus vaccination up to date?", ["Yes", "No / due", "Unknown"], key="tetanus")
precautions = [
    "Continue standard patient-care duties unless occupational health identifies another restriction; routine work restriction is not required solely because of an exposure.",
    "Do not donate blood, plasma, organs, tissue, or semen during the follow-up period.",
    "Use barrier protection and avoid sharing injection equipment until HIV infection has been excluded at final follow-up; use additional precautions if infection is diagnosed.",
    "Do not share razors, toothbrushes, or other items that may be contaminated with blood; cover open wounds.",
    "Breastfeeding: HBV exposure alone does not require stopping breastfeeding. If HIV PEP is indicated, discuss continuing versus temporarily interrupting breastfeeding or pumping/discarding milk with the patient, obstetric/pediatric clinician, and HIV expert.",
    "Pregnancy: pregnancy is not a reason to withhold indicated HIV PEP; urgently involve obstetrics and an HIV/perinatal expert in regimen selection and counseling.",
    "Immunosuppression: use closer clinical follow-up; consider additional HCV RNA testing if serologic follow-up may be delayed or unreliable.",
    "Seek immediate medical care for fever, rash, lymphadenopathy, severe fatigue, sore throat, jaundice, dark urine, abdominal pain, nausea/vomiting, unusual bleeding, or other symptoms concerning for acute HIV, HBV, HCV, medication toxicity, or allergic reaction.",
]
if tetanus in ["No / due", "Unknown"]:
    precautions.append("Review wound characteristics and administer tetanus vaccination/Tdap or Td according to current wound-management guidance and immunization history.")

st.markdown(bullet(precautions))

# ---------------------------- 9. interactions ----------------------------
st.header("9. HIV PEP medication interaction checker")
interaction_items = st.multiselect(
    "Select any current medication/supplement categories to screen",
    [
        "Dofetilide",
        "Rifampin or rifabutin",
        "Antacids or supplements containing aluminum, magnesium, calcium, or iron",
        "Metformin",
        "Carbamazepine, phenytoin, phenobarbital, or oxcarbazepine",
        "St. John's wort",
        "Warfarin or other anticoagulant",
        "Hormonal contraception or hormone therapy",
        "Statin or other lipid-lowering medication",
        "Methadone or buprenorphine",
        "Other prescription/OTC/herbal medication",
    ],
    key="interaction_items",
)
interaction_notes = []
if "Dofetilide" in interaction_items:
    interaction_notes.append("Dofetilide: contraindicated with dolutegravir and bictegravir; do not select those regimens without specialist direction.")
if "Rifampin or rifabutin" in interaction_items:
    interaction_notes.append("Rifampin/rifabutin: major interactions with bictegravir, dolutegravir, and boosted regimens; urgent HIV pharmacist/ID consultation is required.")
if "Antacids or supplements containing aluminum, magnesium, calcium, or iron" in interaction_items:
    interaction_notes.append("Polyvalent cations reduce integrase-inhibitor absorption: separate BIC/DTG from aluminum or magnesium products by 2 hours before or 6 hours after; verify exact product instructions.")
if "Metformin" in interaction_items:
    interaction_notes.append("Dolutegravir can increase metformin exposure; verify dosing and monitoring with the prescriber/pharmacist.")
if any(x in interaction_items for x in ["Carbamazepine, phenytoin, phenobarbital, or oxcarbazepine", "St. John's wort"]):
    interaction_notes.append("Enzyme-inducing anticonvulsants and St. John's wort can substantially reduce antiretroviral concentrations; avoid empiric selection without expert consultation.")
if "Hormonal contraception or hormone therapy" in interaction_items:
    interaction_notes.append("Review the exact hormonal product. Boosted protease-inhibitor regimens have more interaction potential; preferred INSTI-based options generally have fewer clinically important interactions.")
if "Methadone or buprenorphine" in interaction_items:
    interaction_notes.append("Methadone and buprenorphine can generally be used with preferred PEP regimens, but assess sedation, withdrawal, and adherence clinically.")
if "Other prescription/OTC/herbal medication" in interaction_items or current_meds:
    interaction_notes.append("Run the complete verified medication list through the Liverpool HIV interaction checker before finalizing the regimen.")
if interaction_notes:
    st.warning("\n".join(f"- {x}" for x in interaction_notes))
else:
    st.info("No selected high-risk interaction category. A complete medication reconciliation and formal interaction check are still required.")
st.markdown(f"[Open the University of Liverpool HIV interaction checker]({SOURCES['Liverpool HIV interaction checker']})")

# Consolidated, explicit dated laboratory orders for the paste-ready plan.
dated_lab_orders = [f"{fmt(evaluation_date)}: " + "; ".join(baseline_labs)]
if hiv_pep_indicated or source_hiv in ["Positive", "Unknown / pending"] or true_exposure:
    if interim_hiv_needed:
        combo = [f"HIV laboratory 4th-generation Ag/Ab + HIV-1 diagnostic NAT — {fmt(add_days(exposure_date, 42))}"]
        if source_hcv in ["HCV RNA positive", "Anti-HCV positive; RNA unknown", "Unknown / cannot test"]:
            combo.append(f"HCV RNA NAT — {fmt(add_days(exposure_date, 42))}")
        dated_lab_orders.append("; ".join(combo))
    dated_lab_orders.append(f"HIV laboratory 4th-generation Ag/Ab + HIV-1 diagnostic NAT — {fmt(add_days(exposure_date, 84))}")
if source_hcv in ["HCV RNA positive", "Anti-HCV positive; RNA unknown", "Unknown / cannot test"] and not interim_hiv_needed:
    dated_lab_orders.append(f"HCV RNA NAT — {fmt(add_days(exposure_date, 42))}")
if source_hcv in ["HCV RNA positive", "Anti-HCV positive; RNA unknown", "Unknown / cannot test"]:
    dated_lab_orders.append(f"HCV anti-HCV with reflex HCV RNA if positive — {fmt(add_days(exposure_date, 183))}")
if susceptible_or_uncertain and source_hbv in ["Positive", "Unknown / pending"]:
    dated_lab_orders.append(f"HBsAg + total anti-HBc — {fmt(add_days(exposure_date, 183))}")
if final_hbv_vaccine_date:
    dated_lab_orders.append(f"Anti-HBs — {fmt(add_days(final_hbv_vaccine_date, 60))} (1–2 months after final HepB vaccine dose)")
dated_lab_orders = list(dict.fromkeys(dated_lab_orders))

# ---------------------------- 10. summary ----------------------------
st.header("10. Paste-ready assessment/plan")
summary_lines = []
summary_lines.append(f"Occupational exposure to bloodborne pathogens on {fmt(exposure_date)} ({timing_label} at evaluation). Exposure: {exposure_type}; source material: {fluid}.")
summary_lines.append("Immediate decontamination performed/advised: wash skin/wound with soap and water; irrigate mucous membranes/eyes with water or saline; do not squeeze, milk, scrub, or apply caustic agents. Exposure reported to occupational health.")
summary_lines.append(f"Baseline labs ordered/collected on {fmt(evaluation_date)}: " + "; ".join(baseline_labs) + ".")
summary_lines.append("Dated laboratory orders: " + " | ".join(dated_lab_orders) + ".")
summary_lines.append("HBV plan: " + (hbv_decision or "complete HBV decision pathway") + ".")
if hbv_followup:
    summary_lines.append("HBV follow-up: " + "; ".join(hbv_followup) + ".")
summary_lines.append("HIV plan: " + hiv_reason)
if hiv_pep_indicated:
    summary_lines.append("HIV PEP: " + hiv_regimen + " First dose should be given immediately/as soon as possible; complete 28 days unless directed otherwise by an HIV expert or source testing establishes HIV-negative status.")
if hiv_followup:
    summary_lines.append("HIV follow-up: " + "; ".join(hiv_followup) + ".")
summary_lines.append("HCV plan: " + hcv_decision + ".")
if hcv_followup:
    summary_lines.append("HCV follow-up: " + "; ".join(hcv_followup) + ".")
summary_lines.append("Precautions: " + " ".join(precautions))
if tetanus in ["No / due", "Unknown"]:
    summary_lines.append("Tetanus: review immunization history and wound category; administer Tdap/Td if indicated.")
else:
    summary_lines.append("Tetanus: reported up to date; verify documentation and wound-specific indication.")
summary_lines.append("Patient instructed to seek immediate medical care for concerns, medication reactions, or symptoms consistent with acute HIV, hepatitis B, or hepatitis C, including fever, rash, sore throat, lymphadenopathy, severe fatigue, jaundice, dark urine, abdominal pain, nausea/vomiting, or unusual bleeding.")
if expert_flags:
    summary_lines.append("Expert consultation recommended for: " + ", ".join(expert_flags) + ".")

summary_text = "\n\n".join(summary_lines)
st.text_area("Assessment/plan text", value=summary_text, height=520, key="summary_text")

st.divider()
st.caption("Embedded references: CDC/USPHS 2025 occupational HIV PEP guidance; CDC HBV occupational exposure guidance; CDC HCV occupational exposure guidance. Always verify updates before clinical use.")
