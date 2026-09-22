"""
main.py — FastAPI application entry point for MedGPT.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Optional
from pathlib import Path

from chat import chat as process_chat
from appointments import (
    create_appointment,
    get_appointments,
    cancel_appointment,
    delete_appointment,
)

# ── App ────────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="MedGPT — AI Medical Assistant Chatbot",
    description="Telemedicine chatbot powered by RAG + LLM (Groq + Gemini + ChromaDB)",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve the frontend static files
FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"
if FRONTEND_DIR.exists():
    css_dir = FRONTEND_DIR / "css"
    js_dir = FRONTEND_DIR / "js"
    if css_dir.exists():
        app.mount("/css", StaticFiles(directory=str(css_dir)), name="css")
    if js_dir.exists():
        app.mount("/js", StaticFiles(directory=str(js_dir)), name="js")
    app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")


# ── Schemas ────────────────────────────────────────────────────────────────────

class ChatMessage(BaseModel):
    role: str       # "user" | "assistant"
    content: str


class ChatRequest(BaseModel):
    message: str
    history: List[ChatMessage] = []


class AppointmentRequest(BaseModel):
    patient_name: str
    doctor: str
    date: str
    time: str
    reason: str
    phone: Optional[str] = ""


# ── Routes ─────────────────────────────────────────────────────────────────────

@app.get("/", include_in_schema=False)
async def serve_frontend():
    index = FRONTEND_DIR / "index.html"
    if index.exists():
        return FileResponse(str(index))
    return {"message": "MedGPT API is running. Open frontend/index.html in a browser."}


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "MedGPT — AI Medical Assistant Chatbot",
        "version": "1.0.0",
    }


@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    try:
        history = [{"role": m.role, "content": m.content} for m in request.history]
        result = process_chat(request.message, history)
        return result
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Chat error: {str(exc)}")


@app.get("/appointments")
async def list_appointments():
    return get_appointments()


@app.post("/appointments")
async def book_appointment(request: AppointmentRequest):
    try:
        appt = create_appointment(
            patient_name=request.patient_name,
            doctor=request.doctor,
            date=request.date,
            time=request.time,
            reason=request.reason,
            phone=request.phone or "",
        )
        return {"success": True, "appointment": appt}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.delete("/appointments/{appointment_id}")
async def cancel_appt(appointment_id: str):
    ok = cancel_appointment(appointment_id)
    if ok:
        return {"success": True, "message": "Appointment cancelled successfully."}
    raise HTTPException(status_code=404, detail="Appointment not found.")


@app.delete("/appointments/{appointment_id}/delete")
async def delete_appt(appointment_id: str):
    ok = delete_appointment(appointment_id)
    if ok:
        return {"success": True, "message": "Appointment deleted."}
    raise HTTPException(status_code=404, detail="Appointment not found.")


# ── Entry ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
