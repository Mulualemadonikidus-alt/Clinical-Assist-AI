import streamlit as st
import json
import os

# --- CONFIGURATION ---
st.set_page_config(page_title="Clinical Assist AI", layout="wide", page_icon="🚨")
DATA_FILE = 'drugs.json'

@st.cache_data
def load_data():
    """Loads and caches the complex drug data from JSON."""
    try:
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        st.error(f"Data file not found at {DATA_FILE}. Please ensure the JSON is saved correctly.")
        return None
    except json.JSONDecodeError:
        st.error("Error reading the JSON file. Please ensure it is formatted correctly.")
        return None

def main():
    data = load_data()
    if not data:
        return

    # --- HEADER ---
    st.title("🚨 Emergency Clinical Assist AI")
    st.markdown(f"**Reference:** {data.get('manual_title', 'Cardiovascular Resuscitation Pharmacology')}")
    st.warning("**DISCLAIMER:** This tool is a decision-support aid. It does not replace clinical judgment or institutional protocols. Always verify calculations before administration.")
    st.markdown("---")

    # --- SIDEBAR NAV ---
    st.sidebar.header("Navigation")
    
    # Create a dictionary of sections for easy lookup
    # Safely get "sections", defaulting to an empty list if it doesn't exist
    sections_list = data.get("sections", [])
    
    # Check if we actually found sections (prevents the KeyError)
    if not sections_list:
        st.error("⚠️ **Data Format Error:** The app could not find any 'sections' in your `drugs.json` file. Please ensure you copied the entirely new JSON structure provided previously, not just the drugs array.")
        return

    sections_dict = {sec["section_name"]: sec for sec in sections_list if "section_name" in sec}
    
    # Dropdown to select the clinical scenario
    selected_section_name = st.sidebar.selectbox("Select Clinical Scenario", list(sections_dict.keys()))
    
    # Guard against empty selection during app initialization
    if not selected_section_name:
        st.info("Please select a clinical scenario from the sidebar.")
        return
        
    # --- MAIN CONTENT DISPLAY ---
    selected_section = sections_dict[selected_section_name]
    st.header(f"Scenario: {selected_section_name}")
    
    # Display section notes if they exist (e.g., the double-strength note in Shock)
    if "section_note" in selected_section:
        st.info(f"ℹ️ **Clinical Note:** {selected_section['section_note']}")

    # Display Medications
    if "medications" in selected_section:
        for med in selected_section["medications"]:
            with st.expander(f"💊 {med['name']}", expanded=False):
                
                # Create a two-column layout for scannability
                col1, col2 = st.columns([1, 1])
                
                with col1:
                    st.markdown("### Dosing & Administration")
                    st.success(f"**Calculated Dosing:**\n\n{med.get('calculated_dosing_and_administration_guide', 'N/A')}")
                    
                    # Safely handle indications (might be missing in some entries)
                    indications = med.get('clinical_indications', [])
                    if indications:
                        st.markdown(f"**Indications:** {', '.join(indications)}")
                    
                with col2:
                    # --- DYNAMIC CALCULATOR ---
    st.sidebar.markdown("---")
    st.sidebar.header("🧮 Rapid Dose Calculator")
    
    # Input fields for the calculation variables
    calc_dose = st.sidebar.number_input("Target Dose (mcg/kg/min)", value=0.1)
    calc_weight = st.sidebar.number_input("Patient Weight (kg)", value=70.0)
    calc_conc = st.sidebar.number_input("Concentration (mcg/mL)", value=16.0)
    
    # Button to trigger the calculation
    if st.sidebar.button("Calculate Rate"):
        # Mathematical formula derived from infusion standards [cite: 1, 16]
        rate = (calc_dose * calc_weight * 60) / calc_conc
        st.sidebar.success(f"Infusion Rate: **{rate:.1f} mL/hr**")
                    st.markdown("### Preparation & Concentrations")
                    st.markdown(f"**Stock Form:** {med.get('available_stock_dosage_forms', 'N/A')}")
                    st.markdown(f"**Prep Method:** {med.get('preparation_methods_and_preferred_solvents', 'N/A')}")
                    st.metric(label="Admin-Ready Concentration", value=med.get('administration_ready_concentration', 'N/A'))

                # Safety Alerts section spanning the bottom
                st.markdown("### ⚠️ Critical Safety Alerts")
                alerts = med.get('critical_safety_alerts', [])
                if alerts:
                    for alert in alerts:
                        st.error(f"• {alert}")
                else:
                    st.write("No specific safety alerts listed.")

    # Display Cross-References if viewing the final section
    if "cross_references" in selected_section:
        st.subheader("Critical Resource Cross-References")
        for ref in selected_section["cross_references"]:
            st.caption(f"🔗 {ref}")

if __name__ == "__main__":
    main()
