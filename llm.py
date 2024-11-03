import streamlit as st
import os 
import sqlite3
from dotenv import load_dotenv
from langchain_huggingface import HuggingFaceEndpoint
from langchain.chains import LLMChain
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder,FewShotChatMessagePromptTemplate,PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_community.vectorstores import Chroma
from langchain_core.example_selectors import SemanticSimilarityExampleSelector
from langchain_huggingface.embeddings import HuggingFaceEndpointEmbeddings
from examples import examples
from prompt import prompt
import chromadb


load_dotenv()
chromadb.api.client.SharedSystemClient.clear_system_cache()

def relevant_examples_selector(examples,user_query):
    hf_embeddings = HuggingFaceEndpointEmbeddings(
    model= "mixedbread-ai/mxbai-embed-large-v1",
    task="feature-extraction",
    huggingfacehub_api_token=os.getenv("HF_TOKEN"),
    )
    vectorstore = Chroma()
    vectorstore.delete_collection()
    example_selector = SemanticSimilarityExampleSelector.from_examples(
        examples,
        hf_embeddings,
        vectorstore,
        k=4,
        input_keys=["input"],
    )
    selected_examples= example_selector.select_examples({"input": user_query})
    example_prompt = ChatPromptTemplate.from_messages(
        [
            ("human","{input}"),
            ("ai","{query}"),
        ]
    )
    
    few_shot_prompt = FewShotChatMessagePromptTemplate(
     example_prompt=example_prompt,
     examples=selected_examples,
     input_variables=["input"],
   )
    return few_shot_prompt



#Funtion to get sql query
def get_query_response(question, template):
    #get access token from env
    hf_token=os.getenv("HF_TOKEN")
    repo_id="mistralai/Mistral-7B-Instruct-v0.2"
    
    #generate prompt
    # prompt = PromptTemplate.from_template(template)

    few_shot_prompt=relevant_examples_selector(examples,question)
    prompt = ChatPromptTemplate.from_messages(
     [
         ("system",template),
         few_shot_prompt,
         ("human", "Frame the query for the given question:{input}. Generate response in keeping in mind the examples above."),
     ]
    )
    print(prompt.format(input = question))
    #setup model
    llm=HuggingFaceEndpoint(repo_id=repo_id,
                            temperature=0.3,
                            huggingfacehub_api_token=hf_token,
                            )

    llm_chain = prompt | llm
    response=llm_chain.invoke({"input": question})
    return response


#Function to retrieve data from our database
def retrieve_data(sql_query,database):
    connection=sqlite3.connect(database)
    cursor=connection.cursor()

    cursor.execute(sql_query)
    data=cursor.fetchall()

    for row in data:
        print(row)
    
    connection.commit()
    connection.close()
    return data

def summarize_output(sql_query,sql_result,user_question):
    answer_prompt = PromptTemplate.from_template(
    """Given the following user question, corresponding SQL query, and SQL result, answer the user question.Do not explain the query.

        Question: {user_question}
        SQL Query: {sql_query}
        SQL Result: {sql_result}
        Answer: """
    )

    hf_token=os.getenv("HF_TOKEN")
    repo_id="mistralai/Mistral-7B-Instruct-v0.2"
    #setup model
    llm=HuggingFaceEndpoint(repo_id=repo_id,
                            temperature=0.2,
                            huggingfacehub_api_token=hf_token,
                            max_length=1024,)

    rephrase_answer_chain = answer_prompt | llm | StrOutputParser()
    response=rephrase_answer_chain.invoke({'user_question':user_question,'sql_query':sql_query,'sql_result':sql_result})
    return response

# SELECT COUNT(*) *100.0 / (SELECT COUNT(*) FROM STUDENT)
#  FROM STUDENT
#  WHERE COMPANY_PLACED NOT LIKE '%Higher_Studies%';
# """
# # Streamlit app interface
# st.title("Text to SQL Converter")
# st.write("Convert natural language text into SQL queries and retrieves relevant data")

# # User input for the natural language query
# text_query = st.text_area("Enter your text query:")

# if st.button("Submit"):
#     if text_query.strip():
#         sql_query = get_query_response(text_query,prompt)
#         print(sql_query)
#         data=retrieve_data(sql_query,'placements.db')
#         final_response=summarize_output(sql_query,data,text_query)
#         st.subheader("Response:")
#         st.header(final_response)

#     else:
#         st.error("Please enter a text query.")