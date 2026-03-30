from collections.abc import Generator
from contextlib import contextmanager

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload, sessionmaker

from db.models import Admin, User


class AdminRepository:
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

    def save(self, admin: Admin) -> None:
        with self._session() as session:
            merged = session.merge(admin)
            session.flush()
            admin.id = merged.id

    def get_by_telegram_id(self, telegram_user_id: int) -> Admin | None:
        with self._session() as session:
            return session.execute(
                select(Admin)
                .join(User, Admin.user_id == User.id)
                .where(User.telegram_user_id == telegram_user_id)
                .options(selectinload(Admin.user))
            ).scalar_one_or_none()

    def get_all(self) -> list[Admin]:
        with self._session() as session:
            return list(session.execute(select(Admin).options(selectinload(Admin.user))).scalars().all())

    def delete(self, admin_id: int) -> bool:
        with self._session() as session:
            row = session.get(Admin, admin_id)
            if row:
                session.delete(row)
                return True
            return False
