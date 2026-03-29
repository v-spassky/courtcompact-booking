from collections.abc import Generator
from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from bot.deps import Deps
from config.settings import Settings
from db.models import Admin, Base, Booking, Court, Location, Student, Trainer, User
from db.repositories.admin import AdminRepository
from db.repositories.booking import BookingRepository
from db.repositories.court import CourtRepository
from db.repositories.location import LocationRepository
from db.repositories.student import StudentRepository
from db.repositories.trainer import TrainerRepository
from db.repositories.user import UserRepository
from services.booking import BookingService
from services.registration import RegistrationService
from services.schedule import ScheduleService


@pytest.fixture(scope='session')
def session_factory() -> sessionmaker[Session]:
    engine = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(engine)
    return sessionmaker(engine, expire_on_commit=False)


@pytest.fixture
def db_session(session_factory: sessionmaker[Session]) -> Generator[Session, None, None]:
    session = session_factory()
    try:
        yield session
    finally:
        session.rollback()
        session.close()


@pytest.fixture
def deps(session_factory: sessionmaker[Session]) -> Deps:
    user_repo = UserRepository(session_factory)
    admin_repo = AdminRepository(session_factory)
    court_repo = CourtRepository(session_factory)
    location_repo = LocationRepository(session_factory)
    trainer_repo = TrainerRepository(session_factory)
    student_repo = StudentRepository(session_factory)
    booking_repo = BookingRepository(session_factory)
    return Deps(
        settings=MagicMock(spec=Settings),
        booking_service=BookingService(court_repo, student_repo, trainer_repo, booking_repo),
        schedule_service=ScheduleService(court_repo, booking_repo, student_repo, trainer_repo),
        registration_service=RegistrationService(user_repo, student_repo, trainer_repo),
        location_repo=location_repo,
        court_repo=court_repo,
        trainer_repo=trainer_repo,
        student_repo=student_repo,
        booking_repo=booking_repo,
        user_repo=user_repo,
        admin_repo=admin_repo,
    )


@pytest.fixture
def location(db_session: Session) -> Location:
    obj = Location(name='Test Location', maps_link=None)
    db_session.add(obj)
    db_session.flush()
    return obj


@pytest.fixture
def court(db_session: Session, location: Location) -> Court:
    obj = Court(name='Court 1', description=None, location_id=location.id)
    db_session.add(obj)
    db_session.flush()
    return obj


@pytest.fixture
def user(db_session: Session) -> User:
    obj = User(telegram_user_id=100000001, name='Test User')
    db_session.add(obj)
    db_session.flush()
    return obj


@pytest.fixture
def admin(db_session: Session, user: User) -> Admin:
    obj = Admin(user_id=user.id)
    db_session.add(obj)
    db_session.flush()
    return obj


@pytest.fixture
def trainer(db_session: Session, user: User) -> Trainer:
    obj = Trainer(user_id=user.id, description='Experienced trainer')
    db_session.add(obj)
    db_session.flush()
    return obj


@pytest.fixture
def student_user(db_session: Session) -> User:
    obj = User(telegram_user_id=100000002, name='Test Student')
    db_session.add(obj)
    db_session.flush()
    return obj


@pytest.fixture
def student(db_session: Session, student_user: User) -> Student:
    obj = Student(user_id=student_user.id, phone='+1234567890')
    db_session.add(obj)
    db_session.flush()
    return obj


@pytest.fixture
def booking(db_session: Session, court: Court, student: Student, trainer: Trainer) -> Booking:
    now = datetime.now(timezone.utc).replace(microsecond=0)
    obj = Booking(
        court_id=court.id,
        student_id=student.id,
        trainer_id=trainer.id,
        start_time=now,
        end_time=now + timedelta(hours=1),
    )
    db_session.add(obj)
    db_session.flush()
    return obj
