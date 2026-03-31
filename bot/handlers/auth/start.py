from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from bot.handlers.auth._utils import _is_admin, _is_authorized, _log_user_action
from bot.handlers.base import Handler


class StartCommand(Handler):
    async def _authorize(self) -> bool:
        return True

    async def _process(self) -> None:
        from bot.handlers.auth.show_auth_request import ShowAuthorizationRequest

        assert self._update.message is not None
        assert self._update.effective_user is not None
        _log_user_action(self._update.effective_user, 'used /start command')
        if not _is_authorized(self._update.effective_user.id, self._deps):
            await ShowAuthorizationRequest(self._update, self._context, self._deps).handle()
            return
        keyboard = [
            [InlineKeyboardButton(self._messages.btn_schedule_by_date, callback_data='select_date_schedule')],
            [InlineKeyboardButton(self._messages.btn_schedule_weekly, callback_data='schedule_weekly')],
            [InlineKeyboardButton(self._messages.btn_trainer_schedule, callback_data='trainer_schedule')],
            [InlineKeyboardButton(self._messages.btn_book_court, callback_data='book_court')],
            [InlineKeyboardButton(self._messages.btn_my_bookings, callback_data='my_bookings')],
            [InlineKeyboardButton(self._messages.btn_cancel_booking, callback_data='cancel_booking')],
        ]
        if _is_admin(self._update.effective_user.id, self._deps):
            keyboard.append([InlineKeyboardButton(self._messages.btn_admin_panel, callback_data='admin_menu')])
        await self._update.message.reply_text(
            self._messages.welcome_start,
            reply_markup=InlineKeyboardMarkup(keyboard),
        )
