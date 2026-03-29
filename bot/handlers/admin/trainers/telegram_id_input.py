import logging

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from bot.handlers.base import TextInputHandler
from localization import get_messages

logger = logging.getLogger(__name__)


class AdminTrainerTelegramIdInput(TextInputHandler):
    async def _authorize(self) -> bool:
        return True

    async def _process(self) -> None:
        assert self._update.message is not None
        assert self._context.user_data is not None
        msgs = get_messages()
        trainer_name = self._context.user_data.get('admin_trainer_name', 'Unknown')

        try:
            telegram_id = int(self._text.strip())
        except ValueError:
            text = msgs.admin_trainer_id_not_a_number
            keyboard = [
                [InlineKeyboardButton(msgs.btn_retry, callback_data='admin_create_trainer')],
                [InlineKeyboardButton(msgs.btn_cancel, callback_data='admin_trainers')],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await self._update.message.reply_text(text, reply_markup=reply_markup)
            self._context.user_data.pop('admin_state', None)
            return

        existing = self._deps.trainer_repo.get_by_telegram_id(telegram_id)
        if existing:
            text = msgs.admin_trainer_id_exists(telegram_id=telegram_id, name=existing.user.name)
            keyboard = [
                [InlineKeyboardButton(msgs.btn_retry, callback_data='admin_create_trainer')],
                [InlineKeyboardButton(msgs.btn_back_to_trainers_list, callback_data='admin_trainers')],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await self._update.message.reply_text(text, reply_markup=reply_markup)
            self._context.user_data.pop('admin_state', None)
            return

        self._context.user_data['admin_trainer_telegram_id'] = telegram_id
        self._context.user_data['admin_state'] = 'awaiting_trainer_description'

        text = msgs.admin_trainer_create_step3(name=trainer_name, telegram_id=telegram_id)

        keyboard = [[InlineKeyboardButton(msgs.btn_cancel, callback_data='admin_trainers')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await self._update.message.reply_text(text, reply_markup=reply_markup)
