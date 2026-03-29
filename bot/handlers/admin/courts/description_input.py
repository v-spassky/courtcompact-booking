import logging
from uuid import uuid4

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from bot.deps import get_deps
from bot.handlers.admin._utils import _clear_admin_state
from bot.handlers.auth import _log_user_action
from db.models import Court
from localization import get_messages

logger = logging.getLogger(__name__)


async def _handle_admin_court_description_input(
    update: Update, context: ContextTypes.DEFAULT_TYPE, description: str
) -> None:
    assert update.message is not None
    assert context.user_data is not None
    msgs = get_messages()
    deps = get_deps(context)
    court_name = context.user_data.get('admin_court_name', 'Unknown')
    location_id = context.user_data.get('admin_court_location_id')

    _clear_admin_state(context)

    court_description = None if description.strip() == '-' else description.strip()

    try:
        court = Court(
            id=str(uuid4()),
            name=court_name,
            description=court_description,
            location_id=location_id,
        )
        deps.court_repo.save(court)

        if update.effective_user:
            _log_user_action(update.effective_user, f'created court: {court_name}')

        text = msgs.admin_court_created(name=court_name)

        if location_id:
            location = deps.location_repo.get(location_id)
            if location:
                text += msgs.admin_court_location_line(name=location.name)

        if court_description:
            text += msgs.admin_court_description_line(desc=court_description)

        keyboard = [
            [InlineKeyboardButton(msgs.btn_create_another, callback_data='admin_create_court')],
            [InlineKeyboardButton(msgs.btn_back_to_courts, callback_data='admin_courts')],
            [InlineKeyboardButton(msgs.btn_main_menu, callback_data='main_menu')],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(text, reply_markup=reply_markup)

    except Exception:
        logger.exception('Failed to create court')
        keyboard = [[InlineKeyboardButton(msgs.btn_back_to_courts, callback_data='admin_courts')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(msgs.admin_court_create_error, reply_markup=reply_markup)
