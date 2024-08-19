import os
import streamlit as st
from groq import Groq
import re

# Initialize the Groq client with your API key from the TOML file
api_key = st.secrets["GROQ"]["api_key"]
client = Groq(api_key=api_key)

model_name = "llama3-70b-8192"
chat_response_token = 600
evaluation_token = 800

def generate_case_studies(user_prompt):
    prompt = user_prompt
    response = client.chat.completions.create(
        model=model_name,
        messages=[{"role": "system", "content": prompt}]
        )
    case_study_text = response.choices[0].message.content
    case_studies = re.split(r'\*\*Case Study \d+:\*\*', case_study_text)
    case_studies.pop(0)
    case_studies = [case.strip() for case in case_studies if case.strip()]
    return case_studies

def get_chat_response( system_prompt, dynamic_prompt):
    chat_completion = client.chat.completions.create(
        model=model_name,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": dynamic_prompt}
        ],
        max_tokens=chat_response_token,
        stream=True,
    )
    return chat_completion

def evaluate_performance(evaluation_prompt):
    evaluation_response = client.chat.completions.create(
        model=model_name,
        messages=[{"role": "system", "content": evaluation_prompt}],
        max_tokens=evaluation_token
    )

    return evaluation_response.choices[0].message.content
