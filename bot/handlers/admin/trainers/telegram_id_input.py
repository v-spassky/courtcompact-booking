import logging

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from bot.deps import get_deps
from localization import get_messages

logger = logging.getLogger(__name__)


async def _handle_admin_trainer_id_input(update: Update, context: ContextTypes.DEFAULT_TYPE, id_text: str) -> None:
    assert update.message is not None
    assert context.user_data is not None
    msgs = get_messages()
    deps = get_deps(context)
    trainer_name = context.user_data.get('admin_trainer_name', 'Unknown')

    try:
        telegram_id = int(id_text.strip())
    except ValueError:
        text = msgs.admin_trainer_id_not_a_number
        keyboard = [
            [InlineKeyboardButton(msgs.btn_retry, callback_data='admin_create_trainer')],
            [InlineKeyboardButton(msgs.btn_cancel, callback_data='admin_trainers')],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(text, reply_markup=reply_markup)
        context.user_data.pop('admin_state', None)
        return

    existing = deps.trainer_repo.get_by_telegram_id(telegram_id)
    if existing:
        text = msgs.admin_trainer_id_exists(telegram_id=telegram_id, name=existing.name)
        keyboard = [
            [InlineKeyboardButton(msgs.btn_retry, callback_data='admin_create_trainer')],
            [InlineKeyboardButton(msgs.btn_back_to_trainers_list, callback_data='admin_trainers')],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(text, reply_markup=reply_markup)
        context.user_data.pop('admin_state', None)
        return

    context.user_data['admin_trainer_telegram_id'] = telegram_id
    context.user_data['admin_state'] = 'awaiting_trainer_description'

    text = msgs.admin_trainer_create_step3(name=trainer_name, telegram_id=telegram_id)

    keyboard = [[InlineKeyboardButton(msgs.btn_cancel, callback_data='admin_trainers')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(text, reply_markup=reply_markup)
