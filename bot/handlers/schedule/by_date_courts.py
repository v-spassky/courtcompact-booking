import logging
from datetime import datetime

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from bot.deps import get_deps
from localization import get_messages

logger = logging.getLogger(__name__)


async def _handle_schedule_for_date_show_courts(
    update: Update, context: ContextTypes.DEFAULT_TYPE, date: datetime, location_id: str | None
) -> None:
    if not update.callback_query:
        return

    msgs = get_messages()
    deps = get_deps(context)

    try:
        location = None
        if location_id:
            location = deps.location_repo.get(location_id)
            courts = deps.location_repo.get_courts(location_id)
        else:
            courts = deps.court_repo.get_all()

        if not courts:
            text = msgs.schedule_no_courts(location_name=location.name if location else None)
            keyboard = [
                [
                    InlineKeyboardButton(
                        msgs.btn_select_other_location, callback_data=f'date_{date.year}_{date.month}_{date.day}'
                    )
                ],
                [InlineKeyboardButton(msgs.btn_back_to_main_menu, callback_data='main_menu')],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.callback_query.edit_message_text(text, reply_markup=reply_markup)
            return

        text = msgs.schedule_select_court(
            date=date.strftime('%d.%m.%Y'),
            location_name=location.name if location else None,
            maps_link=location.maps_link if location else None,
        )

        keyboard = []
        for court in courts:
            callback_data = f'court_day_{court.id}_{date.year}_{date.month}_{date.day}'
            keyboard.append([InlineKeyboardButton(f'🎾 {court.name}', callback_data=callback_data)])

        if location:
            keyboard.append(
                [
                    InlineKeyboardButton(
                        msgs.btn_select_other_location, callback_data=f'date_{date.year}_{date.month}_{date.day}'
                    )
                ]
            )
        keyboard.append([InlineKeyboardButton(msgs.btn_back_to_main_menu, callback_data='main_menu')])
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.callback_query.edit_message_text(
            text, reply_markup=reply_markup, parse_mode='HTML', disable_web_page_preview=True
        )
    except Exception:
        logger.exception('Failed to show court selection')
        await update.callback_query.edit_message_text(msgs.generic_error)
