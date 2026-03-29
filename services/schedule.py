import logging
from dataclasses import dataclass
from datetime import datetime, timedelta

from config.settings import now_kiev
from db.models import Booking
from db.repositories.booking import BookingRepository
from db.repositories.court import CourtRepository
from db.repositories.student import StudentRepository
from db.repositories.trainer import TrainerRepository

logger = logging.getLogger(__name__)


@dataclass
class TimeSlot:
    start_time: datetime
    end_time: datetime
    court_id: str
    is_available: bool
    booking_id: str | None


class ScheduleService:
    def __init__(
        self,
        courts: CourtRepository,
        bookings: BookingRepository,
        students: StudentRepository,
        trainers: TrainerRepository,
    ) -> None:
        self.courts = courts
        self.bookings = bookings
        self.students = students
        self.trainers = trainers

    def get_available_time_slots(
        self,
        court_id: str,
        date: datetime,
        duration_minutes: int = 30,
        start_hour: int = 6,
        end_hour: int = 22,
    ) -> list[TimeSlot]:
        start_of_day = date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = start_of_day + timedelta(days=1)

        all_bookings = self.bookings.get_in_range(start_of_day, end_of_day)
        court_bookings = [b for b in all_bookings if b.court_id == court_id]

        time_slots = []
        current_time = start_of_day.replace(hour=start_hour)
        slot_duration = timedelta(minutes=duration_minutes)
        now = now_kiev()

        while current_time.hour < end_hour:
            slot_end = current_time + slot_duration

            is_past = current_time < now
            is_available = not is_past
            conflicting_booking = None

            if not is_past:
                for booking in court_bookings:
                    if current_time < booking.end_time and slot_end > booking.start_time:
                        is_available = False
                        conflicting_booking = booking
                        break

            time_slot = TimeSlot(
                start_time=current_time,
                end_time=slot_end,
                court_id=court_id,
                is_available=is_available,
                booking_id=conflicting_booking.id if conflicting_booking else None,
            )
            time_slots.append(time_slot)

            current_time += slot_duration

        return time_slots

    def get_all_time_slots_for_date(self, date: datetime) -> list[TimeSlot]:
        courts = self.courts.get_all()
        all_slots = []

        for court in courts:
            slots = self.get_available_time_slots(court.id, date)
            all_slots.extend(slots)

        return all_slots

    def get_user_bookings(self, telegram_user_id: int) -> list[Booking]:
        bookings = []
        seen_ids: set[str] = set()

        student = self.students.get_by_telegram_id(telegram_user_id)
        if student:
            for b in self.bookings.get_by_student(student.id):
                if b.id not in seen_ids:
                    bookings.append(b)
                    seen_ids.add(b.id)

        trainer = self.trainers.get_by_telegram_id(telegram_user_id)
        if trainer:
            for b in self.bookings.get_by_trainer(trainer.id):
                if b.id not in seen_ids:
                    bookings.append(b)
                    seen_ids.add(b.id)

        return bookings
