import logging

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from bot.deps import Deps
from bot.handlers.auth import _is_admin
from bot.handlers.base import Handler
from bot.handlers.callback_args import AdminConfirmDeleteStudentArg, AdminDeleteStudentArg

logger = logging.getLogger(__name__)


class AdminDeleteStudentConfirm(Handler):
    def __init__(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
        deps: Deps,
        args: AdminDeleteStudentArg,
    ) -> None:
        super().__init__(update, context, deps)
        self._args = args

    async def _authorize(self) -> bool:
        assert self._update.callback_query is not None
        assert self._update.effective_user is not None
        if not _is_admin(self._update.effective_user.id, self._deps):
            await self._update.callback_query.edit_message_text(self._messages.admin_no_access)
            return False
        return True

    async def _process(self) -> None:
        assert self._update.callback_query is not None
        student = self._deps.student_repo.get(self._args.id)
        if not student:
            await self._update.callback_query.edit_message_text(
                self._messages.admin_student_not_found,
                reply_markup=InlineKeyboardMarkup(
                    [[InlineKeyboardButton(self._messages.btn_back, callback_data='admin_students')]],
                ),
            )
            return
        student_name = student.user.name if student.user else student.phone
        await self._update.callback_query.edit_message_text(
            self._messages.admin_student_confirm_delete(name=student_name),
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            self._messages.btn_confirm_delete,
                            callback_data=AdminConfirmDeleteStudentArg(id=student.id).to_callback_data(),
                        ),
                    ],
                    [InlineKeyboardButton(self._messages.btn_cancel, callback_data='admin_students')],
                ],
            ),
        )
