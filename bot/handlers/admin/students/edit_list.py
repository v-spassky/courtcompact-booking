import logging

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from bot.handlers.auth import _is_admin
from bot.handlers.base import Handler
from localization import get_messages

logger = logging.getLogger(__name__)


class AdminEditStudentList(Handler):
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

        students = self._deps.student_repo.get_all()

        if not students:
            keyboard = [[InlineKeyboardButton(msgs.btn_back, callback_data='admin_students')]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await self._update.callback_query.edit_message_text(
                msgs.admin_student_no_students, reply_markup=reply_markup
            )
            return

        keyboard = []
        for student in students:
            student_id_short = str(student.id)[:8]
            status = '✅' if student.telegram_user_id else '⏳'
            button_text = f'{status} {student.name}'
            keyboard.append([InlineKeyboardButton(button_text, callback_data=f'admin_edit_student_{student_id_short}')])

        keyboard.append([InlineKeyboardButton(msgs.btn_back, callback_data='admin_students')])
        reply_markup = InlineKeyboardMarkup(keyboard)

        await self._update.callback_query.edit_message_text(
            msgs.admin_student_select_to_edit, reply_markup=reply_markup
        )
