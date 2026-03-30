import logging

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from bot.handlers.admin._utils import _clear_admin_state
from bot.handlers.auth import _is_admin
from bot.handlers.base import Handler
from localization import get_messages

logger = logging.getLogger(__name__)


class AdminDeleteLocationList(Handler):
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
        msgs = get_messages()
        _clear_admin_state(self._context)
        locations = self._deps.location_repo.get_all()
        if not locations:
            await self._update.callback_query.edit_message_text(
                msgs.admin_location_no_locations,
                reply_markup=InlineKeyboardMarkup(
                    [[InlineKeyboardButton(msgs.btn_back, callback_data='admin_locations')]],
                ),
            )
            return
        keyboard = []
        for location in locations:
            keyboard.append(
                [InlineKeyboardButton(f'📍 {location.name}', callback_data=f'admin_delete_location_{location.id}')],
            )
        keyboard.append([InlineKeyboardButton(msgs.btn_back, callback_data='admin_locations')])
        await self._update.callback_query.edit_message_text(
            msgs.admin_location_select_to_delete,
            reply_markup=InlineKeyboardMarkup(keyboard),
        )
