import logging

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from bot.handlers.admin._utils import _clear_admin_state
from bot.handlers.auth import _is_admin
from bot.handlers.base import Handler
from localization import get_messages

logger = logging.getLogger(__name__)


class AdminDeleteCourtList(Handler):
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
        _clear_admin_state(self._context)
        courts = self._deps.court_repo.get_all()
        if not courts:
            await self._update.callback_query.edit_message_text(
                msgs.admin_court_no_courts,
                reply_markup=InlineKeyboardMarkup(
                    [[InlineKeyboardButton(msgs.btn_back, callback_data='admin_courts')]],
                ),
            )
            return
        keyboard = []
        for court in courts:
            keyboard.append([InlineKeyboardButton(f'🎾 {court.name}', callback_data=f'admin_delete_court_{court.id}')])
        keyboard.append([InlineKeyboardButton(msgs.btn_back, callback_data='admin_courts')])
        await self._update.callback_query.edit_message_text(
            msgs.admin_court_select_to_delete,
            reply_markup=InlineKeyboardMarkup(keyboard),
        )
