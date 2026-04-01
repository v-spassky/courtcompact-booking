import logging

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from bot.handlers.admin._utils import _clear_admin_state
from bot.handlers.auth import _is_admin
from bot.handlers.base import Handler
from bot.handlers.callback_args import AdminDeleteLocationArg

logger = logging.getLogger(__name__)


class AdminDeleteLocationList(Handler):
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
        locations = self._deps.location_repo.get_all()
        if not locations:
            await self._update.callback_query.edit_message_text(
                self._messages.admin_location_no_locations,
                reply_markup=InlineKeyboardMarkup(
                    [[InlineKeyboardButton(self._messages.btn_back, callback_data='admin_locations')]],
                ),
            )
            return
        keyboard = []
        for location in locations:
            keyboard.append(
                [
                    InlineKeyboardButton(
                        f'📍 {location.name}',
                        callback_data=AdminDeleteLocationArg(id=location.id).to_callback_data(),
                    ),
                ],
            )
        keyboard.append([InlineKeyboardButton(self._messages.btn_back, callback_data='admin_locations')])
        await self._update.callback_query.edit_message_text(
            self._messages.admin_location_select_to_delete,
            reply_markup=InlineKeyboardMarkup(keyboard),
        )
