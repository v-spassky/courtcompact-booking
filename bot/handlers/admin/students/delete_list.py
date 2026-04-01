import logging

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from bot.handlers.auth import _is_admin
from bot.handlers.base import Handler
from bot.handlers.callback_args import AdminDeleteStudentArg

logger = logging.getLogger(__name__)


class AdminDeleteStudentList(Handler):
    async def _authorize(self) -> bool:
        assert self._update.callback_query is not None
        assert self._update.effective_user is not None
        if not _is_admin(self._update.effective_user.id, self._deps):
            await self._update.callback_query.edit_message_text(self._messages.admin_no_access)
            return False
        return True

    async def _process(self) -> None:
        assert self._update.callback_query is not None
        students = self._deps.student_repo.get_all()
        if not students:
            await self._update.callback_query.edit_message_text(
                self._messages.admin_student_no_students,
                reply_markup=InlineKeyboardMarkup(
                    [[InlineKeyboardButton(self._messages.btn_back, callback_data='admin_students')]],
                ),
            )
            return
        keyboard = []
        for student in students:
            status = '✅' if student.user_id else '⏳'
            student_name = student.user.name if student.user else student.phone
            button_text = f'{status} {student_name}'
            keyboard.append(
                [
                    InlineKeyboardButton(
                        button_text,
                        callback_data=AdminDeleteStudentArg(id=student.id).to_callback_data(),
                    ),
                ],
            )
        keyboard.append([InlineKeyboardButton(self._messages.btn_back, callback_data='admin_students')])
        await self._update.callback_query.edit_message_text(
            self._messages.admin_student_select_to_delete,
            reply_markup=InlineKeyboardMarkup(keyboard),
        )
