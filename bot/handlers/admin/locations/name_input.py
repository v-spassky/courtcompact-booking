import logging

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from localization import get_messages

logger = logging.getLogger(__name__)


async def _handle_admin_location_name_input(update: Update, context: ContextTypes.DEFAULT_TYPE, name: str) -> None:
    assert update.message is not None
    assert context.user_data is not None
    msgs = get_messages()

    if len(name) < 1 or len(name) > 100:
        text = '❌ Название локации должно быть от 1 до 100 символов. Попробуйте снова.'
        keyboard = [
            [InlineKeyboardButton('🔄 Попробовать снова', callback_data='admin_create_location')],
            [InlineKeyboardButton(msgs.btn_cancel, callback_data='admin_locations')],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(text, reply_markup=reply_markup)
        context.user_data.pop('admin_state', None)
        return

    context.user_data['admin_location_name'] = name
    context.user_data['admin_state'] = 'awaiting_location_maps_link'

    text = f"""📍 Создание локации

Название: {name}

Шаг 2/2: Отправьте ссылку на Google Maps или "-" чтобы пропустить:

💡 Откройте нужную локацию в Google Maps и скопируйте ссылку из адресной строки"""

    keyboard = [[InlineKeyboardButton(msgs.btn_cancel, callback_data='admin_locations')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(text, reply_markup=reply_markup)
