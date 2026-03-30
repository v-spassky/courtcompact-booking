from collections.abc import Generator
from contextlib import contextmanager

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload, sessionmaker

from db.models import Trainer, User


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
            merged = session.merge(trainer)
            session.flush()
            trainer.id = merged.id

    def get(self, trainer_id: int) -> Trainer | None:
        with self._session() as session:
            return session.execute(
                select(Trainer).where(Trainer.id == trainer_id).options(selectinload(Trainer.user))
            ).scalar_one_or_none()

    def get_by_telegram_id(self, telegram_user_id: int) -> Trainer | None:
        with self._session() as session:
            return session.execute(
                select(Trainer)
                .join(User, Trainer.user_id == User.id)
                .where(User.telegram_user_id == telegram_user_id)
                .options(selectinload(Trainer.user))
            ).scalar_one_or_none()

    def get_all(self) -> list[Trainer]:
        with self._session() as session:
            return list(session.execute(select(Trainer).options(selectinload(Trainer.user))).scalars().all())

    def delete(self, trainer_id: int) -> bool:
        with self._session() as session:
            row = session.get(Trainer, trainer_id)
            if row:
                session.delete(row)
                return True
            return False
