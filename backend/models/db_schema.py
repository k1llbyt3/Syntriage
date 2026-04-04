from typing import List, Optional
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship

class Patient(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    first_name: str
    last_name: str
    email: str = Field(unique=True, index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    history: Optional["MedicalHistory"] = Relationship(back_populates="patient")
    appointments: List["Appointment"] = Relationship(back_populates="patient")
    # insurance: Optional["InsuranceProfile"] = Relationship(back_populates="patient") # Removing for now to fix recursive error if any

class MedicalHistory(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    patient_id: int = Field(foreign_key="patient.id")
    allergies: Optional[str] = None
    medications: Optional[str] = None
    past_surgeries: Optional[str] = None
    
    patient: Patient = Relationship(back_populates="history")

class Appointment(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    patient_id: int = Field(foreign_key="patient.id")
    appointment_time: datetime
    status: str = "Scheduled" 
    
    patient: Patient = Relationship(back_populates="appointments")
    notes: List["ClinicalNote"] = Relationship(back_populates="appointment")

class ClinicalNote(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    appointment_id: Optional[int] = Field(default=None, foreign_key="appointment.id")
    note_content: str
    urgency_level: str = "Low" 
    is_debated: bool = Field(default=False)
    debate_transcript: Optional[str] = None
    override_by: Optional[str] = None
    override_at: Optional[datetime] = None
    
    appointment: Optional[Appointment] = Relationship(back_populates="notes")

class InsuranceProfile(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    patient_id: int = Field(foreign_key="patient.id")
    provider_name: str
    member_id: str
    group_id: Optional[str] = None
    
    # patient: Patient = Relationship(back_populates="insurance")
