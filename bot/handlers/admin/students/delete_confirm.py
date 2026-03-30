import logging

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from bot.deps import Deps
from bot.handlers.auth import _is_admin
from bot.handlers.base import Handler
from localization import get_messages

logger = logging.getLogger(__name__)


class AdminDeleteStudentConfirm(Handler):
    def __init__(self, update: Update, context: ContextTypes.DEFAULT_TYPE, deps: Deps, callback_data: str) -> None:
        super().__init__(update, context, deps)
        self._callback_data = callback_data

    async def _authorize(self) -> bool:
        assert self._update.callback_query is not None
        assert self._update.effective_user is not None
        msgs = get_messages()
        if not _is_admin(self._update.effective_user.id, self._deps):
            await self._update.callback_query.edit_message_text(msgs.admin_no_access)
            return False
        return True

    async def _process(self) -> None:
        assert self._update.callback_query is not None
        msgs = get_messages()
        student_id = int(self._callback_data.replace('admin_delete_student_', ''))
        student = self._deps.student_repo.get(student_id)
        if not student:
            await self._update.callback_query.edit_message_text(
                msgs.admin_student_not_found,
                reply_markup=InlineKeyboardMarkup(
                    [[InlineKeyboardButton(msgs.btn_back, callback_data='admin_students')]],
                ),
            )
            return
        student_name = student.user.name if student.user else student.phone
        await self._update.callback_query.edit_message_text(
            msgs.admin_student_confirm_delete(name=student_name),
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            msgs.btn_confirm_delete,
                            callback_data=f'admin_confirm_delete_student_{student.id}',
                        ),
                    ],
                    [InlineKeyboardButton(msgs.btn_cancel, callback_data='admin_students')],
                ],
            ),
        )
