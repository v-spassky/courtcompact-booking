import logging

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from bot.deps import get_deps
from localization import get_messages

logger = logging.getLogger(__name__)


async def _handle_admin_court_name_input(update: Update, context: ContextTypes.DEFAULT_TYPE, name: str) -> None:
    assert update.message is not None
    assert context.user_data is not None
    msgs = get_messages()
    deps = get_deps(context)

    if len(name) < 1 or len(name) > 100:
        text = '❌ Название корта должно быть от 1 до 100 символов. Попробуйте снова.'
        keyboard = [
            [InlineKeyboardButton('🔄 Попробовать снова', callback_data='admin_create_court')],
            [InlineKeyboardButton(msgs.btn_cancel, callback_data='admin_courts')],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(text, reply_markup=reply_markup)
        context.user_data.pop('admin_state', None)
        return

    context.user_data['admin_court_name'] = name
    context.user_data['admin_state'] = 'awaiting_court_description'

    location_id = context.user_data.get('admin_court_location_id')
    location_name = 'Не указана'
    if location_id:
        location = deps.location_repo.get(location_id)
        if location:
            location_name = location.name

    text = f"""🎾 Создание корта

📍 Локация: {location_name}
Название: {name}

Шаг 3/3: Введите описание корта (или отправьте "-" чтобы пропустить):"""

    keyboard = [[InlineKeyboardButton(msgs.btn_cancel, callback_data='admin_courts')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(text, reply_markup=reply_markup)
