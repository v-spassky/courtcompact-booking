import logging

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from bot.deps import get_deps
from bot.handlers.auth import _is_admin
from localization import get_messages

logger = logging.getLogger(__name__)


async def _handle_admin_edit_student_list(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.callback_query or not update.effective_user:
        return

    msgs = get_messages()
    deps = get_deps(context)

    if not _is_admin(update.effective_user.id):
        await update.callback_query.edit_message_text(msgs.admin_no_access)
        return

    students = deps.student_repo.get_all()

    if not students:
        keyboard = [[InlineKeyboardButton(msgs.btn_back, callback_data='admin_students')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.callback_query.edit_message_text(msgs.admin_student_no_students, reply_markup=reply_markup)
        return

    keyboard = []
    for student in students:
        student_id_short = str(student.id)[:8]
        status = '✅' if student.telegram_user_id else '⏳'
        button_text = f'{status} {student.name}'
        keyboard.append([InlineKeyboardButton(button_text, callback_data=f'admin_edit_student_{student_id_short}')])

    keyboard.append([InlineKeyboardButton(msgs.btn_back, callback_data='admin_students')])
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.callback_query.edit_message_text(msgs.admin_student_select_to_edit, reply_markup=reply_markup)
