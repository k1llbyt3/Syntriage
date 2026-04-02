import asyncio
import json
from agents.coordinator import coordinator
from core.database import SessionLocal
from models.db_schema import Patient, Appointment, VisitNote

async def simulate_patient_flow():
    print("--- Simulating Patient Intake Flow ---")
    
    # 1. Triage Simulation
    print("\n[Step 1] Triage: Patient says 'I have a severe headache and high fever'")
    response = await coordinator.get_response("I have a severe headache and high fever. My name is John Doe and email is john@example.com.")
    print(f"Coordinator: {response}")

    # 2. Check Database for Patient (Mocking auto-save logic if added)
    db = SessionLocal()
    try:
        # Manually create a patient to simulate the system knowing who it is
        test_patient = db.query(Patient).filter(Patient.email == "john@example.com").first()
        if not test_patient:
            test_patient = Patient(first_name="John", last_name="Doe", email="john@example.com")
            db.add(test_patient)
            db.commit()
            db.refresh(test_patient)
            print(f"\n[DB] Created test patient: {test_patient.id}")

        # 3. Test Tool Calling (e.g. Triage or Note)
        print("\n[Step 2] Testing Tool calling through prompt...")
        response2 = await coordinator.get_response("Please save a note that the patient has a possible migraine.")
        print(f"Coordinator: {response2}")
        
        # 4. Verify Note exists in DB
        note = db.query(VisitNote).first()
        if note:
            print(f"\n[DB SUCCESS] Note saved: {note.note_content}")
        else:
            print("\n[DB ERROR] Note was not saved.")

    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(simulate_patient_flow())
