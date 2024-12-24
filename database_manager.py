import sqlite3
import logging
from typing import Any, Union, List, Dict
import sqlparse
from sqlparse.sql import IdentifierList, Identifier
from sqlparse.tokens import Keyword, DML



logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DatabaseManager():
    def __init__(self, db_path):
        self.db_path=db_path
        self.connection=sqlite3.connect(self.db_path)
        self.cursor=self.connection.cursor()
        self.query=""
        self.query_result=""
        self.exception=""

    def execute_sql_query(self,sql_query:str,fetch: Union[str, int]="all")-> Any:
        self.query=sql_query
        logger.info(f"Query generated:{sql_query}")
        try:
            self.cursor.execute(sql_query)
            if fetch == "all":
                self.query_result = self.cursor.fetchall()
            elif fetch == "one":
                self.query_result = self.cursor.fetchone()
            elif isinstance(fetch,int):
                self.query_result = self.cursor.fetchmany(fetch)
        
        except Exception as e:
                self.query_result=""
                self.exception = e
                logger.error(f"Error executing SQL query: {e}")
                raise self.exception
        finally:
            if self.connection:
                self.connection.close()
        
        self.log_records()
        return self.query_result
    
    def log_records(self):
         logger.info("These are the records extracted:")
         for record in self.query_result:
             logger.info(f"{record}")
    def extract_tables(self):
        """
        Extract table names from a SQL statement.
        
        Args:
            sql (str): The SQL query.
        
        Returns:
            list: A list of table names used in the SQL statement.
        """
        # Parse the SQL statement
        parsed = sqlparse.parse(self.query)
        if not parsed:
            return []

        # Take the first statement
        stmt = parsed[0]
        tables = set()
        from_seen = False

        for token in stmt.tokens:
            # Check for 'FROM' or 'JOIN' keyword
            if token.ttype is Keyword and token.value.upper() in ["FROM", "JOIN"]:
                from_seen = True
            elif from_seen and isinstance(token, (Identifier, IdentifierList)):
                # Extract table name(s)
                if isinstance(token, IdentifierList):
                    for identifier in token.get_identifiers():
                        tables.add(identifier.get_real_name())
                elif isinstance(token, Identifier):
                    tables.add(token.get_real_name())
                from_seen = False  # Reset flag after processing

        return list(tables)
        
    
    def get_table_schema(self, table_name: str) -> list:
        """
        Retrieves the schema of a specified table in the SQLite database.

        Args:
            table_name (str): Name of the table.

        Returns:
            list: A list of column names in the table.
        """
        try:
            self.connection=sqlite3.connect(self.db_path)
            self.cursor=self.connection.cursor()
            self.cursor.execute(f"PRAGMA table_info({table_name});")
            schema = [column[1] for column in self.cursor.fetchall()]
        except sqlite3.Error as e:
            raise RuntimeError(f"Database error: {e}")
        finally:
            if self.connection:
                self.connection.close()

        return schema
    
    def print_schema_table(self,table_name,schema):
        formatted_string = "\n".join(f"- {col}" for col in schema)
        return f"""{table_name} table schema:\n{formatted_string}
        """
        
    
    def get_schema_for_query(self):
        if self.query:
            tables=self.extract_tables()
            schemas=[]
            for table in tables:
                schema=self.get_table_schema(table)
                logger.info(self.print_schema_table(table,schema))
                schemas.append(schema)
            return schemas

    
if __name__ =="__main__":
    query="""SELECT COUNT(*),INTERNSHIP_OFFERS.STUDENTS_COUNT FROM STUDENT,INTERNSHIP_OFFERS WHERE STUDENT.COMPANY_PLACED= INTERNSHIP_OFFERS.COMPANY AND  STUDENT.COMPANY_PLACED='Google';"""
    db=DatabaseManager(db_path="placements.db")
    db.execute_sql_query(query,fetch="all")
    db.get_schema_for_query()