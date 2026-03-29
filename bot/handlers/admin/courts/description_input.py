import logging
from uuid import uuid4

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from bot.handlers.admin._utils import _clear_admin_state
from bot.handlers.auth import _log_user_action
from bot.handlers.base import TextInputHandler
from db.models import Court
from localization import get_messages

logger = logging.getLogger(__name__)


class AdminCourtDescriptionInput(TextInputHandler):
    async def _authorize(self) -> bool:
        return True

    async def _process(self) -> None:
        assert self._update.message is not None
        assert self._context.user_data is not None
        msgs = get_messages()
        court_name = self._context.user_data.get('admin_court_name', 'Unknown')
        location_id = self._context.user_data.get('admin_court_location_id')

        _clear_admin_state(self._context)

        court_description = None if self._text.strip() == '-' else self._text.strip()

        court = Court(
            id=str(uuid4()),
            name=court_name,
            description=court_description,
            location_id=location_id,
        )
        self._deps.court_repo.save(court)

        if self._update.effective_user:
            _log_user_action(self._update.effective_user, f'created court: {court_name}')

        text = msgs.admin_court_created(name=court_name)

        if location_id:
            location = self._deps.location_repo.get(location_id)
            if location:
                text += msgs.admin_court_location_line(name=location.name)

        if court_description:
            text += msgs.admin_court_description_line(desc=court_description)

        keyboard = [
            [InlineKeyboardButton(msgs.btn_create_another, callback_data='admin_create_court')],
            [InlineKeyboardButton(msgs.btn_back_to_courts, callback_data='admin_courts')],
            [InlineKeyboardButton(msgs.btn_main_menu, callback_data='main_menu')],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await self._update.message.reply_text(text, reply_markup=reply_markup)

    async def _on_error(self, error: Exception) -> None:
        logger.exception('Failed to create court')
        msgs = get_messages()
        assert self._update.message is not None
        keyboard = [[InlineKeyboardButton(msgs.btn_back_to_courts, callback_data='admin_courts')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await self._update.message.reply_text(msgs.admin_court_create_error, reply_markup=reply_markup)
