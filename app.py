import streamlit as st
from case_study import case_study_page
from chat_page import chat_page
from evaluation_page import evaluation_page

# Initialize the app and define pages
if "page" not in st.session_state:
    st.session_state.page = "case_selection"

# Handle page routing
if st.session_state.page == "case_selection":
    case_study_page()

elif st.session_state.page == "chat_page":
    chat_page()

elif st.session_state.page == "evaluation":
    evaluation_page()
