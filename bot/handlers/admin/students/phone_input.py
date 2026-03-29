import logging

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from bot.handlers.admin._utils import _clear_admin_state
from bot.handlers.auth import _log_user_action
from bot.handlers.base import TextInputHandler
from db.models import Student
from localization import get_messages

logger = logging.getLogger(__name__)


class AdminStudentPhoneInput(TextInputHandler):
    async def _authorize(self) -> bool:
        return True

    async def _process(self) -> None:
        assert self._update.message is not None
        assert self._context.user_data is not None
        msgs = get_messages()
        student_name = self._context.user_data.get('admin_student_name', '')
        if not student_name:
            _clear_admin_state(self._context)
            return
        if not self._text or self._text == '-':
            self._context.user_data.pop('admin_state', None)
            text = msgs.admin_student_phone_required
            keyboard = [
                [InlineKeyboardButton(msgs.btn_retry, callback_data='admin_create_student')],
                [InlineKeyboardButton(msgs.btn_cancel, callback_data='admin_students')],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await self._update.message.reply_text(text, reply_markup=reply_markup)
            return
        existing = self._deps.student_repo.get_by_phone(self._text)
        if existing:
            _clear_admin_state(self._context)
            keyboard = [
                [InlineKeyboardButton(msgs.btn_retry, callback_data='admin_create_student')],
                [InlineKeyboardButton(msgs.btn_cancel, callback_data='admin_students')],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await self._update.message.reply_text(msgs.admin_student_phone_exists, reply_markup=reply_markup)
            return
        _clear_admin_state(self._context)
        student = Student(user_id=None, phone=self._text)
        self._deps.student_repo.save(student)
        if self._update.effective_user:
            _log_user_action(self._update.effective_user, f'created student with phone: {self._text}')
        text = msgs.admin_student_created(name=student_name)
        text += msgs.admin_student_phone_line(phone=self._text)
        keyboard = [
            [InlineKeyboardButton(msgs.btn_create_another, callback_data='admin_create_student')],
            [InlineKeyboardButton(msgs.btn_back_to_students, callback_data='admin_students')],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await self._update.message.reply_text(text, reply_markup=reply_markup)

    async def _on_error(self, error: Exception) -> None:
        logger.exception('Failed to create student')
        msgs = get_messages()
        assert self._update.message is not None
        keyboard = [[InlineKeyboardButton(msgs.btn_back_to_students, callback_data='admin_students')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await self._update.message.reply_text(msgs.admin_student_create_error, reply_markup=reply_markup)
