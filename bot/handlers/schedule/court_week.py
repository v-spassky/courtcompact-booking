import logging
from datetime import date, datetime, timedelta
from typing import Any

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from bot.deps import Deps
from bot.handlers.base import Handler
from config.settings import now_kiev
from localization import get_messages

logger = logging.getLogger(__name__)


class CourtScheduleForWeek(Handler):
    def __init__(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE, deps: Deps, court_id: str, start_of_week: datetime
    ) -> None:
        super().__init__(update, context, deps)
        self._court_id = court_id
        self._start_of_week = start_of_week

    async def _authorize(self) -> bool:
        return True

    async def _process(self) -> None:
        assert self._update.callback_query is not None
        msgs = get_messages()

        court = self._deps.court_repo.get(self._court_id)
        court_name = court.name if court else msgs.unknown_court

        all_slots = []
        for i in range(7):
            day = self._start_of_week + timedelta(days=i)
            day_slots = self._deps.schedule_service.get_all_time_slots_for_date(day)
            court_day_slots = [s for s in day_slots if str(s.court_id) == self._court_id]
            all_slots.extend(court_day_slots)

        week_end = self._start_of_week + timedelta(days=6)

        location = court.location if court else None

        text = msgs.schedule_weekly_court(
            court_name=court_name,
            start=self._start_of_week.strftime('%d.%m'),
            end=week_end.strftime('%d.%m.%Y'),
            location_name=location.name if location else None,
            maps_link=location.maps_link if location else None,
        )

        now = now_kiev()
        slots_by_day: dict[date, list[Any]] = {}
        for i in range(7):
            day = self._start_of_week + timedelta(days=i)
            slots_by_day[day.date()] = []

        for slot in all_slots:
            if slot.start_time < now:
                continue
            slot_date = slot.start_time.date()
            if slot_date in slots_by_day:
                slots_by_day[slot_date].append(slot)

        for i in range(7):
            day = self._start_of_week + timedelta(days=i)
            day_date = day.date()
            day_slots = slots_by_day.get(day_date, [])

            day_name = msgs.day_names[day.weekday()]

            if not day_slots:
                text += msgs.schedule_weekly_day_row(
                    day_name=day_name,
                    date=day.strftime('%d.%m'),
                    available=0,
                    total=0,
                    trainer_count=0,
                )
            else:
                available_count = sum(1 for s in day_slots if s.is_available)
                total_count = len(day_slots)

                trainer_count = 0
                for slot in day_slots:
                    if not slot.is_available and slot.booking_id:
                        booking = self._deps.booking_repo.get(slot.booking_id)
                        if booking and booking.trainer:
                            trainer_count += 1

                text += msgs.schedule_weekly_day_row(
                    day_name=day_name,
                    date=day.strftime('%d.%m'),
                    available=available_count,
                    total=total_count,
                    trainer_count=trainer_count,
                )

        keyboard = [[InlineKeyboardButton(msgs.btn_back_to_main_menu, callback_data='main_menu')]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await self._update.callback_query.edit_message_text(
            text, reply_markup=reply_markup, parse_mode='HTML', disable_web_page_preview=True
        )

    async def _on_error(self, error: Exception) -> None:
        logger.exception('Failed to generate court weekly schedule')
        msgs = get_messages()
        assert self._update.callback_query is not None
        await self._update.callback_query.edit_message_text(msgs.schedule_weekly_error)
