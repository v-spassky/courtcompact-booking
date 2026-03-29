from collections.abc import Generator
from contextlib import contextmanager

from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker

from db.models import Court, Location


class LocationRepository:
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

    def save(self, location: Location) -> None:
        with self._session() as session:
            session.merge(location)

    def get(self, location_id: str) -> Location | None:
        with self._session() as session:
            return session.get(Location, location_id)

    def get_all(self) -> list[Location]:
        with self._session() as session:
            return list(session.execute(select(Location)).scalars().all())

    def delete(self, location_id: str) -> bool:
        with self._session() as session:
            row = session.get(Location, location_id)
            if row:
                session.delete(row)
                return True
            return False

    def get_courts(self, location_id: str) -> list[Court]:
        with self._session() as session:
            return list(session.execute(select(Court).where(Court.location_id == location_id)).scalars().all())
