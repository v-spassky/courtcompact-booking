import logging
from datetime import datetime, timedelta

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from bot.deps import Deps
from bot.handlers.base import Handler
from bot.handlers.callback_args import CourtWeekArg

logger = logging.getLogger(__name__)


class ScheduleWeeklyShowCourts(Handler):
    def __init__(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
        deps: Deps,
        start_of_week: datetime,
        location_id: int | None,
    ) -> None:
        super().__init__(update, context, deps)
        self._start_of_week = start_of_week
        self._location_id = location_id

    async def _authorize(self) -> bool:
        return True

    async def _process(self) -> None:
        assert self._update.callback_query is not None
        location = None
        if self._location_id:
            location = self._deps.location_repo.get(self._location_id)
            courts = self._deps.location_repo.get_courts(self._location_id)
        else:
            courts = self._deps.court_repo.get_all()
        week_end = self._start_of_week + timedelta(days=6)
        if not courts:
            await self._update.callback_query.edit_message_text(
                self._messages.schedule_weekly_no_courts(location_name=location.name if location else None),
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                self._messages.btn_select_other_location,
                                callback_data='schedule_weekly',
                            ),
                        ],
                        [InlineKeyboardButton(self._messages.btn_back_to_main_menu, callback_data='main_menu')],
                    ],
                ),
            )
            return
        text = self._messages.schedule_weekly_select_court(
            start=self._start_of_week.strftime('%d.%m'),
            end=week_end.strftime('%d.%m.%Y'),
            location_name=location.name if location else None,
            maps_link=location.maps_link if location else None,
        )
        keyboard = []
        for court in courts:
            court_callback = CourtWeekArg(
                court_id=court.id,
                year=self._start_of_week.year,
                month=self._start_of_week.month,
                day=self._start_of_week.day,
            ).to_callback_data()
            keyboard.append([InlineKeyboardButton(f'🎾 {court.name}', callback_data=court_callback)])
        if location:
            keyboard.append(
                [InlineKeyboardButton(self._messages.btn_select_other_location, callback_data='schedule_weekly')],
            )
        keyboard.append([InlineKeyboardButton(self._messages.btn_back_to_main_menu, callback_data='main_menu')])
        await self._update.callback_query.edit_message_text(
            text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='HTML',
            disable_web_page_preview=True,
        )

    async def _on_error(self, error: Exception) -> None:
        logger.exception('Failed to show court selection for weekly')
        assert self._update.callback_query is not None
        await self._update.callback_query.edit_message_text(self._messages.generic_error)
