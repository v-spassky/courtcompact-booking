import logging

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from bot.deps import get_deps
from bot.handlers.admin._utils import _clear_admin_state
from bot.handlers.auth import _log_user_action
from localization import get_messages

logger = logging.getLogger(__name__)


async def _handle_admin_edit_student_phone_input(
    update: Update, context: ContextTypes.DEFAULT_TYPE, phone: str
) -> None:
    assert update.message is not None
    assert context.user_data is not None
    msgs = get_messages()
    deps = get_deps(context)
    student_id = context.user_data.get('admin_student_id')
    new_name = context.user_data.get('admin_student_name')

    if not student_id or not new_name:
        _clear_admin_state(context)
        return

    student = deps.student_repo.get(student_id)
    if not student:
        _clear_admin_state(context)
        keyboard = [[InlineKeyboardButton(msgs.btn_back, callback_data='admin_students')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(msgs.admin_student_not_found, reply_markup=reply_markup)
        return

    new_phone = phone if phone and phone != '-' else student.phone

    if new_phone != student.phone:
        existing = deps.student_repo.get_by_phone(new_phone)
        if existing and str(existing.id) != student_id:
            _clear_admin_state(context)
            text = msgs.admin_student_phone_taken(name=existing.name)
            keyboard = [[InlineKeyboardButton(msgs.btn_back_to_students, callback_data='admin_students')]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text(text, reply_markup=reply_markup)
            return

    _clear_admin_state(context)

    try:
        student.name = new_name
        student.phone = new_phone
        deps.student_repo.save(student)

        if update.effective_user:
            _log_user_action(update.effective_user, f'edited student: {student.name}')

        text = msgs.admin_student_updated(name=student.name)

        keyboard = [
            [InlineKeyboardButton(msgs.btn_edit_another, callback_data='admin_edit_student')],
            [InlineKeyboardButton(msgs.btn_back_to_students, callback_data='admin_students')],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(text, reply_markup=reply_markup)

    except Exception:
        logger.exception('Failed to edit student')
        keyboard = [[InlineKeyboardButton(msgs.btn_back_to_students, callback_data='admin_students')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(msgs.admin_student_update_error, reply_markup=reply_markup)
