import logging

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from bot.deps import Deps
from bot.handlers.base import Handler
from bot.handlers.booking._utils import _create_booking_calendar
from config.settings import now_kiev
from localization import get_messages

logger = logging.getLogger(__name__)


class TrainerSelectionForBooking(Handler):
    def __init__(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE, deps: Deps, callback_data: str, user_id: int
    ) -> None:
        super().__init__(update, context, deps)
        self._callback_data = callback_data
        self._user_id = user_id

    async def _authorize(self) -> bool:
        return True

    async def _process(self) -> None:
        assert self._update.callback_query is not None
        msgs = get_messages()
        parts = self._callback_data.split('_')
        trainer_id_short = parts[2] if parts[2] != 'none' else None
        court_id_short = parts[3]

        courts = self._deps.court_repo.get_all()
        court_id: str | None = None
        for court in courts:
            if str(court.id).startswith(court_id_short):
                court_id = court.id
                break

        if not court_id:
            raise ValueError(f'Court not found for ID starting with {court_id_short}')

        trainer_id = None
        trainer_name = None
        if trainer_id_short and trainer_id_short != 'none':
            trainers = self._deps.trainer_repo.get_all()
            for trainer in trainers:
                if str(trainer.id).startswith(trainer_id_short):
                    trainer_id = trainer.id
                    trainer_name = trainer.name
                    break

        court_obj = self._deps.court_repo.get(court_id)
        court_name = court_obj.name if court_obj else msgs.unknown_court

        now = now_kiev()
        calendar_markup = _create_booking_calendar(now.year, now.month, court_id, trainer_id, self._deps)

        text = msgs.booking_select_date(court_name=court_name, trainer_name=trainer_name)

        await self._update.callback_query.edit_message_text(text, reply_markup=calendar_markup)

    async def _on_error(self, error: Exception) -> None:
        logger.exception('Failed to show booking calendar')
        msgs = get_messages()
        assert self._update.callback_query is not None
        keyboard = [[InlineKeyboardButton(msgs.btn_back_to_main_menu, callback_data='main_menu')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await self._update.callback_query.edit_message_text(msgs.generic_error, reply_markup=reply_markup)
