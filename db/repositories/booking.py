from collections.abc import Generator
from contextlib import contextmanager
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload, sessionmaker
from sqlalchemy.orm.interfaces import LoaderOption

from db.models import Booking, Student, Trainer


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

    def _booking_options(self) -> list[LoaderOption]:
        return [
            selectinload(Booking.court),
            selectinload(Booking.student).selectinload(Student.user),
            selectinload(Booking.trainer).selectinload(Trainer.user),
        ]

    def save(self, booking: Booking) -> None:
        with self._session() as session:
            merged = session.merge(booking)
            session.flush()
            booking.id = merged.id

    def get(self, booking_id: int) -> Booking | None:
        with self._session() as session:
            return session.execute(
                select(Booking).where(Booking.id == booking_id).options(*self._booking_options()),
            ).scalar_one_or_none()

    def get_by_student(self, student_id: int) -> list[Booking]:
        with self._session() as session:
            return list(
                session.execute(
                    select(Booking).where(Booking.student_id == student_id).options(*self._booking_options()),
                )
                .scalars()
                .all(),
            )

    def get_by_trainer(self, trainer_id: int) -> list[Booking]:
        with self._session() as session:
            return list(
                session.execute(
                    select(Booking).where(Booking.trainer_id == trainer_id).options(*self._booking_options()),
                )
                .scalars()
                .all(),
            )

    def get_in_range(self, start: datetime, end: datetime) -> list[Booking]:
        with self._session() as session:
            return list(
                session.execute(
                    select(Booking)
                    .where(Booking.start_time <= end, Booking.end_time >= start)
                    .options(*self._booking_options()),
                )
                .scalars()
                .all(),
            )

    def delete(self, booking_id: int) -> bool:
        with self._session() as session:
            row = session.get(Booking, booking_id)
            if row:
                session.delete(row)
                return True
            return False
