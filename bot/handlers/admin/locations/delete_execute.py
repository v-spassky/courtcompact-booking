import logging

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from bot.deps import Deps
from bot.handlers.auth import _is_admin, _log_user_action
from bot.handlers.base import Handler
from bot.handlers.callback_args import AdminConfirmDeleteLocationArg

logger = logging.getLogger(__name__)


class AdminDeleteLocationExecute(Handler):
    def __init__(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
        deps: Deps,
        args: AdminConfirmDeleteLocationArg,
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
        location = self._deps.location_repo.get(self._args.id)
        if not location:
            await self._update.callback_query.edit_message_text(
                self._messages.admin_location_not_found,
                reply_markup=InlineKeyboardMarkup(
                    [[InlineKeyboardButton(self._messages.btn_back, callback_data='admin_locations')]],
                ),
            )
            return
        self._deps.location_repo.delete(location.id)
        _log_user_action(self._update.effective_user, f'deleted location: {location.name}')
        await self._update.callback_query.edit_message_text(
            self._messages.admin_location_deleted(name=location.name),
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton(self._messages.btn_back_to_locations, callback_data='admin_locations')]],
            ),
        )

    async def _on_error(self, error: Exception) -> None:
        logger.exception('Failed to delete location')
        assert self._update.callback_query is not None
        await self._update.callback_query.edit_message_text(
            self._messages.admin_location_delete_error,
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton(self._messages.btn_back_to_locations, callback_data='admin_locations')]],
            ),
        )
