from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import google.generativeai as genai
from dotenv import load_dotenv
import os
import json
from datetime import datetime

from search_engine import load_documents, search_docs

# Load environment variables
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Load Gemini model
model = genai.GenerativeModel("models/gemini-1.5-pro")

# Load knowledge base
docs = load_documents("knowledge_base")

# FastAPI app setup
app = FastAPI()

# CORS config
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request schema for chat
class ChatRequest(BaseModel):
    messages: list[str]

# Request schema for feedback
class Feedback(BaseModel):
    question: str
    reply: str
    feedback: str  # "up" or "down"

# Chat logging function
def log_chat(user_message, matched_docs, reply, fallback):
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "question": user_message,
        "matched_docs": [doc['filename'] for doc, _ in matched_docs] if matched_docs else [],
        "fallback_used": fallback,
        "reply": reply
    }

    log_file_path = "logs/chat_log.jsonl"
    os.makedirs(os.path.dirname(log_file_path), exist_ok=True)

    with open(log_file_path, "a", encoding="utf-8") as log_file:
        log_file.write(json.dumps(log_entry) + "\n")

# Feedback logging function
@app.post("/api/feedback")
async def feedback(data: Feedback):
    try:
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "question": data.question,
            "reply": data.reply,
            "feedback": data.feedback
        }

        log_file_path = "logs/feedback_log.jsonl"
        os.makedirs(os.path.dirname(log_file_path), exist_ok=True)

        with open(log_file_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry) + "\n")

        return {"message": "Feedback received."}
    except Exception as e:
        return {"error": str(e)}

# Chat endpoint
@app.post("/api/chat")
async def chat(req: ChatRequest):
    try:
        user_message = req.messages[-1]
        top_docs_with_scores = search_docs(docs, user_message, top_k=3, threshold=0.7)

        # Fallback condition
        if not top_docs_with_scores or not any(score >= 0.75 for _, score in top_docs_with_scores):
            fallback_reply = (
                "I'm not sure I have the right answer for that. "
                "Please check our documentation or contact support!"
            )
            log_chat(user_message, [], fallback_reply, fallback=True)
            return {"reply": fallback_reply}

        # Construct context from docs
        context_text = "\n\n".join(
            [f"From {doc['filename']}:\n{doc['content']}" for doc, score in top_docs_with_scores]
        )

        # Construct prompt for Gemini
        prompt = f"""You are a helpful AI support assistant for a SaaS product called Formly.

Here is some documentation to help answer the user's question:

{context_text}

User question: {user_message}

Answer using the documentation above. If not found, reply with a polite fallback message.
"""

        # Generate response
        response = model.generate_content(prompt)
        log_chat(user_message, top_docs_with_scores, response.text, fallback=False)
        return {"reply": response.text}

    except Exception as e:
        return {"error": str(e)}