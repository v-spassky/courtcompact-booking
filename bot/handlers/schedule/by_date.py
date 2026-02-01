import logging
from datetime import datetime

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from bot.deps import get_deps
from bot.handlers.schedule.by_date_courts import _handle_schedule_for_date_show_courts
from localization import get_messages

logger = logging.getLogger(__name__)


async def _handle_schedule_for_date(update: Update, context: ContextTypes.DEFAULT_TYPE, date: datetime) -> None:
    if not update.callback_query:
        return

    msgs = get_messages()
    deps = get_deps(context)

    try:
        locations = deps.location_repo.get_active()

        if not locations:
            await _handle_schedule_for_date_show_courts(update, context, date, None)
            return

        text = msgs.schedule_select_location(date=date.strftime('%d.%m.%Y'))

        for location in locations:
            if location.google_maps_link:
                text += f'📍 <a href="{location.google_maps_link}">{location.name}</a>\n\n'
            else:
                text += f'📍 {location.name}\n\n'

        keyboard = []
        for location in locations:
            location_id_short = str(location.id)[:8]
            callback_data = f'schedule_location_{location_id_short}_{date.year}_{date.month}_{date.day}'
            keyboard.append([InlineKeyboardButton(f'📍 {location.name}', callback_data=callback_data)])

        keyboard.append([InlineKeyboardButton(msgs.btn_back_to_main_menu, callback_data='main_menu')])
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.callback_query.edit_message_text(
            text, reply_markup=reply_markup, parse_mode='HTML', disable_web_page_preview=True
        )
    except Exception:
        logger.exception('Failed to show location selection')
        await update.callback_query.edit_message_text(msgs.generic_error)
