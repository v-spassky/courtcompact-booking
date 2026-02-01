from collections.abc import Generator
from contextlib import contextmanager
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker

from db.models import Booking


class BookingRepository:
    def __init__(self, factory: sessionmaker[Session]) -> None:
        self._factory = factory

    @contextmanager
    def _session(self) -> Generator[Session, None, None]:
        session = self._factory()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def save(self, booking: Booking) -> None:
        if not booking.created_at:
            booking.created_at = datetime.utcnow()
        booking.updated_at = datetime.utcnow()
        with self._session() as session:
            session.merge(booking)

    def get(self, booking_id: str) -> Booking | None:
        with self._session() as session:
            return session.get(Booking, booking_id)

    def get_by_student(self, student_id: str) -> list[Booking]:
        with self._session() as session:
            return list(session.execute(select(Booking).where(Booking.student_id == student_id)).scalars().all())

    def get_by_trainer(self, trainer_id: str) -> list[Booking]:
        with self._session() as session:
            return list(session.execute(select(Booking).where(Booking.trainer_id == trainer_id)).scalars().all())

    def get_in_range(self, start: datetime, end: datetime) -> list[Booking]:
        with self._session() as session:
            return list(
                session.execute(select(Booking).where(Booking.start_time <= end, Booking.end_time >= start))
                .scalars()
                .all()
            )

    def delete(self, booking_id: str) -> bool:
        with self._session() as session:
            row = session.get(Booking, booking_id)
            if row:
                session.delete(row)
                return True
            return False
