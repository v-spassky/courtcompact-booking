import logging

from telegram import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from bot.deps import get_deps
from bot.handlers.booking._utils import _create_booking_calendar
from config.settings import now_kiev
from localization import get_messages

logger = logging.getLogger(__name__)


async def _handle_trainer_selection_for_booking(
    update: Update, context: ContextTypes.DEFAULT_TYPE, query: CallbackQuery, data: str, user_id: int
) -> None:
    msgs = get_messages()
    deps = get_deps(context)
    parts = data.split('_')
    trainer_id_short = parts[2] if parts[2] != 'none' else None
    court_id_short = parts[3]

    try:
        courts = deps.court_repo.get_active()
        court_id: str | None = None
        for court in courts:
            if str(court.id).startswith(court_id_short):
                court_id = court.id
                break

        if not court_id:
            raise ValueError(f'Court not found for ID starting with {court_id_short}')

        trainer_id = None
        trainer_name = None
        if trainer_id_short and trainer_id_short != 'none':
            trainers = deps.trainer_repo.get_all()
            for trainer in trainers:
                if str(trainer.id).startswith(trainer_id_short):
                    trainer_id = trainer.id
                    trainer_name = trainer.name
                    break

        assert court_id is not None
        court_obj = deps.court_repo.get(court_id)
        court_name = court_obj.name if court_obj else 'Неизвестный корт'

        now = now_kiev()
        calendar_markup = _create_booking_calendar(now.year, now.month, court_id, trainer_id, deps)

        text = msgs.booking_select_date(court_name=court_name, trainer_name=trainer_name)

        await query.edit_message_text(text, reply_markup=calendar_markup)
    except Exception:
        logger.exception('Failed to show booking calendar')
        keyboard = [[InlineKeyboardButton(msgs.btn_back_to_main_menu, callback_data='main_menu')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(msgs.generic_error, reply_markup=reply_markup)
