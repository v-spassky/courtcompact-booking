import logging

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from bot.handlers.admin._utils import _clear_admin_state
from bot.handlers.auth import _log_user_action
from bot.handlers.base import TextInputHandler
from db.models import Trainer
from localization import get_messages

logger = logging.getLogger(__name__)


class AdminTrainerDescriptionInput(TextInputHandler):
    async def _authorize(self) -> bool:
        return True

    async def _process(self) -> None:
        assert self._update.message is not None
        assert self._context.user_data is not None
        msgs = get_messages()
        trainer_name = self._context.user_data.get('admin_trainer_name', 'Unknown')
        telegram_id = self._context.user_data.get('admin_trainer_telegram_id', 0)

        _clear_admin_state(self._context)

        description = None if self._text.strip() == '-' else self._text.strip()

        trainer = Trainer(
            telegram_user_id=telegram_id,
            name=trainer_name,
            description=description,
        )
        self._deps.trainer_repo.save(trainer)

        if self._update.effective_user:
            _log_user_action(self._update.effective_user, f'created trainer: {trainer_name} (ID: {telegram_id})')

        text = msgs.admin_trainer_created(name=trainer_name)
        text += f'\n🆔 Telegram ID: {telegram_id}\n'
        if description:
            text += msgs.admin_trainer_description_line(desc=description)

        keyboard = [
            [InlineKeyboardButton(msgs.btn_create_another, callback_data='admin_create_trainer')],
            [InlineKeyboardButton(msgs.btn_back_to_trainers_list, callback_data='admin_trainers')],
            [InlineKeyboardButton(msgs.btn_main_menu, callback_data='main_menu')],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await self._update.message.reply_text(text, reply_markup=reply_markup)

    async def _on_error(self, error: Exception) -> None:
        logger.exception('Failed to create trainer')
        msgs = get_messages()
        assert self._update.message is not None
        keyboard = [[InlineKeyboardButton(msgs.btn_back_to_trainers_list, callback_data='admin_trainers')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await self._update.message.reply_text(msgs.admin_trainer_create_error, reply_markup=reply_markup)
