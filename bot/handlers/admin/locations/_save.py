import logging

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from bot.deps import get_deps
from bot.handlers.admin._utils import _clear_admin_state
from bot.handlers.auth import _log_user_action
from db.models import Location
from localization.base import Messages

logger = logging.getLogger(__name__)


async def _save_location(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    assert update.message is not None
    assert context.user_data is not None
    deps = get_deps(context)
    msgs = Messages.get_for_language((update.effective_user.language_code or '') if update.effective_user else '')
    location_name = context.user_data.get('admin_location_name', 'Unknown')
    maps_link = context.user_data.get('admin_location_maps_link')
    _clear_admin_state(context)
    try:
        location = Location(
            name=location_name,
            maps_link=maps_link,
        )
        deps.location_repo.save(location)
        if update.effective_user:
            _log_user_action(update.effective_user, f'created location: {location_name}')
        text = msgs.admin_location_created(name=location_name)
        if maps_link:
            text += f'\n🗺️ <a href="{maps_link}">Google Maps</a>'
        await update.message.reply_text(
            text,
            reply_markup=InlineKeyboardMarkup(
                [
                    [InlineKeyboardButton(msgs.btn_create_another, callback_data='admin_create_location')],
                    [InlineKeyboardButton(msgs.btn_back_to_locations, callback_data='admin_locations')],
                    [InlineKeyboardButton(msgs.btn_main_menu, callback_data='main_menu')],
                ],
            ),
            parse_mode='HTML',
            disable_web_page_preview=True,
        )
    except Exception:
        logger.exception('Failed to create location')
        await update.message.reply_text(
            msgs.admin_location_create_error,
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton(msgs.btn_back_to_locations, callback_data='admin_locations')]],
            ),
        )
