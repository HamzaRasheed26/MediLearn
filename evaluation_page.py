import streamlit as st
import pandas as pd
import plotly.express as px
import json
import re
from utils import evaluate_performance

def extract_json_from_string(s):
    try:
        # Extract the JSON part using regular expressions
        json_str = re.search(r"\{.*\}", s, re.DOTALL).group(0)
        return json.loads(json_str)
    except (json.JSONDecodeError, AttributeError):
        raise ValueError("Could not extract valid JSON from the evaluation content.")

def get_evaluation_prompt():
    prompt = f"""
    You are a senior doctor tasked with evaluating a junior doctor's performance based on their conversation with a patient.
    Please provide the evaluation strictly in the following JSON format, without any additional text:

    {{
        "Diagnostic Accuracy": {{
            "Score": [Score from 0-10],
            "Comments": "[Specific comments on the accuracy of the diagnosis, including correct and incorrect decisions]"
        }},
        "Reasoning and Correctness": {{
            "Score": [Score from 0-10],
            "Comments": "[Specific comments on the logical reasoning and correctness of the junior doctor's thought process]"
        }},
        "Patient Management": {{
            "Score": [Score from 0-10],
            "Comments": "[Specific comments on how well the junior doctor managed the patient, including any recommendations for improvement]"
        }},
        "Communication Skills": {{
            "Score": [Score from 0-10],
            "Comments": "[Evaluation of how well the junior doctor communicated with the patient, including empathy, clarity, and listening skills]"
        }},
        "Time Management": {{
            "Score": [Score from 0-10],
            "Comments": "[Assessment of how efficiently the junior doctor managed the consultation time]"
        }},
        "Overall Impression": {{
            "Score": [Score from 0-10],
            "Comments": "[General comments on the junior doctor's overall performance, including strengths and areas for improvement]"
        }},
        "Feedback": "[Detailed feedback highlighting strengths, mistakes, and suggestions for improvement]"
    }}

    The junior doctor was working on the following case study:
    "{st.session_state.selected_case_study}"

    Here is the full conversation for reference:
    """

    for message in st.session_state.messages:
        role = "Senior Doctor" if message["role"] == "assistant" else "Junior Doctor"
        prompt += f"{role}: {message['content']}\n"

    prompt += "\nPlease provide the evaluation in JSON format only."
    return prompt


def evaluation_page():
    if "evaluation" not in st.session_state:
        st.session_state.evaluation = {
            "diagnostic_accuracy": None,
            "reasoning": None,
            "patient_management": None,
            "communication_skills": None,
            "time_management": None,
            "overall_impression": None,
            "feedback": None
        }

    st.title("Doctor-Patient Chat Evaluation")
    st.subheader("Final Evaluation")

    evaluation_prompt = get_evaluation_prompt()

    try:
        evaluation_content = evaluate_performance(evaluation_prompt)
        
        # Debugging: Check the content before parsing
        #st.write("Raw Evaluation Content:", evaluation_content)

        # Extract JSON from the evaluation content
        evaluation_dict = extract_json_from_string(evaluation_content)

        # Update the session state with the evaluation content
        st.session_state.evaluation.update({
            "diagnostic_accuracy": evaluation_dict["Diagnostic Accuracy"],
            "reasoning": evaluation_dict["Reasoning and Correctness"],
            "patient_management": evaluation_dict["Patient Management"],
            "communication_skills": evaluation_dict["Communication Skills"],
            "time_management": evaluation_dict["Time Management"],
            "overall_impression": evaluation_dict["Overall Impression"],
            "feedback": evaluation_dict["Feedback"]
        })

    except ValueError as e:
        st.error(f"Error extracting or parsing evaluation JSON: {e}")
    except Exception as e:
        st.error(f"Error generating evaluation: {e}")

    if st.session_state.evaluation["feedback"]:
        st.subheader("Feedback from Senior Doctor")
        st.markdown("---")
        st.markdown(st.session_state.evaluation["feedback"])

        # Extract categories, scores, and comments
        categories = ["Diagnostic Accuracy", "Reasoning and Correctness", "Patient Management",
                      "Communication Skills", "Time Management", "Overall Impression"]

        scores = [st.session_state.evaluation["diagnostic_accuracy"]["Score"],
                  st.session_state.evaluation["reasoning"]["Score"],
                  st.session_state.evaluation["patient_management"]["Score"],
                  st.session_state.evaluation["communication_skills"]["Score"],
                  st.session_state.evaluation["time_management"]["Score"],
                  st.session_state.evaluation["overall_impression"]["Score"]]

        comments = [st.session_state.evaluation["diagnostic_accuracy"]["Comments"],
                    st.session_state.evaluation["reasoning"]["Comments"],
                    st.session_state.evaluation["patient_management"]["Comments"],
                    st.session_state.evaluation["communication_skills"]["Comments"],
                    st.session_state.evaluation["time_management"]["Comments"],
                    st.session_state.evaluation["overall_impression"]["Comments"]]

        # Create DataFrame
        df_scores = pd.DataFrame({
            "Category": categories,
            "Score": scores,
            "Comments": comments
        })

        # Display table
        st.table(df_scores)

        # Create and display a bar chart
        fig = px.bar(df_scores, x="Category", y="Score", range_y=[0, 10], title="Evaluation Scores")
        st.plotly_chart(fig)

    if st.button("Start New Session"):
        st.session_state.page = "case_selection"
        st.session_state.messages = []
        st.session_state.selected_case_study = None
        st.rerun()
