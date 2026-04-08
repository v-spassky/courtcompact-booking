import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from datetime import datetime, timedelta

from config.settings import now_kiev, settings
from db.models import Booking, Court, Location, Student, Trainer, User, make_session_factory
from db.repositories.booking import BookingRepository
from db.repositories.court import CourtRepository
from db.repositories.location import LocationRepository
from db.repositories.student import StudentRepository
from db.repositories.trainer import TrainerRepository
from db.repositories.user import UserRepository


def _slot(base: datetime, days: int, hour: int, minute: int) -> dict[str, datetime]:
    start = base + timedelta(days=days, hours=hour, minutes=minute)
    return {'start_time': start, 'end_time': start + timedelta(minutes=30)}


def main() -> None:
    factory = make_session_factory(settings.db_url)
    location_repo = LocationRepository(factory)
    court_repo = CourtRepository(factory)
    user_repo = UserRepository(factory)
    trainer_repo = TrainerRepository(factory)
    student_repo = StudentRepository(factory)
    booking_repo = BookingRepository(factory)

    # Locations

    loc_central = Location(
        name='Central Sports Complex',
        maps_link='https://maps.google.com/?q=Central+Sports+Complex',
    )
    loc_riverside = Location(
        name='Riverside Tennis Club',
        maps_link='https://maps.google.com/?q=Riverside+Tennis+Club',
    )
    loc_community = Location(name='Community Sports Hall', maps_link=None)

    for loc in (loc_central, loc_riverside, loc_community):
        location_repo.save(loc)
        print(f'Created location: {loc.name} (id={loc.id})')

    # Courts

    court_a = Court(name='Court A', description='Outdoor hard court, floodlit', location_id=loc_central.id)
    court_b = Court(name='Court B', description='Outdoor clay court', location_id=loc_central.id)
    court_main = Court(name='Main Court', description='Championship-size grass court', location_id=loc_riverside.id)
    court_indoor = Court(name='Indoor Court', description=None, location_id=loc_community.id)

    for court in (court_a, court_b, court_main, court_indoor):
        court_repo.save(court)
        print(f'Created court: {court.name} (id={court.id})')

    # Trainers

    user_trainer_1 = User(telegram_user_id=10001, name='Oleksiy Kovalenko')
    user_trainer_2 = User(telegram_user_id=10002, name='Maria Petrenko')
    user_trainer_3 = User(telegram_user_id=10003, name='Dmytro Savchenko')

    for user in (user_trainer_1, user_trainer_2, user_trainer_3):
        user_repo.save(user)

    trainer_1 = Trainer(user_id=user_trainer_1.id, description='10+ years experience, specialises in beginners')
    trainer_2 = Trainer(user_id=user_trainer_2.id, description='Former tournament player, advanced techniques')
    trainer_3 = Trainer(user_id=user_trainer_3.id, description='Youth coaching specialist')

    for trainer in (trainer_1, trainer_2, trainer_3):
        trainer_repo.save(trainer)
        print(f'Created trainer: {user_repo.get(trainer.user_id).name} (id={trainer.id})')  # type: ignore

    # Students — two authorized (have Telegram accounts), two not yet authorized

    user_student_1 = User(telegram_user_id=20001, name='Oksana Melnyk')
    user_student_2 = User(telegram_user_id=20002, name='Ivan Bondarenko')

    for user in (user_student_1, user_student_2):
        user_repo.save(user)

    student_1 = Student(user_id=user_student_1.id, phone='+380991234567')
    student_2 = Student(user_id=user_student_2.id, phone='+380992345678')
    student_3 = Student(user_id=None, phone='+380993456789')
    student_4 = Student(user_id=None, phone='+380994567890')

    for student in (student_1, student_2, student_3, student_4):
        student_repo.save(student)
        print(f'Created student: {student.phone} (id={student.id})')

    # Bookings

    today = now_kiev().replace(hour=0, minute=0, second=0, microsecond=0)

    bookings: list[Booking] = [
        # Day +1
        Booking(
            court_id=court_a.id,
            student_id=student_1.id,
            trainer_id=trainer_1.id,
            **_slot(base=today, days=1, hour=9, minute=0),
        ),
        Booking(
            court_id=court_a.id,
            student_id=student_2.id,
            trainer_id=None,
            **_slot(base=today, days=1, hour=10, minute=0),
        ),
        Booking(
            court_id=court_b.id,
            student_id=None,
            trainer_id=trainer_3.id,
            **_slot(base=today, days=1, hour=11, minute=0),
        ),
        # Day +2
        Booking(
            court_id=court_main.id,
            student_id=student_1.id,
            trainer_id=trainer_2.id,
            **_slot(base=today, days=2, hour=9, minute=30),
        ),
        Booking(
            court_id=court_main.id,
            student_id=student_2.id,
            trainer_id=trainer_1.id,
            **_slot(base=today, days=2, hour=14, minute=0),
        ),
        # Day +3
        Booking(
            court_id=court_a.id,
            student_id=student_2.id,
            trainer_id=None,
            **_slot(base=today, days=3, hour=10, minute=0),
        ),
        Booking(
            court_id=court_indoor.id,
            student_id=None,
            trainer_id=trainer_2.id,
            **_slot(base=today, days=3, hour=15, minute=0),
        ),
        # Day +5
        Booking(
            court_id=court_b.id,
            student_id=student_1.id,
            trainer_id=trainer_3.id,
            **_slot(base=today, days=5, hour=9, minute=0),
        ),
    ]

    for booking in bookings:
        booking_repo.save(booking)
        print(f'Created booking: court_id={booking.court_id} {booking.start_time} (id={booking.id})')

    print(f'Done. Created {len(bookings)} bookings.')


if __name__ == '__main__':
    main()
