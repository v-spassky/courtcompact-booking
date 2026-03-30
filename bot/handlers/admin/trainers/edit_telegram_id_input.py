import logging

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from bot.handlers.admin._utils import _clear_admin_state
from bot.handlers.base import TextInputHandler

logger = logging.getLogger(__name__)


class AdminEditTrainerTelegramIdInput(TextInputHandler):
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
            try:
                telegram_id = int(self._text.strip())
                existing = self._deps.trainer_repo.get_by_telegram_id(telegram_id)
                if existing and existing.id != trainer.id:
                    await self._update.message.reply_text(
                        self._messages.admin_trainer_id_taken(name=existing.user.name),
                        reply_markup=InlineKeyboardMarkup(
                            [[InlineKeyboardButton(self._messages.btn_cancel, callback_data='admin_trainers')]],
                        ),
                    )
                    return
                self._context.user_data['admin_trainer_telegram_id'] = telegram_id
            except ValueError:
                await self._update.message.reply_text(
                    self._messages.admin_trainer_id_not_a_number_edit,
                    reply_markup=InlineKeyboardMarkup(
                        [[InlineKeyboardButton(self._messages.btn_cancel, callback_data='admin_trainers')]],
                    ),
                )
                return
        else:
            self._context.user_data['admin_trainer_telegram_id'] = trainer.user.telegram_user_id
        self._context.user_data['admin_state'] = 'awaiting_edit_trainer_description'
        await self._update.message.reply_text(
            self._messages.admin_trainer_edit_step3(
                new_name=self._context.user_data['admin_trainer_name'],
                new_telegram_id=self._context.user_data['admin_trainer_telegram_id'],
                description=trainer.description,
            ),
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton(self._messages.btn_cancel, callback_data='admin_trainers')]],
            ),
        )
