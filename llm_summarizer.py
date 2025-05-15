from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_huggingface import HuggingFaceEndpoint

class Summarizer:
    def __init__(self, data_records,user_query,sql_query,model_id="mistralai/Mistral-7B-Instruct-v0.3"):
        self.llm_model_id=model_id
        self.data_records = data_records
        self.user_query = user_query
        self.sql_query = sql_query
        self.summary_prompt=PromptTemplate.from_template(
        """You are tasked with generating a user-friendly response based on the given user question, SQL query, and SQL result. Follow these strict guidelines: 
            1. Output Requirements:
            - Answer the question directly based on the provided SQL result.  
            - If the SQL result contains multiple rows, present them in a **well-structured table** with clear headings.  
            - Display all rows without truncation or omission.  

            2. Formatting Rules:
            - Use a clean and readable table format for multi-row results.  
            - Include column names exactly as provided in the SQL result.  
            - Do not merge or manipulate any data values.  

            3. Concluding Statement:
            - Add a brief concluding line summarizing the results.  

            4. Content Restrictions:
            - Do **not** explain the SQL query.  
            - Do **not** add any extra examples, assumptions, or interpretations. 
            - Do not generate tables, if there is a single value. Just summarize it. 
            - Maintain numerical precision (e.g., compensation values should be in lakhs per annum and stipend is lakhs per month).  
            - Internship stipend is in Lakhs per month
            - Keep answers to the point catering to user query.
            - Answer should be based on retrieved results and generated SQL query from placement database.Do not manipulate the results.
            - Avoid speculative statements, hypothetical scenarios, or additional commentary. 
            - Display all rows without any truncation or omission.  
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