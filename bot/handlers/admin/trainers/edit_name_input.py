import logging

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from bot.deps import get_deps
from bot.handlers.admin._utils import _clear_admin_state
from localization import get_messages

logger = logging.getLogger(__name__)


async def _handle_admin_edit_trainer_name_input(update: Update, context: ContextTypes.DEFAULT_TYPE, name: str) -> None:
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

    if name.strip() != '-':
        if len(name) < 1 or len(name) > 100:
            text = '❌ Имя должно быть от 1 до 100 символов. Попробуйте снова.'
            keyboard = [[InlineKeyboardButton(msgs.btn_cancel, callback_data='admin_trainers')]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text(text, reply_markup=reply_markup)
            return
        context.user_data['admin_trainer_name'] = name.strip()
    else:
        context.user_data['admin_trainer_name'] = trainer.name

    context.user_data['admin_state'] = 'awaiting_edit_trainer_telegram_id'

    text = f"""✏️ Редактирование тренера

Новое имя: {context.user_data['admin_trainer_name']}
Текущий Telegram ID: {trainer.telegram_user_id}

Шаг 2/3: Введите новый Telegram ID (или "-" чтобы оставить текущий):"""

    keyboard = [[InlineKeyboardButton(msgs.btn_cancel, callback_data='admin_trainers')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(text, reply_markup=reply_markup)
