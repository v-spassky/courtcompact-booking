import logging

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from bot.handlers.admin._utils import _clear_admin_state
from bot.handlers.base import TextInputHandler
from localization import get_messages

logger = logging.getLogger(__name__)


class AdminEditCourtNameInput(TextInputHandler):
    async def _authorize(self) -> bool:
        return True

    async def _process(self) -> None:
        assert self._update.message is not None
        assert self._context.user_data is not None
        msgs = get_messages()
        court_id = self._context.user_data.get('admin_court_id')
        if not court_id:
            _clear_admin_state(self._context)
            return
        court = self._deps.court_repo.get(int(court_id))
        if not court:
            _clear_admin_state(self._context)
            return
        if self._text.strip() != '-':
            if len(self._text) < 1 or len(self._text) > 100:
                await self._update.message.reply_text(
                    msgs.admin_court_name_too_long_edit,
                    reply_markup=InlineKeyboardMarkup(
                        [[InlineKeyboardButton(msgs.btn_cancel, callback_data='admin_courts')]],
                    ),
                )
                return
            self._context.user_data['admin_court_name'] = self._text.strip()
        else:
            self._context.user_data['admin_court_name'] = court.name
        self._context.user_data['admin_state'] = 'awaiting_edit_court_description'
        await self._update.message.reply_text(
            msgs.admin_court_edit_step2(
                name=self._context.user_data['admin_court_name'],
                description=court.description,
            ),
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(msgs.btn_cancel, callback_data='admin_courts')]]),
        )
