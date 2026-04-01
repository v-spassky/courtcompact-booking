from typing import Self

from pydantic import BaseModel


class AdminEditLocationArg(BaseModel):
    id: int

    @classmethod
    def from_callback_data(cls, data: str) -> Self:
        return cls(id=int(data.removeprefix('admin_edit_location_')))

    def to_callback_data(self) -> str:
        return f'admin_edit_location_{self.id}'


class AdminDeleteLocationArg(BaseModel):
    id: int

    @classmethod
    def from_callback_data(cls, data: str) -> Self:
        return cls(id=int(data.removeprefix('admin_delete_location_')))

    def to_callback_data(self) -> str:
        return f'admin_delete_location_{self.id}'


class AdminConfirmDeleteLocationArg(BaseModel):
    id: int

    @classmethod
    def from_callback_data(cls, data: str) -> Self:
        return cls(id=int(data.removeprefix('admin_confirm_delete_location_')))

    def to_callback_data(self) -> str:
        return f'admin_confirm_delete_location_{self.id}'


class AdminCourtLocationArg(BaseModel):
    id: int

    @classmethod
    def from_callback_data(cls, data: str) -> Self:
        return cls(id=int(data.removeprefix('admin_court_location_')))

    def to_callback_data(self) -> str:
        return f'admin_court_location_{self.id}'


class AdminEditCourtArg(BaseModel):
    id: int

    @classmethod
    def from_callback_data(cls, data: str) -> Self:
        return cls(id=int(data.removeprefix('admin_edit_court_')))

    def to_callback_data(self) -> str:
        return f'admin_edit_court_{self.id}'


class AdminDeleteCourtArg(BaseModel):
    id: int

    @classmethod
    def from_callback_data(cls, data: str) -> Self:
        return cls(id=int(data.removeprefix('admin_delete_court_')))

    def to_callback_data(self) -> str:
        return f'admin_delete_court_{self.id}'


class AdminConfirmDeleteCourtArg(BaseModel):
    id: int

    @classmethod
    def from_callback_data(cls, data: str) -> Self:
        return cls(id=int(data.removeprefix('admin_confirm_delete_court_')))

    def to_callback_data(self) -> str:
        return f'admin_confirm_delete_court_{self.id}'


class AdminEditTrainerArg(BaseModel):
    id: int

    @classmethod
    def from_callback_data(cls, data: str) -> Self:
        return cls(id=int(data.removeprefix('admin_edit_trainer_')))

    def to_callback_data(self) -> str:
        return f'admin_edit_trainer_{self.id}'


class AdminDeleteTrainerArg(BaseModel):
    id: int

    @classmethod
    def from_callback_data(cls, data: str) -> Self:
        return cls(id=int(data.removeprefix('admin_delete_trainer_')))

    def to_callback_data(self) -> str:
        return f'admin_delete_trainer_{self.id}'


class AdminConfirmDeleteTrainerArg(BaseModel):
    id: int

    @classmethod
    def from_callback_data(cls, data: str) -> Self:
        return cls(id=int(data.removeprefix('admin_confirm_delete_trainer_')))

    def to_callback_data(self) -> str:
        return f'admin_confirm_delete_trainer_{self.id}'


class AdminEditStudentArg(BaseModel):
    id: int

    @classmethod
    def from_callback_data(cls, data: str) -> Self:
        return cls(id=int(data.removeprefix('admin_edit_student_')))

    def to_callback_data(self) -> str:
        return f'admin_edit_student_{self.id}'


class AdminDeleteStudentArg(BaseModel):
    id: int

    @classmethod
    def from_callback_data(cls, data: str) -> Self:
        return cls(id=int(data.removeprefix('admin_delete_student_')))

    def to_callback_data(self) -> str:
        return f'admin_delete_student_{self.id}'


class AdminConfirmDeleteStudentArg(BaseModel):
    id: int

    @classmethod
    def from_callback_data(cls, data: str) -> Self:
        return cls(id=int(data.removeprefix('admin_confirm_delete_student_')))

    def to_callback_data(self) -> str:
        return f'admin_confirm_delete_student_{self.id}'


class CalendarNavArg(BaseModel):
    year: int
    month: int

    @classmethod
    def from_callback_data(cls, data: str) -> Self:
        parts = data.split('_')
        return cls(year=int(parts[1]), month=int(parts[2]))

    def to_callback_data(self) -> str:
        return f'cal_{self.year}_{self.month}'


class ScheduleDateArg(BaseModel):
    year: int
    month: int
    day: int

    @classmethod
    def from_callback_data(cls, data: str) -> Self:
        parts = data.split('_')
        return cls(year=int(parts[1]), month=int(parts[2]), day=int(parts[3]))

    def to_callback_data(self) -> str:
        return f'date_{self.year}_{self.month}_{self.day}'


class ScheduleLocationArg(BaseModel):
    location_id: int
    year: int
    month: int
    day: int

    @classmethod
    def from_callback_data(cls, data: str) -> Self:
        parts = data.split('_')
        return cls(location_id=int(parts[2]), year=int(parts[3]), month=int(parts[4]), day=int(parts[5]))

    def to_callback_data(self) -> str:
        return f'schedule_location_{self.location_id}_{self.year}_{self.month}_{self.day}'


class CourtDayArg(BaseModel):
    court_id: int
    year: int
    month: int
    day: int

    @classmethod
    def from_callback_data(cls, data: str) -> Self:
        parts = data.split('_')
        return cls(court_id=int(parts[2]), year=int(parts[3]), month=int(parts[4]), day=int(parts[5]))

    def to_callback_data(self) -> str:
        return f'court_day_{self.court_id}_{self.year}_{self.month}_{self.day}'


class CourtWeekArg(BaseModel):
    court_id: int
    year: int
    month: int
    day: int

    @classmethod
    def from_callback_data(cls, data: str) -> Self:
        parts = data.split('_')
        return cls(court_id=int(parts[2]), year=int(parts[3]), month=int(parts[4]), day=int(parts[5]))

    def to_callback_data(self) -> str:
        return f'court_week_{self.court_id}_{self.year}_{self.month}_{self.day}'


class WeeklyLocationArg(BaseModel):
    location_id: int
    year: int
    month: int
    day: int

    @classmethod
    def from_callback_data(cls, data: str) -> Self:
        parts = data.split('_')
        return cls(location_id=int(parts[2]), year=int(parts[3]), month=int(parts[4]), day=int(parts[5]))

    def to_callback_data(self) -> str:
        return f'weekly_location_{self.location_id}_{self.year}_{self.month}_{self.day}'


class ViewTrainerArg(BaseModel):
    trainer_id: int

    @classmethod
    def from_callback_data(cls, data: str) -> Self:
        return cls(trainer_id=int(data.split('_')[2]))

    def to_callback_data(self) -> str:
        return f'view_trainer_{self.trainer_id}'


class BookLocationArg(BaseModel):
    location_id: int

    @classmethod
    def from_callback_data(cls, data: str) -> Self:
        return cls(location_id=int(data.removeprefix('book_location_')))

    def to_callback_data(self) -> str:
        return f'book_location_{self.location_id}'


class SelectCourtArg(BaseModel):
    court_id: int

    @classmethod
    def from_callback_data(cls, data: str) -> Self:
        return cls(court_id=int(data.split('_')[2]))

    def to_callback_data(self) -> str:
        return f'select_court_{self.court_id}'


class SelectTrainerArg(BaseModel):
    trainer_id: int | None
    court_id: int

    @classmethod
    def from_callback_data(cls, data: str) -> Self:
        parts = data.split('_')
        trainer_id_str = parts[2]
        return cls(
            trainer_id=int(trainer_id_str) if trainer_id_str != 'none' else None,
            court_id=int(parts[3]),
        )

    def to_callback_data(self) -> str:
        trainer_str = str(self.trainer_id) if self.trainer_id is not None else 'none'
        return f'select_trainer_{trainer_str}_{self.court_id}'


class BookCalArg(BaseModel):
    court_id: int
    trainer_id: int | None
    year: int
    month: int

    @classmethod
    def from_callback_data(cls, data: str) -> Self:
        parts = data.split('_')
        trainer_id_str = parts[3]
        return cls(
            court_id=int(parts[2]),
            trainer_id=int(trainer_id_str) if trainer_id_str != 'none' else None,
            year=int(parts[4]),
            month=int(parts[5]),
        )

    def to_callback_data(self) -> str:
        trainer_str = str(self.trainer_id) if self.trainer_id is not None else 'none'
        return f'book_cal_{self.court_id}_{trainer_str}_{self.year}_{self.month}'


class BookDateArg(BaseModel):
    court_id: int
    trainer_id: int | None
    year: int
    month: int
    day: int

    @classmethod
    def from_callback_data(cls, data: str) -> Self:
        parts = data.split('_')
        trainer_id_str = parts[3]
        return cls(
            court_id=int(parts[2]),
            trainer_id=int(trainer_id_str) if trainer_id_str != 'none' else None,
            year=int(parts[4]),
            month=int(parts[5]),
            day=int(parts[6]),
        )

    def to_callback_data(self) -> str:
        trainer_str = str(self.trainer_id) if self.trainer_id is not None else 'none'
        return f'book_date_{self.court_id}_{trainer_str}_{self.year}_{self.month}_{self.day}'


class BookSlotArg(BaseModel):
    court_id: int
    trainer_id: int | None
    year: int
    month: int
    day: int
    hour: int
    minute: int

    @classmethod
    def from_callback_data(cls, data: str) -> Self:
        parts = data.split('_')
        trainer_id_str = parts[3]
        date_str = parts[4]
        time_code = parts[5]
        return cls(
            court_id=int(parts[2]),
            trainer_id=int(trainer_id_str) if trainer_id_str != 'none' else None,
            year=int(date_str[0:4]),
            month=int(date_str[4:6]),
            day=int(date_str[6:8]),
            hour=int(time_code[0:2]),
            minute=int(time_code[2:4]) if len(time_code) >= 4 else 0,
        )

    def to_callback_data(self) -> str:
        trainer_str = str(self.trainer_id) if self.trainer_id is not None else 'none'
        date_str = f'{self.year:04d}{self.month:02d}{self.day:02d}'
        time_str = f'{self.hour:02d}{self.minute:02d}'
        return f'book_slot_{self.court_id}_{trainer_str}_{date_str}_{time_str}'


class CancelBookingArg(BaseModel):
    booking_id: int

    @classmethod
    def from_callback_data(cls, data: str) -> Self:
        return cls(booking_id=int(data.split('_')[2]))

    def to_callback_data(self) -> str:
        return f'cancel_booking_{self.booking_id}'
