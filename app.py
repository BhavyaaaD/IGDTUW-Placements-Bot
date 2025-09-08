import streamlit as st
from dotenv import load_dotenv
from langchain_core.messages import AIMessage, HumanMessage
import matplotlib.pyplot as plt
import numpy as np
from config import config
from executor import execute_user_query
from database_manager import DatabaseManager
import typing

load_dotenv()


st.set_page_config(page_title='Streaming Bot',page_icon='🤖')
st.title("IGDTUW Placements Info Bot")
st.markdown(
    """
    <style>
    .stApp {
        background-image: url('https://careerinitiative.in/assets/images/blog/Indira%20Gandhi%20Delhi%20Technical%20University%20for%20Women%20(IGDTUW).jpg');
        background-size: cover;
        background-position: center;
    }
    .stApp::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(255, 255, 255, 0.5); /* White with 50% opacity for transparency */
        z-index: -1;  /* Place the overlay behind the content */
    }

    /* Apply white background to the sidebar */
    .css-1d391kg {
        background-color: white !important;
        color: black !important;
    }

    /* Apply white background to chat container */
    .css-18e3th9 {
        background-color: white !important;
        padding: 20px;
        border-radius: 8px;
        box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1);
    }
    .chat-container {
        background-color: rgba(255, 255, 255, 0.9);  /* Semi-transparent white */
        width: 80%;  /* Adjust width of chat container */
        max-width: 600px;  /* Limit the max width */
        margin: 0 auto;  /* Center the container */
        padding: 30px;  /* Padding inside the container */
        border-radius: 15px;  /* Rounded corners */
        box-shadow: 0px 4px 15px rgba(0, 0, 0, 0.1);  /* Soft shadow */
        overflow-y: auto;
        height: 75vh;  /* Limit the height of the chat area */
        display: flex;
        flex-direction: column;
    }

    /* White background for individual chat messages */
    .stChatMessage {
        background-color: black !important;
        padding: 15px;
        margin-bottom: 10px;
        border-radius: 10px;
        box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1);
    }

 

    </style>
    """,
    unsafe_allow_html=True,
)

# --- SIDEBAR SETTINGS ---
st.sidebar.title("Settings")

# Clear chat button
if st.sidebar.button("Clear Chat 🗑️"):
    st.session_state.chat_history = [
        AIMessage(content="Hello, I am a Placements Info bot. How can I help you?"),
    ]
    st.rerun()

# --- SESSION STATE ---
if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
        AIMessage(content="Hello, I am a Placements Info bot. How can I help you?"),
    ]

for message in st.session_state.chat_history:
    if isinstance(message, AIMessage):
        with st.chat_message("AI",avatar="🤖"):
            st.write(message.content)
    elif isinstance(message, HumanMessage):
        with st.chat_message("Human",avatar="👤"):
            st.write(message.content)

# user input
user_query = st.chat_input("Type your message here...")
if user_query is not None and user_query != "":
    st.session_state.chat_history.append(HumanMessage(content=user_query))

    with st.chat_message("Human"):
        st.markdown(user_query)

    with st.chat_message("AI"):
        with st.spinner("Typing..."):
            response,data = execute_user_query(user_query=user_query)
            st.session_state.last_query_data = data
            print(data)
            st.write(response)

    st.session_state.chat_history.append(AIMessage(content=response))

# --- SIDEBAR CHART OPTIONS ---
st.sidebar.title("📊 Charts")

# Chart selection
chart_type = st.sidebar.radio("Select Chart Type", ["None", "Placement Stats (Pie)", "Top Recruiters (Bar)","Compensation Distribution (Histogram)"])
# --- HANDLE CHART REQUESTS ---
if chart_type == "Placement Stats (Pie)":
    db=DatabaseManager(db_path=config['database']['path'])
    placed=db.execute_sql_query(sql_query="SELECT COUNT(*) FROM STUDENT WHERE COMPANY_PLACED NOT LIKE '%Higher_Studies%';")[0][0]
    unplaced=db.execute_sql_query(sql_query="SELECT COUNT(*) FROM STUDENT WHERE COMPANY_PLACED LIKE '%Higher_Studies%';")[0][0]
    # Display Chart as Query Response
    with st.chat_message("assistant", avatar="🤖"):
        st.markdown("### 🎯 Placement Stats - Placed vs Unplaced Students")
        labels = ['Placed', 'Unplaced']
        sizes = [placed, unplaced]  # Example values
        colors = ['#4CAF50', '#F44336']
        explode = (0.1, 0)

        fig1, ax1 = plt.subplots()
        ax1.pie(sizes, explode=explode, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
        ax1.axis('equal')
        st.pyplot(fig1)
    chart_type="None"

elif chart_type == "Top Recruiters (Bar)":
    db=DatabaseManager(db_path=config['database']['path'])
    top_recruiters=db.execute_sql_query(sql_query="SELECT COMPANY_PLACED, COUNT(*) FROM STUDENT WHERE COMPANY_PLACED NOT LIKE '%Higher_Studies%' GROUP BY COMPANY_PLACED ORDER BY COUNT(*) DESC LIMIT 10;")
    # Display Chart as Query Response
    with st.chat_message("assistant", avatar="🤖"):
        st.markdown("### 🏢 Top 5 Hiring Companies")
        companies = [company for company, count in top_recruiters]
        students_hired = [count for company, count in top_recruiters]
        fig2, ax2 = plt.subplots(figsize=(15, 10))
        bars=ax2.bar(companies, students_hired, color=['#FF5733', '#33FF57', '#3357FF', '#F1C40F', '#9B59B6', '#8E44AD', '#F39C12', '#1F77B4', '#3498DB', '#2ECC71'])
        # Add count labels on top of the bars
        for bar in bars:
            yval = bar.get_height()  # Get the height of the bar
            ax2.text(bar.get_x() + bar.get_width() / 2, yval + 0.5,  # Position text slightly above the bar
                    str(int(yval)), ha='center', va='bottom', fontsize=10)  # Add the text label

        ax2.set_xlabel('Companies')
        ax2.set_ylabel('Offers Made')
        ax2.set_title('Top 5 Hiring Companies')
        st.pyplot(fig2)
    chart_type="None"

elif chart_type == "Compensation Distribution (Histogram)":
    db=DatabaseManager(db_path=config['database']['path'])
    compensation_values=db.execute_sql_query(sql_query="SELECT AVG(COMPENSATION_OFFERED) FROM STUDENT GROUP BY COMPANY_PLACED;")
    print(compensation_values)
    compensation=[x[0] for x in compensation_values if isinstance(x[0], (int, float))]
    print(compensation)
    # Display Histogram for Compensation Distribution
    with st.chat_message("assistant", avatar="🤖"):
        st.markdown("### 💼 Compensation Distribution (Histogram)")

        # Create Histogram
        fig3, ax3 = plt.subplots()
        ax3.hist(compensation,bins=20, color='#1f77b4', edgecolor='black')
        ax3.set_xlabel('Compensation (in Lakhs)')
        ax3.set_ylabel('Number of Students')
        ax3.set_title('Compensation Distribution')
        st.pyplot(fig3)
    chart_type="None"