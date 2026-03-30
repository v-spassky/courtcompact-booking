import logging

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from bot.handlers.base import Handler
from localization import get_messages

logger = logging.getLogger(__name__)


class TrainerScheduleMenu(Handler):
    async def _authorize(self) -> bool:
        return True

    async def _process(self) -> None:
        assert self._update.callback_query is not None
        msgs = get_messages()
        trainers = self._deps.trainer_repo.get_all()
        if not trainers:
            await self._update.callback_query.edit_message_text(
                msgs.trainer_schedule_no_trainers,
                reply_markup=InlineKeyboardMarkup(
                    [[InlineKeyboardButton(msgs.btn_back_to_main_menu, callback_data='main_menu')]],
                ),
            )
            return
        keyboard = []
        for trainer in trainers:
            button_text = f'👨‍🏫 {trainer.user.name}'
            keyboard.append([InlineKeyboardButton(button_text, callback_data=f'view_trainer_{trainer.id}')])
        keyboard.append([InlineKeyboardButton(msgs.btn_back_to_main_menu, callback_data='main_menu')])
        await self._update.callback_query.edit_message_text(
            msgs.trainer_schedule_select,
            reply_markup=InlineKeyboardMarkup(keyboard),
        )

    async def _on_error(self, error: Exception) -> None:
        logger.exception('Failed to show trainer selection')
        msgs = get_messages()
        assert self._update.callback_query is not None
        await self._update.callback_query.edit_message_text(msgs.generic_error)
