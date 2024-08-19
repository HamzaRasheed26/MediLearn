import streamlit as st
from pubmed_requests import PubMedClient

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