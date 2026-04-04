from sqlmodel import Session, select
from core.database import engine
from models.db_schema import MedicalHistory

def update_allergies(patient_id: int, allergies: str):
    """Updates the allergies section of a patient's medical history."""
    with Session(engine) as db:
        try:
            statement = select(MedicalHistory).where(MedicalHistory.patient_id == patient_id)
            history = db.exec(statement).first()
            if not history:
                history = MedicalHistory(patient_id=patient_id, allergies=allergies)
                db.add(history)
            else:
                history.allergies = allergies
            db.commit()
            return {"status": "success"}
        except Exception as e:
            db.rollback()
            return {"status": "error", "message": str(e)}

def add_medication(patient_id: int, medication: str):
    """Appends a new medication to the patient's record."""
    with Session(engine) as db:
        try:
            statement = select(MedicalHistory).where(MedicalHistory.patient_id == patient_id)
            history = db.exec(statement).first()
            if not history:
                history = MedicalHistory(patient_id=patient_id, medications=medication)
                db.add(history)
            else:
                current_meds = history.medications if history.medications else ""
                history.medications = f"{current_meds}, {medication}".strip(", ")
            db.commit()
            return {"status": "success"}
        except Exception as e:
            db.rollback()
            return {"status": "error", "message": str(e)}

from models.db_schema import MedicalHistory, ClinicalNote, Appointment

def fetch_medical_history(patient_id: int):
    """Retrieves the full medical history and recent clinical encounters for a patient."""
    with Session(engine) as db:
        try:
            # 1. Base Medical History
            statement = select(MedicalHistory).where(MedicalHistory.patient_id == patient_id)
            history = db.exec(statement).first()
            
            # 2. Recent Clinical Insights (Memory)
            # Find the most recent note for this patient
            note_stmt = select(ClinicalNote).join(Appointment).where(Appointment.patient_id == patient_id).order_by(ClinicalNote.id.desc())
            recent_note = db.exec(note_stmt).first()
            
            clinical_insights = None
            if recent_note:
                clinical_insights = {
                    "last_triage_urgency": recent_note.urgency_level,
                    "summary": recent_note.content,
                    "finalized_by": recent_note.override_by if recent_note.override_by else "AI Coordinator"
                }

            if history:
                return {
                    "status": "success",
                    "allergies": history.allergies,
                    "medications": history.medications,
                    "past_surgeries": history.past_surgeries,
                    "recent_clinical_insights": clinical_insights
                }
            return {
                "status": "partial", 
                "message": "No static history, but retrieved recent insights.",
                "recent_clinical_insights": clinical_insights
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}
