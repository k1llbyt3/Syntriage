from sqlmodel import Session, select
from core.database import engine
from models.db_schema import Appointment
from datetime import datetime, timedelta

def get_available_slots(date_str: str):
    """Queries the database for open appointment slots on a given date (YYYY-MM-DD)."""
    with Session(engine) as db:
        try:
            query_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            # Standard clinical hours: 09:00 to 17:00
            start_time = datetime.combine(query_date, datetime.min.time())
            end_time = datetime.combine(query_date + timedelta(days=1), datetime.min.time())
            
            statement = select(Appointment).where(
                Appointment.appointment_time >= start_time,
                Appointment.appointment_time < end_time
            )
            booked_appointments = db.exec(statement).all()
            
            booked_times = [a.appointment_time.strftime("%H:%M") for a in booked_appointments]
            available_slots = [f"{hour:02d}:00" for hour in range(9, 17) if f"{hour:02d}:00" not in booked_times]
            
            return {
                "date": date_str, 
                "available_slots": available_slots,
                "message": f"Successfully retrieved {len(available_slots)} open slots from the calendar database."
            }
        except Exception as e:
            return {"status": "error", "message": f"DATABASE_QUERY_FAIL: {str(e)}"}

def book_slot(patient_id: int, time_slot_str: str):
    """Finalizes an appointment booking in the database. time_slot_str: YYYY-MM-DD HH:MM."""
    with Session(engine) as db:
        try:
            app_time = datetime.strptime(time_slot_str, "%Y-%m-%d %H:%M")
            
            # Conflict check
            statement = select(Appointment).where(Appointment.appointment_time == app_time)
            existing = db.exec(statement).first()
            if existing:
                return {"status": "error", "message": "Conflict detected: This slot was just taken."}
                
            new_app = Appointment(patient_id=patient_id, appointment_time=app_time, status="Scheduled")
            db.add(new_app)
            db.commit()
            db.refresh(new_app)
            return {"status": "success", "appointment_id": new_app.id, "message": "Record finalized in appointment database."}
        except Exception as e:
            db.rollback()
            return {"status": "error", "message": f"DATABASE_WRITE_FAIL: {str(e)}"}
