import logging

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from bot.deps import Deps
from bot.handlers.auth import _is_admin
from bot.handlers.base import Handler

logger = logging.getLogger(__name__)


class AdminDeleteCourtConfirm(Handler):
    def __init__(self, update: Update, context: ContextTypes.DEFAULT_TYPE, deps: Deps, callback_data: str) -> None:
        super().__init__(update, context, deps)
        self._callback_data = callback_data

    async def _authorize(self) -> bool:
        assert self._update.callback_query is not None
        assert self._update.effective_user is not None
        if not _is_admin(self._update.effective_user.id, self._deps):
            await self._update.callback_query.edit_message_text(self._messages.admin_no_access)
            return False
        return True

    async def _process(self) -> None:
        assert self._update.callback_query is not None
        court_id = int(self._callback_data.replace('admin_delete_court_', ''))
        court = self._deps.court_repo.get(court_id)
        if not court:
            await self._update.callback_query.edit_message_text(
                self._messages.admin_court_not_found,
                reply_markup=InlineKeyboardMarkup(
                    [[InlineKeyboardButton(self._messages.btn_back, callback_data='admin_courts')]],
                ),
            )
            return
        await self._update.callback_query.edit_message_text(
            self._messages.admin_court_confirm_delete(name=court.name),
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            self._messages.btn_confirm_delete,
                            callback_data=f'admin_confirm_delete_court_{court.id}',
                        ),
                    ],
                    [InlineKeyboardButton(self._messages.btn_cancel, callback_data='admin_courts')],
                ],
            ),
        )
