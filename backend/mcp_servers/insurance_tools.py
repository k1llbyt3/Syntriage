from sqlmodel import Session, select
from core.database import engine
from models.db_schema import InsuranceProfile

def verify_coverage(provider_name: str, member_id: str):
    """Simulates insurance coverage verification."""
    # Mocking external API
    valid_providers = ["BlueShield", "Aetna", "UnitedHealth", "Cigna"]
    if provider_name in valid_providers:
        return {"status": "Verified", "copay": 25, "coverage_level": "Full"}
    else:
        return {"status": "Provider Not Found", "message": "Please check your provider details or pay out of pocket."}

def verify_billing_status(patient_id: int):
    """Verifies the billing and insurance status for a specific patient by ID."""
    with Session(engine) as db:
        try:
            statement = select(InsuranceProfile).where(InsuranceProfile.patient_id == patient_id)
            profile = db.exec(statement).first()
            if profile:
                return {"status": "Active", "provider": profile.provider_name, "copay": 25, "coverage_level": "Full"}
            else:
                return {"status": "No Insurance Profile Found", "message": "Patient must pay out of pocket."}
        except Exception as e:
            return {"status": "error", "message": str(e)}
