import logging
from datetime import datetime

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from bot.deps import get_deps
from localization import get_messages

logger = logging.getLogger(__name__)


async def _handle_booking_date_selection(update: Update, context: ContextTypes.DEFAULT_TYPE, data: str) -> None:
    if not update.callback_query:
        return

    msgs = get_messages()
    deps = get_deps(context)

    try:
        parts = data.split('_')
        court_id_short = parts[2]
        trainer_id_short = parts[3]
        year = int(parts[4])
        month = int(parts[5])
        day = int(parts[6])

        selected_date = datetime(year, month, day)

        courts = deps.court_repo.get_active()
        court_id: str | None = None
        for court in courts:
            if str(court.id).startswith(court_id_short):
                court_id = court.id
                break

        trainer_id = None
        trainer_name = None
        if trainer_id_short != 'none':
            trainers = deps.trainer_repo.get_all()
            for trainer in trainers:
                if str(trainer.id).startswith(trainer_id_short):
                    trainer_id = trainer.id
                    trainer_name = trainer.name
                    break

        court_obj = deps.court_repo.get(court_id) if court_id else None
        court_name = court_obj.name if court_obj else msgs.unknown_court

        time_slots = deps.schedule_service.get_all_time_slots_for_date(selected_date)
        court_slots = [slot for slot in time_slots if str(slot.court_id) == str(court_id)]

        trainer_busy_times = set()
        if trainer_id:
            all_slots = deps.schedule_service.get_all_time_slots_for_date(selected_date)
            for other_slot in all_slots:
                if not other_slot.is_available and other_slot.booking_id:
                    booking = deps.booking_repo.get(other_slot.booking_id)
                    if booking and str(booking.trainer_id) == str(trainer_id):
                        trainer_busy_times.add((booking.start_time, booking.end_time))

        if not court_slots:
            keyboard = [[InlineKeyboardButton(msgs.btn_back_to_main_menu, callback_data='main_menu')]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.callback_query.edit_message_text(msgs.booking_no_slots_for_date, reply_markup=reply_markup)
            return

        text = msgs.booking_select_slot(
            court_name=court_name,
            date=selected_date.strftime('%d.%m.%Y'),
            trainer_name=trainer_name,
        )

        buttons = []
        for slot in sorted(court_slots, key=lambda s: s.start_time):
            is_available = slot.is_available

            if is_available and trainer_id:
                for busy_start, busy_end in trainer_busy_times:
                    if slot.start_time < busy_end and slot.end_time > busy_start:
                        is_available = False
                        break

            if is_available:
                time_str = f'{slot.start_time.strftime("%H:%M")}-{slot.end_time.strftime("%H:%M")}'
                date_str = selected_date.strftime('%Y%m%d')
                time_code = slot.start_time.strftime('%H%M')
                callback_data = f'book_slot_{court_id_short}_{trainer_id_short}_{date_str}_{time_code}'
            else:
                time_str = msgs.slot_occupied
                callback_data = 'ignore'

            buttons.append(InlineKeyboardButton(time_str, callback_data=callback_data))

        keyboard = []
        for i in range(0, len(buttons), 2):
            row = [buttons[i]]
            if i + 1 < len(buttons):
                row.append(buttons[i + 1])
            keyboard.append(row)

        keyboard.append([InlineKeyboardButton(msgs.btn_back_to_main_menu, callback_data='main_menu')])
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.callback_query.edit_message_text(text, reply_markup=reply_markup)
    except Exception:
        logger.exception('Failed to show time slots')
        await update.callback_query.edit_message_text(msgs.generic_error)
