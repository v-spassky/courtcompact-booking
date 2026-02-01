import logging
from uuid import uuid4

from db.models import Student, Trainer
from db.repositories.student import StudentRepository
from db.repositories.trainer import TrainerRepository

logger = logging.getLogger(__name__)


class RegistrationService:
    def __init__(self, students: StudentRepository, trainers: TrainerRepository) -> None:
        self.students = students
        self.trainers = trainers

    def register_student(self, name: str, phone: str, telegram_user_id: int | None = None) -> Student:
        """Register a new student. Phone is required, telegram_user_id is set when student authorizes."""
        existing = self.students.get_by_phone(phone)
        if existing:
            return existing

        student = Student(
            id=str(uuid4()),
            telegram_user_id=telegram_user_id,
            name=name,
            phone=phone,
        )
        self.students.save(student)
        logger.info(f'Registered new student: {name} (Phone: {phone})')
        return student

    def register_trainer(self, telegram_user_id: int, name: str, description: str | None = None) -> Trainer:
        existing = self.trainers.get_by_telegram_id(telegram_user_id)
        if existing:
            return existing

        trainer = Trainer(
            id=str(uuid4()),
            telegram_user_id=telegram_user_id,
            name=name,
            description=description,
        )
        self.trainers.save(trainer)
        logger.info(f'Registered new trainer: {name} (Telegram ID: {telegram_user_id})')
        return trainer
