import logging

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from bot.deps import get_deps
from bot.handlers.auth import _is_admin, _log_user_action
from localization import get_messages

logger = logging.getLogger(__name__)


async def _handle_admin_delete_court_execute(update: Update, context: ContextTypes.DEFAULT_TYPE, data: str) -> None:
    if not update.callback_query or not update.effective_user:
        return

    msgs = get_messages()
    deps = get_deps(context)

    if not _is_admin(update.effective_user.id):
        await update.callback_query.edit_message_text(msgs.admin_no_access)
        return

    court_id_short = data.replace('admin_confirm_delete_court_', '')

    courts = deps.court_repo.get_active()
    court = None
    for c in courts:
        if str(c.id).startswith(court_id_short):
            court = c
            break

    if not court:
        keyboard = [[InlineKeyboardButton(msgs.btn_back, callback_data='admin_courts')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.callback_query.edit_message_text(msgs.admin_court_not_found, reply_markup=reply_markup)
        return

    try:
        court_name = court.name
        court.is_active = False
        deps.court_repo.save(court)
        _log_user_action(update.effective_user, f'deleted court: {court_name}')

        text = msgs.admin_court_deleted(name=court_name)
        keyboard = [[InlineKeyboardButton(msgs.btn_back_to_courts, callback_data='admin_courts')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.callback_query.edit_message_text(text, reply_markup=reply_markup)

    except Exception:
        logger.exception('Failed to delete court')
        keyboard = [[InlineKeyboardButton(msgs.btn_back_to_courts, callback_data='admin_courts')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.callback_query.edit_message_text(msgs.admin_court_delete_error, reply_markup=reply_markup)
