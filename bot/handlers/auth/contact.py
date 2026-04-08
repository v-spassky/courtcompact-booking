from telegram import ReplyKeyboardRemove

from bot.handlers.auth._utils import _log_user_action
from bot.handlers.base import Handler
from phone import normalize_phone


class HandleContact(Handler):
    async def _authorize(self) -> bool:
        return True

    async def _process(self) -> None:
        from bot.handlers.auth.main_menu import ShowMainMenu

        assert self._update.message is not None
        assert self._update.message.contact is not None
        assert self._update.effective_user is not None
        if self._update.message.contact.user_id != self._update.effective_user.id:
            await self._update.message.reply_text(
                self._messages.auth_wrong_contact,
                reply_markup=ReplyKeyboardRemove(),
            )
            return
        _log_user_action(
            self._update.effective_user,
            f'shared phone number: {self._update.message.contact.phone_number}',
        )
        phone = normalize_phone(self._update.message.contact.phone_number)
        student = self._deps.student_repo.get_by_phone(phone)
        if student:
            from db.models import User as DbUser

            db_user = self._deps.user_repo.get_by_telegram_id(self._update.effective_user.id)
            if db_user is None:
                db_user = DbUser(
                    telegram_user_id=self._update.effective_user.id,
                    name=self._update.effective_user.full_name
                    or self._update.effective_user.username
                    or str(self._update.effective_user.id),
                )
                self._deps.user_repo.save(db_user)
            if student.user_id is None:
                student.user_id = db_user.id
                self._deps.student_repo.save(student)
            student_name = db_user.name
            _log_user_action(self._update.effective_user, f'authorized as student: {student_name}')
            await self._update.message.reply_text(
                self._messages.auth_success(student_name),
                reply_markup=ReplyKeyboardRemove(),
            )
            await ShowMainMenu(self._update, self._context, self._deps, edit_message=False).handle()
        else:
            await self._update.message.reply_text(
                self._messages.auth_phone_not_found,
                reply_markup=ReplyKeyboardRemove(),
            )
