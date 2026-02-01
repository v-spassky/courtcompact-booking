import logging

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from bot.deps import get_deps
from bot.handlers.admin._utils import _clear_admin_state
from bot.handlers.auth import _is_admin
from localization import get_messages

logger = logging.getLogger(__name__)


async def _handle_admin_edit_student_start(update: Update, context: ContextTypes.DEFAULT_TYPE, data: str) -> None:
    if not update.callback_query or not update.effective_user:
        return

    msgs = get_messages()
    deps = get_deps(context)

    if not _is_admin(update.effective_user.id):
        await update.callback_query.edit_message_text(msgs.admin_no_access)
        return

    student_id_short = data.replace('admin_edit_student_', '')
    students = deps.student_repo.get_all()
    student = None
    for s in students:
        if str(s.id).startswith(student_id_short):
            student = s
            break

    if not student:
        keyboard = [[InlineKeyboardButton(msgs.btn_back, callback_data='admin_students')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.callback_query.edit_message_text('❌ Ученик не найден.', reply_markup=reply_markup)
        return

    _clear_admin_state(context)
    assert context.user_data is not None
    context.user_data['admin_student_id'] = str(student.id)
    context.user_data['admin_state'] = 'awaiting_edit_student_name'

    status = 'Авторизован' if student.telegram_user_id else 'Не авторизован'
    text = f"""✏️ Редактирование ученика

Текущее имя: {student.name}
Телефон: {student.phone}
Статус: {status}

Шаг 1/2: Введите новое имя (или "-" чтобы оставить текущее):"""

    keyboard = [[InlineKeyboardButton(msgs.btn_cancel, callback_data='admin_students')]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.callback_query.edit_message_text(text, reply_markup=reply_markup)
