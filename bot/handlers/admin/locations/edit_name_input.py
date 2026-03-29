import logging

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from bot.handlers.admin._utils import _clear_admin_state
from bot.handlers.base import TextInputHandler
from localization import get_messages

logger = logging.getLogger(__name__)


class AdminEditLocationNameInput(TextInputHandler):
    async def _authorize(self) -> bool:
        return True

    async def _process(self) -> None:
        assert self._update.message is not None
        assert self._context.user_data is not None
        msgs = get_messages()
        location_id = self._context.user_data.get('admin_location_id')
        if not location_id:
            _clear_admin_state(self._context)
            return

        location = self._deps.location_repo.get(location_id)
        if not location:
            _clear_admin_state(self._context)
            return

        if self._text.strip() != '-':
            if len(self._text) < 1 or len(self._text) > 100:
                text = msgs.admin_location_name_too_long_edit
                keyboard = [[InlineKeyboardButton(msgs.btn_cancel, callback_data='admin_locations')]]
                reply_markup = InlineKeyboardMarkup(keyboard)
                await self._update.message.reply_text(text, reply_markup=reply_markup)
                return
            self._context.user_data['admin_location_name'] = self._text.strip()
        else:
            self._context.user_data['admin_location_name'] = location.name

        self._context.user_data['admin_state'] = 'awaiting_edit_location_maps_link'

        new_name = self._context.user_data['admin_location_name']
        text = msgs.admin_location_edit_step2(new_name=new_name, maps_link=location.maps_link)

        keyboard = [[InlineKeyboardButton(msgs.btn_cancel, callback_data='admin_locations')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await self._update.message.reply_text(text, reply_markup=reply_markup)
