from langchain_community.vectorstores import Chroma
from langchain_core.example_selectors import SemanticSimilarityExampleSelector
from langchain_huggingface.embeddings import HuggingFaceEndpointEmbeddings
from langchain_core.prompts import ChatPromptTemplate,FewShotChatMessagePromptTemplate

def setup_vector_store(model: str, api_token: str) -> Chroma:
    """
    Initializes the Chroma vector store with HuggingFace embeddings.

    Args:
        model (str): HuggingFace model ID for embeddings.
        api_token (str): HuggingFace API token.

    Returns:
        Chroma: An instance of the Chroma vector store and embedding model.
    """
    hf_embeddings = HuggingFaceEndpointEmbeddings(
        model=model,
        task="feature-extraction",
        huggingfacehub_api_token=api_token,
    )

    vector_store = Chroma()
    vector_store.delete_collection()
    return vector_store, hf_embeddings


def few_shot_prompt_builder(selected_examples):
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

def dynamic_prompt_builder(query: str,examples:list,config:dict):
    """
    Retrieves the top-k similar examples for a given query.

    Args:
        query (str): The query to find similar examples for.
        k (int): Number of top similar examples to retrieve.

    Returns:
        Few-shot-prompt for text-to-sql generation.
    """
    vector_store,hf_embeddings=setup_vector_store(config["vectorstore"]["embedding_model"],config["api_token"])
    example_selector = SemanticSimilarityExampleSelector.from_examples(
        examples,
        hf_embeddings,
        vector_store,
        k=config["vectorstore"]["k"],
        input_keys=["input"],
    )
    selected_examples= example_selector.select_examples({"input": query})
    return few_shot_prompt_builder(selected_examples)
