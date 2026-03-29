import logging

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from bot.deps import get_deps
from bot.handlers.admin._utils import _clear_admin_state
from localization import get_messages

logger = logging.getLogger(__name__)


async def _handle_admin_edit_student_name_input(update: Update, context: ContextTypes.DEFAULT_TYPE, name: str) -> None:
    assert update.message is not None
    assert context.user_data is not None
    msgs = get_messages()
    deps = get_deps(context)
    student_id = context.user_data.get('admin_student_id')
    if not student_id:
        _clear_admin_state(context)
        return

    student = deps.student_repo.get(student_id)
    if not student:
        _clear_admin_state(context)
        keyboard = [[InlineKeyboardButton(msgs.btn_back, callback_data='admin_students')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(msgs.admin_student_not_found, reply_markup=reply_markup)
        return

    if name and name != '-':
        context.user_data['admin_student_name'] = name
    else:
        context.user_data['admin_student_name'] = student.name

    context.user_data['admin_state'] = 'awaiting_edit_student_phone'

    text = msgs.admin_student_edit_step2(new_name=context.user_data['admin_student_name'], phone=student.phone)

    keyboard = [[InlineKeyboardButton(msgs.btn_cancel, callback_data='admin_students')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(text, reply_markup=reply_markup)
