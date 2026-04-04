from sqlmodel import Session, select
from core.database import engine
from models.db_schema import Appointment
from datetime import datetime, timedelta

def get_available_slots(date_str: str, preferred_time: str = None, time_window: str = None):
    """
    Queries the database for open appointment slots on a given date (YYYY-MM-DD).
    - preferred_time: Optional HH:MM filter.
    - time_window: Optional "morning" (09-12) or "afternoon" (13-17) filter.
    """
    with Session(engine) as db:
        try:
            query_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            start_time = datetime.combine(query_date, datetime.min.time())
            end_time = datetime.combine(query_date + timedelta(days=1), datetime.min.time())
            
            statement = select(Appointment).where(
                Appointment.appointment_time >= start_time,
                Appointment.appointment_time < end_time
            )
            booked_appointments = db.exec(statement).all()
            booked_times = [a.appointment_time.strftime("%H:%M") for a in booked_appointments]
            
            # Filter hour range based on window
            hour_range = range(9, 17)
            if time_window == "morning":
                hour_range = range(9, 13)
            elif time_window == "afternoon":
                hour_range = range(13, 17)
            
            available_slots = [f"{hour:02d}:00" for hour in hour_range if f"{hour:02d}:00" not in booked_times]
            
            # If a specific time was requested, prioritize it
            if preferred_time and preferred_time in available_slots:
                available_slots = [preferred_time]
            elif preferred_time:
                # If preferred is taken, show a few around it instead of all
                pref_hour = int(preferred_time.split(":")[0])
                available_slots = [s for s in available_slots if abs(int(s.split(":")[0]) - pref_hour) <= 2]

            return {
                "date": date_str, 
                "available_slots": available_slots,
                "message": f"Retrieved {len(available_slots)} relevant slots."
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
