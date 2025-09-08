from config import config
from prompt import prompt
from vectorstore_manager import dynamic_prompt_builder
from examples import examples
from prompt import prompt as template
from langchain_core.prompts import ChatPromptTemplate
from langchain_huggingface import HuggingFaceEndpoint
from langchain_ollama.llms import OllamaLLM
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TextToSQL:
    def __init__(self, db_name, user_text_query):
        self.llm_model_name="llama3.1"
        self.user_text_query=user_text_query
        self.db_name=db_name
        self.template=template
        self.few_shot_prompt=dynamic_prompt_builder(self.user_text_query,examples,config)
        self.llm_prompt=""
    
    
    def get_sql_query(self)-> str:
        # Get the SQL query from the user's text query using the LLaMA model
        self.llm_prompt=prompt =ChatPromptTemplate.from_messages(
     [
         ("system",template),
         self.few_shot_prompt,
         ("human", "Frame the query for the given question:{input}. Generate sql query for the given input. Response should be a 'single' syntactically valid SQL query.No further explanation or examples needed.Do not generate things on your own. Strictly adhere to examples for query generation."),
     ]) 
        if hasattr(self.few_shot_prompt, 'examples'):
            examples = self.few_shot_prompt.examples
            if examples:
                logger.info(f"Extracted Few-Shot Prompt Examples for given query: {self.user_text_query}:")
                for i,example in enumerate(examples):
                    logger.info(f"Example {i+1}: {example['input']}\n SQL Query:{example['query']}")
            else:
                logger.info("No examples found in few-shot prompt.")
        # model=HuggingFaceEndpoint(repo_id="bigcode/starcoder2-7b",
        #                     temperature=0.4,
        #                     huggingfacehub_api_token=config['api_token'],
        #                     )
        model=OllamaLLM(model=self.llm_model_name)
        llm_chain = prompt | model
        response=llm_chain.invoke({"input": self.user_text_query})
        return response



