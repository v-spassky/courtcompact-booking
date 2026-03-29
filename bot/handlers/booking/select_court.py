import logging

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from bot.deps import get_deps
from localization import get_messages

logger = logging.getLogger(__name__)


async def _handle_book_court(update: Update, context: ContextTypes.DEFAULT_TYPE, data: str | None = None) -> None:
    if not update.callback_query or not update.effective_user:
        return

    msgs = get_messages()
    deps = get_deps(context)

    location = None
    courts = []

    if data and data.startswith('book_location_'):
        location_id_short = data.replace('book_location_', '')

        locations = deps.location_repo.get_all()
        for loc in locations:
            if str(loc.id).startswith(location_id_short):
                location = loc
                break

        if location:
            courts = deps.location_repo.get_courts(location.id)
    else:
        courts = deps.court_repo.get_all()

    if not courts:
        text = msgs.book_no_courts(location_name=location.name if location else None)
        keyboard = [
            [InlineKeyboardButton(msgs.btn_select_other_location, callback_data='book_court')],
            [InlineKeyboardButton(msgs.btn_back_to_main_menu, callback_data='main_menu')],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.callback_query.edit_message_text(text, reply_markup=reply_markup)
        return

    text = msgs.book_select_court(
        location_name=location.name if location else None,
        maps_link=location.maps_link if location else None,
    )

    keyboard = []
    for court in courts:
        keyboard.append([InlineKeyboardButton(f'🎾 {court.name}', callback_data=f'select_court_{court.id}')])

    if location:
        keyboard.append([InlineKeyboardButton(msgs.btn_select_other_location, callback_data='book_court')])
    keyboard.append([InlineKeyboardButton(msgs.btn_back_to_main_menu, callback_data='main_menu')])
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.callback_query.edit_message_text(
        text, reply_markup=reply_markup, parse_mode='HTML', disable_web_page_preview=True
    )
