import logging

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from bot.handlers.admin._utils import _clear_admin_state
from bot.handlers.auth import _log_user_action
from bot.handlers.base import TextInputHandler
from db.models import Court

logger = logging.getLogger(__name__)


class AdminCourtDescriptionInput(TextInputHandler):
    async def _authorize(self) -> bool:
        return True

    async def _process(self) -> None:
        assert self._update.message is not None
        assert self._context.user_data is not None
        court_name = self._context.user_data.get('admin_court_name', 'Unknown')
        location_id_str = self._context.user_data.get('admin_court_location_id')
        location_id = int(location_id_str) if location_id_str else None
        _clear_admin_state(self._context)
        court_description = None if self._text.strip() == '-' else self._text.strip()
        court = Court(
            name=court_name,
            description=court_description,
            location_id=location_id,
        )
        self._deps.court_repo.save(court)
        if self._update.effective_user:
            _log_user_action(self._update.effective_user, f'created court: {court_name}')
        text = self._messages.admin_court_created(name=court_name)
        if location_id:
            location = self._deps.location_repo.get(location_id)
            if location:
                text += self._messages.admin_court_location_line(name=location.name)
        if court_description:
            text += self._messages.admin_court_description_line(desc=court_description)
        await self._update.message.reply_text(
            text,
            reply_markup=InlineKeyboardMarkup(
                [
                    [InlineKeyboardButton(self._messages.btn_create_another, callback_data='admin_create_court')],
                    [InlineKeyboardButton(self._messages.btn_back_to_courts, callback_data='admin_courts')],
                    [InlineKeyboardButton(self._messages.btn_main_menu, callback_data='main_menu')],
                ],
            ),
        )

    async def _on_error(self, error: Exception) -> None:
        logger.exception('Failed to create court')
        assert self._update.message is not None
        await self._update.message.reply_text(
            self._messages.admin_court_create_error,
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton(self._messages.btn_back_to_courts, callback_data='admin_courts')]],
            ),
        )
