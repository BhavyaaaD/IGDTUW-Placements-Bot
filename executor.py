import logging
import chromadb
from config import config
from llm_integration import TextToSQL
from llm_summarizer import Summarizer
from database_manager import DatabaseManager


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def execute_user_query(user_query):
    chromadb.api.client.SharedSystemClient.clear_system_cache()
    #generating sql_query
    text_to_sql=TextToSQL(db_name=config["database"]["path"],user_text_query=user_query)
    sql_query=text_to_sql.get_sql_query()

    #hitting the query on database to retrive records
    db_manager=DatabaseManager(db_path=config["database"]["path"])
    schemas_used=db_manager.get_schema_for_query()
    retrived_records=db_manager.execute_sql_query(sql_query=sql_query)

    #summarizing the records
    summarizer=Summarizer(data_records=retrived_records,user_query=user_query,sql_query=sql_query)
    return summarizer.generate_summary(config)


