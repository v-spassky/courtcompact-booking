import logging

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from bot.deps import get_deps
from bot.handlers.booking.select_court import _handle_book_court
from localization import get_messages

logger = logging.getLogger(__name__)


async def _handle_book_court_select_location(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.callback_query or not update.effective_user:
        return

    msgs = get_messages()
    deps = get_deps(context)

    locations = deps.location_repo.get_all()

    if not locations:
        await _handle_book_court(update, context, None)
        return

    text = msgs.book_select_location

    for location in locations:
        if location.maps_link:
            text += f'📍 <a href="{location.maps_link}">{location.name}</a>\n\n'
        else:
            text += f'📍 {location.name}\n\n'

    keyboard = []
    for location in locations:
        location_id_short = str(location.id)[:8]
        button_text = f'📍 {location.name}'
        keyboard.append([InlineKeyboardButton(button_text, callback_data=f'book_location_{location_id_short}')])

    keyboard.append([InlineKeyboardButton(msgs.btn_back_to_main_menu, callback_data='main_menu')])
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.callback_query.edit_message_text(
        text, reply_markup=reply_markup, parse_mode='HTML', disable_web_page_preview=True
    )
