from sqlmodel import Session, select
from core.database import engine
from models.db_schema import Patient

def get_patient_profile(email: str):
    """Retrieves the full patient profile from the registry if they exist."""
    with Session(engine) as db:
        try:
            statement = select(Patient).where(Patient.email == email)
            patient = db.exec(statement).first()
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

def register_patient(first_name: str, last_name: str, email: str):
    """Registers a new patient into the clinical system using name and email only."""
    with Session(engine) as db:
        try:
            # Check if already exists
            statement = select(Patient).where(Patient.email == email)
            existing = db.exec(statement).first()
            if existing:
                return {"status": "Exists", "id": existing.id, "message": "Patient already registered."}
            
            new_patient = Patient(
                first_name=first_name,
                last_name=last_name,
                email=email
            )
            db.add(new_patient)
            db.commit()
            db.refresh(new_patient)
            return {"status": "success", "id": new_patient.id, "message": "New patient record created via Email-only identity."}
        except Exception as e:
            db.rollback()
            return {"status": "error", "message": str(e)}
