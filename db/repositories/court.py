from collections.abc import Generator
from contextlib import contextmanager

from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker

from db.models import Court


class CourtRepository:
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

    def save(self, court: Court) -> None:
        with self._session() as session:
            session.merge(court)

    def get(self, court_id: str) -> Court | None:
        with self._session() as session:
            return session.get(Court, court_id)

    def get_all(self) -> list[Court]:
        with self._session() as session:
            return list(session.execute(select(Court)).scalars().all())

    def get_active(self) -> list[Court]:
        with self._session() as session:
            return list(session.execute(select(Court).where(Court.is_active.is_(True))).scalars().all())

    def delete(self, court_id: str) -> bool:
        with self._session() as session:
            row = session.get(Court, court_id)
            if row:
                session.delete(row)
                return True
            return False
