from collections.abc import Generator
from contextlib import contextmanager
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload, sessionmaker

from db.models import Student, User


class StudentRepository:
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

    def save(self, student: Student) -> None:
        with self._session() as session:
            session.merge(student)

    def get(self, student_id: UUID) -> Student | None:
        with self._session() as session:
            return session.execute(
                select(Student).where(Student.id == student_id).options(selectinload(Student.user))
            ).scalar_one_or_none()

    def get_by_telegram_id(self, telegram_user_id: int) -> Student | None:
        with self._session() as session:
            return session.execute(
                select(Student)
                .join(User, Student.user_id == User.id)
                .where(User.telegram_user_id == telegram_user_id)
                .options(selectinload(Student.user))
            ).scalar_one_or_none()

    def get_by_phone(self, phone: str) -> Student | None:
        normalized = ''.join(c for c in phone if c.isdigit() or c == '+')
        with self._session() as session:
            rows = session.execute(select(Student).options(selectinload(Student.user))).scalars().all()
            for row in rows:
                row_phone = ''.join(c for c in (row.phone or '') if c.isdigit() or c == '+')
                if row_phone == normalized:
                    return row
        return None

    def get_all(self) -> list[Student]:
        with self._session() as session:
            return list(session.execute(select(Student).options(selectinload(Student.user))).scalars().all())

    def delete(self, student_id: UUID) -> bool:
        with self._session() as session:
            row = session.get(Student, student_id)
            if row:
                session.delete(row)
                return True
            return False
