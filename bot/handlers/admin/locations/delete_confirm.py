import logging

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from bot.deps import Deps
from bot.handlers.auth import _is_admin
from bot.handlers.base import Handler

logger = logging.getLogger(__name__)


class AdminDeleteLocationConfirm(Handler):
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
        location_id = int(self._callback_data.replace('admin_delete_location_', ''))
        location = self._deps.location_repo.get(location_id)
        if not location:
            await self._update.callback_query.edit_message_text(
                self._messages.admin_location_not_found,
                reply_markup=InlineKeyboardMarkup(
                    [[InlineKeyboardButton(self._messages.btn_back, callback_data='admin_locations')]],
                ),
            )
            return
        courts = self._deps.location_repo.get_courts(location.id)
        text = self._messages.admin_location_confirm_delete(name=location.name)
        if courts:
            text += self._messages.admin_location_courts_warning(count=len(courts))
        await self._update.callback_query.edit_message_text(
            text,
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            self._messages.btn_confirm_delete,
                            callback_data=f'admin_confirm_delete_location_{location.id}',
                        ),
                    ],
                    [InlineKeyboardButton(self._messages.btn_cancel, callback_data='admin_locations')],
                ],
            ),
        )
