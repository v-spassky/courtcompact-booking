import logging

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from bot.handlers.admin._utils import _clear_admin_state
from bot.handlers.base import TextInputHandler

logger = logging.getLogger(__name__)


class AdminEditLocationNameInput(TextInputHandler):
    async def _authorize(self) -> bool:
        return True

    async def _process(self) -> None:
        assert self._update.message is not None
        assert self._context.user_data is not None
        location_id = self._context.user_data.get('admin_location_id')
        if not location_id:
            _clear_admin_state(self._context)
            return
        location = self._deps.location_repo.get(int(location_id))
        if not location:
            _clear_admin_state(self._context)
            return
        if self._text.strip() != '-':
            if len(self._text) < 1 or len(self._text) > 100:
                await self._update.message.reply_text(
                    self._messages.admin_location_name_too_long_edit,
                    reply_markup=InlineKeyboardMarkup(
                        [[InlineKeyboardButton(self._messages.btn_cancel, callback_data='admin_locations')]],
                    ),
                )
                return
            self._context.user_data['admin_location_name'] = self._text.strip()
        else:
            self._context.user_data['admin_location_name'] = location.name
        self._context.user_data['admin_state'] = 'awaiting_edit_location_maps_link'
        await self._update.message.reply_text(
            self._messages.admin_location_edit_step2(
                new_name=self._context.user_data['admin_location_name'],
                maps_link=location.maps_link,
            ),
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton(self._messages.btn_cancel, callback_data='admin_locations')]],
            ),
        )
