from core.database import SessionLocal
from models.db_schema import MedicalHistory

def update_allergies(patient_id: int, allergies: str):
    """Updates the allergies section of a patient's medical history."""
    db = SessionLocal()
    try:
        history = db.query(MedicalHistory).filter(MedicalHistory.patient_id == patient_id).first()
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
    finally:
        db.close()

def add_medication(patient_id: int, medication: str):
    """Appends a new medication to the patient's record."""
    db = SessionLocal()
    try:
        history = db.query(MedicalHistory).filter(MedicalHistory.patient_id == patient_id).first()
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
    finally:
        db.close()
