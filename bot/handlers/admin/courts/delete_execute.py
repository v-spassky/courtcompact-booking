import logging

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from bot.deps import Deps
from bot.handlers.auth import _is_admin, _log_user_action
from bot.handlers.base import Handler
from localization import get_messages

logger = logging.getLogger(__name__)


class AdminDeleteCourtExecute(Handler):
    def __init__(self, update: Update, context: ContextTypes.DEFAULT_TYPE, deps: Deps, callback_data: str) -> None:
        super().__init__(update, context, deps)
        self._callback_data = callback_data

    async def _authorize(self) -> bool:
        assert self._update.callback_query is not None
        assert self._update.effective_user is not None
        msgs = get_messages()
        if not _is_admin(self._update.effective_user.id, self._deps):
            await self._update.callback_query.edit_message_text(msgs.admin_no_access)
            return False
        return True

    async def _process(self) -> None:
        assert self._update.callback_query is not None
        assert self._update.effective_user is not None
        msgs = get_messages()
        court_id = int(self._callback_data.replace('admin_confirm_delete_court_', ''))
        court = self._deps.court_repo.get(court_id)
        if not court:
            await self._update.callback_query.edit_message_text(
                msgs.admin_court_not_found,
                reply_markup=InlineKeyboardMarkup(
                    [[InlineKeyboardButton(msgs.btn_back, callback_data='admin_courts')]],
                ),
            )
            return
        self._deps.court_repo.delete(court.id)
        _log_user_action(self._update.effective_user, f'deleted court: {court.name}')
        await self._update.callback_query.edit_message_text(
            msgs.admin_court_deleted(name=court.name),
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton(msgs.btn_back_to_courts, callback_data='admin_courts')]],
            ),
        )

    async def _on_error(self, error: Exception) -> None:
        logger.exception('Failed to delete court')
        msgs = get_messages()
        assert self._update.callback_query is not None
        await self._update.callback_query.edit_message_text(
            msgs.admin_court_delete_error,
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton(msgs.btn_back_to_courts, callback_data='admin_courts')]],
            ),
        )
