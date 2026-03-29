import logging
from uuid import UUID

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from bot.handlers.admin._utils import _clear_admin_state
from bot.handlers.base import TextInputHandler
from localization import get_messages

logger = logging.getLogger(__name__)


class AdminEditStudentNameInput(TextInputHandler):
    async def _authorize(self) -> bool:
        return True

    async def _process(self) -> None:
        assert self._update.message is not None
        assert self._context.user_data is not None
        msgs = get_messages()
        student_id = self._context.user_data.get('admin_student_id')
        if not student_id:
            _clear_admin_state(self._context)
            return

        student = self._deps.student_repo.get(UUID(student_id))
        if not student:
            _clear_admin_state(self._context)
            keyboard = [[InlineKeyboardButton(msgs.btn_back, callback_data='admin_students')]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await self._update.message.reply_text(msgs.admin_student_not_found, reply_markup=reply_markup)
            return

        if self._text and self._text != '-':
            self._context.user_data['admin_student_name'] = self._text
        else:
            self._context.user_data['admin_student_name'] = student.name

        self._context.user_data['admin_state'] = 'awaiting_edit_student_phone'

        text = msgs.admin_student_edit_step2(
            new_name=self._context.user_data['admin_student_name'], phone=student.phone
        )

        keyboard = [[InlineKeyboardButton(msgs.btn_cancel, callback_data='admin_students')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await self._update.message.reply_text(text, reply_markup=reply_markup)
