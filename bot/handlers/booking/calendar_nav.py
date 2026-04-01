import logging

from telegram import Update
from telegram.ext import ContextTypes

from bot.deps import Deps
from bot.handlers.base import Handler
from bot.handlers.booking._utils import _create_booking_calendar
from bot.handlers.callback_args import BookCalArg

logger = logging.getLogger(__name__)


class BookingCalendarNavigation(Handler):
    def __init__(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
        deps: Deps,
        args: BookCalArg,
    ) -> None:
        super().__init__(update, context, deps)
        self._args = args

    async def _authorize(self) -> bool:
        return True

    async def _process(self) -> None:
        assert self._update.callback_query is not None
        court = self._deps.court_repo.get(self._args.court_id)
        if not court:
            raise ValueError(f'Court not found with ID {self._args.court_id}')
        trainer_name = None
        if self._args.trainer_id is not None:
            trainer = self._deps.trainer_repo.get(self._args.trainer_id)
            if trainer:
                trainer_name = trainer.user.name
        calendar_markup = _create_booking_calendar(
            self._args.year,
            self._args.month,
            self._args.court_id,
            self._args.trainer_id,
            self._deps,
        )
        text = self._messages.booking_select_date(court_name=court.name, trainer_name=trainer_name)
        await self._update.callback_query.edit_message_text(text, reply_markup=calendar_markup)

    async def _on_error(self, error: Exception) -> None:
        logger.exception('Failed to navigate booking calendar')
        assert self._update.callback_query is not None
        await self._update.callback_query.edit_message_text(self._messages.generic_error)
