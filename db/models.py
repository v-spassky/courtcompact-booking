from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, relationship, sessionmaker


class Base(DeclarativeBase):
    pass


class Location(Base):
    __tablename__ = 'locations'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255))
    maps_link: Mapped[str | None] = mapped_column(Text)


class Court(Base):
    __tablename__ = 'courts'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text)
    location_id: Mapped[int | None] = mapped_column(Integer, ForeignKey('locations.id'))
    location: Mapped['Location | None'] = relationship(lazy='raise')


class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    telegram_user_id: Mapped[int] = mapped_column(Integer, unique=True)
    name: Mapped[str] = mapped_column(String(255))


class Admin(Base):
    __tablename__ = 'admins'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'))
    user: Mapped['User'] = relationship(lazy='raise')


class Trainer(Base):
    __tablename__ = 'trainers'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'))
    description: Mapped[str | None] = mapped_column(Text)
    user: Mapped['User'] = relationship(lazy='raise')


class Student(Base):
    __tablename__ = 'students'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int | None] = mapped_column(Integer, ForeignKey('users.id'))
    phone: Mapped[str] = mapped_column(String(50))
    user: Mapped['User | None'] = relationship(lazy='raise')


class Booking(Base):
    __tablename__ = 'bookings'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    court_id: Mapped[int] = mapped_column(Integer, ForeignKey('courts.id'))
    student_id: Mapped[int | None] = mapped_column(Integer, ForeignKey('students.id'))
    trainer_id: Mapped[int | None] = mapped_column(Integer, ForeignKey('trainers.id'))
    start_time: Mapped[datetime] = mapped_column(DateTime)
    end_time: Mapped[datetime] = mapped_column(DateTime)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    court: Mapped['Court'] = relationship(lazy='raise')
    student: Mapped['Student | None'] = relationship(lazy='raise')
    trainer: Mapped['Trainer | None'] = relationship(lazy='raise')


def make_session_factory(db_url: str) -> sessionmaker[Session]:
    engine = create_engine(db_url)
    return sessionmaker(engine, expire_on_commit=False)
