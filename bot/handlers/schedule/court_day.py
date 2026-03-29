import logging
from datetime import datetime
from uuid import UUID

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from bot.deps import Deps
from bot.handlers.base import Handler
from config.settings import now_kiev
from localization import get_messages

logger = logging.getLogger(__name__)


class CourtScheduleForDay(Handler):
    def __init__(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE, deps: Deps, court_id: UUID, date: datetime
    ) -> None:
        super().__init__(update, context, deps)
        self._court_id = court_id
        self._date = date

    async def _authorize(self) -> bool:
        return True

    async def _process(self) -> None:
        assert self._update.callback_query is not None
        msgs = get_messages()

        time_slots = self._deps.schedule_service.get_all_time_slots_for_date(self._date)
        court = self._deps.court_repo.get(self._court_id)
        court_name = court.name if court else msgs.unknown_court

        court_slots = [
            slot
            for slot in time_slots
            if slot.court_id == self._court_id and slot.start_time.date() == self._date.date()
        ]

        location = court.location if court else None

        text = msgs.schedule_court_day(
            court_name=court_name,
            date=self._date.strftime('%d.%m.%Y'),
            location_name=location.name if location else None,
            maps_link=location.maps_link if location else None,
        )

        now = now_kiev()
        future_slots = [s for s in court_slots if s.start_time >= now]

        if not future_slots:
            text += msgs.schedule_no_slots
        else:
            available_count = sum(1 for s in future_slots if s.is_available)
            total_count = len(future_slots)
            text += msgs.schedule_slots_summary(available=available_count, total=total_count)

            has_slots = False
            for slot in sorted(future_slots, key=lambda s: s.start_time):
                has_slots = True
                time_range = f'{slot.start_time.strftime("%H:%M")}-{slot.end_time.strftime("%H:%M")}'
                if slot.is_available:
                    text += f'✅ {time_range}\n'
                else:
                    booking_info = time_range
                    if slot.booking_id:
                        booking = self._deps.booking_repo.get(slot.booking_id)
                        if booking:
                            if booking.student:
                                booking_info += f' ({booking.student.name})'
                            if booking.trainer:
                                booking_info += f' 👨‍🏫 {booking.trainer.name}'
                    text += f'❌ {booking_info}\n'

            if not has_slots:
                text += msgs.schedule_no_slots_for_day

        keyboard = [[InlineKeyboardButton(msgs.btn_back_to_main_menu, callback_data='main_menu')]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await self._update.callback_query.edit_message_text(
            text, reply_markup=reply_markup, parse_mode='HTML', disable_web_page_preview=True
        )

    async def _on_error(self, error: Exception) -> None:
        logger.exception('Failed to generate court schedule')
        msgs = get_messages()
        assert self._update.callback_query is not None
        await self._update.callback_query.edit_message_text(msgs.schedule_court_error)
