import logging

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from bot.deps import Deps
from bot.handlers.auth import _is_admin, _log_user_action
from bot.handlers.base import Handler
from bot.handlers.callback_args import AdminConfirmDeleteTrainerArg

logger = logging.getLogger(__name__)


class AdminDeleteTrainerExecute(Handler):
    def __init__(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
        deps: Deps,
        args: AdminConfirmDeleteTrainerArg,
    ) -> None:
        super().__init__(update, context, deps)
        self._args = args

    async def _authorize(self) -> bool:
        assert self._update.callback_query is not None
        assert self._update.effective_user is not None
        if not _is_admin(self._update.effective_user.id, self._deps):
            await self._update.callback_query.edit_message_text(self._messages.admin_no_access)
            return False
        return True

    async def _process(self) -> None:
        assert self._update.callback_query is not None
        assert self._update.effective_user is not None
        trainer = self._deps.trainer_repo.get(self._args.id)
        if not trainer:
            await self._update.callback_query.edit_message_text(
                self._messages.admin_trainer_not_found,
                reply_markup=InlineKeyboardMarkup(
                    [[InlineKeyboardButton(self._messages.btn_back, callback_data='admin_trainers')]],
                ),
            )
            return
        self._deps.trainer_repo.delete(trainer.id)
        _log_user_action(self._update.effective_user, f'deleted trainer: {trainer.user.name}')
        await self._update.callback_query.edit_message_text(
            self._messages.admin_trainer_deleted(name=trainer.user.name),
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton(self._messages.btn_back_to_trainers_list, callback_data='admin_trainers')]],
            ),
        )

    async def _on_error(self, error: Exception) -> None:
        logger.exception('Failed to delete trainer')
        assert self._update.callback_query is not None
        await self._update.callback_query.edit_message_text(
            self._messages.admin_trainer_delete_error,
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton(self._messages.btn_back_to_trainers_list, callback_data='admin_trainers')]],
            ),
        )
