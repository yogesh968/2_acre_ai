from app.core.celery_app import celery_app
from datetime import datetime, timedelta
from sqlalchemy import select, and_
from app.models.database import Appointment, Patient, AppointmentStatus
from app.db.session import AsyncSessionLocal
import asyncio

@celery_app.task(name="send_appointment_reminder")
def send_appointment_reminder(appointment_id: str):
    """Send appointment reminder to patient"""
    asyncio.run(_send_reminder_async(appointment_id))

async def _send_reminder_async(appointment_id: str):
    """Async implementation of reminder sending"""
    async with AsyncSessionLocal() as db:
        stmt = select(Appointment).where(Appointment.id == appointment_id)
        result = await db.execute(stmt)
        appointment = result.scalar_one_or_none()
        
        if not appointment:
            return
        
        # Get patient
        stmt = select(Patient).where(Patient.id == appointment.patient_id)
        result = await db.execute(stmt)
        patient = result.scalar_one_or_none()
        
        if not patient:
            return
        
        # Here you would trigger an outbound call
        # For now, we'll just log it
        print(f"Reminder: {patient.name} has appointment on {appointment.appointment_datetime}")
        
        # In production, this would:
        # 1. Initiate outbound call via telephony API
        # 2. Use TTS to speak reminder message
        # 3. Listen for patient response (confirm/cancel/reschedule)
        # 4. Update appointment status accordingly

@celery_app.task(name="schedule_daily_reminders")
def schedule_daily_reminders():
    """Schedule reminders for appointments in next 24 hours"""
    asyncio.run(_schedule_reminders_async())

async def _schedule_reminders_async():
    """Async implementation of reminder scheduling"""
    async with AsyncSessionLocal() as db:
        tomorrow = datetime.utcnow() + timedelta(days=1)
        day_after = tomorrow + timedelta(days=1)
        
        stmt = select(Appointment).where(
            and_(
                Appointment.appointment_datetime >= tomorrow,
                Appointment.appointment_datetime < day_after,
                Appointment.status.in_([
                    AppointmentStatus.SCHEDULED,
                    AppointmentStatus.CONFIRMED
                ])
            )
        )
        
        result = await db.execute(stmt)
        appointments = result.scalars().all()
        
        for appointment in appointments:
            # Schedule reminder task
            send_appointment_reminder.apply_async(
                args=[appointment.id],
                eta=appointment.appointment_datetime - timedelta(hours=24)
            )

@celery_app.task(name="outbound_campaign")
def outbound_campaign(campaign_id: str, patient_ids: list):
    """Execute outbound calling campaign"""
    asyncio.run(_outbound_campaign_async(campaign_id, patient_ids))

async def _outbound_campaign_async(campaign_id: str, patient_ids: list):
    """Async implementation of outbound campaign"""
    async with AsyncSessionLocal() as db:
        for patient_id in patient_ids:
            stmt = select(Patient).where(Patient.id == patient_id)
            result = await db.execute(stmt)
            patient = result.scalar_one_or_none()
            
            if patient:
                # Initiate outbound call
                print(f"Calling patient: {patient.name} at {patient.phone}")
                
                # In production:
                # 1. Place call via telephony API
                # 2. Handle conversation with voice agent
                # 3. Log results
                # 4. Update patient records

# Periodic task configuration
celery_app.conf.beat_schedule = {
    'daily-reminders': {
        'task': 'schedule_daily_reminders',
        'schedule': timedelta(hours=24),
    },
}
