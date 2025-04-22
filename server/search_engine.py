import os
import google.generativeai as genai
from dotenv import load_dotenv
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

EMBED_MODEL = "models/embedding-001"

def embed_text(text):
    response = genai.embed_content(
        model=EMBED_MODEL,
        content=text,
        task_type="retrieval_document"
    )
    return response['embedding']

def load_documents(folder_path="knowledge_base"):
    documents = []
    for filename in os.listdir(folder_path):
        if filename.endswith(".md"):
            with open(os.path.join(folder_path, filename), "r", encoding="utf-8") as f:
                content = f.read()
                documents.append({
                    "filename": filename,
                    "content": content,
                    "embedding": embed_text(content)
                })
    return documents

def search_docs(documents, query, top_k=3, threshold=0.7):
    query_vec = np.array(embed_text(query)).reshape(1, -1)
    doc_vectors = np.array([doc['embedding'] for doc in documents])
    
    scores = cosine_similarity(query_vec, doc_vectors)[0]
    top_indices = scores.argsort()[::-1]

    top_results = []
    for idx in top_indices:
        if scores[idx] < threshold:
            continue
        top_results.append((documents[idx], scores[idx]))
        if len(top_results) >= top_k:
            break

    return top_results  # list of (doc, score) tuples
