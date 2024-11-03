import streamlit as st
import time 
from Langchain_basics.llm import get_query_response,retrieve_data,summarize_output
from Langchain_basics.prompt import prompt
# Function to stream a string with a delay
def stream_str(s, speed=250):
    """Yields characters from a string with a delay to simulate streaming."""
    for c in s:
        yield c
        time.sleep(1 / speed)


# Function to stream the response from the AI
def stream_response(response):
    """Yields responses from the AI, replacing placeholders as needed."""
    for r in response:
        content = r.choices[0].delta.content
        # prevent $ from rendering as LaTeX
        content = content.replace("$", "\$")
        yield content
# Function to add a message to the chat
def add_message(msg, agent="ai", stream=True, store=True):
    """Adds a message to the chat interface, optionally streaming the output."""
    if stream and isinstance(msg, str):
        msg = stream_str(msg)

    with st.chat_message(agent):
        if stream:
            output = st.write_stream(msg)
        else:
            output = msg
            st.write(msg)

    if store:
        st.session_state.messages.append({"role":agent, "content":output})

def generate_response(text_query,prompt):
    sql_query = get_query_response(text_query,prompt)
    data=retrieve_data(sql_query,'placements.db')
    final_response=summarize_output(sql_query,data,text_query)
    return final_response

# Main application logic
def main():
    """Main function to run the application logic."""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if st.sidebar.button("🔴 Reset conversation"):
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    query = st.chat_input("Ask something about IGDTUW's Placement Stats...")

    if not st.session_state.messages:
        add_message("Ask me anything!")

    if query:
        add_message(query, agent="human", stream=False, store=True)
        # reply(query, index, chunks)
        response= generate_response(query,prompt)
        # Display assistant response in chat message container
        with st.chat_message("assistant"):
            st.markdown(response)
        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": response})

main()