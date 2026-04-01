import logging
from datetime import timedelta

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from bot.handlers.base import Handler
from bot.handlers.callback_args import WeeklyLocationArg
from bot.handlers.schedule.weekly_courts import ScheduleWeeklyShowCourts
from config.settings import now_kiev

logger = logging.getLogger(__name__)


class ScheduleWeekly(Handler):
    async def _authorize(self) -> bool:
        return True

    async def _process(self) -> None:
        assert self._update.callback_query is not None
        locations = self._deps.location_repo.get_all()
        today = now_kiev()
        start_date = today
        end_date = start_date + timedelta(days=6)
        if not locations:
            await ScheduleWeeklyShowCourts(self._update, self._context, self._deps, start_date, None).handle()
            return
        text = self._messages.schedule_weekly_select_location(
            start=start_date.strftime('%d.%m'),
            end=end_date.strftime('%d.%m.%Y'),
        )
        for location in locations:
            if location.maps_link:
                text += f'📍 <a href="{location.maps_link}">{location.name}</a>\n\n'
            else:
                text += f'📍 {location.name}\n\n'
        keyboard = []
        for location in locations:
            loc_callback = WeeklyLocationArg(
                location_id=location.id,
                year=start_date.year,
                month=start_date.month,
                day=start_date.day,
            ).to_callback_data()
            keyboard.append([InlineKeyboardButton(f'📍 {location.name}', callback_data=loc_callback)])
        keyboard.append([InlineKeyboardButton(self._messages.btn_back_to_main_menu, callback_data='main_menu')])
        await self._update.callback_query.edit_message_text(
            text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='HTML',
            disable_web_page_preview=True,
        )

    async def _on_error(self, error: Exception) -> None:
        logger.exception('Failed to show location selection for weekly')
        assert self._update.callback_query is not None
        await self._update.callback_query.edit_message_text(self._messages.generic_error)
