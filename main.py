# -*- coding: utf-8 -*-
"""
This script creates a FastAPI application to serve the comment analysis pipeline.
It loads the models once on startup and provides an endpoint to analyze comments.
"""
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
import analysis # Our refactored analysis logic

# --- Model Loading ---
# This section runs only once when the application starts.
print("Loading models...")

# Stage 1: Malicious Comment Filter
malicious_model_name = "unitary/toxic-bert"
malicious_tokenizer = AutoTokenizer.from_pretrained(malicious_model_name)
malicious_model = AutoModelForSequenceClassification.from_pretrained(malicious_model_name)

# Stage 2: Sentiment Analysis
sentiment_model_name = "distilbert-base-uncased-finetuned-sst-2-english"
sentiment_tokenizer = AutoTokenizer.from_pretrained(sentiment_model_name)
sentiment_model = AutoModelForSequenceClassification.from_pretrained(sentiment_model_name)

# Stage 3: Topic Classification
topic_classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")

print("Models loaded successfully!")
# --- End of Model Loading ---


# Initialize FastAPI app
app = FastAPI()

# Define the request body structure using Pydantic
class CommentsRequest(BaseModel):
    comments: List[str]

@app.post("/analyze/")
def analyze_comments(request: CommentsRequest):
    """
    Analyzes a batch of comments through the 3-stage pipeline.
    """
    # Stage 1: Filter malicious comments
    malicious_flags = analysis.is_malicious(
        request.comments, model=malicious_model, tokenizer=malicious_tokenizer
    )

    # Filter out malicious comments for the next stages
    non_malicious_comments = [
        comment for comment, is_mal in zip(request.comments, malicious_flags) if not is_mal
    ]

    # Initialize results list
    final_results = []
    
    if non_malicious_comments:
        # Stage 2 & 3: Run on the clean comments
        sentiments = analysis.analyze_sentiment(
            non_malicious_comments, model=sentiment_model, tokenizer=sentiment_tokenizer
        )
        topics = analysis.classify_topic(non_malicious_comments, classifier=topic_classifier)
        
        # Prepare the results for non-malicious comments
        clean_results = iter(zip(sentiments, topics))
        for comment, is_mal in zip(request.comments, malicious_flags):
            if not is_mal:
                sentiment, topic = next(clean_results)
                final_results.append({
                    "comment": comment, "is_malicious": False, "sentiment": sentiment, "topic": topic
                })
            else:
                final_results.append({"comment": comment, "is_malicious": True})
    else:
        # Handle case where all comments were malicious
        for comment in request.comments:
            final_results.append({"comment": comment, "is_malicious": True})

    return {"results": final_results}

@app.get("/")
def read_root():
    return {"message": "Comment Analysis API is running."}
