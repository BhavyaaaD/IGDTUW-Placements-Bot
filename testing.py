import pytest
from config import config
from transformers import AutoTokenizer
import requests
from database_manager import DatabaseManager
from llm_integration import TextToSQL
from test_cases import test_cases
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def generate_sql():

    # Replace with your Hugging Face token
    HUGGINGFACE_API_TOKEN = config['api_token']

    # Model and endpoint
    model = "bigcode/starcoder2-7b"
    api_url = f"https://api-inference.huggingface.co/models/{model}"

    # Initialize tokenizer
    tokenizer = AutoTokenizer.from_pretrained(model)

    # Input text
    input_text = "def add_numbers(a, b):"

    # Tokenize input
    inputs = tokenizer(input_text, return_tensors="json")

    # Make the API call
    headers = {"Authorization": f"Bearer {HUGGINGFACE_API_TOKEN}"}
    response = requests.post(api_url, headers=headers, json=inputs)

    # Decode response
    if response.status_code == 200:
        outputs = response.json()
        generated_code = tokenizer.decode(outputs['generated_text'], skip_special_tokens=True)
        print("Generated Code:", generated_code)
    else:
        print(f"Error: {response.status_code}, {response.text}")


# executes sql query and fetches records 
def execute_query(query):
    db_object=DatabaseManager(config['database']['path'])
    try:
        results= db_object.execute_sql_query(sql_query=query)
        return results, None
    except Exception as e:
        return None, str(e)
    
# gets generated sql query from LLM
def generate_sql_query(user_input):
    try:
        text_to_sql=TextToSQL(db_name=config["database"]["path"],user_text_query=user_input)
        sql_query=text_to_sql.get_sql_query()
        # sql_query=sql_query.split('AI:', 1)[1].strip()
        return sql_query,None
    except Exception as e:
        return None, str(e)
    


def compute_execution_accuracy(expected_results, generated_results):
    """
    Computes Execution Accuracy.
    Checks if the results of the generated query match the expected query results.
    """
    return expected_results == generated_results


def compute_component_match(expected_query, generated_query, components=["SELECT", "WHERE", "GROUP BY", "ORDER BY"]):
    """
    Computes Component Match by comparing individual query components (e.g., SELECT, WHERE).
    """
    matches = {}
    for component in components:
        expected_component = extract_component(expected_query, component)
        generated_component = extract_component(generated_query, component)
        matches[component] = expected_component == generated_component
    return matches


def extract_component(query, component):
    """
    Extracts a specific component from an SQL query (e.g., SELECT, WHERE).
    """
    import re
    pattern = re.compile(f"{component} (.+?)(?: WHERE| GROUP BY| ORDER BY|$)", re.IGNORECASE)
    match = pattern.search(query)
    return match.group(1).strip() if match else ""


def compute_partial_match(expected_results, generated_results):
    """
    Computes Partial Match by comparing the overlap between expected and generated results.
    """
    expected_set = set(expected_results)
    generated_set = set(generated_results)
    overlap = expected_set.intersection(generated_set)
    return len(overlap) / max(len(expected_set), 1)


def compute_metrics(test_cases):
    """
    Computes evaluation metrics for a set of test cases.
    """
    metrics = {
        "execution_accuracy": [],
        "component_match": [],
        "partial_match": []
    }

    for test_case in test_cases:
        user_input = test_case["input"]
        expected_query = test_case["query"]
        generated_query,e=generate_sql_query(user_input=user_input)

        logger.info(user_input)
        logger.info(expected_query)
        logger.info(generated_query)
    
        
        if e:
            logger.error(e)
            continue

        # Execute expected and generated queries
        expected_results, error_expected = execute_query(expected_query)
        generated_results, error_generated = execute_query(generated_query)

        # Execution Accuracy
        exec_accuracy = compute_execution_accuracy(expected_results, generated_results)
        metrics["execution_accuracy"].append(exec_accuracy)

        # Component Match
        comp_match = compute_component_match(expected_query, generated_query)
        metrics["component_match"].append(comp_match)

        # Partial Match
        partial_match = compute_partial_match(expected_results or [], generated_results or [])
        metrics["partial_match"].append(partial_match)

    # Summarize metrics
    summary = {
        "execution_accuracy": sum(metrics["execution_accuracy"]) / len(metrics["execution_accuracy"]),
        "component_match": {
            component: sum(match[component] for match in metrics["component_match"]) / len(metrics["component_match"])
            for component in ["SELECT", "WHERE", "GROUP BY", "ORDER BY"]
        },
        "partial_match": sum(metrics["partial_match"]) / len(metrics["partial_match"])
    }
    return summary


if __name__=="__main__":
    summary=compute_metrics(test_cases=test_cases)
    print(summary)