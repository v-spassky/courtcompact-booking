import logging

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from bot.deps import Deps
from bot.handlers.admin._utils import _clear_admin_state
from bot.handlers.auth import _is_admin
from bot.handlers.base import Handler
from localization import get_messages

logger = logging.getLogger(__name__)


class AdminEditTrainerStart(Handler):
    def __init__(self, update: Update, context: ContextTypes.DEFAULT_TYPE, deps: Deps, callback_data: str) -> None:
        super().__init__(update, context, deps)
        self._callback_data = callback_data

    async def _authorize(self) -> bool:
        assert self._update.callback_query is not None
        assert self._update.effective_user is not None
        msgs = get_messages()
        if not _is_admin(self._update.effective_user.id, self._deps):
            await self._update.callback_query.edit_message_text(msgs.admin_no_access)
            return False
        return True

    async def _process(self) -> None:
        assert self._update.callback_query is not None
        msgs = get_messages()
        trainer_id = int(self._callback_data.replace('admin_edit_trainer_', ''))
        trainer = self._deps.trainer_repo.get(trainer_id)
        if not trainer:
            keyboard = [[InlineKeyboardButton(msgs.btn_back, callback_data='admin_trainers')]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await self._update.callback_query.edit_message_text(msgs.admin_trainer_not_found, reply_markup=reply_markup)
            return
        _clear_admin_state(self._context)
        assert self._context.user_data is not None
        self._context.user_data['admin_trainer_id'] = str(trainer.id)
        self._context.user_data['admin_state'] = 'awaiting_edit_trainer_name'
        text = msgs.admin_trainer_edit_step1(
            name=trainer.user.name,
            telegram_id=trainer.user.telegram_user_id,
            description=trainer.description,
        )
        keyboard = [[InlineKeyboardButton(msgs.btn_cancel, callback_data='admin_trainers')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await self._update.callback_query.edit_message_text(text, reply_markup=reply_markup)
