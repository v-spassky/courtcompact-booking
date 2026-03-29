from collections.abc import Generator
from contextlib import contextmanager
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker

from db.models import User


class UserRepository:
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

    def save(self, user: User) -> None:
        with self._session() as session:
            session.merge(user)

    def get(self, user_id: UUID) -> User | None:
        with self._session() as session:
            return session.get(User, user_id)

    def get_by_telegram_id(self, telegram_user_id: int) -> User | None:
        with self._session() as session:
            return session.execute(select(User).where(User.telegram_user_id == telegram_user_id)).scalar_one_or_none()

    def get_all(self) -> list[User]:
        with self._session() as session:
            return list(session.execute(select(User)).scalars().all())

    def delete(self, user_id: UUID) -> bool:
        with self._session() as session:
            row = session.get(User, user_id)
            if row:
                session.delete(row)
                return True
            return False
