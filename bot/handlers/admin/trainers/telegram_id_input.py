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
        text = '❌ Telegram ID должен быть числом. Попробуйте снова.'
        keyboard = [
            [InlineKeyboardButton('🔄 Попробовать снова', callback_data='admin_create_trainer')],
            [InlineKeyboardButton(msgs.btn_cancel, callback_data='admin_trainers')],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(text, reply_markup=reply_markup)
        context.user_data.pop('admin_state', None)
        return

    existing = deps.trainer_repo.get_by_telegram_id(telegram_id)
    if existing:
        text = f'❌ Тренер с Telegram ID {telegram_id} уже существует ({existing.name}).'
        keyboard = [
            [InlineKeyboardButton('🔄 Попробовать снова', callback_data='admin_create_trainer')],
            [InlineKeyboardButton('◀️ К тренерам', callback_data='admin_trainers')],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(text, reply_markup=reply_markup)
        context.user_data.pop('admin_state', None)
        return

    context.user_data['admin_trainer_telegram_id'] = telegram_id
    context.user_data['admin_state'] = 'awaiting_trainer_description'

    text = f"""👨‍🏫 Создание тренера

Имя: {trainer_name}
Telegram ID: {telegram_id}

Шаг 3/3: Введите описание тренера (или "-" чтобы пропустить):"""

    keyboard = [[InlineKeyboardButton(msgs.btn_cancel, callback_data='admin_trainers')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(text, reply_markup=reply_markup)
