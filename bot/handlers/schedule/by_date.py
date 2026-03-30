import logging
from datetime import datetime

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from bot.deps import Deps
from bot.handlers.base import Handler
from bot.handlers.schedule.by_date_courts import ScheduleForDateShowCourts

logger = logging.getLogger(__name__)


class ScheduleForDate(Handler):
    def __init__(self, update: Update, context: ContextTypes.DEFAULT_TYPE, deps: Deps, date: datetime) -> None:
        super().__init__(update, context, deps)
        self._date = date

    async def _authorize(self) -> bool:
        return True

    async def _process(self) -> None:
        assert self._update.callback_query is not None
        locations = self._deps.location_repo.get_all()
        if not locations:
            await ScheduleForDateShowCourts(self._update, self._context, self._deps, self._date, None).handle()
            return
        text = self._messages.schedule_select_location(date=self._date.strftime('%d.%m.%Y'))
        for location in locations:
            if location.maps_link:
                text += f'📍 <a href="{location.maps_link}">{location.name}</a>\n\n'
            else:
                text += f'📍 {location.name}\n\n'
        keyboard = []
        for location in locations:
            loc_callback = f'schedule_location_{location.id}_{self._date.year}_{self._date.month}_{self._date.day}'
            keyboard.append([InlineKeyboardButton(f'📍 {location.name}', callback_data=loc_callback)])
        keyboard.append([InlineKeyboardButton(self._messages.btn_back_to_main_menu, callback_data='main_menu')])
        await self._update.callback_query.edit_message_text(
            text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='HTML',
            disable_web_page_preview=True,
        )

    async def _on_error(self, error: Exception) -> None:
        logger.exception('Failed to show location selection')
        assert self._update.callback_query is not None
        await self._update.callback_query.edit_message_text(self._messages.generic_error)
