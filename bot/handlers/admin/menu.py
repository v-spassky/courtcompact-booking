import logging

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from bot.handlers.admin._utils import _clear_admin_state
from bot.handlers.auth import _is_admin, _log_user_action
from bot.handlers.base import Handler
from localization import get_messages

logger = logging.getLogger(__name__)


class AdminMenu(Handler):
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
        assert self._update.effective_user is not None
        msgs = get_messages()

        _log_user_action(self._update.effective_user, 'opened admin menu')
        _clear_admin_state(self._context)

        keyboard = [
            [InlineKeyboardButton(msgs.btn_admin_locations, callback_data='admin_locations')],
            [InlineKeyboardButton(msgs.btn_admin_courts, callback_data='admin_courts')],
            [InlineKeyboardButton(msgs.btn_admin_trainers, callback_data='admin_trainers')],
            [InlineKeyboardButton(msgs.btn_admin_students, callback_data='admin_students')],
            [InlineKeyboardButton(msgs.btn_back_to_main_menu, callback_data='main_menu')],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await self._update.callback_query.edit_message_text(msgs.admin_menu_title, reply_markup=reply_markup)


class AdminCourtsMenu(Handler):
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

        _clear_admin_state(self._context)

        courts = self._deps.court_repo.get_all()
        text = msgs.admin_courts_menu(count=len(courts))

        keyboard = [
            [InlineKeyboardButton(msgs.btn_admin_create_court, callback_data='admin_create_court')],
            [InlineKeyboardButton(msgs.btn_admin_edit_court, callback_data='admin_edit_court')],
            [InlineKeyboardButton(msgs.btn_admin_delete_court, callback_data='admin_delete_court')],
            [InlineKeyboardButton(msgs.btn_back, callback_data='admin_menu')],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await self._update.callback_query.edit_message_text(text, reply_markup=reply_markup)


class AdminTrainersMenu(Handler):
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

        _clear_admin_state(self._context)

        trainers = self._deps.trainer_repo.get_all()
        text = msgs.admin_trainers_menu(count=len(trainers))

        keyboard = [
            [InlineKeyboardButton(msgs.btn_admin_create_trainer, callback_data='admin_create_trainer')],
            [InlineKeyboardButton(msgs.btn_admin_edit_trainer, callback_data='admin_edit_trainer')],
            [InlineKeyboardButton(msgs.btn_admin_delete_trainer, callback_data='admin_delete_trainer')],
            [InlineKeyboardButton(msgs.btn_back, callback_data='admin_menu')],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await self._update.callback_query.edit_message_text(text, reply_markup=reply_markup)


class AdminLocationsMenu(Handler):
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

        _clear_admin_state(self._context)

        locations = self._deps.location_repo.get_all()
        text = msgs.admin_locations_menu(count=len(locations))

        keyboard = [
            [InlineKeyboardButton(msgs.btn_admin_create_location, callback_data='admin_create_location')],
            [InlineKeyboardButton(msgs.btn_admin_edit_location, callback_data='admin_edit_location')],
            [InlineKeyboardButton(msgs.btn_admin_delete_location, callback_data='admin_delete_location')],
            [InlineKeyboardButton(msgs.btn_back, callback_data='admin_menu')],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await self._update.callback_query.edit_message_text(text, reply_markup=reply_markup)


class AdminStudentsMenu(Handler):
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
        assert self._update.effective_user is not None
        msgs = get_messages()

        _log_user_action(self._update.effective_user, 'opened students admin menu')
        _clear_admin_state(self._context)

        students = self._deps.student_repo.get_all()
        text = msgs.admin_students_menu(
            total=len(students),
            authorized=sum(1 for s in students if s.telegram_user_id),
        )

        keyboard = [
            [InlineKeyboardButton(msgs.btn_add_student, callback_data='admin_create_student')],
            [InlineKeyboardButton(msgs.btn_edit_student, callback_data='admin_edit_student')],
            [InlineKeyboardButton(msgs.btn_delete_student, callback_data='admin_delete_student')],
            [InlineKeyboardButton(msgs.btn_back, callback_data='admin_menu')],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await self._update.callback_query.edit_message_text(text, reply_markup=reply_markup)
