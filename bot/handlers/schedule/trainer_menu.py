import logging

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from bot.deps import get_deps
from localization import get_messages

logger = logging.getLogger(__name__)


async def _handle_trainer_schedule_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.callback_query:
        return

    msgs = get_messages()
    deps = get_deps(context)

    try:
        trainers = deps.trainer_repo.get_all()

        if not trainers:
            keyboard = [[InlineKeyboardButton(msgs.btn_back_to_main_menu, callback_data='main_menu')]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.callback_query.edit_message_text(msgs.trainer_schedule_no_trainers, reply_markup=reply_markup)
            return

        keyboard = []
        for trainer in trainers:
            button_text = f'👨‍🏫 {trainer.name}'
            keyboard.append([InlineKeyboardButton(button_text, callback_data=f'view_trainer_{str(trainer.id)[:8]}')])

        keyboard.append([InlineKeyboardButton(msgs.btn_back_to_main_menu, callback_data='main_menu')])
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.callback_query.edit_message_text(msgs.trainer_schedule_select, reply_markup=reply_markup)
    except Exception:
        logger.exception('Failed to show trainer selection')
        await update.callback_query.edit_message_text(msgs.generic_error)
