import logging

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from bot.deps import Deps
from bot.handlers.base import Handler
from bot.handlers.booking._utils import _create_booking_calendar
from bot.handlers.callback_args import SelectCourtArg, SelectTrainerArg
from config.settings import now_kiev

logger = logging.getLogger(__name__)


class CourtSelectionForBooking(Handler):
    def __init__(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
        deps: Deps,
        args: SelectCourtArg,
        user_id: int,
    ) -> None:
        super().__init__(update, context, deps)
        self._args = args
        self._user_id = user_id

    async def _authorize(self) -> bool:
        return True

    async def _process(self) -> None:
        assert self._update.callback_query is not None
        court = self._deps.court_repo.get(self._args.court_id)
        court_name = court.name if court else self._messages.unknown_court
        user_trainer = self._deps.trainer_repo.get_by_telegram_id(self._user_id)
        if user_trainer:
            now = now_kiev()
            calendar_markup = _create_booking_calendar(
                now.year,
                now.month,
                self._args.court_id,
                user_trainer.id,
                self._deps,
            )
            text = self._messages.booking_select_date(court_name=court_name, trainer_name=user_trainer.user.name)
            await self._update.callback_query.edit_message_text(text, reply_markup=calendar_markup)
            return
        trainers = self._deps.trainer_repo.get_all()
        keyboard = []
        keyboard.append(
            [
                InlineKeyboardButton(
                    self._messages.btn_no_trainer,
                    callback_data=SelectTrainerArg(trainer_id=None, court_id=self._args.court_id).to_callback_data(),
                ),
            ],
        )
        for trainer in trainers:
            button_text = f'👨‍🏫 {trainer.user.name}'
            keyboard.append(
                [
                    InlineKeyboardButton(
                        button_text,
                        callback_data=SelectTrainerArg(
                            trainer_id=trainer.id,
                            court_id=self._args.court_id,
                        ).to_callback_data(),
                    ),
                ],
            )
        keyboard.append([InlineKeyboardButton(self._messages.btn_back_to_main_menu, callback_data='main_menu')])
        await self._update.callback_query.edit_message_text(
            self._messages.booking_select_trainer(court_name=court_name),
            reply_markup=InlineKeyboardMarkup(keyboard),
        )

    async def _on_error(self, error: Exception) -> None:
        logger.exception('Failed to show trainer selection')
        assert self._update.callback_query is not None
        await self._update.callback_query.edit_message_text(self._messages.generic_error)
