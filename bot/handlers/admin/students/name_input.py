import logging

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from bot.handlers.base import TextInputHandler
from localization import get_messages

logger = logging.getLogger(__name__)


class AdminStudentNameInput(TextInputHandler):
    async def _authorize(self) -> bool:
        return True

    async def _process(self) -> None:
        assert self._update.message is not None
        assert self._context.user_data is not None
        msgs = get_messages()
        if not self._text or self._text == '-':
            self._context.user_data.pop('admin_state', None)
            await self._update.message.reply_text(
                msgs.admin_student_name_empty,
                reply_markup=InlineKeyboardMarkup(
                    [
                        [InlineKeyboardButton(msgs.btn_retry, callback_data='admin_create_student')],
                        [InlineKeyboardButton(msgs.btn_cancel, callback_data='admin_students')],
                    ],
                ),
            )
            return
        self._context.user_data['admin_student_name'] = self._text
        self._context.user_data['admin_state'] = 'awaiting_student_phone'
        await self._update.message.reply_text(
            msgs.admin_student_create_step2(name=self._text),
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton(msgs.btn_cancel, callback_data='admin_students')]],
            ),
        )
