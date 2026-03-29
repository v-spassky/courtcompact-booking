import logging

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from bot.deps import get_deps
from bot.handlers.admin._utils import _clear_admin_state
from localization import get_messages

logger = logging.getLogger(__name__)


async def _handle_admin_edit_court_name_input(update: Update, context: ContextTypes.DEFAULT_TYPE, name: str) -> None:
    assert update.message is not None
    assert context.user_data is not None
    msgs = get_messages()
    deps = get_deps(context)
    court_id = context.user_data.get('admin_court_id')
    if not court_id:
        _clear_admin_state(context)
        return

    court = deps.court_repo.get(court_id)
    if not court:
        _clear_admin_state(context)
        return

    if name.strip() != '-':
        if len(name) < 1 or len(name) > 100:
            text = msgs.admin_court_name_too_long_edit
            keyboard = [[InlineKeyboardButton(msgs.btn_cancel, callback_data='admin_courts')]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text(text, reply_markup=reply_markup)
            return
        context.user_data['admin_court_name'] = name.strip()
    else:
        context.user_data['admin_court_name'] = court.name

    context.user_data['admin_state'] = 'awaiting_edit_court_description'

    new_name = context.user_data['admin_court_name']
    text = msgs.admin_court_edit_step2(name=new_name, description=court.description)

    keyboard = [[InlineKeyboardButton(msgs.btn_cancel, callback_data='admin_courts')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(text, reply_markup=reply_markup)
