from dataclasses import dataclass
from datetime import datetime
from enum import Enum

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, sessionmaker


class BookingStatus(str, Enum):
    PENDING = 'pending'
    CONFIRMED = 'confirmed'
    CANCELLED = 'cancelled'
    COMPLETED = 'completed'


class UserRole(str, Enum):
    STUDENT = 'student'
    TRAINER = 'trainer'
    ADMIN = 'admin'


class Base(DeclarativeBase):
    pass


class Location(Base):
    __tablename__ = 'locations'

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    google_maps_link: Mapped[str | None] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(Boolean)


class Court(Base):
    __tablename__ = 'courts'

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text)
    location_id: Mapped[str | None] = mapped_column(String(36), ForeignKey('locations.id'))
    is_active: Mapped[bool] = mapped_column(Boolean)


class Trainer(Base):
    __tablename__ = 'trainers'

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    telegram_user_id: Mapped[int] = mapped_column(Integer)
    name: Mapped[str] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text)


class Student(Base):
    __tablename__ = 'students'

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    telegram_user_id: Mapped[int | None] = mapped_column(Integer)
    name: Mapped[str] = mapped_column(String(255))
    phone: Mapped[str] = mapped_column(String(50))


class Booking(Base):
    __tablename__ = 'bookings'

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    court_id: Mapped[str] = mapped_column(String(36), ForeignKey('courts.id'))
    student_id: Mapped[str | None] = mapped_column(String(36), ForeignKey('students.id'))
    trainer_id: Mapped[str | None] = mapped_column(String(36), ForeignKey('trainers.id'))
    start_time: Mapped[datetime] = mapped_column(DateTime)
    end_time: Mapped[datetime] = mapped_column(DateTime)
    status: Mapped[str] = mapped_column(String(20))
    notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime)
    updated_at: Mapped[datetime] = mapped_column(DateTime)


@dataclass
class TimeSlot:
    start_time: datetime
    end_time: datetime
    court_id: str
    is_available: bool = True
    booking_id: str | None = None


def make_session_factory(db_url: str) -> sessionmaker[Session]:
    engine = create_engine(db_url)
    return sessionmaker(engine, expire_on_commit=False)
