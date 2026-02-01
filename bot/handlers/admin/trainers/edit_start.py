import logging

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from bot.deps import get_deps
from bot.handlers.admin._utils import _clear_admin_state
from bot.handlers.auth import _is_admin
from localization import get_messages

logger = logging.getLogger(__name__)


async def _handle_admin_edit_trainer_start(update: Update, context: ContextTypes.DEFAULT_TYPE, data: str) -> None:
    if not update.callback_query or not update.effective_user:
        return

    msgs = get_messages()
    deps = get_deps(context)

    if not _is_admin(update.effective_user.id):
        await update.callback_query.edit_message_text(msgs.admin_no_access)
        return

    trainer_id_short = data.replace('admin_edit_trainer_', '')

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

    _clear_admin_state(context)
    assert context.user_data is not None
    context.user_data['admin_trainer_id'] = str(trainer.id)
    context.user_data['admin_state'] = 'awaiting_edit_trainer_name'

    desc_text = trainer.description if trainer.description else '(не указано)'

    text = f"""✏️ Редактирование тренера

Текущие данные:
👨‍🏫 Имя: {trainer.name}
🆔 Telegram ID: {trainer.telegram_user_id}
📝 Описание: {desc_text}

Шаг 1/3: Введите новое имя (или "-" чтобы оставить текущее):"""

    keyboard = [[InlineKeyboardButton(msgs.btn_cancel, callback_data='admin_trainers')]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.callback_query.edit_message_text(text, reply_markup=reply_markup)
