import logging
from datetime import datetime, timedelta

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from bot.deps import Deps
from bot.handlers.base import Handler
from localization import get_messages

logger = logging.getLogger(__name__)


class ScheduleWeeklyShowCourts(Handler):
    def __init__(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
        deps: Deps,
        start_of_week: datetime,
        location_id: str | None,
    ) -> None:
        super().__init__(update, context, deps)
        self._start_of_week = start_of_week
        self._location_id = location_id

    async def _authorize(self) -> bool:
        return True

    async def _process(self) -> None:
        assert self._update.callback_query is not None
        msgs = get_messages()

        location = None
        if self._location_id:
            location = self._deps.location_repo.get(self._location_id)
            courts = self._deps.location_repo.get_courts(self._location_id)
        else:
            courts = self._deps.court_repo.get_all()

        week_end = self._start_of_week + timedelta(days=6)

        if not courts:
            text = msgs.schedule_weekly_no_courts(location_name=location.name if location else None)
            keyboard = [
                [InlineKeyboardButton(msgs.btn_select_other_location, callback_data='schedule_weekly')],
                [InlineKeyboardButton(msgs.btn_back_to_main_menu, callback_data='main_menu')],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await self._update.callback_query.edit_message_text(text, reply_markup=reply_markup)
            return

        text = msgs.schedule_weekly_select_court(
            start=self._start_of_week.strftime('%d.%m'),
            end=week_end.strftime('%d.%m.%Y'),
            location_name=location.name if location else None,
            maps_link=location.maps_link if location else None,
        )

        keyboard = []
        for court in courts:
            court_callback = f'court_week_{court.id}_{self._start_of_week.year}_{self._start_of_week.month}_{self._start_of_week.day}'
            keyboard.append([InlineKeyboardButton(f'🎾 {court.name}', callback_data=court_callback)])

        if location:
            keyboard.append([InlineKeyboardButton(msgs.btn_select_other_location, callback_data='schedule_weekly')])
        keyboard.append([InlineKeyboardButton(msgs.btn_back_to_main_menu, callback_data='main_menu')])
        reply_markup = InlineKeyboardMarkup(keyboard)

        await self._update.callback_query.edit_message_text(
            text, reply_markup=reply_markup, parse_mode='HTML', disable_web_page_preview=True
        )

    async def _on_error(self, error: Exception) -> None:
        logger.exception('Failed to show court selection for weekly')
        msgs = get_messages()
        assert self._update.callback_query is not None
        await self._update.callback_query.edit_message_text(msgs.generic_error)
