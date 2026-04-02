from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Patient(Base):
    __tablename__ = 'patients'
    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(50))
    last_name = Column(String(50))
    email = Column(String(100), unique=True, index=True)
    phone = Column(String(20))
    created_at = Column(DateTime, default=datetime.utcnow)

    history = relationship("MedicalHistory", back_populates="patient", uselist=False)
    appointments = relationship("Appointment", back_populates="patient")
    insurance = relationship("InsuranceProfile", back_populates="patient", uselist=False)

class MedicalHistory(Base):
    __tablename__ = 'medical_histories'
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey('patients.id'))
    allergies = Column(Text)
    medications = Column(Text)
    past_surgeries = Column(Text)
    
    patient = relationship("Patient", back_populates="history")

class Appointment(Base):
    __tablename__ = 'appointments'
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey('patients.id'))
    appointment_time = Column(DateTime)
    status = Column(String(20)) # e.g., Scheduled, Completed, Cancelled
    
    patient = relationship("Patient", back_populates="appointments")
    notes = relationship("VisitNote", back_populates="appointment")

class VisitNote(Base):
    __tablename__ = 'visit_notes'
    id = Column(Integer, primary_key=True, index=True)
    appointment_id = Column(Integer, ForeignKey('appointments.id'))
    note_content = Column(Text)
    urgency_level = Column(String(20)) # Low, Med, High, ER
    
    appointment = relationship("Appointment", back_populates="notes")

class InsuranceProfile(Base):
    __tablename__ = 'insurance_profiles'
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey('patients.id'))
    provider_name = Column(String(100))
    member_id = Column(String(50))
    group_id = Column(String(50))
    
    patient = relationship("Patient", back_populates="insurance")
