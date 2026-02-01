import logging

from telegram import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from bot.deps import get_deps
from bot.handlers.auth import _log_user_action
from localization import get_messages

logger = logging.getLogger(__name__)


async def _handle_booking_cancellation(
    update: Update, context: ContextTypes.DEFAULT_TYPE, query: CallbackQuery, data: str, user_id: int
) -> None:
    msgs = get_messages()
    deps = get_deps(context)
    booking_id = data.split('_')[2]

    try:
        booking = deps.booking_repo.get(booking_id)
        if not booking:
            keyboard = [[InlineKeyboardButton(msgs.btn_back_to_main_menu, callback_data='main_menu')]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(msgs.booking_not_found, reply_markup=reply_markup)
            return

        court = deps.court_repo.get(booking.court_id)
        court_name = court.name if court else 'Неизвестный корт'
        student = deps.student_repo.get(booking.student_id) if booking.student_id else None
        trainer = deps.trainer_repo.get(booking.trainer_id) if booking.trainer_id else None

        is_student_cancelling = student and student.telegram_user_id == user_id
        is_trainer_cancelling = trainer and trainer.telegram_user_id == user_id

        success = deps.booking_service.cancel_booking(booking_id, user_id)

        keyboard = [[InlineKeyboardButton(msgs.btn_back_to_main_menu, callback_data='main_menu')]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        if success:
            _log_user_action(query.from_user, f'cancelled booking: {booking_id}')
            await query.edit_message_text(msgs.booking_cancelled, reply_markup=reply_markup)

            notify_text = msgs.booking_cancelled_notification(
                court_name=court_name,
                date=booking.start_time.strftime('%d.%m.%Y'),
                time=f'{booking.start_time.strftime("%H:%M")} - {booking.end_time.strftime("%H:%M")}',
            )

            try:
                notify_keyboard = [[InlineKeyboardButton(msgs.btn_main_menu, callback_data='main_menu')]]
                notify_markup = InlineKeyboardMarkup(notify_keyboard)
                if is_student_cancelling and trainer and trainer.telegram_user_id != user_id:
                    student_name = query.from_user.full_name if query.from_user else 'Студент'
                    notify_text += msgs.booking_cancelled_by_student(student_name=student_name)
                    await context.bot.send_message(
                        chat_id=trainer.telegram_user_id, text=notify_text, reply_markup=notify_markup
                    )
                elif (
                    is_trainer_cancelling
                    and student
                    and student.telegram_user_id
                    and student.telegram_user_id != user_id
                ):
                    trainer_name = trainer.name if trainer else 'Тренер'
                    notify_text += msgs.booking_cancelled_by_trainer(trainer_name=trainer_name)
                    await context.bot.send_message(
                        chat_id=student.telegram_user_id, text=notify_text, reply_markup=notify_markup
                    )
            except Exception as e:
                logger.warning(f'Failed to send cancellation notification: {e}')
        else:
            await query.edit_message_text(
                msgs.cancel_booking_failed,
                reply_markup=reply_markup,
            )
    except Exception:
        logger.exception('Failed to cancel booking')
        keyboard = [[InlineKeyboardButton(msgs.btn_back_to_main_menu, callback_data='main_menu')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(msgs.cancel_booking_error, reply_markup=reply_markup)
