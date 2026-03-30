import logging

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from bot.handlers.admin._utils import _clear_admin_state
from bot.handlers.base import TextInputHandler

logger = logging.getLogger(__name__)


class AdminEditStudentNameInput(TextInputHandler):
    async def _authorize(self) -> bool:
        return True

    async def _process(self) -> None:
        assert self._update.message is not None
        assert self._context.user_data is not None
        student_id = self._context.user_data.get('admin_student_id')
        if not student_id:
            _clear_admin_state(self._context)
            return
        student = self._deps.student_repo.get(int(student_id))
        if not student:
            _clear_admin_state(self._context)
            await self._update.message.reply_text(
                self._messages.admin_student_not_found,
                reply_markup=InlineKeyboardMarkup(
                    [[InlineKeyboardButton(self._messages.btn_back, callback_data='admin_students')]],
                ),
            )
            return
        current_name = student.user.name if student.user else ''
        if self._text and self._text != '-':
            self._context.user_data['admin_student_name'] = self._text
        else:
            self._context.user_data['admin_student_name'] = current_name
        self._context.user_data['admin_state'] = 'awaiting_edit_student_phone'
        await self._update.message.reply_text(
            self._messages.admin_student_edit_step2(
                new_name=self._context.user_data['admin_student_name'],
                phone=student.phone,
            ),
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton(self._messages.btn_cancel, callback_data='admin_students')]],
            ),
        )
