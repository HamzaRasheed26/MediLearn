import streamlit as st
from utils import evaluate_performance

def get_evaluation_prompt():
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

def evaluation_page():
    # Page 3: Evaluation by Senior Doctor

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

    evaluation_prompt = get_evaluation_prompt()

    # Fetch feedback and scores from the LLM
    try:
        # Store and display the evaluation scores and feedback
        evaluation_content = evaluate_performance(evaluation_prompt)

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
