import logging

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from bot.deps import get_deps
from bot.handlers.auth import _is_admin, _log_user_action
from localization import get_messages

logger = logging.getLogger(__name__)


async def _handle_admin_delete_location_execute(update: Update, context: ContextTypes.DEFAULT_TYPE, data: str) -> None:
    if not update.callback_query or not update.effective_user:
        return

    msgs = get_messages()
    deps = get_deps(context)

    if not _is_admin(update.effective_user.id):
        await update.callback_query.edit_message_text(msgs.admin_no_access)
        return

    location_id_short = data.replace('admin_confirm_delete_location_', '')

    locations = deps.location_repo.get_active()
    location = None
    for loc in locations:
        if str(loc.id).startswith(location_id_short):
            location = loc
            break

    if not location:
        keyboard = [[InlineKeyboardButton(msgs.btn_back, callback_data='admin_locations')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.callback_query.edit_message_text('❌ Локация не найдена.', reply_markup=reply_markup)
        return

    try:
        location_name = location.name
        deps.location_repo.delete(location.id)
        _log_user_action(update.effective_user, f'deleted location: {location_name}')

        text = msgs.admin_location_deleted(name=location_name)
        keyboard = [[InlineKeyboardButton('◀️ К локациям', callback_data='admin_locations')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.callback_query.edit_message_text(text, reply_markup=reply_markup)

    except Exception:
        logger.exception('Failed to delete location')
        keyboard = [[InlineKeyboardButton('◀️ К локациям', callback_data='admin_locations')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.callback_query.edit_message_text(msgs.admin_location_delete_error, reply_markup=reply_markup)
