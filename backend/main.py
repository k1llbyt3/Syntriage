from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from core.database import engine, get_db
from models.db_schema import Base, Patient, Appointment
from agents.coordinator import coordinator
import json

app = FastAPI(title="Smart Patient Intake & Care Coordinator")

# Add CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, replace with your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup():
    try:
        Base.metadata.create_all(bind=engine)
        print("Tables created successfully.")
    except Exception as e:
        print(f"Error creating tables: {e}")

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.get("/patients")
def get_patients(db: Session = Depends(get_db)):
    patients = db.query(Patient).all()
    result = []
    for p in patients:
        appointments = db.query(Appointment).filter(Appointment.patient_id == p.id).all()
        result.append({
            "id": p.id,
            "name": f"{p.first_name} {p.last_name}",
            "email": p.email,
            "appointments": len(appointments)
        })
    return result

@app.websocket("/ws/chat")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            try:
                payload = json.loads(data)
                user_message = payload.get("message")
            except json.JSONDecodeError:
                await websocket.send_json({"type": "error", "content": "Invalid JSON format"})
                continue
            
            if user_message:
                await websocket.send_json({"type": "status", "content": "Coordinator is thinking..."})
                try:
                    response = await coordinator.get_response(user_message)
                    await websocket.send_json({"type": "message", "content": response})
                except Exception as e:
                    await websocket.send_json({"type": "error", "content": f"AI Error: {str(e)}"})
    except WebSocketDisconnect:
        print("Client disconnected")
    except Exception as e:
        print(f"WS Critical Error: {e}")
    finally:
        try:
            await websocket.close()
        except:
            pass

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
