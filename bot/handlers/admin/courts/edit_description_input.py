import logging

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from bot.deps import get_deps
from bot.handlers.admin._utils import _clear_admin_state
from bot.handlers.auth import _log_user_action
from localization import get_messages

logger = logging.getLogger(__name__)


async def _handle_admin_edit_court_description_input(
    update: Update, context: ContextTypes.DEFAULT_TYPE, description: str
) -> None:
    assert update.message is not None
    assert context.user_data is not None
    msgs = get_messages()
    deps = get_deps(context)
    court_id = context.user_data.get('admin_court_id')
    new_name = context.user_data.get('admin_court_name')

    if not court_id:
        _clear_admin_state(context)
        return

    court = deps.court_repo.get(court_id)
    if not court:
        _clear_admin_state(context)
        return

    _clear_admin_state(context)

    try:
        if new_name is not None:
            court.name = new_name
        if description.strip() == '-':
            pass
        elif description.strip() == '--':
            court.description = None
        else:
            court.description = description.strip()

        deps.court_repo.save(court)
        if update.effective_user:
            _log_user_action(update.effective_user, f'edited court: {court.name}')

        text = msgs.admin_court_updated(name=court.name)
        keyboard = [
            [InlineKeyboardButton(msgs.btn_edit_another, callback_data='admin_edit_court')],
            [InlineKeyboardButton(msgs.btn_back_to_courts, callback_data='admin_courts')],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(text, reply_markup=reply_markup)

    except Exception:
        logger.exception('Failed to edit court')
        keyboard = [[InlineKeyboardButton(msgs.btn_back_to_courts, callback_data='admin_courts')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(msgs.admin_court_update_error, reply_markup=reply_markup)
