import streamlit as st
import json
import os

# --- 1. CONFIGURATION & DATA INITIALIZATION ---
DATA_DIR = 'data'
DATA_FILE = os.path.join(DATA_DIR, 'drugs.json')

# Define the dataset
INITIAL_DATA = {
    "drugs": [
        {"name": "Epinephrine (Cardiac Arrest)", "category": "Cardiac Arrest", "type": "static", "dose": 1.0, "unit": "mg", "max_dose": 1.0, "prep": "1 mg/10 mL pre-filled syringe (1:10,000)", "safety_alert": "Peripheral extravasation risk. Central line preferred post-ROSC."},
        {"name": "Amiodarone (Cardiac Arrest)", "category": "Cardiac Arrest", "type": "static", "dose": 300.0, "unit": "mg", "max_dose": 300.0, "prep": "Dilute 300 mg (2 vials) into 20-30 mL D5W.", "safety_alert": "Contains polysorbate 80; can induce hypotension."},
        {"name": "Lidocaine", "category": "Cardiac Arrest", "type": "weight_based", "factor": 1.5, "unit": "mg/kg", "max_dose": 100.0, "prep": "100 mg/5 mL syringe.", "safety_alert": "Monitor for Lidocaine toxicity (neurotoxicity)."},
        {"name": "Adenosine", "category": "Tachyarrhythmias", "type": "static", "dose": 6.0, "unit": "mg", "max_dose": 12.0, "prep": "6 mg/2 mL vial (Undiluted).", "safety_alert": "Warn patient of transient asystole/chest pressure."},
        {"name": "Diltiazem", "category": "Tachyarrhythmias", "type": "weight_based", "factor": 0.25, "unit": "mg/kg", "max_dose": 25.0, "prep": "25 mg/5 mL vial.", "safety_alert": "Contraindicated in HF and WPW/AF."},
        {"name": "Atropine", "category": "Bradyarrhythmias", "type": "static", "dose": 1.0, "unit": "mg", "max_dose": 3.0, "prep": "1 mg/10 mL pre-filled syringe.", "safety_alert": "Paradoxical bradycardia if dose < 0.5 mg."},
        {"name": "Ketamine", "category": "Respiratory Arrest", "type": "weight_based", "factor": 1.5, "unit": "mg/kg", "max_dose": 200.0, "prep": "500 mg/10 mL vial.", "safety_alert": "Sympathomimetic; raises HR and BP."},
        {"name": "Norepinephrine", "category": "Shock", "type": "weight_based", "factor": 0.1, "unit": "mcg/kg/min", "max_dose": 1.0, "prep": "4 mg/4 mL in 250 mL D5W.", "safety_alert": "Vesicant; use central line."},
        {"name": "Nitroglycerin", "category": "Acute Cardiovascular Emergencies", "type": "static", "dose": 5.0, "unit": "mcg/min", "max_dose": 200.0, "prep": "50 mg/10 mL in 250 mL D5W.", "safety_alert": "Contraindicated with PDE-5 inhibitors (e.g., Sildenafil)."},
        {"name": "Labetalol", "category": "Acute Cardiovascular Emergencies", "type": "static", "dose": 20.0, "unit": "mg", "max_dose": 300.0, "prep": "100 mg/20 mL vial.", "safety_alert": "Avoid in reactive airway disease and heart block."}
    ]
}

def init_data():
    """Initializes data file if not present."""
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'w') as f:
            json.dump(INITIAL_DATA, f, indent=4)

def load_data():
    """Loads drug data from JSON."""
    with open(DATA_FILE, 'r') as f:
        return json.load(f)['drugs']

# --- 2. LOGIC ---
def calculate_dosage(drug, weight):
    """Calculates dose based on type and applies safety check."""
    if drug['type'] == 'weight_based':
        dose = round(drug['factor'] * weight, 2)
    else:
        dose = drug['dose']
    
    is_unsafe = dose > drug['max_dose']
    return dose, is_unsafe

# --- 3. UI ---
def main():
    init_data()
    st.set_page_config(page_title="Clinical Assist AI", layout="centered")
    
    st.title("🚨 Clinical Assist AI")
    st.markdown("---")
    
    # Disclaimer - Vital for clinical apps
    st.warning("**DISCLAIMER:** This tool is a decision-support aid. It does not replace clinical judgment or institutional protocols. Always verify calculations before administration.")
    
    # Sidebar: Inputs
    st.sidebar.header("Patient Parameters")
    weight = st.sidebar.number_input("Patient Weight (kg)", min_value=1.0, max_value=200.0, value=70.0)
    
    data = load_data()
    categories = sorted(list(set([d['category'] for d in data])))
    selected_cat = st.sidebar.selectbox("Select Clinical Scenario", categories)
    
    # Filtering
    filtered_drugs = [d for d in data if d['category'] == selected_cat]
    
    # Display
    st.subheader(f"Scenario: {selected_cat}")
    
    for drug in filtered_drugs:
        dose, is_unsafe = calculate_dosage(drug, weight)
        
        with st.container(border=True):
            cols = st.columns([1, 2])
            with cols[0]:
                st.metric(label=drug['name'], value=f"{dose} {drug['unit']}")
            
            with cols[1]:
                st.info(f"**Prep:** {drug['prep']}")
                
                # Safety Logic
                if is_unsafe:
                    st.error(f"⚠️ SAFETY ALERT: Dose exceeds standard max ({drug['max_dose']} {drug['unit']})")
                else:
                    st.warning(f"**Safety:** {drug['safety_alert']}")

if __name__ == "__main__":
    main()