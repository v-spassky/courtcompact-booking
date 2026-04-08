import logging
from datetime import datetime, timedelta

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from bot.deps import Deps
from bot.handlers.auth import _get_student_for_user, _log_user_action
from bot.handlers.base import Handler
from bot.handlers.callback_args import BookSlotArg

logger = logging.getLogger(__name__)


class BookingSlotSelection(Handler):
    def __init__(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
        deps: Deps,
        args: BookSlotArg,
        user_id: int,
    ) -> None:
        super().__init__(update, context, deps)
        self._args = args
        self._user_id = user_id

    async def _authorize(self) -> bool:
        return True

    async def _process(self) -> None:
        assert self._update.callback_query is not None
        start_time = datetime(self._args.year, self._args.month, self._args.day, self._args.hour, self._args.minute, 0)
        end_time = start_time + timedelta(minutes=30)
        court = self._deps.court_repo.get(self._args.court_id)
        if not court:
            raise ValueError(f'Court not found with ID {self._args.court_id}')
        user_trainer = self._deps.trainer_repo.get_by_telegram_id(self._user_id)
        is_trainer_booking = user_trainer is not None and self._args.trainer_id == user_trainer.id
        student_id = None
        if not is_trainer_booking:
            student = _get_student_for_user(self._user_id, self._deps)
            if student:
                student_id = student.id
        booking = self._deps.booking_service.create_booking(
            court_id=self._args.court_id,
            start_time=start_time,
            end_time=end_time,
            student_id=student_id,
            trainer_id=self._args.trainer_id,
        )
        if booking:
            court_name = booking.court.name if booking.court else self._messages.unknown_court
            if self._update.callback_query.from_user:
                _log_user_action(
                    self._update.callback_query.from_user,
                    f'created booking: {court_name} on {booking.start_time.strftime("%d.%m.%Y %H:%M")}',
                )
            trainer_name = booking.trainer.user.name if booking.trainer else None
            booked_trainer = booking.trainer
            text = self._messages.booking_confirmed(
                court_name=court_name,
                date=booking.start_time.strftime('%d.%m.%Y'),
                time=f'{booking.start_time.strftime("%H:%M")} - {booking.end_time.strftime("%H:%M")}',
                trainer_name=trainer_name,
                booking_id=str(booking.id),
            )
            await self._update.callback_query.edit_message_text(
                text,
                reply_markup=InlineKeyboardMarkup(
                    [[InlineKeyboardButton(self._messages.btn_back_to_main_menu, callback_data='main_menu')]],
                ),
            )
            if booked_trainer and not is_trainer_booking and booked_trainer.user.telegram_user_id != self._user_id:
                try:
                    student_name = (
                        self._update.callback_query.from_user.full_name
                        if self._update.callback_query.from_user
                        else self._messages.fallback_student_name
                    )
                    notify_text = self._messages.booking_new_notification(
                        student_name=student_name,
                        court_name=court_name,
                        date=booking.start_time.strftime('%d.%m.%Y'),
                        time=f'{booking.start_time.strftime("%H:%M")} - {booking.end_time.strftime("%H:%M")}',
                    )
                    notify_text += self._messages.booking_new_notification_schedule_header
                    slots = self._deps.schedule_service.get_available_time_slots(
                        court_id=self._args.court_id,
                        date=booking.start_time,
                    )
                    for slot in sorted(slots, key=lambda s: s.start_time):
                        time_range = f'{slot.start_time.strftime("%H:%M")}-{slot.end_time.strftime("%H:%M")}'
                        if slot.is_available:
                            line = f'✅ {time_range}'
                        else:
                            slot_info = time_range
                            if slot.booking_id:
                                slot_booking = self._deps.booking_repo.get(slot.booking_id)
                                if slot_booking:
                                    if slot_booking.student and slot_booking.student.user:
                                        slot_info += f' ({slot_booking.student.user.name})'
                                    if slot_booking.trainer:
                                        slot_info += f' 👨‍🏫 {slot_booking.trainer.user.name}'
                            line = f'❌ {slot_info}'
                        if slot.booking_id == booking.id:
                            line = f'➡️ {line}'
                        notify_text += f'{line}\n'
                    await self._context.bot.send_message(
                        chat_id=booked_trainer.user.telegram_user_id,
                        text=notify_text,
                        reply_markup=InlineKeyboardMarkup(
                            [[InlineKeyboardButton(self._messages.btn_main_menu, callback_data='main_menu')]],
                        ),
                    )
                except Exception as e:
                    logger.warning(f'Failed to notify trainer: {e}')
        else:
            await self._update.callback_query.edit_message_text(
                self._messages.booking_slot_unavailable,
                reply_markup=InlineKeyboardMarkup(
                    [[InlineKeyboardButton(self._messages.btn_back_to_main_menu, callback_data='main_menu')]],
                ),
            )

    async def _on_error(self, error: Exception) -> None:
        logger.exception('Failed to create booking')
        assert self._update.callback_query is not None
        await self._update.callback_query.edit_message_text(
            self._messages.booking_generic_error,
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton(self._messages.btn_back_to_main_menu, callback_data='main_menu')]],
            ),
        )
