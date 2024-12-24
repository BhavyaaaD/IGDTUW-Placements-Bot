from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_huggingface import HuggingFaceEndpoint

class Summarizer:
    def __init__(self, data_records,user_query,sql_query,model_id="mistralai/Mistral-7B-Instruct-v0.2"):
        self.llm_model_id=model_id
        self.data_records = data_records
        self.user_query = user_query
        self.sql_query = sql_query
        self.summary_prompt=PromptTemplate.from_template(
        """Given the following user question, corresponding SQL query, and SQL result, answer the user question in a user friendly format.Do not explain the query or generate some other examples.Stick to the given input. Try to generate a table if 'SQL query result' has more than 1 row.
            and ensure that table generated is well structured. Write a concluding line at last to summarize the results. Do not add any kind of explanation or sql queries. 
            Remember the compensation in in lakhs per annum.
            Structure the data records systematically and do not manipulate the results.
            Do not add any extra content . Your response should only contain relevant info for the given user query.
            Question: {user_question}
            SQL Query: {sql_query}
            SQL Result: {sql_result}
            Answer: """
        )
    
    def generate_summary(self,config):
        # Generate a summary of the data records based on the user query and SQL query
        
        #setup model
        model=HuggingFaceEndpoint(repo_id=self.llm_model_id,
                                temperature=0.2,
                                huggingfacehub_api_token=config["api_token"],
                                max_length=1024,)

        rephrase_answer_chain = self.summary_prompt | model | StrOutputParser()
        response=rephrase_answer_chain.invoke({'user_question':self.user_query,'sql_query':self.sql_query,'sql_result':self.data_records})
        return response