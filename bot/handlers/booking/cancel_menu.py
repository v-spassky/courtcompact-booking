import logging

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from bot.handlers.base import Handler
from config.settings import now_kiev
from localization import get_messages

logger = logging.getLogger(__name__)


class CancelBookingMenu(Handler):
    async def _authorize(self) -> bool:
        return True

    async def _process(self) -> None:
        assert self._update.callback_query is not None
        assert self._update.effective_user is not None
        msgs = get_messages()
        user_id = self._update.effective_user.id
        bookings = self._deps.schedule_service.get_user_bookings(user_id)
        future_bookings = [b for b in bookings if b.start_time > now_kiev()]
        if not future_bookings:
            keyboard = [[InlineKeyboardButton(msgs.btn_back_to_main_menu, callback_data='main_menu')]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await self._update.callback_query.edit_message_text(
                msgs.cancel_booking_no_upcoming, reply_markup=reply_markup
            )
            return
        keyboard = []
        for booking in sorted(future_bookings, key=lambda x: x.start_time):
            court_name = booking.court.name if booking.court else msgs.unknown_entity
            button_text = f'{court_name} - {booking.start_time.strftime("%d/%m %H:%M")}'
            keyboard.append([InlineKeyboardButton(button_text, callback_data=f'cancel_booking_{booking.id}')])
        keyboard.append([InlineKeyboardButton(msgs.btn_back_to_main_menu, callback_data='main_menu')])
        reply_markup = InlineKeyboardMarkup(keyboard)
        await self._update.callback_query.edit_message_text(msgs.cancel_booking_select, reply_markup=reply_markup)

    async def _on_error(self, error: Exception) -> None:
        logger.exception('Failed to show cancellation options')
        msgs = get_messages()
        assert self._update.callback_query is not None
        await self._update.callback_query.edit_message_text(msgs.cancel_booking_load_error)
