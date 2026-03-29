import logging

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from bot.handlers.admin._utils import _clear_admin_state
from bot.handlers.auth import _log_user_action
from bot.handlers.base import TextInputHandler
from localization import get_messages

logger = logging.getLogger(__name__)


class AdminEditStudentPhoneInput(TextInputHandler):
    async def _authorize(self) -> bool:
        return True

    async def _process(self) -> None:
        assert self._update.message is not None
        assert self._context.user_data is not None
        msgs = get_messages()
        student_id = self._context.user_data.get('admin_student_id')
        new_name = self._context.user_data.get('admin_student_name')

        if not student_id or not new_name:
            _clear_admin_state(self._context)
            return

        student = self._deps.student_repo.get(student_id)
        if not student:
            _clear_admin_state(self._context)
            keyboard = [[InlineKeyboardButton(msgs.btn_back, callback_data='admin_students')]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await self._update.message.reply_text(msgs.admin_student_not_found, reply_markup=reply_markup)
            return

        new_phone = self._text if self._text and self._text != '-' else student.phone

        if new_phone != student.phone:
            existing = self._deps.student_repo.get_by_phone(new_phone)
            if existing and str(existing.id) != student_id:
                _clear_admin_state(self._context)
                text = msgs.admin_student_phone_taken(name=existing.name)
                keyboard = [[InlineKeyboardButton(msgs.btn_back_to_students, callback_data='admin_students')]]
                reply_markup = InlineKeyboardMarkup(keyboard)
                await self._update.message.reply_text(text, reply_markup=reply_markup)
                return

        _clear_admin_state(self._context)

        student.name = new_name
        student.phone = new_phone
        self._deps.student_repo.save(student)

        if self._update.effective_user:
            _log_user_action(self._update.effective_user, f'edited student: {student.name}')

        text = msgs.admin_student_updated(name=student.name)

        keyboard = [
            [InlineKeyboardButton(msgs.btn_edit_another, callback_data='admin_edit_student')],
            [InlineKeyboardButton(msgs.btn_back_to_students, callback_data='admin_students')],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await self._update.message.reply_text(text, reply_markup=reply_markup)

    async def _on_error(self, error: Exception) -> None:
        logger.exception('Failed to edit student')
        msgs = get_messages()
        assert self._update.message is not None
        keyboard = [[InlineKeyboardButton(msgs.btn_back_to_students, callback_data='admin_students')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await self._update.message.reply_text(msgs.admin_student_update_error, reply_markup=reply_markup)
