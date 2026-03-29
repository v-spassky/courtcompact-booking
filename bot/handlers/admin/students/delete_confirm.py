import logging

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from bot.deps import get_deps
from bot.handlers.auth import _is_admin
from localization import get_messages

logger = logging.getLogger(__name__)


async def _handle_admin_delete_student_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE, data: str) -> None:
    if not update.callback_query or not update.effective_user:
        return

    msgs = get_messages()
    deps = get_deps(context)

    if not _is_admin(update.effective_user.id):
        await update.callback_query.edit_message_text(msgs.admin_no_access)
        return

    student_id_short = data.replace('admin_delete_student_', '')
    students = deps.student_repo.get_all()
    student = None
    for s in students:
        if str(s.id).startswith(student_id_short):
            student = s
            break

    if not student:
        keyboard = [[InlineKeyboardButton(msgs.btn_back, callback_data='admin_students')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.callback_query.edit_message_text(msgs.admin_student_not_found, reply_markup=reply_markup)
        return

    text = msgs.admin_student_confirm_delete(name=student.name)

    keyboard = [
        [
            InlineKeyboardButton(
                msgs.btn_confirm_delete, callback_data=f'admin_confirm_delete_student_{student_id_short}'
            )
        ],
        [InlineKeyboardButton(msgs.btn_cancel, callback_data='admin_students')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.callback_query.edit_message_text(text, reply_markup=reply_markup)
