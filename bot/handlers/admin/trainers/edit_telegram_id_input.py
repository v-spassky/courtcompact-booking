import logging

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from bot.deps import get_deps
from bot.handlers.admin._utils import _clear_admin_state
from localization import get_messages

logger = logging.getLogger(__name__)


async def _handle_admin_edit_trainer_id_input(update: Update, context: ContextTypes.DEFAULT_TYPE, id_text: str) -> None:
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

    if id_text.strip() != '-':
        try:
            telegram_id = int(id_text.strip())
            existing = deps.trainer_repo.get_by_telegram_id(telegram_id)
            if existing and str(existing.id) != trainer_id:
                text = f'❌ Этот Telegram ID уже используется тренером {existing.name}.'
                keyboard = [[InlineKeyboardButton(msgs.btn_cancel, callback_data='admin_trainers')]]
                reply_markup = InlineKeyboardMarkup(keyboard)
                await update.message.reply_text(text, reply_markup=reply_markup)
                return
            context.user_data['admin_trainer_telegram_id'] = telegram_id
        except ValueError:
            text = '❌ Telegram ID должен быть числом.'
            keyboard = [[InlineKeyboardButton(msgs.btn_cancel, callback_data='admin_trainers')]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text(text, reply_markup=reply_markup)
            return
    else:
        context.user_data['admin_trainer_telegram_id'] = trainer.telegram_user_id

    context.user_data['admin_state'] = 'awaiting_edit_trainer_description'

    desc_text = trainer.description if trainer.description else '(не указано)'

    text = f"""✏️ Редактирование тренера

Имя: {context.user_data['admin_trainer_name']}
Telegram ID: {context.user_data['admin_trainer_telegram_id']}
Текущее описание: {desc_text}

Шаг 3/3: Введите новое описание (или "-" чтобы оставить, "--" чтобы очистить):"""

    keyboard = [[InlineKeyboardButton(msgs.btn_cancel, callback_data='admin_trainers')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(text, reply_markup=reply_markup)
