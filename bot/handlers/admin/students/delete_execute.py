import logging

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from bot.deps import Deps
from bot.handlers.auth import _is_admin, _log_user_action
from bot.handlers.base import Handler

logger = logging.getLogger(__name__)


class AdminDeleteStudentExecute(Handler):
    def __init__(self, update: Update, context: ContextTypes.DEFAULT_TYPE, deps: Deps, callback_data: str) -> None:
        super().__init__(update, context, deps)
        self._callback_data = callback_data

    async def _authorize(self) -> bool:
        assert self._update.callback_query is not None
        assert self._update.effective_user is not None
        if not _is_admin(self._update.effective_user.id, self._deps):
            await self._update.callback_query.edit_message_text(self._messages.admin_no_access)
            return False
        return True

    async def _process(self) -> None:
        assert self._update.callback_query is not None
        assert self._update.effective_user is not None
        student_id = int(self._callback_data.replace('admin_confirm_delete_student_', ''))
        student = self._deps.student_repo.get(student_id)
        if not student:
            await self._update.callback_query.edit_message_text(
                self._messages.admin_student_not_found,
                reply_markup=InlineKeyboardMarkup(
                    [[InlineKeyboardButton(self._messages.btn_back, callback_data='admin_students')]],
                ),
            )
            return
        self._deps.student_repo.delete(student.id)
        _log_user_action(
            self._update.effective_user,
            f'deleted student: {student.user.name if student.user else student.phone}',
        )
        await self._update.callback_query.edit_message_text(
            self._messages.admin_student_deleted(name=student.user.name if student.user else student.phone),
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton(self._messages.btn_back_to_students, callback_data='admin_students')]],
            ),
        )

    async def _on_error(self, error: Exception) -> None:
        logger.exception('Failed to delete student')
        assert self._update.callback_query is not None
        await self._update.callback_query.edit_message_text(
            self._messages.admin_student_delete_error,
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton(self._messages.btn_back_to_students, callback_data='admin_students')]],
            ),
        )
