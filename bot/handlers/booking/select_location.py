import logging

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from bot.handlers.base import Handler
from bot.handlers.booking.select_court import BookCourt
from localization import get_messages

logger = logging.getLogger(__name__)


class BookCourtSelectLocation(Handler):
    async def _authorize(self) -> bool:
        return True

    async def _process(self) -> None:
        assert self._update.callback_query is not None
        msgs = get_messages()

        locations = self._deps.location_repo.get_all()

        if not locations:
            await BookCourt(self._update, self._context, self._deps, None).handle()
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

        await self._update.callback_query.edit_message_text(
            text, reply_markup=reply_markup, parse_mode='HTML', disable_web_page_preview=True
        )
