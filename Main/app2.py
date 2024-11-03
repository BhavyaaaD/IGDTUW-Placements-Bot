import streamlit as st
from llm import get_query_response,retrieve_data,summarize_output
from prompt import prompt
import chromadb


# Streamlit app interface
st.title("Text to SQL Converter")
st.write("Convert natural language text into SQL queries and retrieves relevant data")

# User input for the natural language query
text_query = st.text_area("Enter your text query:")

if st.button("Submit"):
    chromadb.api.client.SharedSystemClient.clear_system_cache()
    if text_query.strip():
        sql_query = get_query_response(text_query,prompt)
        print(sql_query)
        data=retrieve_data(sql_query,'placements.db')
        final_response=summarize_output(sql_query,data,text_query)
        st.subheader("Response:")
        st.header(final_response)

    else:
        st.error("Please enter a text query.")