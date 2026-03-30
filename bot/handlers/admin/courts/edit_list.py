import logging

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from bot.handlers.admin._utils import _clear_admin_state
from bot.handlers.auth import _is_admin
from bot.handlers.base import Handler

logger = logging.getLogger(__name__)


class AdminEditCourtList(Handler):
    async def _authorize(self) -> bool:
        assert self._update.callback_query is not None
        assert self._update.effective_user is not None
        if not _is_admin(self._update.effective_user.id, self._deps):
            await self._update.callback_query.edit_message_text(self._messages.admin_no_access)
            return False
        return True

    async def _process(self) -> None:
        assert self._update.callback_query is not None
        _clear_admin_state(self._context)
        courts = self._deps.court_repo.get_all()
        if not courts:
            await self._update.callback_query.edit_message_text(
                self._messages.admin_court_no_courts,
                reply_markup=InlineKeyboardMarkup(
                    [[InlineKeyboardButton(self._messages.btn_back, callback_data='admin_courts')]],
                ),
            )
            return
        keyboard = []
        for court in courts:
            keyboard.append([InlineKeyboardButton(f'🎾 {court.name}', callback_data=f'admin_edit_court_{court.id}')])
        keyboard.append([InlineKeyboardButton(self._messages.btn_back, callback_data='admin_courts')])
        await self._update.callback_query.edit_message_text(
            self._messages.admin_court_select_to_edit,
            reply_markup=InlineKeyboardMarkup(keyboard),
        )
