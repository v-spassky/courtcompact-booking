import logging

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from bot.handlers.admin._utils import _clear_admin_state
from bot.handlers.auth import _log_user_action
from bot.handlers.base import TextInputHandler
from db.models import Trainer, User

logger = logging.getLogger(__name__)


class AdminTrainerDescriptionInput(TextInputHandler):
    async def _authorize(self) -> bool:
        return True

    async def _process(self) -> None:
        assert self._update.message is not None
        assert self._context.user_data is not None
        trainer_name = self._context.user_data.get('admin_trainer_name', 'Unknown')
        telegram_id = self._context.user_data.get('admin_trainer_telegram_id', 0)
        _clear_admin_state(self._context)
        description = None if self._text.strip() == '-' else self._text.strip()
        user = self._deps.user_repo.get_by_telegram_id(telegram_id)
        if user is None:
            user = User(telegram_user_id=telegram_id, name=trainer_name)
            self._deps.user_repo.save(user)
        else:
            user.name = trainer_name
            self._deps.user_repo.save(user)
        trainer = Trainer(user_id=user.id, description=description)
        self._deps.trainer_repo.save(trainer)
        if self._update.effective_user:
            _log_user_action(self._update.effective_user, f'created trainer: {trainer_name} (ID: {telegram_id})')
        text = self._messages.admin_trainer_created(name=trainer_name)
        text += f'\n🆔 Telegram ID: {telegram_id}\n'
        if description:
            text += self._messages.admin_trainer_description_line(desc=description)
        await self._update.message.reply_text(
            text,
            reply_markup=InlineKeyboardMarkup(
                [
                    [InlineKeyboardButton(self._messages.btn_create_another, callback_data='admin_create_trainer')],
                    [InlineKeyboardButton(self._messages.btn_back_to_trainers_list, callback_data='admin_trainers')],
                    [InlineKeyboardButton(self._messages.btn_main_menu, callback_data='main_menu')],
                ],
            ),
        )

    async def _on_error(self, error: Exception) -> None:
        logger.exception('Failed to create trainer')
        assert self._update.message is not None
        await self._update.message.reply_text(
            self._messages.admin_trainer_create_error,
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton(self._messages.btn_back_to_trainers_list, callback_data='admin_trainers')]],
            ),
        )
