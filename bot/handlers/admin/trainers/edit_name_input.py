import logging

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from bot.handlers.admin._utils import _clear_admin_state
from bot.handlers.base import TextInputHandler

logger = logging.getLogger(__name__)


class AdminEditTrainerNameInput(TextInputHandler):
    async def _authorize(self) -> bool:
        return True

    async def _process(self) -> None:
        assert self._update.message is not None
        assert self._context.user_data is not None
        trainer_id = self._context.user_data.get('admin_trainer_id')
        if not trainer_id:
            _clear_admin_state(self._context)
            return
        trainer = self._deps.trainer_repo.get(int(trainer_id))
        if not trainer:
            _clear_admin_state(self._context)
            return
        if self._text.strip() != '-':
            if len(self._text) < 1 or len(self._text) > 100:
                await self._update.message.reply_text(
                    self._messages.admin_trainer_name_too_long_edit,
                    reply_markup=InlineKeyboardMarkup(
                        [[InlineKeyboardButton(self._messages.btn_cancel, callback_data='admin_trainers')]],
                    ),
                )
                return
            self._context.user_data['admin_trainer_name'] = self._text.strip()
        else:
            self._context.user_data['admin_trainer_name'] = trainer.user.name
        self._context.user_data['admin_state'] = 'awaiting_edit_trainer_telegram_id'
        await self._update.message.reply_text(
            self._messages.admin_trainer_edit_step2(
                new_name=self._context.user_data['admin_trainer_name'],
                telegram_id=trainer.user.telegram_user_id,
            ),
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton(self._messages.btn_cancel, callback_data='admin_trainers')]],
            ),
        )
