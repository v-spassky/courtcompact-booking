import logging
from datetime import datetime

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from bot.deps import get_deps
from config.settings import now_kiev
from localization import get_messages

logger = logging.getLogger(__name__)


async def _handle_court_schedule_for_day(
    update: Update, context: ContextTypes.DEFAULT_TYPE, court_id: str, date: datetime
) -> None:
    if not update.callback_query:
        return

    msgs = get_messages()
    deps = get_deps(context)

    try:
        time_slots = deps.schedule_service.get_all_time_slots_for_date(date)
        court = deps.court_repo.get(court_id)
        court_name = court.name if court else 'Неизвестный корт'

        court_slots = [
            slot for slot in time_slots if str(slot.court_id) == court_id and slot.start_time.date() == date.date()
        ]

        location = None
        if court and court.location_id:
            location = deps.location_repo.get(court.location_id)

        text = msgs.schedule_court_day(
            court_name=court_name,
            date=date.strftime('%d.%m.%Y'),
            location_name=location.name if location else None,
            maps_link=location.google_maps_link if location else None,
        )

        now = now_kiev()
        future_slots = [s for s in court_slots if s.start_time >= now]

        if not future_slots:
            text += msgs.schedule_no_slots
        else:
            available_count = sum(1 for s in future_slots if s.is_available)
            total_count = len(future_slots)
            text += msgs.schedule_slots_summary(available=available_count, total=total_count)

            has_slots = False
            for slot in sorted(future_slots, key=lambda s: s.start_time):
                has_slots = True
                time_range = f'{slot.start_time.strftime("%H:%M")}-{slot.end_time.strftime("%H:%M")}'
                if slot.is_available:
                    text += f'✅ {time_range}\n'
                else:
                    booking_info = time_range
                    if slot.booking_id:
                        booking = deps.booking_repo.get(slot.booking_id)
                        if booking:
                            student = deps.student_repo.get(booking.student_id) if booking.student_id else None
                            if student:
                                booking_info += f' ({student.name})'
                            if booking.trainer_id:
                                trainer = deps.trainer_repo.get(booking.trainer_id)
                                if trainer:
                                    booking_info += f' 👨‍🏫 {trainer.name}'
                    text += f'❌ {booking_info}\n'

            if not has_slots:
                text += msgs.schedule_no_slots_for_day

        keyboard = [[InlineKeyboardButton(msgs.btn_back_to_main_menu, callback_data='main_menu')]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.callback_query.edit_message_text(
            text, reply_markup=reply_markup, parse_mode='HTML', disable_web_page_preview=True
        )
    except Exception:
        logger.exception('Failed to generate court schedule')
        await update.callback_query.edit_message_text(msgs.schedule_court_error)
