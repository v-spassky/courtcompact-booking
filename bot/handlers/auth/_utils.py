import calendar as cal
import logging
from datetime import datetime

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, User

from bot.deps import Deps
from config.settings import now_kiev
from db.models import Student
from localization.base import Messages

logger = logging.getLogger(__name__)


def _get_user_display(user: User) -> str:
    if user.username:
        return f'@{user.username}'
    elif user.full_name:
        return f'{user.full_name} (id:{user.id})'
    else:
        return f'User (id:{user.id})'


def _log_user_action(user: User, action: str) -> None:
    user_display = _get_user_display(user)
    logger.info(f'User {user_display} {action}')


def _is_admin(user_id: int, deps: Deps) -> bool:
    return deps.admin_repo.get_by_telegram_id(user_id) is not None


def _is_trainer(user_id: int, deps: Deps) -> bool:
    return deps.trainer_repo.get_by_telegram_id(user_id) is not None


def _is_authorized_student(user_id: int, deps: Deps) -> Student | None:
    return deps.student_repo.get_by_telegram_id(user_id)


def _is_authorized(user_id: int, deps: Deps) -> bool:
    return deps.user_repo.get_by_telegram_id(user_id) is not None


def _get_student_for_user(user_id: int, deps: Deps) -> Student | None:
    return deps.student_repo.get_by_telegram_id(user_id)


def _create_calendar(year: int, month: int) -> InlineKeyboardMarkup:
    msgs = Messages.get_for_language('')
    keyboard = []
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
                if date >= today:
                    row.append(InlineKeyboardButton(str(day), callback_data=f'date_{year}_{month}_{day}'))
                else:
                    row.append(InlineKeyboardButton('·', callback_data='ignore'))
        keyboard.append(row)
    nav_row = []
    prev_month = month - 1 if month > 1 else 12
    prev_year = year if month > 1 else year - 1
    if datetime(prev_year, prev_month, 1).date() >= datetime(today.year, today.month, 1).date():
        nav_row.append(InlineKeyboardButton('◀️', callback_data=f'cal_{prev_year}_{prev_month}'))
    else:
        nav_row.append(InlineKeyboardButton(' ', callback_data='ignore'))
    nav_row.append(InlineKeyboardButton(msgs.btn_menu, callback_data='main_menu'))
    next_month = month + 1 if month < 12 else 1
    next_year = year if month < 12 else year + 1
    nav_row.append(InlineKeyboardButton('▶️', callback_data=f'cal_{next_year}_{next_month}'))
    keyboard.append(nav_row)
    return InlineKeyboardMarkup(keyboard)
