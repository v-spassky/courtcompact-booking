import logging

from telegram import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from bot.deps import get_deps
from bot.handlers.booking._utils import _create_booking_calendar
from config.settings import now_kiev
from localization import get_messages

logger = logging.getLogger(__name__)


async def _handle_court_selection_for_booking(
    update: Update, context: ContextTypes.DEFAULT_TYPE, query: CallbackQuery, data: str, user_id: int
) -> None:
    msgs = get_messages()
    deps = get_deps(context)
    court_id = data.split('_')[2]

    try:
        court = deps.court_repo.get(court_id)
        court_name = court.name if court else 'Неизвестный корт'

        user_trainer = deps.trainer_repo.get_by_telegram_id(user_id)
        if user_trainer:
            now = now_kiev()
            calendar_markup = _create_booking_calendar(now.year, now.month, court_id, user_trainer.id, deps)

            text = msgs.booking_select_date(court_name=court_name, trainer_name=user_trainer.name)

            await query.edit_message_text(text, reply_markup=calendar_markup)
            return

        trainers = deps.trainer_repo.get_all()

        keyboard = []
        keyboard.append(
            [InlineKeyboardButton(msgs.btn_no_trainer, callback_data=f'select_trainer_none_{str(court_id)[:8]}')]
        )

        for trainer in trainers:
            button_text = f'👨‍🏫 {trainer.name}'
            keyboard.append(
                [
                    InlineKeyboardButton(
                        button_text, callback_data=f'select_trainer_{str(trainer.id)[:8]}_{str(court_id)[:8]}'
                    )
                ]
            )

        keyboard.append([InlineKeyboardButton(msgs.btn_back_to_main_menu, callback_data='main_menu')])
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(msgs.booking_select_trainer(court_name=court_name), reply_markup=reply_markup)
    except Exception:
        logger.exception('Failed to show trainer selection')
        await query.edit_message_text(msgs.generic_error)
