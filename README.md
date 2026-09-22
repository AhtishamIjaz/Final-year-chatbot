# MedGPT — AI Medical Assistant Chatbot 🏥

**Telemedicine Platform powered by RAG + LLM**
   
## 🚀 How to Run (Step by Step)

### Step 1 — Prerequisites
Make sure Python 3.9+ is installed on your PC.  
Check by running: `python --version`

### Step 2 — Setup (Run ONCE)
Double-click **`setup.bat`** — this will:
- Install all Python packages
- Load the medical knowledge base into ChromaDB

### Step 3 — Start the Application
Double-click **`run.bat`** — this will:
- Start the FastAPI backend server
- Open your browser at `http://localhost:8000`

---

## 📁 Project Structure

```
MedGPT/
├── backend/
│   ├── main.py          ← FastAPI server (entry point)
│   ├── chat.py          ← Groq LLM + RAG chat logic
│   ├── rag.py           ← RAG pipeline (Gemini + ChromaDB)
│   ├── ingest.py        ← Knowledge base ingestion script
│   ├── appointments.py  ← Appointment management
│   ├── config.py        ← API keys & settings
│   ├── .env             ← Environment variables
│   └── requirements.txt
├── knowledge_base/
│   ├── symptoms.txt
│   ├── diseases.txt
│   ├── medications.txt
│   ├── first_aid.txt
│   └── clinical_guidelines.txt
├── frontend/
│   ├── index.html       ← Main UI
│   ├── css/style.css    ← Styling
│   └── js/app.js        ← Frontend logic
├── setup.bat            ← One-click setup
└── run.bat              ← One-click run
```

---

## 🔑 API Keys

| Service | Key Location | Purpose |
|---------|-------------|---------|
| Groq    | `backend/.env` | LLM (Llama 3.1 70B) |
| Gemini  | `backend/.env` | Text Embeddings |

---

## 🏗️ Architecture

```
User Browser
    │
    ▼
[Frontend: HTML/CSS/JS]
    │  POST /chat
    ▼
[FastAPI Backend (Python)]
    │
    ├──► [RAG Pipeline]
    │        ├── Gemini Embedding API  ← embeds user query
    │        └── ChromaDB Vector Store ← retrieves top-K chunks
    │
    └──► [Groq LLM API — Llama 3.1 70B]
             └── Generates verified, cited medical response
```

---

## ✨ Features

- 🔍 **Symptom Checker** — AI-powered conversational symptom analysis
- 💊 **Medication Information** — Drug details, dosages, side effects
- 📅 **Appointment Booking** — Schedule with specialist doctors
- 📚 **Source Citations** — Every response cites medical knowledge sources
- 🚨 **Emergency Guidance** — First aid & emergency contact information
- 🌐 **Multilingual** — Supports multiple languages via LLM

---

## 🛠️ Technology Stack

| Component | Technology |
|-----------|-----------|
| Backend   | Python, FastAPI |
| LLM       | Groq API (Llama 3.1 70B) — Free |
| Embeddings | Google Gemini text-embedding-004 — Free |
| Vector DB | ChromaDB (local) |
| RAG       | LangChain |
| Frontend  | HTML5, CSS3, JavaScript |

---

## ⚠️ Medical Disclaimer

MedGPT is an academic project for educational purposes. It provides general health information only and is **not** a substitute for professional medical advice, diagnosis, or treatment. Always consult a qualified healthcare professional.
