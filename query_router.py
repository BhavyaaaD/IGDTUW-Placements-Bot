from config import config
from prompt import query_router_prompt as prompt
from langchain_core.output_parsers import StrOutputParser
from langchain_huggingface import HuggingFaceEndpoint
from langchain_core.prompts import PromptTemplate
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class QueryRouter:
    def __init__(self,config, llm ="mistralai/Mistral-7B-Instruct-v0.1", prompt=prompt):
        self.llm=llm
        self.prompt=PromptTemplate.from_template(prompt)
        self.config=config
        
    def classify_query(self, query ):
        # classify the query into categories : rag or text-to-sql
        model=HuggingFaceEndpoint(repo_id=self.llm,
                                temperature=0.2,
                                huggingfacehub_api_token=self.config["api_token"],
                                max_length=1024,)

        rephrase_answer_chain = self.prompt | model | StrOutputParser()
        response=rephrase_answer_chain.invoke({'user_query': query})
        print(response)
        return response
    
# class QueryRouter:
#     def __init__(self, config, llm="google/flan-t5-base", prompt=prompt):
#         self.llm = llm
#         self.prompt = PromptTemplate.from_template(prompt)
#         self.config = config

#     def classify_query(self, query):
#         model = HuggingFaceEndpoint(
#             repo_id=self.llm,
#             temperature=0.2,
#             huggingfacehub_api_token=self.config["api_token"],
#             max_length=1024
#         )
#         rephrase_answer_chain = self.prompt | model | StrOutputParser()
#         response = rephrase_answer_chain.invoke({'user_query': query})
#         logger.info(f"Query classification: {response}")
#         return response