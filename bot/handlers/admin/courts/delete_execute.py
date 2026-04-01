import logging

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from bot.deps import Deps
from bot.handlers.auth import _is_admin, _log_user_action
from bot.handlers.base import Handler
from bot.handlers.callback_args import AdminConfirmDeleteCourtArg

logger = logging.getLogger(__name__)


class AdminDeleteCourtExecute(Handler):
    def __init__(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
        deps: Deps,
        args: AdminConfirmDeleteCourtArg,
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
        court = self._deps.court_repo.get(self._args.id)
        if not court:
            await self._update.callback_query.edit_message_text(
                self._messages.admin_court_not_found,
                reply_markup=InlineKeyboardMarkup(
                    [[InlineKeyboardButton(self._messages.btn_back, callback_data='admin_courts')]],
                ),
            )
            return
        self._deps.court_repo.delete(court.id)
        _log_user_action(self._update.effective_user, f'deleted court: {court.name}')
        await self._update.callback_query.edit_message_text(
            self._messages.admin_court_deleted(name=court.name),
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton(self._messages.btn_back_to_courts, callback_data='admin_courts')]],
            ),
        )

    async def _on_error(self, error: Exception) -> None:
        logger.exception('Failed to delete court')
        assert self._update.callback_query is not None
        await self._update.callback_query.edit_message_text(
            self._messages.admin_court_delete_error,
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton(self._messages.btn_back_to_courts, callback_data='admin_courts')]],
            ),
        )
