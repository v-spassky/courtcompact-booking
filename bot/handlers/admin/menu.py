import logging

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from bot.deps import get_deps
from bot.handlers.admin._utils import _clear_admin_state as _clear_admin_state
from bot.handlers.auth import _is_admin, _log_user_action
from localization import get_messages

logger = logging.getLogger(__name__)


async def _handle_admin_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.callback_query or not update.effective_user:
        return

    msgs = get_messages()
    user_id = update.effective_user.id

    if not _is_admin(user_id):
        await update.callback_query.edit_message_text(msgs.admin_no_access)
        return

    _log_user_action(update.effective_user, 'opened admin menu')
    _clear_admin_state(context)

    keyboard = [
        [InlineKeyboardButton(msgs.btn_admin_locations, callback_data='admin_locations')],
        [InlineKeyboardButton(msgs.btn_admin_courts, callback_data='admin_courts')],
        [InlineKeyboardButton(msgs.btn_admin_trainers, callback_data='admin_trainers')],
        [InlineKeyboardButton(msgs.btn_admin_students, callback_data='admin_students')],
        [InlineKeyboardButton(msgs.btn_back_to_main_menu, callback_data='main_menu')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.callback_query.edit_message_text(msgs.admin_menu_title, reply_markup=reply_markup)


async def _handle_admin_courts_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.callback_query or not update.effective_user:
        return

    msgs = get_messages()
    deps = get_deps(context)

    if not _is_admin(update.effective_user.id):
        await update.callback_query.edit_message_text(msgs.admin_no_access)
        return

    _clear_admin_state(context)

    courts = deps.court_repo.get_active()
    text = msgs.admin_courts_menu(count=len(courts))

    keyboard = [
        [InlineKeyboardButton(f'{msgs.btn_create} корт', callback_data='admin_create_court')],
        [InlineKeyboardButton(f'{msgs.btn_edit} корт', callback_data='admin_edit_court')],
        [InlineKeyboardButton(f'{msgs.btn_delete} корт', callback_data='admin_delete_court')],
        [InlineKeyboardButton(msgs.btn_back, callback_data='admin_menu')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.callback_query.edit_message_text(text, reply_markup=reply_markup)


async def _handle_admin_trainers_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.callback_query or not update.effective_user:
        return

    msgs = get_messages()
    deps = get_deps(context)

    if not _is_admin(update.effective_user.id):
        await update.callback_query.edit_message_text(msgs.admin_no_access)
        return

    _clear_admin_state(context)

    trainers = deps.trainer_repo.get_all()
    text = msgs.admin_trainers_menu(count=len(trainers))

    keyboard = [
        [InlineKeyboardButton(f'{msgs.btn_create} тренера', callback_data='admin_create_trainer')],
        [InlineKeyboardButton(f'{msgs.btn_edit} тренера', callback_data='admin_edit_trainer')],
        [InlineKeyboardButton(f'{msgs.btn_delete} тренера', callback_data='admin_delete_trainer')],
        [InlineKeyboardButton(msgs.btn_back, callback_data='admin_menu')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.callback_query.edit_message_text(text, reply_markup=reply_markup)


async def _handle_admin_locations_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.callback_query or not update.effective_user:
        return

    msgs = get_messages()
    deps = get_deps(context)

    if not _is_admin(update.effective_user.id):
        await update.callback_query.edit_message_text(msgs.admin_no_access)
        return

    _clear_admin_state(context)

    locations = deps.location_repo.get_active()
    text = msgs.admin_locations_menu(count=len(locations))

    keyboard = [
        [InlineKeyboardButton(f'{msgs.btn_create} локацию', callback_data='admin_create_location')],
        [InlineKeyboardButton(f'{msgs.btn_edit} локацию', callback_data='admin_edit_location')],
        [InlineKeyboardButton(f'{msgs.btn_delete} локацию', callback_data='admin_delete_location')],
        [InlineKeyboardButton(msgs.btn_back, callback_data='admin_menu')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.callback_query.edit_message_text(text, reply_markup=reply_markup)


async def _handle_admin_students_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.callback_query or not update.effective_user:
        return

    msgs = get_messages()
    deps = get_deps(context)

    if not _is_admin(update.effective_user.id):
        await update.callback_query.edit_message_text(msgs.admin_no_access)
        return

    _log_user_action(update.effective_user, 'opened students admin menu')
    _clear_admin_state(context)

    students = deps.student_repo.get_all()
    text = msgs.admin_students_menu(
        total=len(students),
        authorized=sum(1 for s in students if s.telegram_user_id),
    )

    keyboard = [
        [InlineKeyboardButton('➕ Добавить ученика', callback_data='admin_create_student')],
        [InlineKeyboardButton('✏️ Редактировать ученика', callback_data='admin_edit_student')],
        [InlineKeyboardButton('🗑️ Удалить ученика', callback_data='admin_delete_student')],
        [InlineKeyboardButton(msgs.btn_back, callback_data='admin_menu')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.callback_query.edit_message_text(text, reply_markup=reply_markup)
