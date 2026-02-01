import logging

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from bot.deps import get_deps
from bot.handlers.admin._utils import _clear_admin_state
from bot.handlers.auth import _log_user_action
from localization import get_messages

logger = logging.getLogger(__name__)


async def _handle_admin_edit_trainer_description_input(
    update: Update, context: ContextTypes.DEFAULT_TYPE, desc_text: str
) -> None:
    assert update.message is not None
    assert context.user_data is not None
    msgs = get_messages()
    deps = get_deps(context)
    trainer_id = context.user_data.get('admin_trainer_id')
    if not trainer_id:
        _clear_admin_state(context)
        return

    trainers = deps.trainer_repo.get_all()
    trainer = None
    for t in trainers:
        if str(t.id) == trainer_id:
            trainer = t
            break

    if not trainer:
        _clear_admin_state(context)
        return

    new_name = context.user_data.get('admin_trainer_name', trainer.name)
    new_telegram_id = context.user_data.get('admin_trainer_telegram_id', trainer.telegram_user_id)

    if desc_text.strip() == '-':
        new_description = trainer.description
    elif desc_text.strip() == '--':
        new_description = None
    else:
        new_description = desc_text.strip()

    _clear_admin_state(context)

    try:
        trainer.name = new_name
        trainer.telegram_user_id = new_telegram_id
        trainer.description = new_description

        deps.trainer_repo.save(trainer)
        if update.effective_user:
            _log_user_action(update.effective_user, f'edited trainer: {trainer.name}')

        text = msgs.admin_trainer_updated(name=trainer.name)
        keyboard = [
            [InlineKeyboardButton('✏️ Редактировать ещё', callback_data='admin_edit_trainer')],
            [InlineKeyboardButton('◀️ К тренерам', callback_data='admin_trainers')],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(text, reply_markup=reply_markup)

    except Exception:
        logger.exception('Failed to edit trainer')
        keyboard = [[InlineKeyboardButton('◀️ К тренерам', callback_data='admin_trainers')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(msgs.admin_trainer_update_error, reply_markup=reply_markup)
