import logging

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from bot.deps import Deps
from bot.handlers.base import Handler
from localization import get_messages

logger = logging.getLogger(__name__)


class BookCourt(Handler):
    def __init__(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
        deps: Deps,
        callback_data: str | None = None,
    ) -> None:
        super().__init__(update, context, deps)
        self._callback_data = callback_data

    async def _authorize(self) -> bool:
        return True

    async def _process(self) -> None:
        assert self._update.callback_query is not None
        msgs = get_messages()
        location = None
        courts = []
        if self._callback_data and self._callback_data.startswith('book_location_'):
            location_id_short = self._callback_data.replace('book_location_', '')
            locations = self._deps.location_repo.get_all()
            for loc in locations:
                if str(loc.id).startswith(location_id_short):
                    location = loc
                    break
            if location:
                courts = self._deps.location_repo.get_courts(location.id)
        else:
            courts = self._deps.court_repo.get_all()
        if not courts:
            text = msgs.book_no_courts(location_name=location.name if location else None)
            keyboard = [
                [InlineKeyboardButton(msgs.btn_select_other_location, callback_data='book_court')],
                [InlineKeyboardButton(msgs.btn_back_to_main_menu, callback_data='main_menu')],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await self._update.callback_query.edit_message_text(text, reply_markup=reply_markup)
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
        await self._update.callback_query.edit_message_text(
            text, reply_markup=reply_markup, parse_mode='HTML', disable_web_page_preview=True
        )
