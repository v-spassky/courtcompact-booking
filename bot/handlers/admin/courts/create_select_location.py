import logging

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from bot.deps import get_deps
from bot.handlers.admin._utils import _clear_admin_state
from bot.handlers.auth import _is_admin
from localization import get_messages

logger = logging.getLogger(__name__)


async def _handle_admin_create_court_select_location(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
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
        text = msgs.admin_court_no_locations
        keyboard = [
            [InlineKeyboardButton(msgs.btn_create_location, callback_data='admin_create_location')],
            [InlineKeyboardButton(msgs.btn_back, callback_data='admin_courts')],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.callback_query.edit_message_text(text, reply_markup=reply_markup)
        return

    text = msgs.admin_court_select_location

    keyboard = []
    for location in locations:
        location_id_short = str(location.id)[:8]
        button_text = f'📍 {location.name}'
        if location.maps_link:
            button_text += ' 🗺️'
        keyboard.append([InlineKeyboardButton(button_text, callback_data=f'admin_court_location_{location_id_short}')])

    keyboard.append([InlineKeyboardButton(msgs.btn_cancel, callback_data='admin_courts')])
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.callback_query.edit_message_text(text, reply_markup=reply_markup)
