import logging

from telegram import Update
from telegram.ext import ContextTypes

from bot.deps import Deps
from bot.handlers.base import Handler
from bot.handlers.booking._utils import _create_booking_calendar
from localization import get_messages

logger = logging.getLogger(__name__)


class BookingCalendarNavigation(Handler):
    def __init__(self, update: Update, context: ContextTypes.DEFAULT_TYPE, deps: Deps, callback_data: str) -> None:
        super().__init__(update, context, deps)
        self._callback_data = callback_data

    async def _authorize(self) -> bool:
        return True

    async def _process(self) -> None:
        assert self._update.callback_query is not None
        msgs = get_messages()
        parts = self._callback_data.split('_')
        court_id = int(parts[2])
        trainer_id_str = parts[3]
        year = int(parts[4])
        month = int(parts[5])
        trainer_id = int(trainer_id_str) if trainer_id_str != 'none' else None
        court = self._deps.court_repo.get(court_id)
        if not court:
            raise ValueError(f'Court not found with ID {court_id}')
        trainer_name = None
        if trainer_id is not None:
            trainer = self._deps.trainer_repo.get(trainer_id)
            if trainer:
                trainer_name = trainer.user.name
        calendar_markup = _create_booking_calendar(year, month, court_id, trainer_id, self._deps)
        text = msgs.booking_select_date(court_name=court.name, trainer_name=trainer_name)
        await self._update.callback_query.edit_message_text(text, reply_markup=calendar_markup)

    async def _on_error(self, error: Exception) -> None:
        logger.exception('Failed to navigate booking calendar')
        msgs = get_messages()
        assert self._update.callback_query is not None
        await self._update.callback_query.edit_message_text(msgs.generic_error)
