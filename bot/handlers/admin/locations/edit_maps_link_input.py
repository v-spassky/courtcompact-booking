import logging

from telegram import Update
from telegram.ext import ContextTypes

from bot.deps import get_deps
from bot.handlers.admin._utils import _clear_admin_state
from bot.handlers.admin.locations._save_edited import _save_edited_location

logger = logging.getLogger(__name__)


async def _handle_admin_edit_location_maps_link_input(
    update: Update, context: ContextTypes.DEFAULT_TYPE, link_text: str
) -> None:
    assert context.user_data is not None
    deps = get_deps(context)
    location_id = context.user_data.get('admin_location_id')
    if not location_id:
        _clear_admin_state(context)
        return

    location = deps.location_repo.get(location_id)
    if not location:
        _clear_admin_state(context)
        return

    if link_text.strip() == '--':
        context.user_data['admin_location_maps_link'] = None
    elif link_text.strip() == '-':
        context.user_data['admin_location_maps_link'] = location.google_maps_link
    else:
        context.user_data['admin_location_maps_link'] = link_text.strip()

    await _save_edited_location(update, context)
