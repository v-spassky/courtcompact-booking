import logging
from uuid import uuid4

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from bot.deps import get_deps
from bot.handlers.admin._utils import _clear_admin_state
from bot.handlers.auth import _log_user_action
from db.models import Trainer
from localization import get_messages

logger = logging.getLogger(__name__)


async def _handle_admin_trainer_description_input(
    update: Update, context: ContextTypes.DEFAULT_TYPE, desc_text: str
) -> None:
    assert update.message is not None
    assert context.user_data is not None
    msgs = get_messages()
    deps = get_deps(context)
    trainer_name = context.user_data.get('admin_trainer_name', 'Unknown')
    telegram_id = context.user_data.get('admin_trainer_telegram_id', 0)

    _clear_admin_state(context)

    description = None if desc_text.strip() == '-' else desc_text.strip()

    try:
        trainer = Trainer(
            id=str(uuid4()),
            telegram_user_id=telegram_id,
            name=trainer_name,
            description=description,
        )
        deps.trainer_repo.save(trainer)

        if update.effective_user:
            _log_user_action(update.effective_user, f'created trainer: {trainer_name} (ID: {telegram_id})')

        text = msgs.admin_trainer_created(name=trainer_name)
        text += f'\n🆔 Telegram ID: {telegram_id}\n'
        if description:
            text += f'📝 Описание: {description}\n'

        keyboard = [
            [InlineKeyboardButton('➕ Создать ещё', callback_data='admin_create_trainer')],
            [InlineKeyboardButton('◀️ К тренерам', callback_data='admin_trainers')],
            [InlineKeyboardButton(msgs.btn_main_menu, callback_data='main_menu')],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(text, reply_markup=reply_markup)

    except Exception:
        logger.exception('Failed to create trainer')
        keyboard = [[InlineKeyboardButton('◀️ К тренерам', callback_data='admin_trainers')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(msgs.admin_trainer_create_error, reply_markup=reply_markup)
