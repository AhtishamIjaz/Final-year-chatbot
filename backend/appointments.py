"""
appointments.py — Simple JSON-file based appointment management.
"""

import json
import uuid
import os
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, os.path.dirname(__file__))

APPOINTMENTS_FILE = Path(__file__).resolve().parent.parent / "appointments.json"


def _load() -> list[dict]:
    if APPOINTMENTS_FILE.exists():
        try:
            return json.loads(APPOINTMENTS_FILE.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return []
    return []


def _save(data: list[dict]) -> None:
    APPOINTMENTS_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


# ── CRUD ───────────────────────────────────────────────────────────────────────

def create_appointment(
    patient_name: str,
    doctor: str,
    date: str,
    time: str,
    reason: str,
    phone: str = "",
) -> dict:
    """Book a new appointment and persist it."""
    appointments = _load()
    appt = {
        "id": str(uuid.uuid4()),
        "patient_name": patient_name,
        "doctor": doctor,
        "date": date,
        "time": time,
        "reason": reason,
        "phone": phone,
        "status": "confirmed",
        "created_at": datetime.now().isoformat(),
    }
    appointments.append(appt)
    _save(appointments)
    return appt


def get_appointments() -> list[dict]:
    """Return all appointments sorted by date (newest first)."""
    appts = _load()
    return sorted(appts, key=lambda a: a.get("created_at", ""), reverse=True)


def cancel_appointment(appointment_id: str) -> bool:
    """Mark an appointment as cancelled. Returns True if found."""
    appointments = _load()
    for appt in appointments:
        if appt["id"] == appointment_id:
            appt["status"] = "cancelled"
            _save(appointments)
            return True
    return False


def delete_appointment(appointment_id: str) -> bool:
    """Permanently delete an appointment record."""
    appointments = _load()
    new_list = [a for a in appointments if a["id"] != appointment_id]
    if len(new_list) == len(appointments):
        return False          # not found
    _save(new_list)
    return True
