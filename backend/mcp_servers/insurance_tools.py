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

def register_insurance_profile(patient_id: int, provider_name: str, member_id: str, group_id: str = None):
    """Saves or updates the insurance profile for a patient."""
    with Session(engine) as db:
        try:
            statement = select(InsuranceProfile).where(InsuranceProfile.patient_id == patient_id)
            profile = db.exec(statement).first()
            if not profile:
                profile = InsuranceProfile(
                    patient_id=patient_id,
                    provider_name=provider_name,
                    member_id=member_id,
                    group_id=group_id
                )
                db.add(profile)
            else:
                profile.provider_name = provider_name
                profile.member_id = member_id
                profile.group_id = group_id
            db.commit()
            return {"status": "success", "message": f"Insurance profile for {provider_name} successfully linked."}
        except Exception as e:
            db.rollback()
            return {"status": "error", "message": str(e)}

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
