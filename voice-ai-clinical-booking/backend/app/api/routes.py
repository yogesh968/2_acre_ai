from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.session import get_db
from app.models.database import Patient, Appointment, Doctor
from app.models.schemas import (
    PatientCreate, PatientResponse,
    AppointmentCreate, AppointmentResponse, AppointmentUpdate
)
from app.services.scheduling import SchedulingEngine
from typing import List

router = APIRouter()

# Patient endpoints
@router.post("/patients", response_model=PatientResponse)
async def create_patient(
    patient: PatientCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new patient"""
    db_patient = Patient(**patient.dict())
    db.add(db_patient)
    await db.flush()
    await db.refresh(db_patient)
    return db_patient

@router.get("/patients/{patient_id}", response_model=PatientResponse)
async def get_patient(
    patient_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get patient by ID"""
    stmt = select(Patient).where(Patient.id == patient_id)
    result = await db.execute(stmt)
    patient = result.scalar_one_or_none()
    
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    return patient

# Appointment endpoints
@router.post("/appointments", response_model=AppointmentResponse)
async def create_appointment(
    appointment: AppointmentCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new appointment"""
    scheduler = SchedulingEngine(db)
    
    db_appointment = await scheduler.book_appointment(
        patient_id=appointment.patient_id,
        doctor_id=appointment.doctor_id,
        appointment_datetime=appointment.appointment_datetime,
        duration_minutes=appointment.duration_minutes,
        reason=appointment.reason
    )
    
    if not db_appointment:
        raise HTTPException(
            status_code=400,
            detail="Unable to book appointment. Time slot may not be available."
        )
    
    await db.commit()
    await db.refresh(db_appointment)
    return db_appointment

@router.get("/appointments/{appointment_id}", response_model=AppointmentResponse)
async def get_appointment(
    appointment_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get appointment by ID"""
    stmt = select(Appointment).where(Appointment.id == appointment_id)
    result = await db.execute(stmt)
    appointment = result.scalar_one_or_none()
    
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    
    return appointment

@router.put("/appointments/{appointment_id}", response_model=AppointmentResponse)
async def update_appointment(
    appointment_id: str,
    appointment_update: AppointmentUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Update an appointment"""
    scheduler = SchedulingEngine(db)
    
    if appointment_update.appointment_datetime:
        db_appointment = await scheduler.reschedule_appointment(
            appointment_id,
            appointment_update.appointment_datetime
        )
    else:
        stmt = select(Appointment).where(Appointment.id == appointment_id)
        result = await db.execute(stmt)
        db_appointment = result.scalar_one_or_none()
        
        if db_appointment:
            if appointment_update.status:
                db_appointment.status = appointment_update.status
            if appointment_update.notes:
                db_appointment.notes = appointment_update.notes
    
    if not db_appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    
    await db.commit()
    await db.refresh(db_appointment)
    return db_appointment

@router.delete("/appointments/{appointment_id}")
async def cancel_appointment(
    appointment_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Cancel an appointment"""
    scheduler = SchedulingEngine(db)
    success = await scheduler.cancel_appointment(appointment_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Appointment not found")
    
    await db.commit()
    return {"message": "Appointment cancelled successfully"}

@router.get("/patients/{patient_id}/appointments", response_model=List[AppointmentResponse])
async def get_patient_appointments(
    patient_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get all appointments for a patient"""
    stmt = select(Appointment).where(
        Appointment.patient_id == patient_id
    ).order_by(Appointment.appointment_datetime.desc())
    
    result = await db.execute(stmt)
    appointments = result.scalars().all()
    
    return appointments

@router.get("/doctors")
async def get_doctors(db: AsyncSession = Depends(get_db)):
    """Get all active doctors"""
    stmt = select(Doctor).where(Doctor.is_active == True)
    result = await db.execute(stmt)
    doctors = result.scalars().all()
    
    return doctors

@router.get("/doctors/availability")
async def get_doctor_availability(
    doctor_id: str,
    start_date: str,
    end_date: str,
    db: AsyncSession = Depends(get_db)
):
    """Get doctor availability slots"""
    from datetime import datetime
    
    start = datetime.fromisoformat(start_date)
    end = datetime.fromisoformat(end_date)
    
    scheduler = SchedulingEngine(db)
    slots = await scheduler.get_next_available_slots(
        doctor_id,
        start,
        num_slots=10
    )
    
    return [{"start_time": slot.isoformat()} for slot in slots]
