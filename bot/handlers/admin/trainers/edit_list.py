import logging

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from bot.deps import get_deps
from bot.handlers.admin._utils import _clear_admin_state
from bot.handlers.auth import _is_admin
from localization import get_messages

logger = logging.getLogger(__name__)


async def _handle_admin_edit_trainer_list(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.callback_query or not update.effective_user:
        return

    msgs = get_messages()
    deps = get_deps(context)

    if not _is_admin(update.effective_user.id):
        await update.callback_query.edit_message_text(msgs.admin_no_access)
        return

    _clear_admin_state(context)
    trainers = deps.trainer_repo.get_all()

    if not trainers:
        keyboard = [[InlineKeyboardButton(msgs.btn_back, callback_data='admin_trainers')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.callback_query.edit_message_text(msgs.admin_trainer_no_trainers, reply_markup=reply_markup)
        return

    keyboard = []
    for trainer in trainers:
        trainer_id_short = str(trainer.id)[:8]
        keyboard.append(
            [InlineKeyboardButton(f'👨‍🏫 {trainer.name}', callback_data=f'admin_edit_trainer_{trainer_id_short}')]
        )
    keyboard.append([InlineKeyboardButton(msgs.btn_back, callback_data='admin_trainers')])
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.callback_query.edit_message_text(msgs.admin_trainer_select_to_edit, reply_markup=reply_markup)
