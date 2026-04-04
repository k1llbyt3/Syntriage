from sqlmodel import Session, select
from core.database import engine
from models.db_schema import ClinicalNote, Patient, Appointment
from datetime import datetime

def save_patient_note(appointment_id: int, note_content: str, urgency: str = "Low", is_debated: bool = False, debate_transcript: str = None):
    """Saves a clinical note for a specific appointment."""
    with Session(engine) as db:
        try:
            new_note = ClinicalNote(
                appointment_id=appointment_id,
                note_content=note_content,
                urgency_level=urgency,
                is_debated=is_debated,
                debate_transcript=debate_transcript
            )
            db.add(new_note)
            db.commit()
            db.refresh(new_note)
            return {"status": "success", "note_id": new_note.id}
        except Exception as e:
            db.rollback()
            return {"status": "error", "message": str(e)}

def get_patient_records(patient_id: int):
    """Retrieves all clinical notes for a specific patient."""
    with Session(engine) as db:
        try:
            statement = select(ClinicalNote).join(Appointment).where(Appointment.patient_id == patient_id)
            notes = db.exec(statement).all()
            return [{"appointment_id": n.appointment_id, "content": n.note_content, "urgency": n.urgency_level} for n in notes]
        except Exception as e:
            return {"status": "error", "message": str(e)}

def save_clinical_note(patient_id: int, summary: str, urgency: str = "Low", is_debated: bool = False, debate_transcript: str = None):
    """Saves a summary clinical note for a patient outside of an appointment."""
    with Session(engine) as db:
        try:
            # Finding the most recent appointment for this patient to link if possible
            statement = select(Appointment).where(Appointment.patient_id == patient_id).order_by(Appointment.appointment_time.desc())
            latest_apt = db.exec(statement).first()
            
            apt_id = latest_apt.id if latest_apt else None
            
            new_note = ClinicalNote(
                appointment_id=apt_id,
                note_content=summary,
                urgency_level=urgency,
                is_debated=is_debated,
                debate_transcript=debate_transcript
            )
            db.add(new_note)
            db.commit()
            db.refresh(new_note)
            return {"status": "success", "note_id": new_note.id}
        except Exception as e:
            db.rollback()
            return {"status": "error", "message": str(e)}
