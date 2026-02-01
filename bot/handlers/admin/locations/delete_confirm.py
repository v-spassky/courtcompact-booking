import logging

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from bot.deps import get_deps
from bot.handlers.auth import _is_admin
from localization import get_messages

logger = logging.getLogger(__name__)


async def _handle_admin_delete_location_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE, data: str) -> None:
    if not update.callback_query or not update.effective_user:
        return

    msgs = get_messages()
    deps = get_deps(context)

    if not _is_admin(update.effective_user.id):
        await update.callback_query.edit_message_text(msgs.admin_no_access)
        return

    location_id_short = data.replace('admin_delete_location_', '')

    locations = deps.location_repo.get_active()
    location = None
    for loc in locations:
        if str(loc.id).startswith(location_id_short):
            location = loc
            break

    if not location:
        keyboard = [[InlineKeyboardButton(msgs.btn_back, callback_data='admin_locations')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.callback_query.edit_message_text('❌ Локация не найдена.', reply_markup=reply_markup)
        return

    courts = deps.location_repo.get_courts(location.id)
    warning = ''
    if courts:
        warning = f'\n\n⚠️ К этой локации привязано {len(courts)} корт(ов)!'

    text = msgs.admin_location_confirm_delete(name=location.name)
    if warning:
        text += warning

    keyboard = [
        [
            InlineKeyboardButton(
                msgs.btn_confirm_delete, callback_data=f'admin_confirm_delete_location_{location_id_short}'
            )
        ],
        [InlineKeyboardButton(msgs.btn_cancel, callback_data='admin_locations')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.callback_query.edit_message_text(text, reply_markup=reply_markup)
