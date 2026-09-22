# MedGPT — AI Medical Assistant Chatbot
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Upgrade pip and install wheel
RUN pip install --no-cache-dir --upgrade pip wheel

# Install dependencies directly with generous timeout and no-deps conflict
COPY backend/requirements.txt /app/backend/requirements.txt
RUN pip install --no-cache-dir --default-timeout=1000 -r /app/backend/requirements.txt

# Copy all project files including existing pre-indexed ChromaDB
COPY backend /app/backend
COPY frontend /app/frontend
COPY knowledge_base /app/knowledge_base

WORKDIR /app/backend

# Verify ingestion / generate ChromaDB if not already present
RUN python -c "import os; from pathlib import Path; p = Path('chroma_db'); exit(0 if p.exists() and any(p.iterdir()) else 1)" || python ingest.py

EXPOSE 8000

CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
