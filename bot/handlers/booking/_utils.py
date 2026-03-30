import calendar as cal
import logging
from datetime import date as DateType
from datetime import datetime

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from bot.deps import Deps
from config.settings import now_kiev
from localization import get_messages

logger = logging.getLogger(__name__)


def _check_date_availability(date: DateType, court_id: int, trainer_id: int | None, deps: Deps) -> bool:
    try:
        date_datetime = datetime.combine(date, datetime.min.time())
        time_slots = deps.schedule_service.get_all_time_slots_for_date(date_datetime)
        court_slots = [slot for slot in time_slots if slot.court_id == court_id]
        if not trainer_id:
            return any(slot.is_available for slot in court_slots)
        available_slots = [slot for slot in court_slots if slot.is_available]
        if not available_slots:
            return False
        for slot in available_slots:
            trainer_busy = False
            all_day_slots = deps.schedule_service.get_all_time_slots_for_date(date_datetime)
            for other_slot in all_day_slots:
                if not other_slot.is_available and other_slot.booking_id:
                    booking = deps.booking_repo.get(other_slot.booking_id)
                    if booking and booking.trainer_id == trainer_id:
                        if slot.start_time < booking.end_time and slot.end_time > booking.start_time:
                            trainer_busy = True
                            break
            if not trainer_busy:
                return True
        return False
    except Exception:
        logger.exception('Error checking date availability')
        return True


def _create_booking_calendar(
    year: int, month: int, court_id: int, trainer_id: int | None, deps: Deps
) -> InlineKeyboardMarkup:
    msgs = get_messages()
    keyboard = []
    trainer_id_str = str(trainer_id) if trainer_id is not None else 'none'
    month_name = cal.month_name[month]
    keyboard.append([InlineKeyboardButton(f'{month_name} {year}', callback_data='ignore')])
    keyboard.append([InlineKeyboardButton(day, callback_data='ignore') for day in msgs.day_names])
    month_calendar = cal.monthcalendar(year, month)
    today = now_kiev().date()
    for week in month_calendar:
        row = []
        for day in week:
            if day == 0:
                row.append(InlineKeyboardButton(' ', callback_data='ignore'))
            else:
                date = datetime(year, month, day).date()
                if date < today:
                    row.append(InlineKeyboardButton('·', callback_data='ignore'))
                else:
                    has_slots = _check_date_availability(date, court_id, trainer_id, deps)
                    if has_slots:
                        callback_data = f'book_date_{court_id}_{trainer_id_str}_{year}_{month}_{day}'
                        row.append(InlineKeyboardButton(str(day), callback_data=callback_data))
                    else:
                        row.append(InlineKeyboardButton('·', callback_data='ignore'))
        keyboard.append(row)
    nav_row = []
    prev_month = month - 1 if month > 1 else 12
    prev_year = year if month > 1 else year - 1
    if datetime(prev_year, prev_month, 1).date() >= datetime(today.year, today.month, 1).date():
        nav_row.append(
            InlineKeyboardButton('◀️', callback_data=f'book_cal_{court_id}_{trainer_id_str}_{prev_year}_{prev_month}')
        )
    else:
        nav_row.append(InlineKeyboardButton(' ', callback_data='ignore'))
    nav_row.append(InlineKeyboardButton(msgs.btn_menu, callback_data='main_menu'))
    next_month = month + 1 if month < 12 else 1
    next_year = year if month < 12 else year + 1
    nav_row.append(
        InlineKeyboardButton('▶️', callback_data=f'book_cal_{court_id}_{trainer_id_str}_{next_year}_{next_month}')
    )
    keyboard.append(nav_row)
    return InlineKeyboardMarkup(keyboard)
