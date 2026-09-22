"""
chat.py — Core chat logic: RAG retrieval + Groq LLM call.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from groq import Groq
from config import GROQ_API_KEY, GROQ_MODEL, SYSTEM_PROMPT
from rag import retrieve_context

_client = Groq(api_key=GROQ_API_KEY)


def chat(user_message: str, history: list[dict]) -> dict:
    """
    Process a user message through the RAG + LLM pipeline.

    Parameters
    ----------
    user_message : str
        The latest message from the patient.
    history : list[dict]
        Previous conversation turns as {"role": ..., "content": ...}.

    Returns
    -------
    dict with keys:
        response  — AI assistant reply text
        sources   — list of source filenames cited
        model     — LLM model name used
    """
    # 1. Retrieve relevant medical context ─────────────────────────────────────
    context, sources = retrieve_context(user_message)

    context_block = ""
    if context:
        context_block = (
            "\n\n═══ RETRIEVED MEDICAL KNOWLEDGE ═══\n"
            f"{context}"
            "\n═══ END OF RETRIEVED KNOWLEDGE ═══\n\n"
            "Use the above retrieved knowledge to answer the question accurately. "
            "Cite the relevant source(s) in your response."
        )

    # 2. Build message list ────────────────────────────────────────────────────
    messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT + context_block,
        }
    ]

    # Keep last 12 turns (6 exchanges) to stay within token limits
    for turn in history[-12:]:
        messages.append({"role": turn["role"], "content": turn["content"]})

    messages.append({"role": "user", "content": user_message})

    # 3. Call Groq LLM ─────────────────────────────────────────────────────────
    completion = _client.chat.completions.create(
        model=GROQ_MODEL,
        messages=messages,
        max_tokens=1024,
        temperature=0.25,   # lower = more factual / conservative
        top_p=0.9,
    )

    assistant_reply = completion.choices[0].message.content

    return {
        "response": assistant_reply,
        "sources": sources,
        "model": GROQ_MODEL,
    }
