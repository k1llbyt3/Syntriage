from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import SQLModel, Session, select
from core.database import engine, get_db
from models.db_schema import Patient, Appointment, ClinicalNote, MedicalHistory, InsuranceProfile
from agents.coordinator import coordinator
import json
from datetime import datetime

app = FastAPI(title="Syntriage: Smart Patient Intake & Care Coordinator")

# Hardened CORS Middleware for Clinical Orchestration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        settings.FRONTEND_URL,
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    from sqlalchemy import text
    from models.db_schema import ClinicalNote # Ensure model is registered
    
    print("DEBUG: Synchronizing clinical database schema...")
    SQLModel.metadata.create_all(bind=engine)
    
    # Force add missing columns if they aren't there (create_all doesn't handle migrations)
    with Session(engine) as session:
        try:
            session.execute(text("ALTER TABLE clinicalnote ADD COLUMN IF NOT EXISTS is_debated BOOLEAN DEFAULT FALSE"))
            session.execute(text("ALTER TABLE clinicalnote ADD COLUMN IF NOT EXISTS debate_transcript TEXT"))
            session.execute(text("ALTER TABLE clinicalnote ADD COLUMN IF NOT EXISTS override_by VARCHAR"))
            session.execute(text("ALTER TABLE clinicalnote ADD COLUMN IF NOT EXISTS override_at TIMESTAMP"))
            session.commit()
            print("DEBUG: Clinical schema synchronized successfully.")
        except Exception as e:
            print(f"DEBUG: Schema sync warning: {e}")
            session.rollback()
    try:
        SQLModel.metadata.create_all(bind=engine)
        print("Tables created successfully.")
    except Exception as e:
        print(f"Error creating tables: {e}")

@app.get("/api/health")
def health_check():
    return {"status": "healthy"}

@app.get("/api/debated-cases")
def get_debated_cases(db: Session = Depends(get_db)):
    try:
        statement = select(ClinicalNote).where(ClinicalNote.is_debated == True)
        debated_notes = db.exec(statement).all()
        return debated_notes
    except Exception as e:
        print(f"ERROR: Failed to retrieve debated cases: {e}")
        return [] # Return empty instead of 500

@app.post("/api/override-note/{note_id}")
def override_note(note_id: int, new_urgency: str, doctor_name: str, db: Session = Depends(get_db)):
    note = db.get(ClinicalNote, note_id)
    if not note:
        return {"error": "Note not found"}
    
    note.urgency_level = new_urgency
    note.override_by = doctor_name
    note.override_at = datetime.utcnow()
    db.add(note)
    db.commit()
    return {"status": "success", "message": f"Urgency overridden to {new_urgency}"}

@app.get("/api/patients")
def get_patients(db: Session = Depends(get_db)):
    statement = select(Patient)
    patients = db.exec(statement).all()
    result = []
    for p in patients:
        statement_apt = select(Appointment).where(Appointment.patient_id == p.id)
        appointments = db.exec(statement_apt).all()
        result.append({
            "id": p.id,
            "name": f"{p.first_name} {p.last_name}",
            "email": p.email,
            "appointments": len(appointments)
        })
    return result

@app.get("/api/patients/{patient_id}")
def get_patient_detail(patient_id: int, db: Session = Depends(get_db)):
    patient = db.get(Patient, patient_id)
    if not patient:
        return {"error": "Patient not found"}
    
    # Fetch related data
    statement_apt = select(Appointment).where(Appointment.patient_id == patient_id)
    appointments = db.exec(statement_apt).all()
    
    return {
        "id": patient.id,
        "first_name": patient.first_name,
        "last_name": patient.last_name,
        "email": patient.email,
        "created_at": patient.created_at,
        "appointments": [
            {"id": a.id, "time": a.appointment_time, "status": a.status}
            for a in appointments
        ]
    }

@app.websocket("/ws/chat")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    
    # Emergency 'Fast-Track' Keywords
    EMERGENCY_KEYWORDS = r"\b(chest pain|shortness of breath|unconscious|heavy bleeding|seizure|choking|stroke)\b"
    import re

    try:
        while True:
            data = await websocket.receive_text()
            try:
                payload = json.loads(data)
                user_message = payload.get("message", "").lower()
            except json.JSONDecodeError:
                await websocket.send_json({"type": "error", "content": "Invalid JSON format"})
                continue
            
            if user_message:
                # Rule 3: Emergency Bypass (Safety First)
                if re.search(EMERGENCY_KEYWORDS, user_message):
                    emergency_response = "EMERGENCY ALERT: High-risk symptoms detected. Please stop using this assistant and call emergency services (911/112) or go to the nearest ER immediately. Your safety is our priority."
                    await websocket.send_json({"type": "status", "content": "EMERGENCY BYPASS ACTIVE"})
                    await websocket.send_json({"type": "message", "content": emergency_response})
                    continue

                # Status Prediction Logic (Phase 6, Req 14: WebSocket Streaming)
                if any(k in user_message for k in ["symptom", "pain", "fever", "cough", "hurt", "ache", "feeling"]):
                    await websocket.send_json({"type": "status", "content": "Triage Agent is evaluating symptoms..."})
                elif any(k in user_message for k in ["history", "allergy", "previous", "record", "medicine", "pill"]):
                    await websocket.send_json({"type": "status", "content": "History Agent is reviewing records..."})
                elif any(k in user_message for k in ["book", "slot", "calendar", "appointment", "schedule"]):
                    await websocket.send_json({"type": "status", "content": "Scheduling Agent is checking calendar..."})
                elif any(k in user_message for k in ["insurance", "bill", "pay", "coverage"]):
                    await websocket.send_json({"type": "status", "content": "Insurance Specialist is verifying billing..."})
                else:
                    await websocket.send_json({"type": "status", "content": "Clinical Coordinator is orchestrating..."})

                try:
                    response, widget_data = await coordinator.get_response_with_widgets(user_message)
                    
                    # Check if the response implies a debate happened (Phase 3 reconciliation)
                    if "History Agent overrode Triage Agent" in response or (widget_data and widget_data.get("type") == "debate_event"):
                         await websocket.send_json({"type": "status", "content": "Clinical Consensus Hub is cross-referencing triage with history..."})
                         import asyncio
                         await asyncio.sleep(1.5) # Allow the user to see the debate status

                    # Handle Tool-based dynamic status if widget_data is a status_update
                    if widget_data and widget_data.get("type") == "status_update":
                        status_msg = f"MCP Server: {widget_data['content']}"
                        await websocket.send_json({"type": "status", "content": status_msg})
                        
                    await websocket.send_json({"type": "message", "content": response})
                    if widget_data and widget_data.get("type") != "status_update":
                        await websocket.send_json({"type": "widget", "content": widget_data})
                except Exception as e:
                    await websocket.send_json({"type": "error", "content": f"Orchestration Error: {str(e)}"})
    except WebSocketDisconnect:
        print("Client disconnected")
    except Exception as e:
        print(f"WS Critical Error: {e}")
    finally:
        try:
            await websocket.close()
        except:
            pass

from sqlmodel import select, delete

@app.delete("/api/patients/{patient_id}")
def delete_patient(patient_id: int, db: Session = Depends(get_db)):
    try:
        patient = db.get(Patient, patient_id)
        if not patient:
            raise HTTPException(status_code=404, detail="Patient not found")
        
        # Optimized Manual Cascade
        # 1. Delete Clinical Notes through Appointments
        appointments = db.exec(select(Appointment).where(Appointment.patient_id == patient_id)).all()
        for apt in appointments:
            db.exec(delete(ClinicalNote).where(ClinicalNote.appointment_id == apt.id))
            
        # 2. Delete Appointments
        db.exec(delete(Appointment).where(Appointment.patient_id == patient_id))
            
        # 3. Delete Medical History
        db.exec(delete(MedicalHistory).where(MedicalHistory.patient_id == patient_id))
            
        # 4. Delete Insurance
        db.exec(delete(InsuranceProfile).where(InsuranceProfile.patient_id == patient_id))
            
        # 5. Finally Delete Patient
        db.delete(patient)
        db.commit()
        return {"status": "success", "message": f"Patient {patient_id} and all related records deleted."}
    except Exception as e:
        db.rollback()
        print(f"ERROR: {e}")
        raise HTTPException(status_code=500, detail=f"Database error during deletion: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
