import logging

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from bot.deps import get_deps
from bot.handlers.admin._utils import _clear_admin_state
from bot.handlers.auth import _is_admin
from localization import get_messages

logger = logging.getLogger(__name__)


async def _handle_admin_delete_location_list(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.callback_query or not update.effective_user:
        return

    msgs = get_messages()
    deps = get_deps(context)

    if not _is_admin(update.effective_user.id):
        await update.callback_query.edit_message_text(msgs.admin_no_access)
        return

    _clear_admin_state(context)
    locations = deps.location_repo.get_all()

    if not locations:
        keyboard = [[InlineKeyboardButton(msgs.btn_back, callback_data='admin_locations')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.callback_query.edit_message_text(msgs.admin_location_no_locations, reply_markup=reply_markup)
        return

    keyboard = []
    for location in locations:
        location_id_short = str(location.id)[:8]
        keyboard.append(
            [InlineKeyboardButton(f'📍 {location.name}', callback_data=f'admin_delete_location_{location_id_short}')]
        )
    keyboard.append([InlineKeyboardButton(msgs.btn_back, callback_data='admin_locations')])
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.callback_query.edit_message_text(msgs.admin_location_select_to_delete, reply_markup=reply_markup)
