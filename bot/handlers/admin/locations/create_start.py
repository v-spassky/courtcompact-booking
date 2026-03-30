import logging

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from bot.handlers.admin._utils import _clear_admin_state
from bot.handlers.auth import _is_admin
from bot.handlers.base import Handler

logger = logging.getLogger(__name__)


class AdminCreateLocationStart(Handler):
    async def _authorize(self) -> bool:
        assert self._update.callback_query is not None
        assert self._update.effective_user is not None
        if not _is_admin(self._update.effective_user.id, self._deps):
            await self._update.callback_query.edit_message_text(self._messages.admin_no_access)
            return False
        return True

    async def _process(self) -> None:
        assert self._update.callback_query is not None
        _clear_admin_state(self._context)
        assert self._context.user_data is not None
        self._context.user_data['admin_state'] = 'awaiting_location_name'
        await self._update.callback_query.edit_message_text(
            self._messages.admin_location_create_step1(),
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton(self._messages.btn_cancel, callback_data='admin_locations')]],
            ),
        )
