from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from app.models.database import Appointment, Doctor, AvailabilitySlot, AppointmentStatus
from typing import List, Optional
import asyncio

class SchedulingEngine:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def check_availability(
        self,
        doctor_id: str,
        appointment_datetime: datetime,
        duration_minutes: int = 30
    ) -> bool:
        """Check if doctor is available at given time"""
        end_time = appointment_datetime + timedelta(minutes=duration_minutes)
        
        # Check for conflicting appointments
        stmt = select(Appointment).where(
            and_(
                Appointment.doctor_id == doctor_id,
                Appointment.status.in_([AppointmentStatus.SCHEDULED, AppointmentStatus.CONFIRMED]),
                Appointment.appointment_datetime < end_time,
                Appointment.appointment_datetime + timedelta(minutes=Appointment.duration_minutes) > appointment_datetime
            )
        )
        result = await self.db.execute(stmt)
        conflicts = result.scalars().all()
        
        if conflicts:
            return False
        
        # Check availability slots
        stmt = select(AvailabilitySlot).where(
            and_(
                AvailabilitySlot.doctor_id == doctor_id,
                AvailabilitySlot.start_time <= appointment_datetime,
                AvailabilitySlot.end_time >= end_time,
                AvailabilitySlot.is_available == True
            )
        )
        result = await self.db.execute(stmt)
        slot = result.scalar_one_or_none()
        
        return slot is not None
    
    async def get_next_available_slots(
        self,
        doctor_id: str,
        start_date: datetime,
        num_slots: int = 5,
        duration_minutes: int = 30
    ) -> List[datetime]:
        """Get next available time slots for a doctor"""
        available_slots = []
        current_date = start_date
        max_days = 30
        
        for _ in range(max_days):
            # Get availability slots for the day
            day_start = current_date.replace(hour=0, minute=0, second=0)
            day_end = current_date.replace(hour=23, minute=59, second=59)
            
            stmt = select(AvailabilitySlot).where(
                and_(
                    AvailabilitySlot.doctor_id == doctor_id,
                    AvailabilitySlot.start_time >= day_start,
                    AvailabilitySlot.end_time <= day_end,
                    AvailabilitySlot.is_available == True
                )
            )
            result = await self.db.execute(stmt)
            slots = result.scalars().all()
            
            for slot in slots:
                # Check every 30-minute interval
                current_time = slot.start_time
                while current_time + timedelta(minutes=duration_minutes) <= slot.end_time:
                    if await self.check_availability(doctor_id, current_time, duration_minutes):
                        available_slots.append(current_time)
                        if len(available_slots) >= num_slots:
                            return available_slots
                    current_time += timedelta(minutes=duration_minutes)
            
            current_date += timedelta(days=1)
        
        return available_slots
    
    async def book_appointment(
        self,
        patient_id: str,
        doctor_id: str,
        appointment_datetime: datetime,
        duration_minutes: int = 30,
        reason: Optional[str] = None
    ) -> Optional[Appointment]:
        """Book an appointment with optimistic locking"""
        # Validate not in past
        if appointment_datetime < datetime.utcnow():
            raise ValueError("Cannot book appointment in the past")
        
        # Check availability
        if not await self.check_availability(doctor_id, appointment_datetime, duration_minutes):
            return None
        
        # Create appointment
        appointment = Appointment(
            patient_id=patient_id,
            doctor_id=doctor_id,
            appointment_datetime=appointment_datetime,
            duration_minutes=duration_minutes,
            reason=reason,
            status=AppointmentStatus.SCHEDULED
        )
        
        self.db.add(appointment)
        
        try:
            await self.db.flush()
            return appointment
        except Exception:
            await self.db.rollback()
            return None
    
    async def reschedule_appointment(
        self,
        appointment_id: str,
        new_datetime: datetime
    ) -> Optional[Appointment]:
        """Reschedule an existing appointment"""
        stmt = select(Appointment).where(Appointment.id == appointment_id)
        result = await self.db.execute(stmt)
        appointment = result.scalar_one_or_none()
        
        if not appointment:
            return None
        
        if not await self.check_availability(
            appointment.doctor_id,
            new_datetime,
            appointment.duration_minutes
        ):
            return None
        
        appointment.appointment_datetime = new_datetime
        appointment.updated_at = datetime.utcnow()
        
        await self.db.flush()
        return appointment
    
    async def cancel_appointment(self, appointment_id: str) -> bool:
        """Cancel an appointment"""
        stmt = select(Appointment).where(Appointment.id == appointment_id)
        result = await self.db.execute(stmt)
        appointment = result.scalar_one_or_none()
        
        if not appointment:
            return False
        
        appointment.status = AppointmentStatus.CANCELLED
        appointment.updated_at = datetime.utcnow()
        
        await self.db.flush()
        return True
