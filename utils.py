import os
from groq import Groq
import re
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize the Groq client with your API key from the .env file
api_key = os.getenv("GROQ_API_KEY")
client = Groq(api_key=api_key)

def generate_case_studies(user_prompt):
    prompt = user_prompt
    response = client.chat.completions.create(
        model="llama3-70b-8192",
        messages=[{"role": "system", "content": prompt}]
        )
    case_study_text = response.choices[0].message.content
    case_studies = re.split(r'\*\*Case Study \d+:\*\*', case_study_text)
    case_studies.pop(0)
    case_studies = [case.strip() for case in case_studies if case.strip()]
    return case_studies

def get_chat_response( system_prompt, dynamic_prompt):
    chat_completion = client.chat.completions.create(
        model="llama3-70b-8192",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": dynamic_prompt}
        ],
        max_tokens=600,
        stream=True,
    )
    return chat_completion

def evaluate_performance(evaluation_prompt):
    evaluation_response = client.chat.completions.create(
        model="llama3-70b-8192",
        messages=[{"role": "system", "content": evaluation_prompt}],
        max_tokens=800
    )

    return evaluation_response.choices[0].message.content
