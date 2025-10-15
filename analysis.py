# -*- coding: utf-8 -*-
"""
This script contains the core logic for the three-stage comment analysis pipeline.
The models are loaded separately and passed into these functions to avoid
reloading them on every request in a production environment.
"""

from transformers import AutoTokenizer, AutoModelForSequenceClassification, Pipeline
import torch
from typing import List, Dict, Any

# Stage 1: Malicious Comment Filtering
def is_malicious(comments: List[str], model: AutoModelForSequenceClassification, tokenizer: AutoTokenizer, threshold: float = 0.5) -> List[bool]:
    """
    Uses a pre-loaded model to detect if a batch of comments is malicious.
    """
    print("Stage 1: Filtering malicious comments...")
    inputs = tokenizer(comments, return_tensors="pt", truncation=True, padding=True)
    with torch.no_grad():
        outputs = model(**inputs)
    probabilities = torch.sigmoid(outputs.logits).numpy()
    results = (probabilities > threshold).any(axis=1).tolist()
    print(f"--> Malicious filter complete. Found {sum(results)} malicious comments.")
    return results

# Stage 2: Sentiment Analysis
def analyze_sentiment(comments: List[str], model: AutoModelForSequenceClassification, tokenizer: AutoTokenizer) -> List[str]:
    """
    Uses a pre-loaded model to classify a batch of comments as positive or negative.
    """
    print("Stage 2: Analyzing sentiment...")
    inputs = tokenizer(comments, return_tensors="pt", truncation=True, padding=True)
    with torch.no_grad():
        outputs = model(**inputs)
    logits = outputs.logits
    predicted_class_ids = torch.argmax(logits, dim=1).tolist()
    sentiments = [model.config.id2label[cid] for cid in predicted_class_ids]
    print("--> Sentiment analysis complete.")
    return sentiments

# Stage 3: Topic Classification
def classify_topic(comments: List[str], classifier: Pipeline) -> List[str]:
    """
    Uses a pre-loaded zero-shot pipeline to classify a batch of comments.
    """
    print("Stage 3: Classifying topic...")
    candidate_labels = ["Product Feedback", "General Comment"]
    results = classifier(comments, candidate_labels, batch_size=8)
    topics = [result['labels'][0] for result in results]
    print("--> Topic classification complete.")
    return topics
