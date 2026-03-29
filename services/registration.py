import logging

from db.models import Student, Trainer, User
from db.repositories.student import StudentRepository
from db.repositories.trainer import TrainerRepository
from db.repositories.user import UserRepository

logger = logging.getLogger(__name__)


class RegistrationService:
    def __init__(
        self,
        users: UserRepository,
        students: StudentRepository,
        trainers: TrainerRepository,
    ) -> None:
        self._users = users
        self._students = students
        self._trainers = trainers

    def register_student(self, phone: str) -> Student:
        """Register a new student by phone (admin pre-creation, no User yet)."""
        existing = self._students.get_by_phone(phone)
        if existing:
            return existing
        student = Student(user_id=None, phone=phone)
        self._students.save(student)
        logger.info(f'Registered new student (Phone: {phone})')
        return student

    def register_trainer(self, telegram_user_id: int, name: str, description: str | None = None) -> Trainer:
        existing = self._trainers.get_by_telegram_id(telegram_user_id)
        if existing:
            return existing
        user = self._users.get_by_telegram_id(telegram_user_id)
        if user is None:
            user = User(telegram_user_id=telegram_user_id, name=name)
            self._users.save(user)
        trainer = Trainer(user_id=user.id, description=description)
        self._trainers.save(trainer)
        logger.info(f'Registered new trainer: {name} (Telegram ID: {telegram_user_id})')
        return trainer
