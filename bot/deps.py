from dataclasses import dataclass
from typing import cast

from telegram.ext import ContextTypes

from config.settings import Settings
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


@dataclass
class Deps:
    settings: Settings
    booking_service: BookingService
    schedule_service: ScheduleService
    registration_service: RegistrationService
    location_repo: LocationRepository
    court_repo: CourtRepository
    trainer_repo: TrainerRepository
    student_repo: StudentRepository
    booking_repo: BookingRepository
    user_repo: UserRepository
    admin_repo: AdminRepository


def get_deps(context: ContextTypes.DEFAULT_TYPE) -> Deps:
    return cast(Deps, context.bot_data['deps'])
