import logging

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from bot.handlers.admin._utils import _clear_admin_state
from bot.handlers.auth import _is_admin
from bot.handlers.base import Handler
from bot.handlers.callback_args import AdminCourtLocationArg

logger = logging.getLogger(__name__)


class AdminCreateCourtSelectLocation(Handler):
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
                self._messages.admin_court_no_locations,
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                self._messages.btn_create_location,
                                callback_data='admin_create_location',
                            ),
                        ],
                        [InlineKeyboardButton(self._messages.btn_back, callback_data='admin_courts')],
                    ],
                ),
            )
            return
        keyboard = []
        for location in locations:
            button_text = f'📍 {location.name}'
            if location.maps_link:
                button_text += ' 🗺️'
            keyboard.append(
                [
                    InlineKeyboardButton(
                        button_text,
                        callback_data=AdminCourtLocationArg(id=location.id).to_callback_data(),
                    ),
                ],
            )
        keyboard.append([InlineKeyboardButton(self._messages.btn_cancel, callback_data='admin_courts')])
        await self._update.callback_query.edit_message_text(
            self._messages.admin_court_select_location,
            reply_markup=InlineKeyboardMarkup(keyboard),
        )
