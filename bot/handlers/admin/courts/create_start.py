import logging

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from bot.deps import get_deps
from bot.handlers.admin._utils import _clear_admin_state
from bot.handlers.auth import _is_admin
from localization import get_messages

logger = logging.getLogger(__name__)


async def _handle_admin_create_court_start(update: Update, context: ContextTypes.DEFAULT_TYPE, data: str) -> None:
    if not update.callback_query or not update.effective_user:
        return

    msgs = get_messages()
    deps = get_deps(context)

    if not _is_admin(update.effective_user.id):
        await update.callback_query.edit_message_text(msgs.admin_no_access)
        return

    location_id_short = data.replace('admin_court_location_', '')

    locations = deps.location_repo.get_all()
    location = None
    for loc in locations:
        if str(loc.id).startswith(location_id_short):
            location = loc
            break

    if not location:
        keyboard = [[InlineKeyboardButton(msgs.btn_back, callback_data='admin_courts')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.callback_query.edit_message_text(msgs.admin_location_not_found, reply_markup=reply_markup)
        return

    _clear_admin_state(context)
    assert context.user_data is not None
    context.user_data['admin_court_location_id'] = str(location.id)
    context.user_data['admin_state'] = 'awaiting_court_name'

    text = msgs.admin_court_create_step2(location_name=location.name)

    keyboard = [[InlineKeyboardButton(msgs.btn_cancel, callback_data='admin_courts')]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.callback_query.edit_message_text(text, reply_markup=reply_markup)
