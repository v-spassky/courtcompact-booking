import logging

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from bot.deps import get_deps
from bot.handlers.auth import _is_admin, _log_user_action
from localization import get_messages

logger = logging.getLogger(__name__)


async def _handle_admin_delete_trainer_execute(update: Update, context: ContextTypes.DEFAULT_TYPE, data: str) -> None:
    if not update.callback_query or not update.effective_user:
        return

    msgs = get_messages()
    deps = get_deps(context)

    if not _is_admin(update.effective_user.id):
        await update.callback_query.edit_message_text(msgs.admin_no_access)
        return

    trainer_id_short = data.replace('admin_confirm_delete_trainer_', '')

    trainers = deps.trainer_repo.get_all()
    trainer = None
    for t in trainers:
        if str(t.id).startswith(trainer_id_short):
            trainer = t
            break

    if not trainer:
        keyboard = [[InlineKeyboardButton(msgs.btn_back, callback_data='admin_trainers')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.callback_query.edit_message_text('❌ Тренер не найден.', reply_markup=reply_markup)
        return

    try:
        trainer_name = trainer.name
        deps.trainer_repo.delete(trainer.id)
        _log_user_action(update.effective_user, f'deleted trainer: {trainer_name}')

        text = msgs.admin_trainer_deleted(name=trainer_name)
        keyboard = [[InlineKeyboardButton('◀️ К тренерам', callback_data='admin_trainers')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.callback_query.edit_message_text(text, reply_markup=reply_markup)

    except Exception:
        logger.exception('Failed to delete trainer')
        keyboard = [[InlineKeyboardButton('◀️ К тренерам', callback_data='admin_trainers')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.callback_query.edit_message_text(msgs.admin_trainer_delete_error, reply_markup=reply_markup)
