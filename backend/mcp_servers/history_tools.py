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

def fetch_medical_history(patient_id: int):
    """Retrieves the full medical history (allergies, medications, surgeries) for a patient."""
    with Session(engine) as db:
        try:
            statement = select(MedicalHistory).where(MedicalHistory.patient_id == patient_id)
            history = db.exec(statement).first()
            if history:
                return {
                    "status": "success",
                    "allergies": history.allergies,
                    "medications": history.medications,
                    "past_surgeries": history.past_surgeries
                }
            return {"status": "not_found", "message": "No medical history on file."}
        except Exception as e:
            return {"status": "error", "message": str(e)}
