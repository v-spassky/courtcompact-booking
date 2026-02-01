import logging

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from localization import get_messages

logger = logging.getLogger(__name__)


async def _handle_admin_student_name_input(update: Update, context: ContextTypes.DEFAULT_TYPE, name: str) -> None:
    assert update.message is not None
    assert context.user_data is not None
    msgs = get_messages()

    if not name or name == '-':
        context.user_data.pop('admin_state', None)
        text = '❌ Имя ученика не может быть пустым.'
        keyboard = [
            [InlineKeyboardButton('🔄 Попробовать снова', callback_data='admin_create_student')],
            [InlineKeyboardButton(msgs.btn_cancel, callback_data='admin_students')],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(text, reply_markup=reply_markup)
        return

    context.user_data['admin_student_name'] = name
    context.user_data['admin_state'] = 'awaiting_student_phone'

    text = f"""👥 Создание ученика

Имя: {name}

Шаг 2/2: Введите номер телефона ученика (например, +7 999 123 45 67):"""

    keyboard = [[InlineKeyboardButton(msgs.btn_cancel, callback_data='admin_students')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(text, reply_markup=reply_markup)
