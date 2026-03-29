import logging

from telegram import Update
from telegram.ext import ContextTypes

from bot.deps import get_deps
from bot.handlers.booking._utils import _create_booking_calendar
from localization import get_messages

logger = logging.getLogger(__name__)


async def _handle_booking_calendar_navigation(update: Update, context: ContextTypes.DEFAULT_TYPE, data: str) -> None:
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

        courts = deps.court_repo.get_all()
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

        calendar_markup = _create_booking_calendar(year, month, court_id or '', trainer_id, deps)

        text = msgs.booking_select_date(court_name=court_name, trainer_name=trainer_name)

        await update.callback_query.edit_message_text(text, reply_markup=calendar_markup)
    except Exception:
        logger.exception('Failed to navigate booking calendar')
        await update.callback_query.edit_message_text(msgs.generic_error)
