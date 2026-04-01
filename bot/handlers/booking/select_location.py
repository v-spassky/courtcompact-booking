import logging

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from bot.handlers.base import Handler
from bot.handlers.booking.select_court import BookCourt
from bot.handlers.callback_args import BookLocationArg

logger = logging.getLogger(__name__)


class BookCourtSelectLocation(Handler):
    async def _authorize(self) -> bool:
        return True

    async def _process(self) -> None:
        assert self._update.callback_query is not None
        locations = self._deps.location_repo.get_all()
        if not locations:
            await BookCourt(self._update, self._context, self._deps, None).handle()
            return
        text = self._messages.book_select_location
        for location in locations:
            if location.maps_link:
                text += f'📍 <a href="{location.maps_link}">{location.name}</a>\n\n'
            else:
                text += f'📍 {location.name}\n\n'
        keyboard = []
        for location in locations:
            button_text = f'📍 {location.name}'
            keyboard.append(
                [
                    InlineKeyboardButton(
                        button_text,
                        callback_data=BookLocationArg(location_id=location.id).to_callback_data(),
                    ),
                ],
            )
        keyboard.append([InlineKeyboardButton(self._messages.btn_back_to_main_menu, callback_data='main_menu')])
        await self._update.callback_query.edit_message_text(
            text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='HTML',
            disable_web_page_preview=True,
        )
