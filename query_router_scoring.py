from sentence_transformers import SentenceTransformer, util
import re

# =========================
# Initialize global models
# =========================
sbert_model = SentenceTransformer('all-MiniLM-L6-v2')

# Domain-specific structured concepts
domain_concepts = [
    "CTC", "package", "placement", "salary", "year", "department",
    "recruiter", "students placed", "job role", "percentage"
]
concept_embeddings = sbert_model.encode(domain_concepts, convert_to_tensor=True)

# =========================
# Compute Syntax Score
# =========================
def compute_syntax_score(query: str) -> float:
    query = query.lower()

    keyword_categories = {
        "aggregation": {
            "keywords": ['sum', 'avg', 'average', 'count', 'total'],
            "weight": 0.25
        },
        "numeric_ops": {
            "keywords": ['max', 'min', 'greater than', 'less than', 'between', '>', '<', '='],
            "weight": 0.25
        },
        "grouping": {
            "keywords": ['group by', 'order by', 'rank', 'top', 'by'],
            "weight": 0.20
        },
        "temporal_filters": {
            "keywords": ['in 2023', 'after', 'before', 'more than', 'less than', 'percent'],
            "weight": 0.15
        },
        "column_refs": {
            "keywords": ['ctc', 'package', 'branch', 'department', 'batch', 'year'],
            "weight": 0.15
        }
    }

    score = 0
    total_possible = sum(cat["weight"] for cat in keyword_categories.values())

    for category in keyword_categories.values():
        if any(keyword in query for keyword in category["keywords"]):
            score += category["weight"]

    return score / total_possible  # normalized to [0,1]

# =========================
# Compute Semantic Score
# =========================
def compute_semantic_score(query: str, top_k: int = 3) -> float:
    query_embedding = sbert_model.encode(query, convert_to_tensor=True)
    cosine_scores = util.cos_sim(query_embedding, concept_embeddings)[0]
    top_k_scores = cosine_scores.topk(top_k).values
    avg_score = top_k_scores.mean().item()
    return avg_score  # Already between 0 and 1

# =========================
# Parse LLM Classification Response
# =========================
def parse_llm_response(response: str):
    label = "unknown"
    confidence = 0.0

    label_match = re.search(r'\b(text-to-SQL|RAG)\b', response, re.IGNORECASE)
    conf_match = re.search(r'Confidence\s*[:=]?\s*(\d*\.?\d+)', response)

    if label_match:
        label = label_match.group(1).lower()

    if conf_match:
        confidence = float(conf_match.group(1))
        confidence = max(0.0, min(confidence, 1.0))  # clamp between 0-1

    return label, confidence

# =========================
# Calibrate Threshold Dynamically
# =========================
def calibrate_threshold(prev_threshold, prev_accuracy, target_accuracy=0.90, alpha=0.05):
    return prev_threshold + alpha * (prev_accuracy - target_accuracy)

# =========================
# Final Routing Function
# =========================
def route_query(query: str, llm_response: str, threshold: float):
    syntax_score = compute_syntax_score(query)
    semantic_score = compute_semantic_score(query)
    label, llm_confidence = parse_llm_response(llm_response)

    final_score = 0.4 * syntax_score + 0.3 * semantic_score + 0.3 * llm_confidence

    if final_score > threshold:
        route = "text-to-SQL"
    else:
        route = "rag"

    return {
        "route": route,
        "final_score": round(final_score, 4),
        "syntax_score": round(syntax_score, 4),
        "semantic_score": round(semantic_score, 4),
        "llm_confidence": round(llm_confidence, 4),
        "classification": label
    }

# =========================
# Evaluate Routing Accuracy & Update Threshold
# =========================
def update_threshold_over_time(prev_threshold, routing_results, true_labels, target_accuracy=0.90, alpha=0.05):
    correct = 0
    for result, truth in zip(routing_results, true_labels):
        if result["route"].lower() == truth.lower():
            correct += 1
    accuracy = correct / len(routing_results)
    new_threshold = calibrate_threshold(prev_threshold, accuracy, target_accuracy, alpha)
    return new_threshold, round(accuracy, 4)