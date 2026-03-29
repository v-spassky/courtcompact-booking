import logging

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from bot.handlers.base import TextInputHandler
from localization import get_messages

logger = logging.getLogger(__name__)


class AdminLocationNameInput(TextInputHandler):
    async def _authorize(self) -> bool:
        return True

    async def _process(self) -> None:
        assert self._update.message is not None
        assert self._context.user_data is not None
        msgs = get_messages()
        if len(self._text) < 1 or len(self._text) > 100:
            text = msgs.admin_location_name_too_long
            keyboard = [
                [InlineKeyboardButton(msgs.btn_retry, callback_data='admin_create_location')],
                [InlineKeyboardButton(msgs.btn_cancel, callback_data='admin_locations')],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await self._update.message.reply_text(text, reply_markup=reply_markup)
            self._context.user_data.pop('admin_state', None)
            return
        self._context.user_data['admin_location_name'] = self._text
        self._context.user_data['admin_state'] = 'awaiting_location_maps_link'
        text = msgs.admin_location_create_step2(name=self._text)
        keyboard = [[InlineKeyboardButton(msgs.btn_cancel, callback_data='admin_locations')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await self._update.message.reply_text(text, reply_markup=reply_markup)
