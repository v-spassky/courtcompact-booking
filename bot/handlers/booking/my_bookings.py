import logging

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from bot.deps import get_deps
from config.settings import now_kiev
from db.models import BookingStatus
from localization import get_messages

logger = logging.getLogger(__name__)


async def _handle_my_bookings(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.callback_query or not update.effective_user:
        return

    msgs = get_messages()
    deps = get_deps(context)
    user_id = update.effective_user.id

    try:
        bookings = deps.schedule_service.get_user_bookings(user_id)

        if not bookings:
            keyboard = [[InlineKeyboardButton(msgs.btn_back_to_main_menu, callback_data='main_menu')]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.callback_query.edit_message_text(msgs.my_bookings_empty, reply_markup=reply_markup)
            return

        now = now_kiev()
        future_bookings = [b for b in bookings if b.start_time > now and b.status != BookingStatus.CANCELLED.value]

        if not future_bookings:
            keyboard = [[InlineKeyboardButton(msgs.btn_back_to_main_menu, callback_data='main_menu')]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.callback_query.edit_message_text(msgs.my_bookings_no_upcoming, reply_markup=reply_markup)
            return

        text = msgs.my_bookings_title
        for booking in sorted(future_bookings, key=lambda x: x.start_time):
            court = deps.court_repo.get(booking.court_id)
            court_name = court.name if court else msgs.unknown_court

            text += msgs.booking_detail_court(name=court_name)
            text += f'📅 {booking.start_time.strftime("%d/%m/%Y %H:%M")} - {booking.end_time.strftime("%H:%M")}\n'

            if booking.trainer_id:
                trainer = deps.trainer_repo.get(booking.trainer_id)
                if trainer:
                    text += msgs.booking_detail_trainer(name=trainer.name)

            if booking.notes:
                text += msgs.booking_detail_notes(notes=booking.notes)
            text += f'🆔 ID: {str(booking.id)[:8]}\n\n'

        keyboard = [[InlineKeyboardButton(msgs.btn_back_to_main_menu, callback_data='main_menu')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.callback_query.edit_message_text(text, reply_markup=reply_markup)
    except Exception:
        logger.exception('Failed to get user bookings')
        keyboard = [[InlineKeyboardButton(msgs.btn_back_to_main_menu, callback_data='main_menu')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.callback_query.edit_message_text(msgs.my_bookings_error, reply_markup=reply_markup)
