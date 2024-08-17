import streamlit as st
from typing import Generator
from groq import Groq

st.set_page_config(page_icon="💬", layout="wide", page_title="Groq Goes Brrrrrrrr...")

def icon(emoji: str):
    """Shows an emoji as a Notion-style page icon."""
    st.write(
        f'<span style="font-size: 78px; line-height: 1">{emoji}</span>',
        unsafe_allow_html=True,
    )

icon("🏎️")

st.subheader("Groq Chat Streamlit App", divider="rainbow", anchor=False)

client = Groq(api_key="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")

# Initialize chat history and selected model
if "messages" not in st.session_state:
    st.session_state['messages'] = []

# Define model details
models = {
    "llama3-70b-8192": {
        "name": "LLaMA3-70b-Instruct",
        "tokens": 8192,
        "developer": "Meta",
    },
    "llama3-8b-8192": {
        "name": "LLaMA3-8b-Instruct",
        "tokens": 8192,
        "developer": "Meta",
    },
    "mixtral-8x7b-32768": {
        "name": "Mixtral-8x7b-Instruct-v0.1",
        "tokens": 32768,
        "developer": "Mistral",
    },
    "gemma-7b-it": {
        "name": "Gemma-7b-it", 
        "tokens": 8192, 
        "developer": "Google"
    },
}

# Layout for model selection and max_tokens slider
col1, col2 = st.columns(2)

with col1:
    model_option = st.selectbox(
        "Choose a model:",
        options=list(models.keys()),
        format_func=lambda x: models[x]["name"],
        index=0,  # Default to the first model in the list
    )

if "selected_model" not in st.session_state:
    st.session_state['selected_model'] = model_option

# Detect model change and clear chat history if model has changed
if st.session_state['selected_model'] != model_option:
    st.session_state.messages = []
    st.session_state.selected_model = model_option

max_tokens_range = models[model_option]["tokens"]

with col2:
    # Adjust max_tokens slider dynamically based on the selected model
    max_tokens = st.slider(
        "Max Tokens:",
        min_value=512,  # Minimum value to allow some flexibility
        max_value=max_tokens_range,
        # Default value or max allowed if less
        value=min(32768, max_tokens_range),
        step=512,
        help=f"Adjust the maximum number of tokens (words) for the model's response. Max for selected model: {max_tokens_range}",
    )

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

# Few-shot examples for prompt engineering
few_shot_examples = """
Example 1:
Senior Doctor: A 45-year-old male presents with chest pain and shortness of breath. The pain is described as a pressure-like sensation, lasting for about 20 minutes. Vital signs are BP 140/90, HR 85 bpm, RR 20 breaths/min. What are your initial observations?
Junior Doctor: The patient’s symptoms and vital signs suggest a possible cardiac issue. We should consider performing an ECG and checking cardiac enzymes.

Example 2:
Senior Doctor: A 60-year-old female presents with a persistent cough and weight loss over the past 3 months. She has a history of smoking. What are your initial observations?
Junior Doctor: The patient's history and symptoms raise concerns about lung cancer. We should consider a chest X-ray and a CT scan.
"""

def get_dynamic_prompt(case_study, user_input):
    prompt = f"""
    You are a senior doctor mentoring a junior doctor. Provide guidance and feedback based on the following case study and junior doctor's input.

    {few_shot_examples}

    Case Study:
    Senior Doctor: {case_study}
    Junior Doctor: {user_input}
    """
    return prompt

# Define case studies
case_studies = [
    "A 30-year-old male presents with abdominal pain and fever. The pain is located in the lower right quadrant and has been worsening over the past 24 hours. Vital signs are BP 130/80, HR 90 bpm, RR 18 breaths/min.",
    # Add more case studies as needed
]

if "selected_case_study" not in st.session_state:
    st.session_state.selected_case_study = case_studies[0]

# Case study selection
case_study = st.selectbox(
    "Select a case study:",
    options=case_studies,
    index=case_studies.index(st.session_state.selected_case_study)
)

# Update selected case study
st.session_state.selected_case_study = case_study

if prompt := st.chat_input("Enter your prompt here..."):
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user", avatar="👨‍💻"):
        st.markdown(prompt)

    # Generate prompt with case study and user input
    dynamic_prompt = get_dynamic_prompt(case_study, prompt)

    # Fetch response from Groq API
    try:
        chat_completion = client.chat.completions.create(
            model=model_option,
            messages=[
                {"role": "user", "content": dynamic_prompt}
            ],
            max_tokens=max_tokens,
            stream=True,
        )

        # Use the generator function with st.write_stream
        with st.chat_message("assistant", avatar="🤖"):
            chat_responses_generator = generate_chat_responses(chat_completion)
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
