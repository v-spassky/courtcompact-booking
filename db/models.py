from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, relationship, sessionmaker


class Base(DeclarativeBase):
    pass


class Location(Base):
    __tablename__ = 'locations'

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    maps_link: Mapped[str | None] = mapped_column(Text)


class Court(Base):
    __tablename__ = 'courts'

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text)
    location_id: Mapped[str | None] = mapped_column(String(36), ForeignKey('locations.id'))
    location: Mapped['Location | None'] = relationship(lazy='raise')


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
    created_at: Mapped[datetime] = mapped_column(DateTime)
    court: Mapped['Court'] = relationship(lazy='raise')
    student: Mapped['Student | None'] = relationship(lazy='raise')
    trainer: Mapped['Trainer | None'] = relationship(lazy='raise')


def make_session_factory(db_url: str) -> sessionmaker[Session]:
    engine = create_engine(db_url)
    return sessionmaker(engine, expire_on_commit=False)
