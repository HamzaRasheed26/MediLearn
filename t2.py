import streamlit as st
import re
from groq import Groq
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Initialize the Groq client with your API key from the .env file
api_key = os.getenv("GROQ_API_KEY")
client = Groq(api_key=api_key)

# Specializations and difficulty levels
specializations = ["Cardiology", "Neurology", "Pediatrics"]
difficulty_levels = ["Beginner", "Intermediate", "Expert"]

# Step 1: Page Setup
if "page" not in st.session_state:
    st.session_state.page = "case_selection"

# Function to switch to the chat page
def next_page():
    st.session_state.page = "chat_page"
    st.rerun()

# Page 1: Case Study Selection
if st.session_state.page == "case_selection":
    st.title("Junior Doctor Training System")
    st.subheader("Dynamic Case Study Generator")

    selected_specialization = st.selectbox("Select your specialization:", specializations)
    selected_difficulty = st.selectbox("Select Difficulty Level:", difficulty_levels)
    mkd = st.markdown("---")

    if st.button("Generate Case Studies"):
        prompt = f"Generate 3 case studies for a {selected_difficulty} level doctor specializing in {selected_specialization} without providing diagnosis."
        
        try:
            # Call the Groq API to generate case studies
            case_study_response = client.chat.completions.create(
                model="llama3-70b-8192",  # Use appropriate model
                messages=[{"role": "system", "content": prompt}],
                max_tokens=500,
            )
            
            # Extract and split the case studies
            case_study_text = case_study_response.choices[0].message.content
            case_studies = re.split(r'\*\*Case Study \d+:\*\*', case_study_text)
            case_studies.pop(0)  # Remove the first empty entry
            case_studies = [case.strip() for case in case_studies if case.strip()]

            # Store case studies in session_state
            st.session_state.case_studies = case_studies
            st.session_state.selected_specialization = selected_specialization
            st.session_state.selected_difficulty = selected_difficulty

        except Exception as e:
            st.error(f"Error generating case studies: {e}")

    # If case studies are generated, display the selection
    if "case_studies" in st.session_state:
        st.markdown("### Case Studies:")
        selected_case_study = st.selectbox("Select a case study:", st.session_state.case_studies)

        # Save the selected case study in session_state
        st.session_state.selected_case_study = selected_case_study

        # Display the selected case study using markdown
        st.markdown("### Selected Case Study:")
        st.markdown(st.session_state.selected_case_study)

        # Button to proceed to chat
        if st.button("Proceed to Chat"):
            next_page()

# Page 2: Chat Interaction
elif st.session_state.page == "chat_page":
    st.title("Doctor-Patient Chat")
    st.subheader("Selected Case Study")

    # Display the selected case study
    st.markdown(f"**Case Study:**\n{st.session_state.selected_case_study}")

    # Chat input for junior doctor
    if st.chat_input("Your response:"):
        st.write("Chat functionality will be implemented here.")
