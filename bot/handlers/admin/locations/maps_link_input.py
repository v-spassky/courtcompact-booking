import logging

from telegram import Update
from telegram.ext import ContextTypes

from bot.handlers.admin.locations._save import _save_location

logger = logging.getLogger(__name__)


async def _handle_admin_location_maps_link_input(
    update: Update, context: ContextTypes.DEFAULT_TYPE, link_text: str
) -> None:
    assert context.user_data is not None
    if link_text.strip() == '-':
        context.user_data['admin_location_maps_link'] = None
    else:
        context.user_data['admin_location_maps_link'] = link_text.strip()

    await _save_location(update, context)
