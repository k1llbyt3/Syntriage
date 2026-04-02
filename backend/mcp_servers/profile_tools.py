from core.database import SessionLocal
from models.db_schema import Patient

def get_patient_profile(email: str):
    """Retrieves the full patient profile from the registry if they exist."""
    db = SessionLocal()
    try:
        patient = db.query(Patient).filter(Patient.email == email).first()
        if patient:
            return {
                "status": "Found",
                "id": patient.id,
                "first_name": patient.first_name,
                "last_name": patient.last_name,
                "email": patient.email
            }
        else:
            return {"status": "New Patient", "message": "Email not found in registry."}
    except Exception as e:
        return {"status": "error", "message": str(e)}
    finally:
        db.close()
