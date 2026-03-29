import logging

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from bot.handlers.base import TextInputHandler
from localization import get_messages

logger = logging.getLogger(__name__)


class AdminTrainerNameInput(TextInputHandler):
    async def _authorize(self) -> bool:
        return True

    async def _process(self) -> None:
        assert self._update.message is not None
        assert self._context.user_data is not None
        msgs = get_messages()

        if len(self._text) < 1 or len(self._text) > 100:
            text = msgs.admin_trainer_name_too_long
            keyboard = [
                [InlineKeyboardButton(msgs.btn_retry, callback_data='admin_create_trainer')],
                [InlineKeyboardButton(msgs.btn_cancel, callback_data='admin_trainers')],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await self._update.message.reply_text(text, reply_markup=reply_markup)
            self._context.user_data.pop('admin_state', None)
            return

        self._context.user_data['admin_trainer_name'] = self._text
        self._context.user_data['admin_state'] = 'awaiting_trainer_telegram_id'

        text = msgs.admin_trainer_create_step2(name=self._text)

        keyboard = [[InlineKeyboardButton(msgs.btn_cancel, callback_data='admin_trainers')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await self._update.message.reply_text(text, reply_markup=reply_markup)
