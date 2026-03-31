from telegram import KeyboardButton, Message, ReplyKeyboardMarkup

from bot.handlers.base import Handler


class ShowAuthorizationRequest(Handler):
    async def _authorize(self) -> bool:
        return True

    async def _process(self) -> None:
        keyboard = [[KeyboardButton(self._messages.btn_share_phone, request_contact=True)]]
        markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
        if self._update.message:
            await self._update.message.reply_text(self._messages.auth_request, reply_markup=markup)
        elif self._update.callback_query:
            msg = self._update.callback_query.message
            if isinstance(msg, Message):
                await msg.reply_text(self._messages.auth_request, reply_markup=markup)
