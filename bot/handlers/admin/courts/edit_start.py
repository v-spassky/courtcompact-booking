import logging

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from bot.deps import get_deps
from bot.handlers.admin._utils import _clear_admin_state
from bot.handlers.auth import _is_admin
from localization import get_messages

logger = logging.getLogger(__name__)


async def _handle_admin_edit_court_start(update: Update, context: ContextTypes.DEFAULT_TYPE, data: str) -> None:
    if not update.callback_query or not update.effective_user:
        return

    msgs = get_messages()
    deps = get_deps(context)

    if not _is_admin(update.effective_user.id):
        await update.callback_query.edit_message_text(msgs.admin_no_access)
        return

    court_id_short = data.replace('admin_edit_court_', '')

    courts = deps.court_repo.get_active()
    court = None
    for c in courts:
        if str(c.id).startswith(court_id_short):
            court = c
            break

    if not court:
        keyboard = [[InlineKeyboardButton(msgs.btn_back, callback_data='admin_courts')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.callback_query.edit_message_text('❌ Корт не найден.', reply_markup=reply_markup)
        return

    _clear_admin_state(context)
    assert context.user_data is not None
    context.user_data['admin_court_id'] = str(court.id)
    context.user_data['admin_state'] = 'awaiting_edit_court_name'

    desc_text = court.description if court.description else '(не указано)'
    text = f"""✏️ Редактирование корта

Текущее название: {court.name}
Текущее описание: {desc_text}

Шаг 1/2: Введите новое название (или "-" чтобы оставить текущее):"""

    keyboard = [[InlineKeyboardButton(msgs.btn_cancel, callback_data='admin_courts')]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.callback_query.edit_message_text(text, reply_markup=reply_markup)
