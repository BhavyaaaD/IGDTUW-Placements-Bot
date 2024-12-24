import os
from dotenv import load_dotenv

load_dotenv()

config = {
    "api_token": os.getenv("HF_TOKEN"),
    "sql_generator_llm": {
        "huggingface": {
            "model_name": "mistralai/Mistral-7B-Instruct-v0.2",
            "temperature": 0.4,
        },
        "ollama": {
            "model_name": "llama3.1",
        },
    },
    "vectorstore": {
        "embedding_model": "mixedbread-ai/mxbai-embed-large-v1",
        "k": 4,
    },
    "database": {
        "path": "placements.db",
    },
    "logging": {
        "level": "INFO",
    },
}
