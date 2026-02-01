import logging
from uuid import uuid4

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from bot.deps import get_deps
from bot.handlers.admin._utils import _clear_admin_state
from bot.handlers.auth import _log_user_action
from db.models import Location
from localization import get_messages

logger = logging.getLogger(__name__)


async def _save_location(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    assert update.message is not None
    assert context.user_data is not None
    msgs = get_messages()
    deps = get_deps(context)
    location_name = context.user_data.get('admin_location_name', 'Unknown')
    google_maps_link = context.user_data.get('admin_location_maps_link')

    _clear_admin_state(context)

    try:
        location = Location(
            id=str(uuid4()),
            name=location_name,
            google_maps_link=google_maps_link,
            is_active=True,
        )
        deps.location_repo.save(location)

        if update.effective_user:
            _log_user_action(update.effective_user, f'created location: {location_name}')

        text = msgs.admin_location_created(name=location_name)
        if google_maps_link:
            text += f'\n🗺️ <a href="{google_maps_link}">Google Maps</a>'

        keyboard = [
            [InlineKeyboardButton('➕ Создать ещё', callback_data='admin_create_location')],
            [InlineKeyboardButton('◀️ К локациям', callback_data='admin_locations')],
            [InlineKeyboardButton(msgs.btn_main_menu, callback_data='main_menu')],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            text, reply_markup=reply_markup, parse_mode='HTML', disable_web_page_preview=True
        )

    except Exception:
        logger.exception('Failed to create location')
        keyboard = [[InlineKeyboardButton('◀️ К локациям', callback_data='admin_locations')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(msgs.admin_location_create_error, reply_markup=reply_markup)
