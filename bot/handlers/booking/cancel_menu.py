import logging

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from bot.handlers.base import Handler
from bot.handlers.callback_args import CancelBookingArg
from config.settings import now_kiev

logger = logging.getLogger(__name__)


class CancelBookingMenu(Handler):
    async def _authorize(self) -> bool:
        return True

    async def _process(self) -> None:
        assert self._update.callback_query is not None
        assert self._update.effective_user is not None
        user_id = self._update.effective_user.id
        bookings = self._deps.schedule_service.get_user_bookings(user_id)
        future_bookings = [b for b in bookings if b.start_time > now_kiev()]
        if not future_bookings:
            await self._update.callback_query.edit_message_text(
                self._messages.cancel_booking_no_upcoming,
                reply_markup=InlineKeyboardMarkup(
                    [[InlineKeyboardButton(self._messages.btn_back_to_main_menu, callback_data='main_menu')]],
                ),
            )
            return
        keyboard = []
        for booking in sorted(future_bookings, key=lambda x: x.start_time):
            court_name = booking.court.name if booking.court else self._messages.unknown_entity
            button_text = f'{court_name} - {booking.start_time.strftime("%d/%m %H:%M")}'
            keyboard.append(
                [
                    InlineKeyboardButton(
                        button_text,
                        callback_data=CancelBookingArg(booking_id=booking.id).to_callback_data(),
                    ),
                ],
            )
        keyboard.append([InlineKeyboardButton(self._messages.btn_back_to_main_menu, callback_data='main_menu')])
        await self._update.callback_query.edit_message_text(
            self._messages.cancel_booking_select,
            reply_markup=InlineKeyboardMarkup(keyboard),
        )

    async def _on_error(self, error: Exception) -> None:
        logger.exception('Failed to show cancellation options')
        assert self._update.callback_query is not None
        await self._update.callback_query.edit_message_text(self._messages.cancel_booking_load_error)
