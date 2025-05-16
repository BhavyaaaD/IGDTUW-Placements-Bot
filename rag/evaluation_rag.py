import csv
import numpy as np
import os
import faiss
import weaviate
import numpy as np
from typing import List, Dict
from pathlib import Path
from sentence_transformers import SentenceTransformer, util
from pymilvus import connections, Collection
from uuid import uuid4
import requests

# ------------------------------------
# Configuration Constants
# ------------------------------------
EMBED_MODEL = "all-MiniLM-L6-v2"  # Sentence-BERT embedding model for vectorization
OLLAMA_API_URL = "http://localhost:11434/api/chat"  # Local Ollama API endpoint for LLaMA

# ------------------------------------
# Embedding Manager
# ------------------------------------
class EmbeddingManager:
    """
    Manages text embedding using Sentence-BERT.
    """

    def __init__(self, model_name=EMBED_MODEL):
        # Load Sentence-BERT model once during initialization
        self.model = SentenceTransformer(model_name)

    def embed_texts(self, texts: List[str]) -> np.ndarray:
        """
        Embed a list of texts into vectors.
        
        Args:
            texts: List of strings to embed.
        Returns:
            numpy ndarray of embeddings.
        """
        return self.model.encode(texts, convert_to_numpy=True)

    def embed_text(self, text: str) -> np.ndarray:
        """
        Embed a single text string.
        
        Args:
            text: Single string to embed.
        Returns:
            numpy ndarray vector.
        """
        return self.embed_texts([text])[0]

# ------------------------------------
# Chunking Utility
# ------------------------------------
def chunk_text(text: str, chunk_size: int = 100, chunk_overlap: int = 20, metadata: Dict = None) -> List[Dict]:
    """
    Splits long text into overlapping chunks with unique IDs.
    
    Args:
        text: Full text document to chunk.
        chunk_size: Number of words per chunk.
        chunk_overlap: Number of words to overlap between chunks.
        metadata: Optional dict to attach to each chunk.
        
    Returns:
        List of chunks, each a dict with 'id', 'text', and 'metadata'.
    """
    words = text.split()
    chunks = []
    start = 0
    while start < len(words):
        end = min(start + chunk_size, len(words))
        chunk_words = words[start:end]
        chunk_text = ' '.join(chunk_words)
        chunks.append({
            "id": str(uuid4()),  # Unique chunk ID
            "text": chunk_text,
            "metadata": metadata or {}
        })
        # Move start by chunk_size minus overlap to create overlapping chunks
        start += chunk_size - chunk_overlap
    return chunks

# ------------------------------------
# FAISS Retriever
# ------------------------------------
class FAISSRetriever:
    """
    Retriever that uses FAISS for dense vector similarity search.
    """

    def __init__(self, chunks: List[Dict], embed_manager: EmbeddingManager):
        """
        Initializes the FAISS index with chunk embeddings.
        
        Args:
            chunks: List of chunk dicts with 'text'.
            embed_manager: EmbeddingManager instance.
        """
        self.texts = [c["text"] for c in chunks]
        self.ids = [c["id"] for c in chunks]
        self.embeddings = embed_manager.embed_texts(self.texts)
        self.index = faiss.IndexFlatL2(self.embeddings.shape[1])  # L2 distance index
        self.index.add(self.embeddings)

    def retrieve(self, query: str, embed_manager: EmbeddingManager, k: int = 5) -> List[str]:
        """
        Retrieves top-k chunks most similar to the query.
        
        Args:
            query: Query string.
            embed_manager: EmbeddingManager instance.
            k: Number of chunks to retrieve.
        
        Returns:
            List of chunk texts.
        """
        query_vec = embed_manager.embed_text(query).reshape(1, -1)
        _, indices = self.index.search(query_vec, k)
        return [self.texts[i] for i in indices[0]]

# ------------------------------------
# Weaviate Retriever
# ------------------------------------
class WeaviateRetriever:
    """
    Retriever that queries Weaviate vector database using semantic search.
    """

    def __init__(self):
        """
        Initializes Weaviate client; assumes local Weaviate running on default port.
        """
        self.client = weaviate.Client("http://localhost:8080")

    def retrieve(self, query: str, k: int = 5) -> List[str]:
        """
        Retrieves top-k semantically relevant chunks from Weaviate.
        
        Args:
            query: Query string.
            k: Number of chunks to retrieve.
        
        Returns:
            List of chunk texts.
        """
        result = (
            self.client.query.get("Chunk", ["text"])
            .with_near_text({"concepts": [query]})
            .with_limit(k)
            .do()
        )
        return [item["text"] for item in result["data"]["Get"]["Chunk"]]

# ------------------------------------
# Milvus Retriever
# ------------------------------------
class MilvusRetriever:
    """
    Retriever that queries Milvus vector database using vector similarity search.
    """

    def __init__(self, collection_name="rag_chunks"):
        """
        Connects to Milvus and loads the specified collection.
        
        Args:
            collection_name: Name of Milvus collection holding chunk embeddings.
        """
        connections.connect("default", host="localhost", port="19530")
        self.collection = Collection(name=collection_name)

    def retrieve(self, query: str, embed_manager: EmbeddingManager, k: int = 5) -> List[str]:
        """
        Retrieves top-k semantically relevant chunks from Milvus.
        
        Args:
            query: Query string.
            embed_manager: EmbeddingManager instance.
            k: Number of chunks to retrieve.
        
        Returns:
            List of chunk texts.
        """
        query_vec = embed_manager.embed_text(query).tolist()
        self.collection.load()
        result = self.collection.search(
            data=[query_vec],
            anns_field="embedding",
            param={"metric_type": "IP", "params": {"nprobe": 10}},
            limit=k,
            output_fields=["text"]
        )
        return [hit.entity.get("text") for hit in result[0]]

# ------------------------------------
# LLM Generator (LLaMA 3.1 via Ollama)
# ------------------------------------
def generate_answer(prompt: str, model: str = "llama3") -> str:
    """
    Sends prompt to Ollama's LLaMA 3.1 model and returns generated answer.
    
    Args:
        prompt: Full prompt with context and question.
        model: Ollama model name (default 'llama3').
        
    Returns:
        Generated answer string or error message.
    """
    try:
        response = requests.post(
            OLLAMA_API_URL,
            headers={"Content-Type": "application/json"},
            json={
                "model": model,
                "messages": [
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": prompt}
                ]
            },
            timeout=30
        )
        response.raise_for_status()
        content = response.json()
        return content.get("message", {}).get("content", "[No content returned by model]")
    except requests.exceptions.RequestException as e:
        return f"[Error contacting Ollama server: {str(e)}]"
    except Exception as e:
        return f"[Unexpected error: {str(e)}]"

# ------------------------------------
# RAG Pipeline
# ------------------------------------
def run_rag_pipeline(query: str, retriever, embed_manager: EmbeddingManager, llm_model: str = "llama3") -> str:
    """
    Runs the full RAG pipeline: retrieve context chunks + generate answer.
    
    Args:
        query: User's natural language query.
        retriever: Retriever instance (FAISS, Weaviate, or Milvus).
        embed_manager: EmbeddingManager instance.
        llm_model: Ollama model name to use.
        
    Returns:
        Generated answer string.
    """
    # Retrieve relevant chunks from retriever
    chunks = retriever.retrieve(query, embed_manager, k=5)
    # Combine chunks into context prompt
    context = "\n\n".join(chunks)
    prompt = f"""Use the following context to answer the question.

Context:
{context}

Question:
{query}"""
    # Generate answer from LLM
    return generate_answer(prompt, model=llm_model)

# ------------------------------------
# Evaluation Metrics for Retriever
# ------------------------------------
def precision_at_k(retrieved: List[str], relevant: List[str], k: int) -> float:
    """
    Precision@k: fraction of top-k retrieved chunks that are relevant.
    """
    return len(set(retrieved[:k]) & set(relevant)) / k

def recall_at_k(retrieved: List[str], relevant: List[str], k: int) -> float:
    """
    Recall@k: fraction of relevant chunks retrieved in top-k.
    """
    return len(set(retrieved[:k]) & set(relevant)) / len(relevant) if relevant else 0.0

def mrr(retrieved: List[str], relevant: List[str]) -> float:
    """
    Mean Reciprocal Rank: inverse rank of first relevant chunk retrieved.
    """
    for i, doc in enumerate(retrieved):
        if doc in relevant:
            return 1 / (i + 1)
    return 0.0

def ndcg_at_k(retrieved: List[str], relevant: List[str], k: int) -> float:
    """
    Normalized Discounted Cumulative Gain at k:
    Measures ranking quality giving higher weight to early relevant chunks.
    """
    def dcg(scores):
        return sum((2 ** s - 1) / np.log2(i + 2) for i, s in enumerate(scores))

    relevance = [1 if doc in relevant else 0 for doc in retrieved[:k]]
    ideal = sorted(relevance, reverse=True)
    dcg_val = dcg(relevance)
    idcg_val = dcg(ideal)
    return dcg_val / idcg_val if idcg_val != 0 else 0.0

def precision_at_k(retrieved_docs, relevant_docs, k):
    """
    Precision@k measures the proportion of top-k retrieved documents that are relevant.
    It answers: "Of the top-k documents returned, how many are actually relevant?"
    
    Args:
        retrieved_docs (list): List of documents retrieved by the system.
        relevant_docs (list): List of ground truth relevant documents.
        k (int): Number of top documents to consider.

    Returns:
        float: Precision@k score between 0 and 1.
    """
    retrieved_k = retrieved_docs[:k]
    relevant_set = set(relevant_docs)
    true_positives = sum(1 for doc in retrieved_k if doc in relevant_set)
    return true_positives / k


def recall_at_k(retrieved_docs, relevant_docs, k):
    """
    Recall@k measures the proportion of all relevant documents that are retrieved
    in the top-k results.
    It answers: "Of all relevant documents, how many did we retrieve in top-k?"
    
    Args:
        retrieved_docs (list): List of documents retrieved by the system.
        relevant_docs (list): List of ground truth relevant documents.
        k (int): Number of top documents to consider.

    Returns:
        float: Recall@k score between 0 and 1.
    """
    retrieved_k = retrieved_docs[:k]
    relevant_set = set(relevant_docs)
    true_positives = sum(1 for doc in retrieved_k if doc in relevant_set)
    return true_positives / len(relevant_set) if relevant_set else 0.0


def f1_at_k(retrieved_docs, relevant_docs, k):
    """
    F1@k is the harmonic mean of Precision@k and Recall@k,
    providing a balanced measure of both precision and recall.
    
    Args:
        retrieved_docs (list): List of documents retrieved by the system.
        relevant_docs (list): List of ground truth relevant documents.
        k (int): Number of top documents to consider.

    Returns:
        float: F1@k score between 0 and 1.
    """
    p = precision_at_k(retrieved_docs, relevant_docs, k)
    r = recall_at_k(retrieved_docs, relevant_docs, k)
    if p + r == 0:
        return 0.0
    return 2 * p * r / (p + r)


def average_precision_at_k(retrieved_docs, relevant_docs, k):
    """
    Average Precision@k (AP@k) measures the average of precision values
    calculated at the points where relevant documents are retrieved.
    It rewards systems that retrieve relevant documents earlier.
    
    Args:
        retrieved_docs (list): List of documents retrieved by the system.
        relevant_docs (list): List of ground truth relevant documents.
        k (int): Number of top documents to consider.

    Returns:
        float: AP@k score between 0 and 1.
    """
    relevant_set = set(relevant_docs)
    hits = 0
    sum_precisions = 0.0
    for i in range(k):
        if i >= len(retrieved_docs):
            break
        if retrieved_docs[i] in relevant_set:
            hits += 1
            sum_precisions += hits / (i + 1)  # precision at this position
    return sum_precisions / min(len(relevant_set), k) if relevant_set else 0.0


def ndcg_at_k(retrieved_docs, relevant_docs, k):
    """
    Normalized Discounted Cumulative Gain (NDCG@k) measures the usefulness,
    or gain, of a document based on its position in the result list,
    giving higher scores to relevant documents appearing earlier.
    
    Args:
        retrieved_docs (list): List of documents retrieved by the system.
        relevant_docs (list): List of ground truth relevant documents.
        k (int): Number of top documents to consider.

    Returns:
        float: NDCG@k score between 0 and 1.
    """
    relevant_set = set(relevant_docs)
    dcg = 0.0
    for i in range(k):
        if i >= len(retrieved_docs):
            break
        rel = 1 if retrieved_docs[i] in relevant_set else 0
        denom = np.log2(i + 2)  # i+2 because i starts at 0
        dcg += rel / denom
    # Ideal DCG (IDCG) is the best possible DCG where all relevant docs appear first
    ideal_rels = [1] * min(len(relevant_set), k)
    idcg = sum(1 / np.log2(i + 2) for i in range(len(ideal_rels)))
    return dcg / idcg if idcg > 0 else 0.0


def exact_match(predicted_answer, ground_truth):
    """
    Exact Match (EM) measures whether the predicted answer exactly matches
    the ground truth answer, ignoring case and leading/trailing whitespace.
    
    Args:
        predicted_answer (str): The generated answer.
        ground_truth (str): The true answer.

    Returns:
        float: 1.0 if exact match, else 0.0.
    """
    return 1.0 if predicted_answer.strip().lower() == ground_truth.strip().lower() else 0.0


def compute_all_metrics(predicted_docs, relevant_docs, predicted_answer, ground_truth, k=5):
    """
    Compute all defined metrics and return them as a dictionary.
    
    Args:
        predicted_docs (list): List of retrieved document identifiers.
        relevant_docs (list): List of ground truth relevant document identifiers.
        predicted_answer (str): Answer generated by the system.
        ground_truth (str): Actual ground truth answer.
        k (int): Number of top documents to consider in ranking metrics.

    Returns:
        dict: Mapping metric names to their float scores.
    """
    return {
        'precision': precision_at_k(predicted_docs, relevant_docs, k),
        'recall': recall_at_k(predicted_docs, relevant_docs, k),
        'f1': f1_at_k(predicted_docs, relevant_docs, k),
        'map': average_precision_at_k(predicted_docs, relevant_docs, k),
        'ndcg': ndcg_at_k(predicted_docs, relevant_docs, k),
        'exact_match': exact_match(predicted_answer, ground_truth),
    }


def compute_overall_score(metrics_dict, use_weights=True):
    """
    Compute overall accuracy from individual metrics.
    - If use_weights=True, use predefined weights reflecting metric importance.
    - Otherwise, compute simple average giving equal weight to all metrics.

    Args:
        metrics_dict (dict): Dictionary of metric scores.
        use_weights (bool): Whether to apply weights.

    Returns:
        float: Overall accuracy score.
    """
    weights = {
        'precision': 0.2,
        'recall': 0.2,
        'f1': 0.2,
        'map': 0.2,
        'ndcg': 0.1,
        'exact_match': 0.1
    }
    if use_weights:
        overall = sum(metrics_dict[m] * weights[m] for m in weights if m in metrics_dict)
    else:
        overall = sum(metrics_dict.values()) / len(metrics_dict)
    return overall


def parse_list_from_csv_field(field_value):
    """
    Convert a comma-separated string from CSV to a list of stripped strings.
    
    Args:
        field_value (str): Comma-separated string from CSV field.

    Returns:
        list: List of individual trimmed strings.
    """
    return [x.strip() for x in field_value.split(",") if x.strip()]


def evaluate_test_cases(csv_file_path, k=5):
    """
    Evaluate RAG model performance on multiple test cases stored in a CSV file.
    Each row should contain:
        - query: The user's question.
        - ground_truth: The true answer string.
        - relevant_docs: Comma-separated list of relevant doc IDs.
        - predicted_docs: Comma-separated list of predicted doc IDs.
        - predicted_answer: The system's answer string.

    Args:
        csv_file_path (str): Path to CSV file containing test cases.
        k (int): Number of top retrieved documents to consider.

    Prints:
        Metric results and overall scores per test case.
    """
    with open(csv_file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for idx, row in enumerate(reader, start=1):
            query = row['query']
            ground_truth = row['ground_truth']
            relevant_docs = parse_list_from_csv_field(row['relevant_docs'])
            predicted_docs = parse_list_from_csv_field(row['predicted_docs'])
            predicted_answer = row['predicted_answer']

            print(f"\nTest Case #{idx}")
            print(f"Query: {query}")
            metrics = compute_all_metrics(predicted_docs, relevant_docs, predicted_answer, ground_truth, k)
            
            # Print each metric with explanation
            for metric_name, metric_value in metrics.items():
                explanation = {
                    'precision': "Precision@k: Proportion of retrieved docs in top-k that are relevant.",
                    'recall': "Recall@k: Proportion of all relevant docs retrieved in top-k.",
                    'f1': "F1@k: Harmonic mean of precision and recall, balancing both.",
                    'map': "MAP@k: Average precision over relevant docs, rewarding earlier retrieval.",
                    'ndcg': "NDCG@k: Discounted gain rewarding relevant docs higher in ranking.",
                    'exact_match': "Exact Match: Whether predicted answer matches ground truth exactly."
                }
                print(f"{metric_name.capitalize()}: {metric_value:.4f} ({explanation.get(metric_name, '')})")

            overall_equal = compute_overall_score(metrics, use_weights=False)
            overall_weighted = compute_overall_score(metrics, use_weights=True)
            print(f"Overall Score (Equal weights): {overall_equal:.4f} (Simple average of all metrics)")
            print(f"Overall Score (Weighted): {overall_weighted:.4f} (Weighted by metric importance)")
            print("-" * 50)


if __name__ == "__main__":
    csv_file = "test_cases.csv"
    evaluate_test_cases(csv_file, k=5)
