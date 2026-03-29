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
        if not _is_admin(self._update.effective_user.id):
            await self._update.callback_query.edit_message_text(msgs.admin_no_access)
            return False
        return True

    async def _process(self) -> None:
        assert self._update.callback_query is not None
        msgs = get_messages()

        student_id_short = self._callback_data.replace('admin_delete_student_', '')
        students = self._deps.student_repo.get_all()
        student = None
        for s in students:
            if str(s.id).startswith(student_id_short):
                student = s
                break

        if not student:
            keyboard = [[InlineKeyboardButton(msgs.btn_back, callback_data='admin_students')]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await self._update.callback_query.edit_message_text(msgs.admin_student_not_found, reply_markup=reply_markup)
            return

        text = msgs.admin_student_confirm_delete(name=student.name)

        keyboard = [
            [
                InlineKeyboardButton(
                    msgs.btn_confirm_delete,
                    callback_data=f'admin_confirm_delete_student_{student_id_short}',
                )
            ],
            [InlineKeyboardButton(msgs.btn_cancel, callback_data='admin_students')],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await self._update.callback_query.edit_message_text(text, reply_markup=reply_markup)
