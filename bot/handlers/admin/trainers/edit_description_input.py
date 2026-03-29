import logging

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from bot.handlers.admin._utils import _clear_admin_state
from bot.handlers.auth import _log_user_action
from bot.handlers.base import TextInputHandler
from localization import get_messages

logger = logging.getLogger(__name__)


class AdminEditTrainerDescriptionInput(TextInputHandler):
    async def _authorize(self) -> bool:
        return True

    async def _process(self) -> None:
        assert self._update.message is not None
        assert self._context.user_data is not None
        msgs = get_messages()
        trainer_id = self._context.user_data.get('admin_trainer_id')
        if not trainer_id:
            _clear_admin_state(self._context)
            return
        trainers = self._deps.trainer_repo.get_all()
        trainer = None
        for t in trainers:
            if str(t.id) == trainer_id:
                trainer = t
                break
        if not trainer:
            _clear_admin_state(self._context)
            return
        new_name = self._context.user_data.get('admin_trainer_name', trainer.user.name)
        new_telegram_id = self._context.user_data.get('admin_trainer_telegram_id', trainer.user.telegram_user_id)
        if self._text.strip() == '-':
            new_description = trainer.description
        elif self._text.strip() == '--':
            new_description = None
        else:
            new_description = self._text.strip()
        _clear_admin_state(self._context)
        trainer.user.name = new_name
        trainer.user.telegram_user_id = new_telegram_id
        trainer.description = new_description
        self._deps.user_repo.save(trainer.user)
        self._deps.trainer_repo.save(trainer)
        if self._update.effective_user:
            _log_user_action(self._update.effective_user, f'edited trainer: {trainer.user.name}')
        text = msgs.admin_trainer_updated(name=trainer.user.name)
        keyboard = [
            [InlineKeyboardButton(msgs.btn_edit_another, callback_data='admin_edit_trainer')],
            [InlineKeyboardButton(msgs.btn_back_to_trainers_list, callback_data='admin_trainers')],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await self._update.message.reply_text(text, reply_markup=reply_markup)

    async def _on_error(self, error: Exception) -> None:
        logger.exception('Failed to edit trainer')
        msgs = get_messages()
        assert self._update.message is not None
        keyboard = [[InlineKeyboardButton(msgs.btn_back_to_trainers_list, callback_data='admin_trainers')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await self._update.message.reply_text(msgs.admin_trainer_update_error, reply_markup=reply_markup)
