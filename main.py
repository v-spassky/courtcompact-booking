import logging

from bot.deps import Deps
from bot.setup import setup_application
from config.settings import settings
from db.models import make_session_factory
from db.repositories.admin import AdminRepository
from db.repositories.booking import BookingRepository
from db.repositories.court import CourtRepository
from db.repositories.location import LocationRepository
from db.repositories.student import StudentRepository
from db.repositories.trainer import TrainerRepository
from db.repositories.user import UserRepository
from services.booking import BookingService
from services.registration import RegistrationService
from services.schedule import ScheduleService

logger = logging.getLogger(__name__)


def build_deps() -> Deps:
    factory = make_session_factory(settings.db_url)
    location_repo = LocationRepository(factory)
    court_repo = CourtRepository(factory)
    trainer_repo = TrainerRepository(factory)
    student_repo = StudentRepository(factory)
    booking_repo = BookingRepository(factory)
    user_repo = UserRepository(factory)
    admin_repo = AdminRepository(factory)
    return Deps(
        settings=settings,
        booking_service=BookingService(court_repo, student_repo, trainer_repo, booking_repo),
        schedule_service=ScheduleService(court_repo, booking_repo, student_repo, trainer_repo),
        registration_service=RegistrationService(user_repo, student_repo, trainer_repo),
        location_repo=location_repo,
        court_repo=court_repo,
        trainer_repo=trainer_repo,
        student_repo=student_repo,
        booking_repo=booking_repo,
        user_repo=user_repo,
        admin_repo=admin_repo,
    )


def main() -> None:
    logging.basicConfig(level=settings.log_level)
    deps = build_deps()
    application = setup_application(deps)
    logger.info('Starting Tennis Booking Bot...')
    application.run_polling()


if __name__ == '__main__':
    main()
