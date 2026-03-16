import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from app.models.database import Base, Doctor, AvailabilitySlot
from app.core.config import get_settings
from datetime import datetime, timedelta

settings = get_settings()

async def init_db():
    """Initialize database with tables and sample data"""
    engine = create_async_engine(
        settings.DATABASE_URL.replace('postgresql://', 'postgresql+asyncpg://'),
        echo=True
    )
    
    async with engine.begin() as conn:
        # Create all tables
        await conn.run_sync(Base.metadata.create_all)
    
    print("Database tables created successfully")
    
    # Add sample doctors and availability
    from app.db.session import AsyncSessionLocal
    
    async with AsyncSessionLocal() as session:
        # Create sample doctors
        doctors = [
            Doctor(
                name="Dr. Sarah Johnson",
                specialization="General Physician",
                phone="+1234567890",
                email="sarah.johnson@clinic.com",
                is_active=True
            ),
            Doctor(
                name="Dr. Raj Kumar",
                specialization="Cardiologist",
                phone="+1234567891",
                email="raj.kumar@clinic.com",
                is_active=True
            ),
            Doctor(
                name="Dr. Priya Sharma",
                specialization="Pediatrician",
                phone="+1234567892",
                email="priya.sharma@clinic.com",
                is_active=True
            )
        ]
        
        for doctor in doctors:
            session.add(doctor)
        
        await session.flush()
        
        # Create availability slots for next 30 days
        for doctor in doctors:
            for day in range(30):
                date = datetime.utcnow() + timedelta(days=day)
                
                # Morning slots: 9 AM - 12 PM
                morning_start = date.replace(hour=9, minute=0, second=0, microsecond=0)
                morning_end = date.replace(hour=12, minute=0, second=0, microsecond=0)
                
                session.add(AvailabilitySlot(
                    doctor_id=doctor.id,
                    start_time=morning_start,
                    end_time=morning_end,
                    is_available=True
                ))
                
                # Afternoon slots: 2 PM - 5 PM
                afternoon_start = date.replace(hour=14, minute=0, second=0, microsecond=0)
                afternoon_end = date.replace(hour=17, minute=0, second=0, microsecond=0)
                
                session.add(AvailabilitySlot(
                    doctor_id=doctor.id,
                    start_time=afternoon_start,
                    end_time=afternoon_end,
                    is_available=True
                ))
        
        await session.commit()
        print("Sample data created successfully")

if __name__ == "__main__":
    asyncio.run(init_db())
