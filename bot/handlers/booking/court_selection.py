import logging
from uuid import UUID

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from bot.deps import Deps
from bot.handlers.base import Handler
from bot.handlers.booking._utils import _create_booking_calendar
from config.settings import now_kiev
from localization import get_messages

logger = logging.getLogger(__name__)


class CourtSelectionForBooking(Handler):
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
        court_id = UUID(self._callback_data.split('_')[2])
        court = self._deps.court_repo.get(court_id)
        court_name = court.name if court else msgs.unknown_court
        user_trainer = self._deps.trainer_repo.get_by_telegram_id(self._user_id)
        if user_trainer:
            now = now_kiev()
            calendar_markup = _create_booking_calendar(now.year, now.month, court_id, user_trainer.id, self._deps)
            text = msgs.booking_select_date(court_name=court_name, trainer_name=user_trainer.user.name)
            await self._update.callback_query.edit_message_text(text, reply_markup=calendar_markup)
            return
        trainers = self._deps.trainer_repo.get_all()
        keyboard = []
        keyboard.append(
            [InlineKeyboardButton(msgs.btn_no_trainer, callback_data=f'select_trainer_none_{str(court_id)[:8]}')]
        )
        for trainer in trainers:
            button_text = f'👨‍🏫 {trainer.user.name}'
            keyboard.append(
                [
                    InlineKeyboardButton(
                        button_text, callback_data=f'select_trainer_{str(trainer.id)[:8]}_{str(court_id)[:8]}'
                    )
                ]
            )
        keyboard.append([InlineKeyboardButton(msgs.btn_back_to_main_menu, callback_data='main_menu')])
        reply_markup = InlineKeyboardMarkup(keyboard)
        await self._update.callback_query.edit_message_text(
            msgs.booking_select_trainer(court_name=court_name), reply_markup=reply_markup
        )

    async def _on_error(self, error: Exception) -> None:
        logger.exception('Failed to show trainer selection')
        msgs = get_messages()
        assert self._update.callback_query is not None
        await self._update.callback_query.edit_message_text(msgs.generic_error)
