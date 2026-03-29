import logging
from datetime import datetime
from uuid import UUID

from db.models import Booking
from db.repositories.booking import BookingRepository
from db.repositories.court import CourtRepository
from db.repositories.student import StudentRepository
from db.repositories.trainer import TrainerRepository

logger = logging.getLogger(__name__)


class BookingService:
    def __init__(
        self,
        courts: CourtRepository,
        students: StudentRepository,
        trainers: TrainerRepository,
        bookings: BookingRepository,
    ) -> None:
        self.courts = courts
        self.students = students
        self.trainers = trainers
        self.bookings = bookings

    def create_booking(
        self,
        court_id: UUID,
        start_time: datetime,
        end_time: datetime,
        student_id: UUID | None = None,
        trainer_id: UUID | None = None,
    ) -> Booking | None:
        # Validate student exists if provided
        if student_id:
            student = self.students.get(student_id)
            if not student:
                logger.warning(f'Student {student_id} not found')
                return None

        # Validate court exists
        court = self.courts.get(court_id)
        if not court:
            logger.warning(f'Court {court_id} not found')
            return None

        # Validate trainer if provided
        if trainer_id:
            trainer = self.trainers.get(trainer_id)
            if not trainer:
                logger.warning(f'Trainer {trainer_id} not found')
                return None

        # Check for conflicts
        if not self._is_time_slot_available(court_id, start_time, end_time):
            logger.warning(f'Time slot not available for court {court_id}')
            return None

        booking = Booking(
            student_id=student_id,
            court_id=court_id,
            trainer_id=trainer_id,
            start_time=start_time,
            end_time=end_time,
        )

        try:
            self.bookings.save(booking)
            saved = self.bookings.get(booking.id)
            logger.info(f'Created booking {booking.id}')
            return saved
        except Exception as e:
            logger.error(f'Failed to create booking: {e}')
            return None

    def cancel_booking(self, booking_id: UUID, user_id: int) -> bool:
        booking = self.bookings.get(booking_id)
        if not booking:
            logger.warning(f'Booking {booking_id} not found')
            return False

        # Check if user has permission to cancel
        is_authorized = False

        if booking.student and booking.student.telegram_user_id == user_id:
            is_authorized = True

        if not is_authorized and booking.trainer and booking.trainer.telegram_user_id == user_id:
            is_authorized = True

        if not is_authorized:
            logger.warning(f'User {user_id} not authorized to cancel booking {booking_id}')
            return False

        try:
            success = self.bookings.delete(booking.id)
            if success:
                logger.info(f'Deleted booking {booking_id}')
            return success
        except Exception as e:
            logger.error(f'Failed to delete booking {booking_id}: {e}')
            return False

    def _is_time_slot_available(self, court_id: UUID, start_time: datetime, end_time: datetime) -> bool:
        bookings = self.bookings.get_in_range(start_time, end_time)
        court_bookings = [b for b in bookings if b.court_id == court_id]

        for booking in court_bookings:
            if start_time < booking.end_time and end_time > booking.start_time:
                return False

        return True
