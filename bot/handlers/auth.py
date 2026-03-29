import calendar as cal
import logging
from datetime import datetime

from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    Message,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    Update,
    User,
)
from telegram.ext import ContextTypes

from bot.deps import Deps, get_deps
from config.settings import now_kiev, settings
from db.models import Student
from localization import get_messages

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Small utility helpers (used across multiple handler modules)
# ---------------------------------------------------------------------------


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


def _is_admin(user_id: int) -> bool:
    return user_id in settings.admin_ids


def _is_trainer(user_id: int, deps: Deps) -> bool:
    trainer = deps.trainer_repo.get_by_telegram_id(user_id)
    return trainer is not None


def _is_authorized_student(user_id: int, deps: Deps) -> Student | None:
    student = deps.student_repo.get_by_telegram_id(user_id)
    return student


def _is_authorized(user_id: int, deps: Deps) -> bool:
    if _is_admin(user_id):
        return True
    if _is_trainer(user_id, deps):
        return True
    if _is_authorized_student(user_id, deps):
        return True
    return False


def _get_student_for_user(user_id: int, deps: Deps) -> Student | None:
    return deps.student_repo.get_by_telegram_id(user_id)


def _create_calendar(year: int, month: int) -> InlineKeyboardMarkup:
    msgs = get_messages()
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
                    callback_data = f'date_{year}_{month}_{day}'
                    row.append(InlineKeyboardButton(str(day), callback_data=callback_data))
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


# ---------------------------------------------------------------------------
# Auth handlers
# ---------------------------------------------------------------------------


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message or not update.effective_user:
        return

    msgs = get_messages()
    deps = get_deps(context)
    _log_user_action(update.effective_user, 'used /start command')
    user_id = update.effective_user.id

    if not _is_authorized(user_id, deps):
        await _show_authorization_request(update, context)
        return

    keyboard = [
        [InlineKeyboardButton(msgs.btn_schedule_by_date, callback_data='select_date_schedule')],
        [InlineKeyboardButton(msgs.btn_schedule_weekly, callback_data='schedule_weekly')],
        [InlineKeyboardButton(msgs.btn_trainer_schedule, callback_data='trainer_schedule')],
        [InlineKeyboardButton(msgs.btn_book_court, callback_data='book_court')],
        [InlineKeyboardButton(msgs.btn_my_bookings, callback_data='my_bookings')],
        [InlineKeyboardButton(msgs.btn_cancel_booking, callback_data='cancel_booking')],
    ]

    if _is_admin(user_id):
        keyboard.append([InlineKeyboardButton(msgs.btn_admin_panel, callback_data='admin_menu')])

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(msgs.welcome_start, reply_markup=reply_markup)


async def _show_authorization_request(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    msgs = get_messages()
    keyboard = [[KeyboardButton(msgs.btn_share_phone, request_contact=True)]]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)

    if update.message:
        await update.message.reply_text(msgs.auth_request, reply_markup=reply_markup)
    elif update.callback_query:
        msg = update.callback_query.message
        if isinstance(msg, Message):
            await msg.reply_text(msgs.auth_request, reply_markup=reply_markup)


async def handle_contact(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message or not update.message.contact or not update.effective_user:
        return

    msgs = get_messages()
    deps = get_deps(context)
    contact = update.message.contact
    user_id = update.effective_user.id

    if contact.user_id != user_id:
        await update.message.reply_text(
            msgs.auth_wrong_contact,
            reply_markup=ReplyKeyboardRemove(),
        )
        return

    phone = contact.phone_number
    _log_user_action(update.effective_user, f'shared phone number: {phone}')

    student = deps.student_repo.get_by_phone(phone)

    if student:
        student.telegram_user_id = user_id
        deps.student_repo.save(student)
        _log_user_action(update.effective_user, f'authorized as student: {student.name}')

        await update.message.reply_text(msgs.auth_success(student.name), reply_markup=ReplyKeyboardRemove())

        keyboard = [
            [InlineKeyboardButton(msgs.btn_schedule_by_date, callback_data='select_date_schedule')],
            [InlineKeyboardButton(msgs.btn_schedule_weekly, callback_data='schedule_weekly')],
            [InlineKeyboardButton(msgs.btn_trainer_schedule, callback_data='trainer_schedule')],
            [InlineKeyboardButton(msgs.btn_book_court, callback_data='book_court')],
            [InlineKeyboardButton(msgs.btn_my_bookings, callback_data='my_bookings')],
            [InlineKeyboardButton(msgs.btn_cancel_booking, callback_data='cancel_booking')],
        ]

        if _is_admin(user_id):
            keyboard.append([InlineKeyboardButton(msgs.btn_admin_panel, callback_data='admin_menu')])

        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(msgs.welcome_after_auth, reply_markup=reply_markup)
    else:
        await update.message.reply_text(
            msgs.auth_phone_not_found,
            reply_markup=ReplyKeyboardRemove(),
        )


async def show_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE, edit_message: bool = False) -> None:
    msgs = get_messages()
    keyboard = [
        [InlineKeyboardButton(msgs.btn_schedule_by_date, callback_data='select_date_schedule')],
        [InlineKeyboardButton(msgs.btn_schedule_weekly, callback_data='schedule_weekly')],
        [InlineKeyboardButton(msgs.btn_trainer_schedule, callback_data='trainer_schedule')],
        [InlineKeyboardButton(msgs.btn_book_court, callback_data='book_court')],
        [InlineKeyboardButton(msgs.btn_my_bookings, callback_data='my_bookings')],
        [InlineKeyboardButton(msgs.btn_cancel_booking, callback_data='cancel_booking')],
    ]

    if update.effective_user and _is_admin(update.effective_user.id):
        keyboard.append([InlineKeyboardButton(msgs.btn_admin_panel, callback_data='admin_menu')])

    reply_markup = InlineKeyboardMarkup(keyboard)

    if edit_message and update.callback_query:
        await update.callback_query.edit_message_text(msgs.welcome_after_auth, reply_markup=reply_markup)
    elif update.message:
        await update.message.reply_text(msgs.welcome_after_auth, reply_markup=reply_markup)


async def handle_unknown_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message or not update.effective_user:
        return

    msgs = get_messages()
    user_id = update.effective_user.id
    message_text = (update.message.text or '').strip()

    assert context.user_data is not None
    admin_state = context.user_data.get('admin_state')

    if admin_state and _is_admin(user_id):
        from bot.handlers.admin import courts, locations, students, trainers

        if admin_state == 'awaiting_location_name':
            await locations._handle_admin_location_name_input(update, context, message_text)
            return
        elif admin_state == 'awaiting_location_maps_link':
            await locations._handle_admin_location_maps_link_input(update, context, message_text)
            return
        elif admin_state == 'awaiting_edit_location_name':
            await locations._handle_admin_edit_location_name_input(update, context, message_text)
            return
        elif admin_state == 'awaiting_edit_location_maps_link':
            await locations._handle_admin_edit_location_maps_link_input(update, context, message_text)
            return
        elif admin_state == 'awaiting_court_name':
            await courts._handle_admin_court_name_input(update, context, message_text)
            return
        elif admin_state == 'awaiting_court_description':
            await courts._handle_admin_court_description_input(update, context, message_text)
            return
        elif admin_state == 'awaiting_edit_court_name':
            await courts._handle_admin_edit_court_name_input(update, context, message_text)
            return
        elif admin_state == 'awaiting_edit_court_description':
            await courts._handle_admin_edit_court_description_input(update, context, message_text)
            return
        elif admin_state == 'awaiting_trainer_name':
            await trainers._handle_admin_trainer_name_input(update, context, message_text)
            return
        elif admin_state == 'awaiting_trainer_telegram_id':
            await trainers._handle_admin_trainer_id_input(update, context, message_text)
            return
        elif admin_state == 'awaiting_trainer_description':
            await trainers._handle_admin_trainer_description_input(update, context, message_text)
            return
        elif admin_state == 'awaiting_edit_trainer_name':
            await trainers._handle_admin_edit_trainer_name_input(update, context, message_text)
            return
        elif admin_state == 'awaiting_edit_trainer_telegram_id':
            await trainers._handle_admin_edit_trainer_id_input(update, context, message_text)
            return
        elif admin_state == 'awaiting_edit_trainer_description':
            await trainers._handle_admin_edit_trainer_description_input(update, context, message_text)
            return
        elif admin_state == 'awaiting_student_name':
            await students._handle_admin_student_name_input(update, context, message_text)
            return
        elif admin_state == 'awaiting_student_phone':
            await students._handle_admin_student_phone_input(update, context, message_text)
            return
        elif admin_state == 'awaiting_edit_student_name':
            await students._handle_admin_edit_student_name_input(update, context, message_text)
            return
        elif admin_state == 'awaiting_edit_student_phone':
            await students._handle_admin_edit_student_phone_input(update, context, message_text)
            return

    keyboard = [[InlineKeyboardButton(msgs.btn_main_menu, callback_data='main_menu')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(msgs.unknown_command, reply_markup=reply_markup)
