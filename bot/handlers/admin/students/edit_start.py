import logging

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from bot.deps import Deps
from bot.handlers.admin._utils import _clear_admin_state
from bot.handlers.auth import _is_admin
from bot.handlers.base import Handler
from localization import get_messages

logger = logging.getLogger(__name__)


class AdminEditStudentStart(Handler):
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

        student_id_short = self._callback_data.replace('admin_edit_student_', '')
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

        _clear_admin_state(self._context)
        assert self._context.user_data is not None
        self._context.user_data['admin_student_id'] = str(student.id)
        self._context.user_data['admin_state'] = 'awaiting_edit_student_name'

        status = msgs.student_status_authorized if student.user_id else msgs.student_status_unauthorized
        student_name = student.user.name if student.user else msgs.unknown_entity
        text = msgs.admin_student_edit_step1(name=student_name, phone=student.phone, status=status)

        keyboard = [[InlineKeyboardButton(msgs.btn_cancel, callback_data='admin_students')]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await self._update.callback_query.edit_message_text(text, reply_markup=reply_markup)
