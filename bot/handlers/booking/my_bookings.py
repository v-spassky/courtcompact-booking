import logging

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from bot.handlers.base import Handler
from config.settings import now_kiev
from localization import get_messages

logger = logging.getLogger(__name__)


class MyBookings(Handler):
    async def _authorize(self) -> bool:
        return True

    async def _process(self) -> None:
        assert self._update.callback_query is not None
        assert self._update.effective_user is not None
        msgs = get_messages()
        user_id = self._update.effective_user.id

        bookings = self._deps.schedule_service.get_user_bookings(user_id)

        if not bookings:
            keyboard = [[InlineKeyboardButton(msgs.btn_back_to_main_menu, callback_data='main_menu')]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await self._update.callback_query.edit_message_text(msgs.my_bookings_empty, reply_markup=reply_markup)
            return

        now = now_kiev()
        future_bookings = [b for b in bookings if b.start_time > now]

        if not future_bookings:
            keyboard = [[InlineKeyboardButton(msgs.btn_back_to_main_menu, callback_data='main_menu')]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await self._update.callback_query.edit_message_text(msgs.my_bookings_no_upcoming, reply_markup=reply_markup)
            return

        text = msgs.my_bookings_title
        for booking in sorted(future_bookings, key=lambda x: x.start_time):
            court = self._deps.court_repo.get(booking.court_id)
            court_name = court.name if court else msgs.unknown_court

            text += msgs.booking_detail_court(name=court_name)
            text += f'📅 {booking.start_time.strftime("%d/%m/%Y %H:%M")} - {booking.end_time.strftime("%H:%M")}\n'

            if booking.trainer_id:
                trainer = self._deps.trainer_repo.get(booking.trainer_id)
                if trainer:
                    text += msgs.booking_detail_trainer(name=trainer.name)

            text += f'🆔 ID: {str(booking.id)[:8]}\n\n'

        keyboard = [[InlineKeyboardButton(msgs.btn_back_to_main_menu, callback_data='main_menu')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await self._update.callback_query.edit_message_text(text, reply_markup=reply_markup)

    async def _on_error(self, error: Exception) -> None:
        logger.exception('Failed to get user bookings')
        msgs = get_messages()
        assert self._update.callback_query is not None
        keyboard = [[InlineKeyboardButton(msgs.btn_back_to_main_menu, callback_data='main_menu')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await self._update.callback_query.edit_message_text(msgs.my_bookings_error, reply_markup=reply_markup)
