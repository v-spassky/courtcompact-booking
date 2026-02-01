import logging

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from localization import get_messages

logger = logging.getLogger(__name__)


async def _handle_admin_trainer_name_input(update: Update, context: ContextTypes.DEFAULT_TYPE, name: str) -> None:
    assert update.message is not None
    assert context.user_data is not None
    msgs = get_messages()

    if len(name) < 1 or len(name) > 100:
        text = '❌ Имя тренера должно быть от 1 до 100 символов. Попробуйте снова.'
        keyboard = [
            [InlineKeyboardButton('🔄 Попробовать снова', callback_data='admin_create_trainer')],
            [InlineKeyboardButton(msgs.btn_cancel, callback_data='admin_trainers')],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(text, reply_markup=reply_markup)
        context.user_data.pop('admin_state', None)
        return

    context.user_data['admin_trainer_name'] = name
    context.user_data['admin_state'] = 'awaiting_trainer_telegram_id'

    text = f"""👨‍🏫 Создание тренера

Имя: {name}

Шаг 2/4: Введите Telegram ID тренера (число):

💡 Тренер может узнать свой ID, написав боту @userinfobot"""

    keyboard = [[InlineKeyboardButton(msgs.btn_cancel, callback_data='admin_trainers')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(text, reply_markup=reply_markup)
