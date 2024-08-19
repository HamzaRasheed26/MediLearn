import streamlit as st
from typing import Generator
from utils import get_chat_response
from pubmed_modal import open_dialog

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

def chat_page():
    st.title("Senior-Junior Doctor - Chat on Case Study")
    st.markdown("---")
    
    st.subheader("Selected Case Study")

    # Display the selected case study
    st.markdown(f"**Case Study:**\n{st.session_state.selected_case_study}")
    st.markdown("---")

    # Initialize chat history and selected model
    if "messages" not in st.session_state:
        st.session_state['messages'] = []

    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        avatar = "🤖" if message["role"] == "assistant" else "👨‍💻"
        with st.chat_message(message["role"], avatar=avatar):
            st.markdown(message["content"])

    case_study = st.session_state.selected_case_study

    if prompt := st.chat_input("Enter your prompt here..."):
        with st.chat_message("user", avatar="👨‍💻"):
            st.markdown(prompt)

        # Generate prompt with case study and user input
        dynamic_prompt = get_dynamic_prompt(case_study, prompt)

        st.session_state.messages.append({"role": "user", "content": prompt})

        # Fetch response from Groq API
        try:
            system_prompt = "You are a senior doctor mentoring a junior doctor. Provide guidance and feedback based on the following case study and junior doctor's input. Help him to diagnose the patient and not tell him the diagnose just give him hints."
            chat_completion = get_chat_response(system_prompt, dynamic_prompt)

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

            # Check if there are any assistant messages
            if assistant_messages_count >= 1:
                st.session_state.page = "evaluation"
                st.rerun()

    with col2:
        if st.button("Search PubMed", use_container_width=True):
            open_dialog()
