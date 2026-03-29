import logging
from datetime import date, timedelta
from typing import Any

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from bot.deps import Deps
from bot.handlers.base import Handler
from config.settings import now_kiev
from localization import get_messages

logger = logging.getLogger(__name__)


class ViewTrainerSchedule(Handler):
    def __init__(self, update: Update, context: ContextTypes.DEFAULT_TYPE, deps: Deps, callback_data: str) -> None:
        super().__init__(update, context, deps)
        self._callback_data = callback_data

    async def _authorize(self) -> bool:
        return True

    async def _process(self) -> None:
        assert self._update.callback_query is not None
        msgs = get_messages()
        trainer_id_short = self._callback_data.split('_')[2]
        trainers = self._deps.trainer_repo.get_all()
        trainer = None
        for t in trainers:
            if str(t.id).startswith(trainer_id_short):
                trainer = t
                break
        if not trainer:
            keyboard = [[InlineKeyboardButton(msgs.btn_back_to_main_menu, callback_data='main_menu')]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await self._update.callback_query.edit_message_text(msgs.generic_error, reply_markup=reply_markup)
            return
        today = now_kiev()
        all_bookings = []
        for i in range(14):
            day = today + timedelta(days=i)
            time_slots = self._deps.schedule_service.get_all_time_slots_for_date(day)
            for slot in time_slots:
                if slot.booking_id:
                    booking = self._deps.booking_repo.get(slot.booking_id)
                    if booking and booking.trainer and str(booking.trainer.id) == str(trainer.id):
                        all_bookings.append(booking)
        text = msgs.trainer_schedule_header(name=trainer.user.name, description=trainer.description)
        if not all_bookings:
            text += msgs.trainer_schedule_no_upcoming
        else:
            text += msgs.trainer_schedule_upcoming_title
            bookings_by_date: dict[date, list[Any]] = {}
            for booking in all_bookings:
                date_key = booking.start_time.date()
                if date_key not in bookings_by_date:
                    bookings_by_date[date_key] = []
                bookings_by_date[date_key].append(booking)
            for date_key in sorted(bookings_by_date.keys()):
                text += f'📆 {date_key.strftime("%d.%m.%Y (%a)")}\n'
                for booking in sorted(bookings_by_date[date_key], key=lambda b: b.start_time):
                    court_name = booking.court.name if booking.court else msgs.unknown_court
                    time_range = f'{booking.start_time.strftime("%H:%M")}-{booking.end_time.strftime("%H:%M")}'
                    text += f'   • {time_range} - {court_name}\n'
                text += '\n'
        keyboard = [
            [InlineKeyboardButton(msgs.btn_back_to_trainers, callback_data='trainer_schedule')],
            [InlineKeyboardButton(msgs.btn_back_to_main_menu, callback_data='main_menu')],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await self._update.callback_query.edit_message_text(text, reply_markup=reply_markup)

    async def _on_error(self, error: Exception) -> None:
        logger.exception('Failed to generate trainer schedule')
        msgs = get_messages()
        assert self._update.callback_query is not None
        await self._update.callback_query.edit_message_text(msgs.trainer_schedule_error)
