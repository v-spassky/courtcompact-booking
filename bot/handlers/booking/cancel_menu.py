import logging

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from bot.deps import get_deps
from config.settings import now_kiev
from db.models import BookingStatus
from localization import get_messages

logger = logging.getLogger(__name__)


async def _handle_cancel_booking_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.callback_query or not update.effective_user:
        return

    msgs = get_messages()
    deps = get_deps(context)
    user_id = update.effective_user.id

    try:
        bookings = deps.schedule_service.get_user_bookings(user_id)
        future_bookings = [
            b for b in bookings if b.start_time > now_kiev() and b.status != BookingStatus.CANCELLED.value
        ]

        if not future_bookings:
            keyboard = [[InlineKeyboardButton(msgs.btn_back_to_main_menu, callback_data='main_menu')]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.callback_query.edit_message_text(msgs.cancel_booking_no_upcoming, reply_markup=reply_markup)
            return

        keyboard = []
        for booking in sorted(future_bookings, key=lambda x: x.start_time):
            court = deps.court_repo.get(booking.court_id)
            court_name = court.name if court else 'Неизвестный'

            button_text = f'{court_name} - {booking.start_time.strftime("%d/%m %H:%M")}'
            keyboard.append([InlineKeyboardButton(button_text, callback_data=f'cancel_booking_{booking.id}')])

        keyboard.append([InlineKeyboardButton(msgs.btn_back_to_main_menu, callback_data='main_menu')])
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.callback_query.edit_message_text(msgs.cancel_booking_select, reply_markup=reply_markup)
    except Exception:
        logger.exception('Failed to show cancellation options')
        await update.callback_query.edit_message_text(msgs.cancel_booking_load_error)
