from core.database import SessionLocal
from models.db_schema import VisitNote, Patient, Appointment
from datetime import datetime

def save_patient_note(appointment_id: int, note_content: str, urgency: str = "Low"):
    """Saves a patient note for a specific appointment."""
    db = SessionLocal()
    try:
        new_note = VisitNote(
            appointment_id=appointment_id,
            note_content=note_content,
            urgency_level=urgency
        )
        db.add(new_note)
        db.commit()
        db.refresh(new_note)
        return {"status": "success", "note_id": new_note.id}
    except Exception as e:
        db.rollback()
        return {"status": "error", "message": str(e)}
    finally:
        db.close()

def get_patient_records(patient_id: int):
    """Retrieves all visit notes for a specific patient."""
    db = SessionLocal()
    try:
        notes = db.query(VisitNote).join(Appointment).filter(Appointment.patient_id == patient_id).all()
        return [{"appointment_id": n.appointment_id, "content": n.note_content, "urgency": n.urgency_level} for n in notes]
    except Exception as e:
        return {"status": "error", "message": str(e)}
    finally:
        db.close()
