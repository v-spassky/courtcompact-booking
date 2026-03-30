import logging

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from bot.handlers.admin._utils import _clear_admin_state
from bot.handlers.auth import _log_user_action
from bot.handlers.base import TextInputHandler
from localization import get_messages

logger = logging.getLogger(__name__)


class AdminEditCourtDescriptionInput(TextInputHandler):
    async def _authorize(self) -> bool:
        return True

    async def _process(self) -> None:
        assert self._update.message is not None
        assert self._context.user_data is not None
        msgs = get_messages()
        court_id = self._context.user_data.get('admin_court_id')
        new_name = self._context.user_data.get('admin_court_name')
        if not court_id:
            _clear_admin_state(self._context)
            return
        court = self._deps.court_repo.get(int(court_id))
        if not court:
            _clear_admin_state(self._context)
            return
        _clear_admin_state(self._context)
        if new_name is not None:
            court.name = new_name
        if self._text.strip() == '-':
            pass
        elif self._text.strip() == '--':
            court.description = None
        else:
            court.description = self._text.strip()
        self._deps.court_repo.save(court)
        if self._update.effective_user:
            _log_user_action(self._update.effective_user, f'edited court: {court.name}')
        text = msgs.admin_court_updated(name=court.name)
        keyboard = [
            [InlineKeyboardButton(msgs.btn_edit_another, callback_data='admin_edit_court')],
            [InlineKeyboardButton(msgs.btn_back_to_courts, callback_data='admin_courts')],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await self._update.message.reply_text(text, reply_markup=reply_markup)

    async def _on_error(self, error: Exception) -> None:
        logger.exception('Failed to edit court')
        msgs = get_messages()
        assert self._update.message is not None
        keyboard = [[InlineKeyboardButton(msgs.btn_back_to_courts, callback_data='admin_courts')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await self._update.message.reply_text(msgs.admin_court_update_error, reply_markup=reply_markup)
