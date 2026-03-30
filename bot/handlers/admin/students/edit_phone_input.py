import logging

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from bot.handlers.admin._utils import _clear_admin_state
from bot.handlers.auth import _log_user_action
from bot.handlers.base import TextInputHandler

logger = logging.getLogger(__name__)


class AdminEditStudentPhoneInput(TextInputHandler):
    async def _authorize(self) -> bool:
        return True

    async def _process(self) -> None:
        assert self._update.message is not None
        assert self._context.user_data is not None
        student_id = self._context.user_data.get('admin_student_id')
        new_name = self._context.user_data.get('admin_student_name')
        if not student_id or not new_name:
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
        new_phone = self._text if self._text and self._text != '-' else student.phone
        if new_phone != student.phone:
            existing = self._deps.student_repo.get_by_phone(new_phone)
            if existing and existing.id != student.id:
                _clear_admin_state(self._context)
                await self._update.message.reply_text(
                    self._messages.admin_student_phone_taken(
                        name=existing.user.name if existing.user else self._messages.unknown_entity,
                    ),
                    reply_markup=InlineKeyboardMarkup(
                        [[InlineKeyboardButton(self._messages.btn_back_to_students, callback_data='admin_students')]],
                    ),
                )
                return
        _clear_admin_state(self._context)
        if student.user and new_name:
            student.user.name = new_name
            self._deps.user_repo.save(student.user)
        student.phone = new_phone
        self._deps.student_repo.save(student)
        display_name = student.user.name if student.user else new_phone
        if self._update.effective_user:
            _log_user_action(self._update.effective_user, f'edited student: {display_name}')
        await self._update.message.reply_text(
            self._messages.admin_student_updated(name=display_name),
            reply_markup=InlineKeyboardMarkup(
                [
                    [InlineKeyboardButton(self._messages.btn_edit_another, callback_data='admin_edit_student')],
                    [InlineKeyboardButton(self._messages.btn_back_to_students, callback_data='admin_students')],
                ],
            ),
        )

    async def _on_error(self, error: Exception) -> None:
        logger.exception('Failed to edit student')
        assert self._update.message is not None
        await self._update.message.reply_text(
            self._messages.admin_student_update_error,
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton(self._messages.btn_back_to_students, callback_data='admin_students')]],
            ),
        )
