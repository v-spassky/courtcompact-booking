import logging
from uuid import UUID

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from bot.deps import Deps
from bot.handlers.auth import _log_user_action
from bot.handlers.base import Handler
from localization import get_messages

logger = logging.getLogger(__name__)


class BookingCancellation(Handler):
    def __init__(
        self, update: Update, context: ContextTypes.DEFAULT_TYPE, deps: Deps, callback_data: str, user_id: int
    ) -> None:
        super().__init__(update, context, deps)
        self._callback_data = callback_data
        self._user_id = user_id

    async def _authorize(self) -> bool:
        return True

    async def _process(self) -> None:
        assert self._update.callback_query is not None
        msgs = get_messages()
        booking_id = UUID(self._callback_data.split('_')[2])
        booking = self._deps.booking_repo.get(booking_id)
        if not booking:
            keyboard = [[InlineKeyboardButton(msgs.btn_back_to_main_menu, callback_data='main_menu')]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await self._update.callback_query.edit_message_text(msgs.booking_not_found, reply_markup=reply_markup)
            return
        court_name = booking.court.name if booking.court else msgs.unknown_court
        student = booking.student
        trainer = booking.trainer
        is_student_cancelling = student and student.user and student.user.telegram_user_id == self._user_id
        is_trainer_cancelling = trainer and trainer.user.telegram_user_id == self._user_id
        success = self._deps.booking_service.cancel_booking(booking_id, self._user_id)
        keyboard = [[InlineKeyboardButton(msgs.btn_back_to_main_menu, callback_data='main_menu')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        if success:
            _log_user_action(self._update.callback_query.from_user, f'cancelled booking: {booking_id}')
            await self._update.callback_query.edit_message_text(msgs.booking_cancelled, reply_markup=reply_markup)
            notify_text = msgs.booking_cancelled_notification(
                court_name=court_name,
                date=booking.start_time.strftime('%d.%m.%Y'),
                time=f'{booking.start_time.strftime("%H:%M")} - {booking.end_time.strftime("%H:%M")}',
            )
            try:
                notify_keyboard = [[InlineKeyboardButton(msgs.btn_main_menu, callback_data='main_menu')]]
                notify_markup = InlineKeyboardMarkup(notify_keyboard)
                if is_student_cancelling and trainer and trainer.user.telegram_user_id != self._user_id:
                    student_name = (
                        self._update.callback_query.from_user.full_name
                        if self._update.callback_query.from_user
                        else msgs.fallback_student_name
                    )
                    notify_text += msgs.booking_cancelled_by_student(student_name=student_name)
                    await self._context.bot.send_message(
                        chat_id=trainer.user.telegram_user_id, text=notify_text, reply_markup=notify_markup
                    )
                elif (
                    is_trainer_cancelling
                    and student
                    and student.user
                    and student.user.telegram_user_id != self._user_id
                ):
                    trainer_name = trainer.user.name if trainer else msgs.fallback_trainer_name
                    notify_text += msgs.booking_cancelled_by_trainer(trainer_name=trainer_name)
                    await self._context.bot.send_message(
                        chat_id=student.user.telegram_user_id, text=notify_text, reply_markup=notify_markup
                    )
            except Exception as e:
                logger.warning(f'Failed to send cancellation notification: {e}')
        else:
            await self._update.callback_query.edit_message_text(
                msgs.cancel_booking_failed,
                reply_markup=reply_markup,
            )

    async def _on_error(self, error: Exception) -> None:
        logger.exception('Failed to cancel booking')
        msgs = get_messages()
        assert self._update.callback_query is not None
        keyboard = [[InlineKeyboardButton(msgs.btn_back_to_main_menu, callback_data='main_menu')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await self._update.callback_query.edit_message_text(msgs.cancel_booking_error, reply_markup=reply_markup)
