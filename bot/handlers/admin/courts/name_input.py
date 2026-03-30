import logging

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from bot.handlers.base import TextInputHandler

logger = logging.getLogger(__name__)


class AdminCourtNameInput(TextInputHandler):
    async def _authorize(self) -> bool:
        return True

    async def _process(self) -> None:
        assert self._update.message is not None
        assert self._context.user_data is not None
        if len(self._text) < 1 or len(self._text) > 100:
            await self._update.message.reply_text(
                self._messages.admin_court_name_too_long,
                reply_markup=InlineKeyboardMarkup(
                    [
                        [InlineKeyboardButton(self._messages.btn_retry, callback_data='admin_create_court')],
                        [InlineKeyboardButton(self._messages.btn_cancel, callback_data='admin_courts')],
                    ],
                ),
            )
            self._context.user_data.pop('admin_state', None)
            return
        self._context.user_data['admin_court_name'] = self._text
        self._context.user_data['admin_state'] = 'awaiting_court_description'
        location_id = self._context.user_data.get('admin_court_location_id')
        location_name = self._messages.not_specified
        if location_id:
            location = self._deps.location_repo.get(int(location_id))
            if location:
                location_name = location.name
        await self._update.message.reply_text(
            self._messages.admin_court_create_step3(location_name=location_name, court_name=self._text),
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton(self._messages.btn_cancel, callback_data='admin_courts')]],
            ),
        )
