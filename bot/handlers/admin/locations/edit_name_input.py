import logging

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from bot.deps import get_deps
from bot.handlers.admin._utils import _clear_admin_state
from localization import get_messages

logger = logging.getLogger(__name__)


async def _handle_admin_edit_location_name_input(update: Update, context: ContextTypes.DEFAULT_TYPE, name: str) -> None:
    assert update.message is not None
    assert context.user_data is not None
    msgs = get_messages()
    deps = get_deps(context)
    location_id = context.user_data.get('admin_location_id')
    if not location_id:
        _clear_admin_state(context)
        return

    location = deps.location_repo.get(location_id)
    if not location:
        _clear_admin_state(context)
        return

    if name.strip() != '-':
        if len(name) < 1 or len(name) > 100:
            text = '❌ Название должно быть от 1 до 100 символов. Попробуйте снова.'
            keyboard = [[InlineKeyboardButton(msgs.btn_cancel, callback_data='admin_locations')]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text(text, reply_markup=reply_markup)
            return
        context.user_data['admin_location_name'] = name.strip()
    else:
        context.user_data['admin_location_name'] = location.name

    context.user_data['admin_state'] = 'awaiting_edit_location_maps_link'

    new_name = context.user_data['admin_location_name']
    current_link = location.google_maps_link if location.google_maps_link else '(не указана)'

    text = f"""✏️ Редактирование локации

Новое название: {new_name}
Текущая ссылка: {current_link}

Шаг 2/2: Отправьте новую ссылку Google Maps (или "-" оставить, "--" очистить):"""

    keyboard = [[InlineKeyboardButton(msgs.btn_cancel, callback_data='admin_locations')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(text, reply_markup=reply_markup)
