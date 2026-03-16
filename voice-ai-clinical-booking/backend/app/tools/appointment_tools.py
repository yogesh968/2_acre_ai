from datetime import datetime
from typing import List, Dict, Any
from app.services.scheduling import SchedulingEngine
from sqlalchemy.ext.asyncio import AsyncSession

class AppointmentTools:
    def __init__(self, db: AsyncSession, patient_id: str):
        self.db = db
        self.patient_id = patient_id
        self.scheduler = SchedulingEngine(db)
    
    async def check_doctor_availability(
        self,
        doctor_id: str,
        date: str,
        time: str
    ) -> Dict[str, Any]:
        """
        Check if a doctor is available at a specific date and time.
        
        Args:
            doctor_id: The ID of the doctor
            date: Date in YYYY-MM-DD format
            time: Time in HH:MM format
        
        Returns:
            Dictionary with availability status and next available slots if not available
        """
        try:
            appointment_datetime = datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M")
            
            is_available = await self.scheduler.check_availability(doctor_id, appointment_datetime)
            
            if is_available:
                return {
                    "available": True,
                    "message": f"Doctor is available on {date} at {time}"
                }
            else:
                next_slots = await self.scheduler.get_next_available_slots(
                    doctor_id,
                    appointment_datetime,
                    num_slots=3
                )
                return {
                    "available": False,
                    "message": f"Doctor is not available on {date} at {time}",
                    "next_available_slots": [slot.strftime("%Y-%m-%d %H:%M") for slot in next_slots]
                }
        except Exception as e:
            return {"error": str(e)}
    
    async def book_appointment(
        self,
        doctor_id: str,
        date: str,
        time: str,
        reason: str = None
    ) -> Dict[str, Any]:
        """
        Book an appointment with a doctor.
        
        Args:
            doctor_id: The ID of the doctor
            date: Date in YYYY-MM-DD format
            time: Time in HH:MM format
            reason: Reason for appointment (optional)
        
        Returns:
            Dictionary with booking confirmation or error
        """
        try:
            appointment_datetime = datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M")
            
            appointment = await self.scheduler.book_appointment(
                patient_id=self.patient_id,
                doctor_id=doctor_id,
                appointment_datetime=appointment_datetime,
                reason=reason
            )
            
            if appointment:
                return {
                    "success": True,
                    "appointment_id": appointment.id,
                    "message": f"Appointment booked successfully for {date} at {time}",
                    "details": {
                        "date": date,
                        "time": time,
                        "doctor_id": doctor_id
                    }
                }
            else:
                return {
                    "success": False,
                    "message": "Unable to book appointment. Time slot may no longer be available."
                }
        except ValueError as e:
            return {"success": False, "error": str(e)}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def reschedule_appointment(
        self,
        appointment_id: str,
        new_date: str,
        new_time: str
    ) -> Dict[str, Any]:
        """
        Reschedule an existing appointment.
        
        Args:
            appointment_id: The ID of the appointment to reschedule
            new_date: New date in YYYY-MM-DD format
            new_time: New time in HH:MM format
        
        Returns:
            Dictionary with reschedule confirmation or error
        """
        try:
            new_datetime = datetime.strptime(f"{new_date} {new_time}", "%Y-%m-%d %H:%M")
            
            appointment = await self.scheduler.reschedule_appointment(
                appointment_id,
                new_datetime
            )
            
            if appointment:
                return {
                    "success": True,
                    "message": f"Appointment rescheduled to {new_date} at {new_time}",
                    "appointment_id": appointment.id
                }
            else:
                return {
                    "success": False,
                    "message": "Unable to reschedule. New time slot may not be available."
                }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def cancel_appointment(self, appointment_id: str) -> Dict[str, Any]:
        """
        Cancel an existing appointment.
        
        Args:
            appointment_id: The ID of the appointment to cancel
        
        Returns:
            Dictionary with cancellation confirmation
        """
        try:
            success = await self.scheduler.cancel_appointment(appointment_id)
            
            if success:
                return {
                    "success": True,
                    "message": "Appointment cancelled successfully"
                }
            else:
                return {
                    "success": False,
                    "message": "Appointment not found or already cancelled"
                }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def get_patient_history(self) -> Dict[str, Any]:
        """
        Get patient's appointment history.
        
        Returns:
            Dictionary with list of past and upcoming appointments
        """
        try:
            from sqlalchemy import select
            from app.models.database import Appointment
            
            stmt = select(Appointment).where(
                Appointment.patient_id == self.patient_id
            ).order_by(Appointment.appointment_datetime.desc())
            
            result = await self.db.execute(stmt)
            appointments = result.scalars().all()
            
            return {
                "success": True,
                "appointments": [
                    {
                        "id": apt.id,
                        "doctor_id": apt.doctor_id,
                        "datetime": apt.appointment_datetime.strftime("%Y-%m-%d %H:%M"),
                        "status": apt.status.value,
                        "reason": apt.reason
                    }
                    for apt in appointments
                ]
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
