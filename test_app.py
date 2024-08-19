import streamlit as st
import re
import os
from groq import Groq
from typing import Generator
from dotenv import load_dotenv
import requests
from urllib.parse import quote_plus
from xml.etree import ElementTree as ET
from pubmed_requests import PubMedClient

# Load environment variables from .env file
load_dotenv()

# Initialize the Groq client with your API key from the .env file
api_key = os.getenv("GROQ_API_KEY")
client = Groq(api_key=api_key)

# Specializations and difficulty levels
specializations = ["Cardiology", "Neurology", "Pediatrics"]
difficulty_levels = ["Beginner", "Intermediate", "Expert"]
# Default values for selected specialization and difficulty
selected_difficulty = "Beginner"
selected_specialization = "Cardiology"


# Step 1: Page Setup
if "page" not in st.session_state:
    st.session_state.page = "case_selection"


@st.dialog("Search PubMed", width="large")
def open_dialog():
    st.write(
        f"Enter your query to search PubMed for related articles.")
    query = st.text_input("Search Query")
    if st.button("Submit"):
        st.session_state.query = query
        st.session_state.articles_table = search_pubmed(query)

    # Display the table within the dialog if results are available
    if "articles_table" in st.session_state and st.session_state.articles_table:
        with st.container():
            with st.expander("Search Results (Click to Expand)", expanded=True):
                st.table(st.session_state.articles_table)


def search_pubmed(query):
    client = PubMedClient()
    article_ids = client.fetch_articles(query)
    if article_ids:
        article_urls = client.generate_pubmed_urls(article_ids)
        article_details = client.fetch_article_details(article_ids)

        # Prepare data for the table
        table_data = []
        for url, article in zip(article_urls, article_details):
            table_data.append({"Title": article['title'], "Link": url})
        return table_data

# Function to switch to the chat page


def next_page():
    st.session_state.page = "chat_page"
    st.rerun()


# Page 1: Case Study Selection
if st.session_state.page == "case_selection":
    st.title("MediLearn")
    st.subheader("Dynamic Case Study Generator")

    selected_specialization = st.selectbox(
        "Select your specialization:", specializations)
    selected_difficulty = st.selectbox(
        "Select Difficulty Level:", difficulty_levels)
    mkd = st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Generate Case Studies", use_container_width=True):
            prompt = f"Generate 3 case studies for a {selected_difficulty} level doctor specializing in {selected_specialization} without providing diagnosis. Each case should include detailed patient history, symptoms, and test results."

            try:
               # Call the Groq API to generate case studies
                case_study_response = client.chat.completions.create(
                    model="llama3-70b-8192",  # Use appropriate model
                    messages=[{"role": "system", "content": prompt}],

                )

                # Extract and split the case studies
                case_study_text = case_study_response.choices[0].message.content
                case_studies = re.split(
                    r'\*\*Case Study \d+:\*\*', case_study_text)
                case_studies.pop(0)  # Remove the first empty entry
                # Create a version for display in the select box (remove '**' using regex)

                case_studies_display = [
                    re.sub(r'\*+', '', case).strip() for case in case_studies]

                case_studies = [case.strip()
                                for case in case_studies if case.strip()]

                # Store case studies in session_state
                st.session_state.case_studies = case_studies
                st.session_state.selected_specialization = selected_specialization
                st.session_state.selected_difficulty = selected_difficulty
                st.session_state.case_studies_display = case_studies_display

            except Exception as e:
                st.error(f"Error generating case studies: {e}")
    with col2:
        if st.button("Search PubMed", use_container_width=True):
            open_dialog()

    # If case studies are generated, display the selection
    if "case_studies" in st.session_state:
        st.markdown("### Case Studies:")
        # selected_case_study = st.selectbox(
        #     "Select a case study:", st.session_state.case_studies)

        # In your select box, use the display version without '**'
        selected_case_study = st.selectbox(
            "Select a case study:", st.session_state.case_studies_display)

        # Save the selected case study in session_state
        st.session_state.selected_case_study = selected_case_study

        # Display the original selected case study with '**'
        original_index = st.session_state.case_studies_display.index(
            selected_case_study)

        # Display the selected case study using markdown
        st.markdown("### Selected Case Study:")
        # st.markdown(st.session_state.selected_case_study)
        st.markdown(st.session_state.case_studies[original_index])

        # Button to proceed to chat
        if st.button("Proceed to Chat"):
            next_page()

# Page 2: Chat Interaction
elif st.session_state.page == "chat_page":
    st.title("Senior-Junior Doctor Chat on Case Study")
    st.subheader("Selected Case Study")

    # Display the selected case study
    st.markdown(f"**Case Study:**\n{st.session_state.selected_case_study}")

    # Initialize chat history and selected model
    if "messages" not in st.session_state:
        st.session_state['messages'] = []

    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        avatar = "🤖" if message["role"] == "assistant" else "👨‍💻"
        with st.chat_message(message["role"], avatar=avatar):
            st.markdown(message["content"])

    def generate_chat_responses(chat_completion) -> Generator[str, None, None]:
        """Yield chat response content from the Groq API response."""
        for chunk in chat_completion:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content

    def get_dynamic_prompt(case_study, user_input):
        # Start with the case study
        prompt = f"Case Study: {case_study}\n\nOur Chat History:\n"

        # Add previous chat history if available
        for message in st.session_state.messages:
            role = "Senior Doctor" if message["role"] == "assistant" else "Junior Doctor"
            prompt += f"{role}: {message['content']}\n"

        # Add the latest input from the junior doctor
        prompt += f"Now Junior Doctor said something: {user_input}"

        return prompt

    case_study = st.session_state.selected_case_study

    if prompt := st.chat_input("Enter your prompt here..."):
        with st.chat_message("user", avatar="👨‍💻"):
            st.markdown(prompt)

        # Generate prompt with case study and user input
        dynamic_prompt = get_dynamic_prompt(case_study, prompt)

        st.session_state.messages.append({"role": "user", "content": prompt})

        # Fetch response from Groq API
        try:
            chat_completion = client.chat.completions.create(
                model="llama3-70b-8192",
                messages=[
                    {"role": "system", "content": "You are a senior doctor mentoring a junior doctor. Mentor a junior doctor by guiding them through diagnosing the case study. Use critical thinking, skepticism, and challenge conventional assumptions. Offer hints, but do not reveal the diagnosis directly."},
                    {"role": "user", "content": dynamic_prompt}
                ],
                max_tokens=600,
                stream=True,
            )

            # Use the generator function with st.write_stream
            with st.chat_message("assistant", avatar="🤖"):
                chat_responses_generator = generate_chat_responses(
                    chat_completion)
                full_response = st.write_stream(chat_responses_generator)
        except Exception as e:
            st.error(e, icon="🚨")

        # Append the full response to session_state.messages
        if isinstance(full_response, str):
            st.session_state.messages.append(
                {"role": "assistant", "content": full_response}
            )
        else:
            # Handle the case where full_response is not a string
            combined_response = "\n".join(str(item) for item in full_response)
            st.session_state.messages.append(
                {"role": "assistant", "content": combined_response}
            )

    col1, col2 = st.columns(2)
    with col1:
        # Button to proceed to performance evaluation below input box
        if st.button("Evaluate Performance", use_container_width=True):
            # Count the number of assistant messages
            assistant_messages_count = sum(
                1 for message in st.session_state.messages if message["role"] == "assistant")

            # Check if there are more than 1 assistant messages
            if assistant_messages_count >= 1:
                st.session_state.page = "evaluation"
                st.rerun()

    with col2:
        if st.button("Search PubMed", use_container_width=True):

            open_dialog()


elif st.session_state.page == "evaluation":
    # Page 3: Evaluation by Senior Doctor

    def evaluate_performance():
        # Senior doctor evaluates junior doctor's performance
        prompt = f"""
        Based on the conversation with the junior doctor, please evaluate the following:
        
        1. Diagnostic Accuracy (0-10): 
        2. Reasoning and Correctness (0-10): 
        3. Patient Management (0-10): 
        
        Provide detailed feedback, highlighting strengths, mistakes, and suggestions for improvement. The junior doctor was working on the following case study:
        {st.session_state.selected_case_study}
        
        Here is the full conversation for reference:
        """

        # Add the chat history to the prompt for evaluation
        for message in st.session_state.messages:
            role = "Senior Doctor" if message["role"] == "assistant" else "Junior Doctor"
            prompt += f"{role}: {message['content']}\n"

        return prompt

    # Store evaluation results
    if "evaluation" not in st.session_state:
        st.session_state.evaluation = {
            "diagnostic_accuracy": None,
            "reasoning": None,
            "patient_management": None,
            "feedback": None
        }

    st.title("Doctor-Patient Chat Evaluation")

    st.subheader("Final Evaluation")

    evaluation_prompt = evaluate_performance()

    # Fetch feedback and scores from the LLM
    try:
        evaluation_response = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[{"role": "system", "content": evaluation_prompt}],
            max_tokens=800
        )

        # Store and display the evaluation scores and feedback
        evaluation_content = evaluation_response.choices[0].message.content

        # Optionally, you can use regex or parsing to extract individual scores from the response
        # For simplicity, we'll store the whole response as feedback for now
        st.session_state.evaluation["feedback"] = evaluation_content

    except Exception as e:
        st.error(f"Error generating evaluation: {e}")

    # Show evaluation feedback
    if st.session_state.evaluation["feedback"]:
        st.subheader("Feedback from Senior Doctor")
        st.markdown(st.session_state.evaluation["feedback"])

    # Allow the junior doctor to reset and start a new session
    if st.button("Start New Session"):
        st.session_state.page = "case_selection"
        st.session_state.messages = []
        st.session_state.evaluation = None
        st.session_state.selected_case_study = None
        st.rerun()
