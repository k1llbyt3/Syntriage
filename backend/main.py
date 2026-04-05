from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import SQLModel, Session, select, delete
from core.database import engine, get_db
from core.config import settings
from models.db_schema import Patient, Appointment, ClinicalNote, MedicalHistory, InsuranceProfile
from agents.coordinator import coordinator
import json
import asyncio
import re
from datetime import datetime
from fastapi.responses import JSONResponse

app = FastAPI(title="Syntriage: Smart Patient Intake & Care Coordinator")

# Hardened CORS Middleware for Clinical Orchestration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    from sqlalchemy import text
    print("DEBUG: Synchronizing clinical database schema...")
    try:
        SQLModel.metadata.create_all(bind=engine)
    except Exception as e:
        print(f"ERROR: Failed to create tables: {e}")

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

@app.get("/")
def read_root():
    return {"message": "Syntriage API is live! Use /api/health for status."}

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
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/override-note/{note_id}")
def override_note(note_id: int, new_urgency: str, reviewer_name: str, db: Session = Depends(get_db)):
    note = db.get(ClinicalNote, note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    note.urgency_level = new_urgency
    note.override_by = reviewer_name
    note.override_at = datetime.now()
    db.add(note)
    db.commit()
    return {"status": "success"}

@app.get("/api/patients")
def get_patients(db: Session = Depends(get_db)):
    try:
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
    except Exception as e:
        return JSONResponse(status_code=500, content={"detail": str(e)})

@app.get("/api/patients/{patient_id}")
def get_patient_detail(patient_id: int, db: Session = Depends(get_db)):
    patient = db.get(Patient, patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    statement_apt = select(Appointment).where(Appointment.patient_id == patient_id)
    appointments = db.exec(statement_apt).all()
    result_appointments = []
    for a in appointments:
        statement_note = select(ClinicalNote).where(ClinicalNote.appointment_id == a.id)
        note = db.exec(statement_note).first()
        result_appointments.append({
            "id": a.id, "time": a.appointment_time, "status": a.status,
            "note": note.note_content if note else None,
            "urgency": note.urgency_level if note else None
        })
    return {"id": patient.id, "first_name": patient.first_name, "last_name": patient.last_name, "email": patient.email, "appointments": result_appointments}

@app.websocket("/ws/chat")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    EMERGENCY_KEYWORDS = r"\b(chest pain|shortness of breath|difficulty breathing|unconscious|heavy bleeding|seizure|choking|stroke|head injury)\b"
    connection_history = []
    try:
        while True:
            data = await websocket.receive_text()
            try:
                payload = json.loads(data)
                user_message = payload.get("message", "").lower()
            except json.JSONDecodeError:
                continue
            
            if user_message:
                if re.search(EMERGENCY_KEYWORDS, user_message):
                    await websocket.send_json({"type": "status", "content": "EMERGENCY BYPASS ACTIVE"})
                    await websocket.send_json({"type": "message", "content": "EMERGENCY ALERT: Please call 911 immediately."})
                    continue

                await websocket.send_json({"type": "status", "content": "Clinical Coordinator is orchestrating..."})

                # Stateless call with connection-scoped history
                response, widget, role, updated_history = await coordinator.get_response_with_widgets(user_message, history=connection_history)
                
                # 55s Retry Logic for 429
                if response == "RETRY_WAIT_55":
                    await websocket.send_json({"type": "status", "content": "Syntriage is experiencing high volume. Retrying in 55 seconds..."})
                    await asyncio.sleep(55)
                    response, widget, role, updated_history = await coordinator.get_response_with_widgets(user_message, history=connection_history)

                connection_history = updated_history
                await websocket.send_json({"type": "agent_role", "content": role})
                await websocket.send_json({"type": "message", "content": response})
                if widget:
                    await websocket.send_json({"type": "widget", "content": widget})
    except WebSocketDisconnect:
        print("Client disconnected")
    except Exception as e:
        print(f"WS Error: {e}")
    finally:
        try:
            await websocket.close()
        except:
            pass

@app.delete("/api/patients/{patient_id}")
def delete_patient(patient_id: int, db: Session = Depends(get_db)):
    try:
        patient = db.get(Patient, patient_id)
        if not patient:
            raise HTTPException(status_code=404, detail="Patient not found")
        db.exec(delete(ClinicalNote).where(ClinicalNote.appointment_id.in_(select(Appointment.id).where(Appointment.patient_id == patient_id))))
        db.exec(delete(Appointment).where(Appointment.patient_id == patient_id))
        db.exec(delete(MedicalHistory).where(MedicalHistory.patient_id == patient_id))
        db.exec(delete(InsuranceProfile).where(InsuranceProfile.patient_id == patient_id))
        db.delete(patient)
        db.commit()
        return {"status": "success"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=settings.PORT, reload=False)
