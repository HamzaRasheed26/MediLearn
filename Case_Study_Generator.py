import streamlit as st
import re
from groq import Groq

# Initialize the Groq client with your API key
client = Groq(api_key="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")

# Specializations and difficulty levels
specializations = ["Cardiology", "Neurology", "Pediatrics"]
difficulty_levels = ["Beginner", "Intermediate", "Expert"]

# Streamlit Layout
st.title("Junior Doctor Training System")
st.subheader("Dynamic Case Study Generator")

# Step 1: Junior doctor selects their specialization
selected_specialization = st.selectbox("Select your specialization:", specializations)

# Step 2: Junior doctor selects the difficulty level
selected_difficulty = st.selectbox("Select Difficulty Level:", difficulty_levels)

mkd = st.markdown("---")

# Initialize session state for case studies and selected case study
if "case_studies" not in st.session_state:
    st.session_state.case_studies = []
if "selected_case_study" not in st.session_state:
    st.session_state.selected_case_study = ""

# Button to generate case studies dynamically based on the selected options
if st.button("Generate Case Studies"):
    # Prompt for the LLM to generate case studies
    prompt = f"Generate 3 case studies for a {selected_difficulty} level doctor specializing in {selected_specialization} and do not give its diagnosis."
    
    try:
        # Call the Groq API to generate case studies
        case_study_response = client.chat.completions.create(
            model="llama3-70b-8192",  # Use appropriate model
            messages=[{"role": "system", "content": prompt}],
            max_tokens=1000,  # Limit tokens to a reasonable amount for short case studies
        )

        # Extract the case studies from the response
        case_study_text = case_study_response.choices[0].message.content

        # Use regex to split the text into individual case studies
        case_studies = re.split(r'\*\*Case Study \d+:\*\*', case_study_text)
        case_studies.pop(0)  # Remove the first empty entry
        case_studies = ["Case Study:\n" + case.strip() for case in case_studies if case.strip()]

        # Clean up and remove any empty entries
        st.session_state.case_studies = [case.strip() for case in case_studies if case.strip()]

    except Exception as e:
        st.error(f"Error generating case studies: {e}")

# Display the generated case studies for selection if available
if st.session_state.case_studies:
    st.session_state.selected_case_study = st.selectbox("Select a case study:", st.session_state.case_studies)

# Display the selected case study if available
if st.session_state.selected_case_study:
    mkd.markdown(f"**Selected Case Study:**\n\n{st.session_state.selected_case_study}")
