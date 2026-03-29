import logging

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from bot.deps import Deps
from bot.handlers.admin._utils import _clear_admin_state
from bot.handlers.auth import _is_admin
from bot.handlers.base import Handler
from localization import get_messages

logger = logging.getLogger(__name__)


class AdminEditLocationStart(Handler):
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

        location_id_short = self._callback_data.replace('admin_edit_location_', '')

        locations = self._deps.location_repo.get_all()
        location = None
        for loc in locations:
            if str(loc.id).startswith(location_id_short):
                location = loc
                break

        if not location:
            keyboard = [[InlineKeyboardButton(msgs.btn_back, callback_data='admin_locations')]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await self._update.callback_query.edit_message_text(
                msgs.admin_location_not_found, reply_markup=reply_markup
            )
            return

        _clear_admin_state(self._context)
        assert self._context.user_data is not None
        self._context.user_data['admin_location_id'] = str(location.id)
        self._context.user_data['admin_state'] = 'awaiting_edit_location_name'

        text = msgs.admin_location_edit_step1(name=location.name, maps_link=location.maps_link)

        keyboard = [[InlineKeyboardButton(msgs.btn_cancel, callback_data='admin_locations')]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await self._update.callback_query.edit_message_text(text, reply_markup=reply_markup)
