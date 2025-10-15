# Comment Analysis Pipeline API
This project provides a REST API for analyzing user comments through a three-stage pipeline. It is built with FastAPI and containerized with Docker for easy deployment and scalability.
## Overview
The API processes a batch of comments and returns a detailed analysis for each one. The pipeline consists of the following stages:
1. Malicious Comment Filtering: Each comment is first checked for toxicity (e.g., insults, threats, obscenity) using the `unitary/toxic-bert` model. Malicious comments are flagged and are not processed further.
2. Sentiment Analysis: Non-malicious comments are analyzed for sentiment (Positive/Negative) using the `distilbert-base-uncased-finetuned-sst-2-english` model.
3. Topic Classification: Finally, the comments are classified into predefined topics (Product Feedback or General Comment) using the `facebook/bart-large-mnli` zero-shot classification model.
## Getting Started
### Prerequisites
You must have Docker installed and running on your machine.
- [Install Docker](https://docs.docker.com/get-docker/)
### Setup and Running the Application
Follow these steps to build the Docker image and run the application.
1. Clone/Download the Project:
   Ensure you have the following files in a single directory:
   ```
   .
   ├── analysis.py
   ├── main.py
   ├── requirements.txt
   └── Dockerfile
   ```
2. Build the Docker Image:
Open a terminal in the project directory and run the following command. This will build the image and download all the necessary models. This step may take some time.
```Bash
docker build -t comment-analysis-api .
```
3. Run the Docker Container:
Once the image is built, start a container with this command. This will expose the API on port 8000.
```Bash
docker run -p 8000:8000 comment-analysis-api
```
You should see log output from Uvicorn indicating that the server has started and the models have been loaded successfully. The API is now ready to accept requests.
## API Usage
### Endpoint:`POST /analyze/`
This endpoint analyzes a list of comments.
### Request Body:
The request body should be a JSON object containing a single key, comments, with a list of strings as its value.
```
{
  "comments": [
    "This is a fantastic product, I love it!",
    "You are all idiots, this is the worst thing ever.",
    "The new update is a bit slow on my device."
  ]
}
```
### Example Request`curl`:
You can test the endpoint from a new terminal window with the following command (in Bash):
```Bash
curl -X POST "http://localhost:8000/analyze/" \
-H "Content-Type: application/json" \
-d '{
  "comments": [
    "This is a fantastic product, I love it!",
    "You are all idiots, this is the worst thing ever.",
    "The new update is a bit slow on my device."
  ]
}'
```
or using Invoke-WebRequest(curl) in PowerShell:
```ps
Invoke-WebRequest -Uri "http://localhost:8000/analyze/" `
-Method POST `
-Headers @{"Content-Type"="application/json"} `
-Body '{
  "comments": [
    "This is a fantastic product, I love it!",
    "You are all idiots, this is the worst thing ever.",
    "The new update is a bit slow on my device."
  ]
}'
```
### Success Response (200 OK):
The API will return a JSON object with a `results` key. Each item in the list corresponds to a comment from the request.
- If a comment is flagged as malicious, the analysis stops there.
- If a comment is clean, it will include the sentiment and topic classification.
```Bash
{
  "results": [
    {
      "comment": "This is a fantastic product, I love it!",
      "is_malicious": false,
      "sentiment": "POSITIVE",
      "topic": "Product Feedback"
    },
    {
      "comment": "You are all idiots, this is the worst thing ever.",
      "is_malicious": true
    },
    {
      "comment": "The new update is a bit slow on my device.",
      "is_malicious": false,
      "sentiment": "NEGATIVE",
      "topic": "Product Feedback"
    }
  ]
}
```
