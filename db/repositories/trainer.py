from collections.abc import Generator
from contextlib import contextmanager
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker

from db.models import Trainer


class TrainerRepository:
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

    def save(self, trainer: Trainer) -> None:
        with self._session() as session:
            session.merge(trainer)

    def get(self, trainer_id: UUID) -> Trainer | None:
        with self._session() as session:
            return session.get(Trainer, trainer_id)

    def get_by_telegram_id(self, telegram_user_id: int) -> Trainer | None:
        with self._session() as session:
            return session.execute(
                select(Trainer).where(Trainer.telegram_user_id == telegram_user_id)
            ).scalar_one_or_none()

    def get_all(self) -> list[Trainer]:
        with self._session() as session:
            return list(session.execute(select(Trainer)).scalars().all())

    def delete(self, trainer_id: UUID) -> bool:
        with self._session() as session:
            row = session.get(Trainer, trainer_id)
            if row:
                session.delete(row)
                return True
            return False
