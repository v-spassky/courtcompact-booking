from collections.abc import Generator
from contextlib import contextmanager

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
            merged = session.merge(student)
            session.flush()
            student.id = merged.id

    def get(self, student_id: int) -> Student | None:
        with self._session() as session:
            return session.execute(
                select(Student).where(Student.id == student_id).options(selectinload(Student.user)),
            ).scalar_one_or_none()

    def get_by_telegram_id(self, telegram_user_id: int) -> Student | None:
        with self._session() as session:
            return session.execute(
                select(Student)
                .join(User, Student.user_id == User.id)
                .where(User.telegram_user_id == telegram_user_id)
                .options(selectinload(Student.user)),
            ).scalar_one_or_none()

    def get_by_phone(self, phone: str) -> Student | None:
        with self._session() as session:
            result = session.execute(
                select(Student).where(Student.phone == phone).options(selectinload(Student.user)),
            )
            return result.scalar_one_or_none()

    def get_all(self) -> list[Student]:
        with self._session() as session:
            return list(session.execute(select(Student).options(selectinload(Student.user))).scalars().all())

    def delete(self, student_id: int) -> bool:
        with self._session() as session:
            row = session.get(Student, student_id)
            if row:
                session.delete(row)
                return True
            return False
