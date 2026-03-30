import logging

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from bot.handlers.admin._utils import _clear_admin_state
from bot.handlers.auth import _is_admin, _log_user_action
from bot.handlers.base import Handler

logger = logging.getLogger(__name__)


class AdminMenu(Handler):
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
        _log_user_action(self._update.effective_user, 'opened admin menu')
        _clear_admin_state(self._context)
        await self._update.callback_query.edit_message_text(
            self._messages.admin_menu_title,
            reply_markup=InlineKeyboardMarkup(
                [
                    [InlineKeyboardButton(self._messages.btn_admin_locations, callback_data='admin_locations')],
                    [InlineKeyboardButton(self._messages.btn_admin_courts, callback_data='admin_courts')],
                    [InlineKeyboardButton(self._messages.btn_admin_trainers, callback_data='admin_trainers')],
                    [InlineKeyboardButton(self._messages.btn_admin_students, callback_data='admin_students')],
                    [InlineKeyboardButton(self._messages.btn_back_to_main_menu, callback_data='main_menu')],
                ],
            ),
        )


class AdminCourtsMenu(Handler):
    async def _authorize(self) -> bool:
        assert self._update.callback_query is not None
        assert self._update.effective_user is not None
        if not _is_admin(self._update.effective_user.id, self._deps):
            await self._update.callback_query.edit_message_text(self._messages.admin_no_access)
            return False
        return True

    async def _process(self) -> None:
        assert self._update.callback_query is not None
        _clear_admin_state(self._context)
        courts = self._deps.court_repo.get_all()
        await self._update.callback_query.edit_message_text(
            self._messages.admin_courts_menu(count=len(courts)),
            reply_markup=InlineKeyboardMarkup(
                [
                    [InlineKeyboardButton(self._messages.btn_admin_create_court, callback_data='admin_create_court')],
                    [InlineKeyboardButton(self._messages.btn_admin_edit_court, callback_data='admin_edit_court')],
                    [InlineKeyboardButton(self._messages.btn_admin_delete_court, callback_data='admin_delete_court')],
                    [InlineKeyboardButton(self._messages.btn_back, callback_data='admin_menu')],
                ],
            ),
        )


class AdminTrainersMenu(Handler):
    async def _authorize(self) -> bool:
        assert self._update.callback_query is not None
        assert self._update.effective_user is not None
        if not _is_admin(self._update.effective_user.id, self._deps):
            await self._update.callback_query.edit_message_text(self._messages.admin_no_access)
            return False
        return True

    async def _process(self) -> None:
        assert self._update.callback_query is not None
        _clear_admin_state(self._context)
        trainers = self._deps.trainer_repo.get_all()
        await self._update.callback_query.edit_message_text(
            self._messages.admin_trainers_menu(count=len(trainers)),
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            self._messages.btn_admin_create_trainer,
                            callback_data='admin_create_trainer',
                        ),
                    ],
                    [InlineKeyboardButton(self._messages.btn_admin_edit_trainer, callback_data='admin_edit_trainer')],
                    [
                        InlineKeyboardButton(
                            self._messages.btn_admin_delete_trainer,
                            callback_data='admin_delete_trainer',
                        ),
                    ],
                    [InlineKeyboardButton(self._messages.btn_back, callback_data='admin_menu')],
                ],
            ),
        )


class AdminLocationsMenu(Handler):
    async def _authorize(self) -> bool:
        assert self._update.callback_query is not None
        assert self._update.effective_user is not None
        if not _is_admin(self._update.effective_user.id, self._deps):
            await self._update.callback_query.edit_message_text(self._messages.admin_no_access)
            return False
        return True

    async def _process(self) -> None:
        assert self._update.callback_query is not None
        _clear_admin_state(self._context)
        locations = self._deps.location_repo.get_all()
        await self._update.callback_query.edit_message_text(
            self._messages.admin_locations_menu(count=len(locations)),
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            self._messages.btn_admin_create_location,
                            callback_data='admin_create_location',
                        ),
                    ],
                    [InlineKeyboardButton(self._messages.btn_admin_edit_location, callback_data='admin_edit_location')],
                    [
                        InlineKeyboardButton(
                            self._messages.btn_admin_delete_location,
                            callback_data='admin_delete_location',
                        ),
                    ],
                    [InlineKeyboardButton(self._messages.btn_back, callback_data='admin_menu')],
                ],
            ),
        )


class AdminStudentsMenu(Handler):
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
        _log_user_action(self._update.effective_user, 'opened students admin menu')
        _clear_admin_state(self._context)
        students = self._deps.student_repo.get_all()
        await self._update.callback_query.edit_message_text(
            self._messages.admin_students_menu(
                total=len(students),
                authorized=sum(1 for s in students if s.user_id),
            ),
            reply_markup=InlineKeyboardMarkup(
                [
                    [InlineKeyboardButton(self._messages.btn_add_student, callback_data='admin_create_student')],
                    [InlineKeyboardButton(self._messages.btn_edit_student, callback_data='admin_edit_student')],
                    [InlineKeyboardButton(self._messages.btn_delete_student, callback_data='admin_delete_student')],
                    [InlineKeyboardButton(self._messages.btn_back, callback_data='admin_menu')],
                ],
            ),
        )
