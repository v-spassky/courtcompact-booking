import logging

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from bot.deps import Deps
from bot.handlers.auth import _log_user_action
from bot.handlers.base import Handler
from bot.handlers.callback_args import CancelBookingArg

logger = logging.getLogger(__name__)


class BookingCancellation(Handler):
    def __init__(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
        deps: Deps,
        args: CancelBookingArg,
        user_id: int,
    ) -> None:
        super().__init__(update, context, deps)
        self._args = args
        self._user_id = user_id

    async def _authorize(self) -> bool:
        return True

    async def _process(self) -> None:
        assert self._update.callback_query is not None
        booking = self._deps.booking_repo.get(self._args.booking_id)
        if not booking:
            await self._update.callback_query.edit_message_text(
                self._messages.booking_not_found,
                reply_markup=InlineKeyboardMarkup(
                    [[InlineKeyboardButton(self._messages.btn_back_to_main_menu, callback_data='main_menu')]],
                ),
            )
            return
        court_name = booking.court.name if booking.court else self._messages.unknown_court
        student = booking.student
        trainer = booking.trainer
        is_student_cancelling = student and student.user and student.user.telegram_user_id == self._user_id
        is_trainer_cancelling = trainer and trainer.user.telegram_user_id == self._user_id
        success = self._deps.booking_service.cancel_booking(self._args.booking_id, self._user_id)
        if success:
            _log_user_action(self._update.callback_query.from_user, f'cancelled booking: {self._args.booking_id}')
            await self._update.callback_query.edit_message_text(
                self._messages.booking_cancelled,
                reply_markup=InlineKeyboardMarkup(
                    [[InlineKeyboardButton(self._messages.btn_back_to_main_menu, callback_data='main_menu')]],
                ),
            )
            notify_text = self._messages.booking_cancelled_notification(
                court_name=court_name,
                date=booking.start_time.strftime('%d.%m.%Y'),
                time=f'{booking.start_time.strftime("%H:%M")} - {booking.end_time.strftime("%H:%M")}',
            )
            try:
                if is_student_cancelling and trainer and trainer.user.telegram_user_id != self._user_id:
                    student_name = (
                        self._update.callback_query.from_user.full_name
                        if self._update.callback_query.from_user
                        else self._messages.fallback_student_name
                    )
                    notify_text += self._messages.booking_cancelled_by_student(student_name=student_name)
                    await self._context.bot.send_message(
                        chat_id=trainer.user.telegram_user_id,
                        text=notify_text,
                        reply_markup=InlineKeyboardMarkup(
                            [[InlineKeyboardButton(self._messages.btn_main_menu, callback_data='main_menu')]],
                        ),
                    )
                elif (
                    is_trainer_cancelling
                    and student
                    and student.user
                    and student.user.telegram_user_id != self._user_id
                ):
                    trainer_name = trainer.user.name if trainer else self._messages.fallback_trainer_name
                    notify_text += self._messages.booking_cancelled_by_trainer(trainer_name=trainer_name)
                    await self._context.bot.send_message(
                        chat_id=student.user.telegram_user_id,
                        text=notify_text,
                        reply_markup=InlineKeyboardMarkup(
                            [[InlineKeyboardButton(self._messages.btn_main_menu, callback_data='main_menu')]],
                        ),
                    )
            except Exception as e:
                logger.warning(f'Failed to send cancellation notification: {e}')
        else:
            await self._update.callback_query.edit_message_text(
                self._messages.cancel_booking_failed,
                reply_markup=InlineKeyboardMarkup(
                    [[InlineKeyboardButton(self._messages.btn_back_to_main_menu, callback_data='main_menu')]],
                ),
            )

    async def _on_error(self, error: Exception) -> None:
        logger.exception('Failed to cancel booking')
        assert self._update.callback_query is not None
        await self._update.callback_query.edit_message_text(
            self._messages.cancel_booking_error,
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton(self._messages.btn_back_to_main_menu, callback_data='main_menu')]],
            ),
        )
