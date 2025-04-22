#  Formly AI Chatbot - AI Intern Assignment

This project is a full-stack AI chatbot application built for a fictional SaaS form builder product called **Formly**. The chatbot answers user questions using a knowledge base of documentation files and Google's **Gemini 1.5 Pro** model.

>  This project fulfills all the requirements listed in the AI Internship assignment.

---

##  Features Implemented

###  LLM Chatbot (Gemini)
- Uses Google Gemini 1.5 Pro model to generate answers
- Prompts are dynamically created based on documentation context

###  Documentation Embedding
- All `.md` files in `knowledge_base/` are embedded using `models/embedding-001`
- Semantic search is performed using cosine similarity (via scikit-learn)

###  Vector Similarity Search
- User query is embedded
- Compared with all document embeddings
- Top 3 most relevant documents (with similarity >= 0.75) are selected

###  Prompt Engineering
- Relevant documentation snippets are injected into Gemini's prompt
- Prompt includes:
  - Assistant role
  - Context block from documentation
  - User's question

###  Fallback Handling
- If no document is a good match, Gemini is **not called**
- A polite fallback message is returned instead

###  Frontend UI (React + Vite)
- Styled chat interface
- Markdown rendering for Gemini responses
- Feedback buttons (👍/👎) for user ratings

###  Chat & Feedback Logging
- Logs all chats in `logs/chat_log.jsonl`
- Logs feedback in `logs/feedback_log.jsonl`
- Each log includes:
  - Timestamp
  - Question
  - Reply
  - Feedback / Fallback usage
  - Matched document filenames (for chat)

---

##  Folder Structure

```
server/
├── main.py                # FastAPI backend
├── search_engine.py       # Embedding + semantic search
├── logs/
│   ├── chat_log.jsonl     # Chat history
│   └── feedback_log.jsonl # Feedback tracking
├── knowledge_base/        # Markdown documentation used for search
└── .env                   # Contains GEMINI_API_KEY

client/
├── src/
│   └── ChatBot.jsx        # Main React component
├── index.html
└── vite.config.js
```

---

##  How to Run This Project

###  Prerequisites
- Python 3.9+
- Node.js (v16+)
- A valid Google Gemini API Key ([get one](https://aistudio.google.com/app/apikey))

---

###  Backend Setup (FastAPI)

1. Navigate to the backend folder:
   ```bash
   cd server
   ```
2. Create and activate virtual environment:
   ```bash
   python -m venv venv
   venv\Scripts\activate  # on Windows
   # or
   source venv/bin/activate  # on macOS/Linux
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Create a `.env` file with your Gemini API key:
   ```env
   GEMINI_API_KEY=your_google_api_key
   ```
5. Run the FastAPI server:
   ```bash
   uvicorn main:app --reload --port 5000
   ```

---

###  Frontend Setup (React + Vite)

1. Navigate to the React client:
   ```bash
   cd client
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Start the dev server:
   ```bash
   npm run dev
   ```
4. Visit:
   http://localhost:5173

---

##  API Endpoints

### `POST /api/chat`
- Sends chat messages
- Returns Gemini response or fallback

**Request body:**
```json
{
  "messages": ["hi", "how do I export data?"]
}
```

**Response:**
```json
{
  "reply": "Go to Responses tab and click Export..."
}
```

---

### `POST /api/feedback`
- Records feedback about the latest bot response

**Request body:**
```json
{
  "question": "How do I export responses?",
  "reply": "Click export in the Responses tab...",
  "feedback": "up"
}
```

**Response:**
```json
{
  "message": "Feedback received."
}
```

---

##  Sample Questions to Ask

> Test the chatbot using questions that are covered by the markdown files:

- "How do I export responses?"
- "Can I customize the form theme?"
- "Is my data private?"
- "Does Formly support file upload?"
- "What’s the free plan limit?"

And test fallback with:
- "Can Formly make coffee?"
- "Is it raining in Tokyo?"

