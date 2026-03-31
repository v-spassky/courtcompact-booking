from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from bot.deps import Deps
from bot.handlers.auth._utils import _is_admin
from bot.handlers.base import Handler


class ShowMainMenu(Handler):
    def __init__(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
        deps: Deps,
        edit_message: bool,
    ) -> None:
        super().__init__(update, context, deps)
        self._edit_message = edit_message

    async def _authorize(self) -> bool:
        return True

    async def _process(self) -> None:
        keyboard = [
            [InlineKeyboardButton(self._messages.btn_schedule_by_date, callback_data='select_date_schedule')],
            [InlineKeyboardButton(self._messages.btn_schedule_weekly, callback_data='schedule_weekly')],
            [InlineKeyboardButton(self._messages.btn_trainer_schedule, callback_data='trainer_schedule')],
            [InlineKeyboardButton(self._messages.btn_book_court, callback_data='book_court')],
            [InlineKeyboardButton(self._messages.btn_my_bookings, callback_data='my_bookings')],
            [InlineKeyboardButton(self._messages.btn_cancel_booking, callback_data='cancel_booking')],
        ]
        if self._update.effective_user and _is_admin(self._update.effective_user.id, self._deps):
            keyboard.append([InlineKeyboardButton(self._messages.btn_admin_panel, callback_data='admin_menu')])
        if self._edit_message:
            assert self._update.callback_query is not None
            await self._update.callback_query.edit_message_text(
                self._messages.welcome_after_auth,
                reply_markup=InlineKeyboardMarkup(keyboard),
            )
        else:
            assert self._update.message is not None
            await self._update.message.reply_text(
                self._messages.welcome_after_auth,
                reply_markup=InlineKeyboardMarkup(keyboard),
            )
