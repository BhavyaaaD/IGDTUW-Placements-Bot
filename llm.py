import streamlit as st
import os 
import sqlite3
from dotenv import load_dotenv
from langchain_huggingface import HuggingFaceEndpoint
from langchain.chains import LLMChain
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder,FewShotChatMessagePromptTemplate,PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_ollama.llms import OllamaLLM
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
        k=2,
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
         ("human", "Frame the query for the given question:{input}. Generate sql query for the given input. Response should be a 'single' syntactically valid SQL query and no further explanation or examples.Do not generate things your own strictly refer to examples for query generation."),
     ]
    )
    print(prompt.format(input = question))
    #setup model
    llm=HuggingFaceEndpoint(repo_id=repo_id,
                            temperature=0.4,
                            huggingfacehub_api_token=hf_token,
                            )
    
    model=OllamaLLM(model="llama3.1")

    llm_chain = prompt | model
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
    """Given the following user question, corresponding SQL query, and SQL result, answer the user question in a user friendly format.Do not explain the query or generate some other examples.Stick to the given input. Try to generate a table if 'SQL query result' has more than 1 row.
        and ensure that table generated is well structured. Write a concluding line at last to summarize the results. Do not add any kind of explanation or sql queries. 
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