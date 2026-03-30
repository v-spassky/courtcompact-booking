import logging

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from bot.deps import get_deps
from bot.handlers.admin._utils import _clear_admin_state
from bot.handlers.auth import _log_user_action
from localization.base import Messages

logger = logging.getLogger(__name__)


async def _save_edited_location(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    assert update.message is not None
    assert context.user_data is not None
    deps = get_deps(context)
    msgs = Messages.get_for_language((update.effective_user.language_code or '') if update.effective_user else '')
    location_id = context.user_data.get('admin_location_id')
    if not location_id:
        _clear_admin_state(context)
        return
    location = deps.location_repo.get(int(location_id))
    if not location:
        _clear_admin_state(context)
        return
    new_name = context.user_data.get('admin_location_name', location.name)
    new_maps_link = context.user_data.get('admin_location_maps_link')
    _clear_admin_state(context)
    try:
        location.name = new_name
        location.maps_link = new_maps_link
        deps.location_repo.save(location)
        if update.effective_user:
            _log_user_action(update.effective_user, f'edited location: {location.name}')
        text = msgs.admin_location_updated(name=location.name)
        if new_maps_link:
            text += f'\n🗺️ <a href="{new_maps_link}">Google Maps</a>'
        await update.message.reply_text(
            text,
            reply_markup=InlineKeyboardMarkup(
                [
                    [InlineKeyboardButton(msgs.btn_edit_another, callback_data='admin_edit_location')],
                    [InlineKeyboardButton(msgs.btn_back_to_locations, callback_data='admin_locations')],
                ],
            ),
            parse_mode='HTML',
            disable_web_page_preview=True,
        )
    except Exception:
        logger.exception('Failed to edit location')
        await update.message.reply_text(
            msgs.admin_location_update_error,
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton(msgs.btn_back_to_locations, callback_data='admin_locations')]],
            ),
        )
