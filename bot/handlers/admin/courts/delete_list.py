import logging

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from bot.deps import get_deps
from bot.handlers.admin._utils import _clear_admin_state
from bot.handlers.auth import _is_admin
from localization import get_messages

logger = logging.getLogger(__name__)


async def _handle_admin_delete_court_list(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.callback_query or not update.effective_user:
        return

    msgs = get_messages()
    deps = get_deps(context)

    if not _is_admin(update.effective_user.id):
        await update.callback_query.edit_message_text(msgs.admin_no_access)
        return

    _clear_admin_state(context)
    courts = deps.court_repo.get_all()

    if not courts:
        keyboard = [[InlineKeyboardButton(msgs.btn_back, callback_data='admin_courts')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.callback_query.edit_message_text(msgs.admin_court_no_courts, reply_markup=reply_markup)
        return

    keyboard = []
    for court in courts:
        court_id_short = str(court.id)[:8]
        keyboard.append(
            [InlineKeyboardButton(f'🎾 {court.name}', callback_data=f'admin_delete_court_{court_id_short}')]
        )
    keyboard.append([InlineKeyboardButton(msgs.btn_back, callback_data='admin_courts')])
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.callback_query.edit_message_text(msgs.admin_court_select_to_delete, reply_markup=reply_markup)
