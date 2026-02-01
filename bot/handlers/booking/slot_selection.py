import logging
from datetime import datetime, timedelta

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from bot.deps import get_deps
from bot.handlers.auth import _get_student_for_user, _log_user_action
from localization import get_messages

logger = logging.getLogger(__name__)


async def _handle_booking_slot_selection(
    update: Update, context: ContextTypes.DEFAULT_TYPE, data: str, user_id: int
) -> None:
    if not update.callback_query:
        return

    msgs = get_messages()
    deps = get_deps(context)
    query = update.callback_query

    try:
        parts = data.split('_')
        court_id_short = parts[2]
        trainer_id_short = parts[3]
        date_str = parts[4]
        time_code = parts[5]

        year = int(date_str[0:4])
        month = int(date_str[4:6])
        day = int(date_str[6:8])
        hour = int(time_code[0:2])
        minute = int(time_code[2:4]) if len(time_code) >= 4 else 0
        start_time = datetime(year, month, day, hour, minute, 0)
        end_time = start_time + timedelta(minutes=30)

        courts = deps.court_repo.get_active()
        court_id = None
        for court in courts:
            if str(court.id).startswith(court_id_short):
                court_id = court.id
                break

        if not court_id:
            raise ValueError(f'Court not found for ID starting with {court_id_short}')

        trainer_id = None
        if trainer_id_short and trainer_id_short != 'none':
            trainers = deps.trainer_repo.get_all()
            for trainer in trainers:
                if str(trainer.id).startswith(trainer_id_short):
                    trainer_id = trainer.id
                    break

        user_trainer = deps.trainer_repo.get_by_telegram_id(user_id)
        is_trainer_booking = user_trainer is not None and trainer_id == user_trainer.id

        student_id = None
        if not is_trainer_booking:
            student = _get_student_for_user(user_id, deps)
            if student:
                student_id = student.id

        booking = deps.booking_service.create_booking(
            court_id=court_id,
            start_time=start_time,
            end_time=end_time,
            student_id=student_id,
            trainer_id=trainer_id,
        )

        if booking:
            booked_court = deps.court_repo.get(booking.court_id)
            court_name = booked_court.name if booked_court else 'Неизвестный корт'

            if query.from_user:
                _log_user_action(
                    query.from_user, f'created booking: {court_name} on {booking.start_time.strftime("%d.%m.%Y %H:%M")}'
                )

            booked_trainer = None
            trainer_name = None
            if booking.trainer_id:
                booked_trainer = deps.trainer_repo.get(booking.trainer_id)
                if booked_trainer:
                    trainer_name = booked_trainer.name

            text = msgs.booking_confirmed(
                court_name=court_name,
                date=booking.start_time.strftime('%d.%m.%Y'),
                time=f'{booking.start_time.strftime("%H:%M")} - {booking.end_time.strftime("%H:%M")}',
                trainer_name=trainer_name,
                booking_id=str(booking.id)[:8],
            )

            keyboard = [[InlineKeyboardButton(msgs.btn_back_to_main_menu, callback_data='main_menu')]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(text, reply_markup=reply_markup)

            if booked_trainer and not is_trainer_booking and booked_trainer.telegram_user_id != user_id:
                try:
                    student_name = query.from_user.full_name if query.from_user else 'Студент'
                    notify_text = msgs.booking_new_notification(
                        student_name=student_name,
                        court_name=court_name,
                        date=booking.start_time.strftime('%d.%m.%Y'),
                        time=f'{booking.start_time.strftime("%H:%M")} - {booking.end_time.strftime("%H:%M")}',
                    )
                    notify_keyboard = [[InlineKeyboardButton(msgs.btn_main_menu, callback_data='main_menu')]]
                    notify_markup = InlineKeyboardMarkup(notify_keyboard)
                    await context.bot.send_message(
                        chat_id=booked_trainer.telegram_user_id, text=notify_text, reply_markup=notify_markup
                    )
                except Exception as e:
                    logger.warning(f'Failed to notify trainer: {e}')
        else:
            keyboard = [[InlineKeyboardButton(msgs.btn_back_to_main_menu, callback_data='main_menu')]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(msgs.booking_slot_unavailable, reply_markup=reply_markup)
    except Exception:
        logger.exception('Failed to create booking')
        keyboard = [[InlineKeyboardButton(msgs.btn_back_to_main_menu, callback_data='main_menu')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(msgs.booking_generic_error, reply_markup=reply_markup)
