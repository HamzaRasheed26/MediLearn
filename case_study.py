import streamlit as st
import re
from utils import generate_case_studies
from pubmed_modal import open_dialog


def case_study_page():
    # Specializations and difficulty levels
    # specializations = ["Cardiology", "Neurology", "Pediatrics"]
    specializations = [
        "Cardiology",
        "Neurology",
        "Pediatrics",
        "Oncology",
        "Dermatology",
        "Endocrinology",
        "Gastroenterology",
        "Hematology",
        "Infectious Disease",
        "Nephrology",
        "Orthopedics",
        "Pulmonology",
        "Rheumatology",
        "Urology",
        "Emergency Medicine",
        "Geriatrics",
        "Ophthalmology",
        "Psychiatry",
        "Radiology",
        "Obstetrics and Gynecology",
        "Anesthesiology",
        "Otolaryngology (ENT)",
        "Allergy and Immunology"
    ]

    difficulty_levels = ["Beginner", "Intermediate", "Expert"]

    st.title("MediLearn 🩺")
    st.subheader("Dynamic Case Study Generator")

    # Selection boxes for specialization and difficulty
    selected_specialization = st.selectbox(
        "Select your specialization:", specializations)
    selected_difficulty = st.selectbox(
        "Select Difficulty Level:", difficulty_levels)
    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Generate Case Studies", use_container_width=True):
            prompt = f"Generate 3 case studies for a {selected_difficulty} level doctor specializing in {selected_specialization} without providing diagnosis. Each case should include detailed patient history, symptoms, and test results."

            try:
                # Generate case studies using the utility function
                case_studies = generate_case_studies(prompt)

                # Prepare case studies for display (cleaning up ** formatting, etc.)
                case_studies_display = [
                    re.sub(r'\*+', '', case).strip() for case in case_studies]

                # Store case studies in session_state
                st.session_state.case_studies = case_studies
                st.session_state.case_studies_display = case_studies_display
                st.session_state.selected_specialization = selected_specialization
                st.session_state.selected_difficulty = selected_difficulty

            except Exception as e:
                st.error(f"Error generating case studies: {e}")
    with col2:
        if st.button("Search PubMed", use_container_width=True):
            open_dialog()

    # If case studies are generated, display the selection
    if "case_studies" in st.session_state:
        st.markdown("### Case Studies:")

        # Select a case study from the display list
        selected_case_study = st.selectbox(
            "Select a case study:", st.session_state.case_studies_display)

        # Get the original index of the selected case study
        if selected_case_study is not None:
            original_index = st.session_state.case_studies_display.index(
                selected_case_study)
            # Save the selected case study in session_state
            st.session_state.selected_case_study = st.session_state.case_studies[original_index]

            # Display the selected case study using markdown
            st.markdown("### Selected Case Study:")
            st.markdown(st.session_state.selected_case_study)

            st.markdown("---")
            # Button to proceed to the chat page
            if st.button("Proceed to Chat"):
                st.session_state.page = "chat_page"
                st.rerun()
