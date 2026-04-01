import logging
from datetime import datetime

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from bot.deps import Deps
from bot.handlers.base import Handler
from bot.handlers.callback_args import BookDateArg, BookSlotArg

logger = logging.getLogger(__name__)


class BookingDateSelection(Handler):
    def __init__(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
        deps: Deps,
        args: BookDateArg,
    ) -> None:
        super().__init__(update, context, deps)
        self._args = args

    async def _authorize(self) -> bool:
        return True

    async def _process(self) -> None:
        assert self._update.callback_query is not None
        selected_date = datetime(self._args.year, self._args.month, self._args.day)
        court_obj = self._deps.court_repo.get(self._args.court_id)
        court_name = court_obj.name if court_obj else self._messages.unknown_court
        trainer_name = None
        if self._args.trainer_id is not None:
            trainer = self._deps.trainer_repo.get(self._args.trainer_id)
            if trainer:
                trainer_name = trainer.user.name
        time_slots = self._deps.schedule_service.get_all_time_slots_for_date(selected_date)
        court_slots = [slot for slot in time_slots if slot.court_id == self._args.court_id]
        trainer_busy_times = set()
        if self._args.trainer_id:
            all_slots = self._deps.schedule_service.get_all_time_slots_for_date(selected_date)
            for other_slot in all_slots:
                if not other_slot.is_available and other_slot.booking_id:
                    booking = self._deps.booking_repo.get(other_slot.booking_id)
                    if booking and booking.trainer_id == self._args.trainer_id:
                        trainer_busy_times.add((booking.start_time, booking.end_time))
        if not court_slots:
            await self._update.callback_query.edit_message_text(
                self._messages.booking_no_slots_for_date,
                reply_markup=InlineKeyboardMarkup(
                    [[InlineKeyboardButton(self._messages.btn_back_to_main_menu, callback_data='main_menu')]],
                ),
            )
            return
        text = self._messages.booking_select_slot(
            court_name=court_name,
            date=selected_date.strftime('%d.%m.%Y'),
            trainer_name=trainer_name,
        )
        buttons = []
        for slot in sorted(court_slots, key=lambda s: s.start_time):
            is_available = slot.is_available
            if is_available and self._args.trainer_id:
                for busy_start, busy_end in trainer_busy_times:
                    if slot.start_time < busy_end and slot.end_time > busy_start:
                        is_available = False
                        break
            if is_available:
                time_str = f'{slot.start_time.strftime("%H:%M")}-{slot.end_time.strftime("%H:%M")}'
                slot_callback = BookSlotArg(
                    court_id=self._args.court_id,
                    trainer_id=self._args.trainer_id,
                    year=self._args.year,
                    month=self._args.month,
                    day=self._args.day,
                    hour=slot.start_time.hour,
                    minute=slot.start_time.minute,
                ).to_callback_data()
            else:
                time_str = self._messages.slot_occupied
                slot_callback = 'ignore'
            buttons.append(InlineKeyboardButton(time_str, callback_data=slot_callback))
        keyboard = []
        for i in range(0, len(buttons), 2):
            row = [buttons[i]]
            if i + 1 < len(buttons):
                row.append(buttons[i + 1])
            keyboard.append(row)
        keyboard.append([InlineKeyboardButton(self._messages.btn_back_to_main_menu, callback_data='main_menu')])
        await self._update.callback_query.edit_message_text(
            text,
            reply_markup=InlineKeyboardMarkup(keyboard),
        )

    async def _on_error(self, error: Exception) -> None:
        logger.exception('Failed to show time slots')
        assert self._update.callback_query is not None
        await self._update.callback_query.edit_message_text(self._messages.generic_error)
