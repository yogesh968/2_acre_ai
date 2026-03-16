import pytest
from datetime import datetime, timedelta
from app.services.scheduling import SchedulingEngine
from app.models.database import Doctor, Patient, Appointment, AvailabilitySlot, AppointmentStatus
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.models.database import Base

@pytest.fixture
async def db_session():
    """Create test database session"""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session() as session:
        yield session
    
    await engine.dispose()

@pytest.fixture
async def sample_doctor(db_session):
    """Create sample doctor"""
    doctor = Doctor(
        name="Dr. Test",
        specialization="General",
        is_active=True
    )
    db_session.add(doctor)
    await db_session.flush()
    return doctor

@pytest.fixture
async def sample_patient(db_session):
    """Create sample patient"""
    patient = Patient(
        name="Test Patient",
        phone="+1234567890",
        language_preference="en"
    )
    db_session.add(patient)
    await db_session.flush()
    return patient

@pytest.fixture
async def availability_slot(db_session, sample_doctor):
    """Create availability slot"""
    tomorrow = datetime.utcnow() + timedelta(days=1)
    start = tomorrow.replace(hour=9, minute=0, second=0, microsecond=0)
    end = tomorrow.replace(hour=17, minute=0, second=0, microsecond=0)
    
    slot = AvailabilitySlot(
        doctor_id=sample_doctor.id,
        start_time=start,
        end_time=end,
        is_available=True
    )
    db_session.add(slot)
    await db_session.flush()
    return slot

@pytest.mark.asyncio
async def test_check_availability_success(db_session, sample_doctor, availability_slot):
    """Test checking availability for an open slot"""
    scheduler = SchedulingEngine(db_session)
    
    tomorrow = datetime.utcnow() + timedelta(days=1)
    appointment_time = tomorrow.replace(hour=10, minute=0, second=0, microsecond=0)
    
    is_available = await scheduler.check_availability(
        sample_doctor.id,
        appointment_time,
        30
    )
    
    assert is_available is True

@pytest.mark.asyncio
async def test_check_availability_conflict(db_session, sample_doctor, sample_patient, availability_slot):
    """Test checking availability when slot is already booked"""
    scheduler = SchedulingEngine(db_session)
    
    tomorrow = datetime.utcnow() + timedelta(days=1)
    appointment_time = tomorrow.replace(hour=10, minute=0, second=0, microsecond=0)
    
    # Book first appointment
    appointment = Appointment(
        patient_id=sample_patient.id,
        doctor_id=sample_doctor.id,
        appointment_datetime=appointment_time,
        duration_minutes=30,
        status=AppointmentStatus.SCHEDULED
    )
    db_session.add(appointment)
    await db_session.flush()
    
    # Try to check same slot
    is_available = await scheduler.check_availability(
        sample_doctor.id,
        appointment_time,
        30
    )
    
    assert is_available is False

@pytest.mark.asyncio
async def test_book_appointment_success(db_session, sample_doctor, sample_patient, availability_slot):
    """Test successful appointment booking"""
    scheduler = SchedulingEngine(db_session)
    
    tomorrow = datetime.utcnow() + timedelta(days=1)
    appointment_time = tomorrow.replace(hour=10, minute=0, second=0, microsecond=0)
    
    appointment = await scheduler.book_appointment(
        patient_id=sample_patient.id,
        doctor_id=sample_doctor.id,
        appointment_datetime=appointment_time,
        duration_minutes=30,
        reason="Checkup"
    )
    
    assert appointment is not None
    assert appointment.patient_id == sample_patient.id
    assert appointment.doctor_id == sample_doctor.id
    assert appointment.status == AppointmentStatus.SCHEDULED

@pytest.mark.asyncio
async def test_book_appointment_past_time(db_session, sample_doctor, sample_patient):
    """Test booking appointment in the past fails"""
    scheduler = SchedulingEngine(db_session)
    
    past_time = datetime.utcnow() - timedelta(days=1)
    
    with pytest.raises(ValueError):
        await scheduler.book_appointment(
            patient_id=sample_patient.id,
            doctor_id=sample_doctor.id,
            appointment_datetime=past_time,
            duration_minutes=30
        )

@pytest.mark.asyncio
async def test_reschedule_appointment(db_session, sample_doctor, sample_patient, availability_slot):
    """Test rescheduling an appointment"""
    scheduler = SchedulingEngine(db_session)
    
    tomorrow = datetime.utcnow() + timedelta(days=1)
    original_time = tomorrow.replace(hour=10, minute=0, second=0, microsecond=0)
    new_time = tomorrow.replace(hour=14, minute=0, second=0, microsecond=0)
    
    # Book original appointment
    appointment = await scheduler.book_appointment(
        patient_id=sample_patient.id,
        doctor_id=sample_doctor.id,
        appointment_datetime=original_time,
        duration_minutes=30
    )
    
    # Reschedule
    rescheduled = await scheduler.reschedule_appointment(
        appointment.id,
        new_time
    )
    
    assert rescheduled is not None
    assert rescheduled.appointment_datetime == new_time

@pytest.mark.asyncio
async def test_cancel_appointment(db_session, sample_doctor, sample_patient, availability_slot):
    """Test cancelling an appointment"""
    scheduler = SchedulingEngine(db_session)
    
    tomorrow = datetime.utcnow() + timedelta(days=1)
    appointment_time = tomorrow.replace(hour=10, minute=0, second=0, microsecond=0)
    
    # Book appointment
    appointment = await scheduler.book_appointment(
        patient_id=sample_patient.id,
        doctor_id=sample_doctor.id,
        appointment_datetime=appointment_time,
        duration_minutes=30
    )
    
    # Cancel
    success = await scheduler.cancel_appointment(appointment.id)
    
    assert success is True
    
    # Verify status
    await db_session.refresh(appointment)
    assert appointment.status == AppointmentStatus.CANCELLED

@pytest.mark.asyncio
async def test_get_next_available_slots(db_session, sample_doctor, availability_slot):
    """Test getting next available slots"""
    scheduler = SchedulingEngine(db_session)
    
    tomorrow = datetime.utcnow() + timedelta(days=1)
    start_time = tomorrow.replace(hour=9, minute=0, second=0, microsecond=0)
    
    slots = await scheduler.get_next_available_slots(
        sample_doctor.id,
        start_time,
        num_slots=5
    )
    
    assert len(slots) > 0
    assert all(slot >= start_time for slot in slots)
