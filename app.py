import streamlit as st
from dotenv import load_dotenv
from langchain_core.messages import AIMessage, HumanMessage
from llm import get_query_response,retrieve_data,summarize_output
from prompt import prompt

def generate_response(text_query,prompt):
    sql_response = get_query_response(text_query,prompt)
    print(sql_response)
    sql_query=sql_response.split('AI:', 1)[1].strip()
    print(sql_query)
    data=retrieve_data(sql_query,'placements.db')
    final_response=summarize_output(sql_query,data,text_query)
    return final_response

st.set_page_config(page_title='Streaming Bot',page_icon='🤖')
st.title("IGDTUW Placements Info Bot")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
        AIMessage(content="Hello, I am a Placements Info bot. How can I help you?"),
    ]

for message in st.session_state.chat_history:
    if isinstance(message, AIMessage):
        with st.chat_message("AI"):
            st.write(message.content)
    elif isinstance(message, HumanMessage):
        with st.chat_message("Human"):
            st.write(message.content)

# user input
user_query = st.chat_input("Type your message here...")
if user_query is not None and user_query != "":
    st.session_state.chat_history.append(HumanMessage(content=user_query))

    with st.chat_message("Human"):
        st.markdown(user_query)

    with st.chat_message("AI"):
        response = generate_response(user_query, prompt)
        st.write(response)

    st.session_state.chat_history.append(AIMessage(content=response))