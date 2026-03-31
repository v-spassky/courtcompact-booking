from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from bot.handlers.auth._utils import _is_admin
from bot.handlers.base import Handler


class HandleUnknownMessage(Handler):
    async def _authorize(self) -> bool:
        return True

    async def _process(self) -> None:
        from bot.handlers.admin.courts.description_input import AdminCourtDescriptionInput
        from bot.handlers.admin.courts.edit_description_input import AdminEditCourtDescriptionInput
        from bot.handlers.admin.courts.edit_name_input import AdminEditCourtNameInput
        from bot.handlers.admin.courts.name_input import AdminCourtNameInput
        from bot.handlers.admin.locations.edit_maps_link_input import AdminEditLocationMapsLinkInput
        from bot.handlers.admin.locations.edit_name_input import AdminEditLocationNameInput
        from bot.handlers.admin.locations.maps_link_input import AdminLocationMapsLinkInput
        from bot.handlers.admin.locations.name_input import AdminLocationNameInput
        from bot.handlers.admin.students.edit_name_input import AdminEditStudentNameInput
        from bot.handlers.admin.students.edit_phone_input import AdminEditStudentPhoneInput
        from bot.handlers.admin.students.name_input import AdminStudentNameInput
        from bot.handlers.admin.students.phone_input import AdminStudentPhoneInput
        from bot.handlers.admin.trainers.description_input import AdminTrainerDescriptionInput
        from bot.handlers.admin.trainers.edit_description_input import AdminEditTrainerDescriptionInput
        from bot.handlers.admin.trainers.edit_name_input import AdminEditTrainerNameInput
        from bot.handlers.admin.trainers.edit_telegram_id_input import AdminEditTrainerTelegramIdInput
        from bot.handlers.admin.trainers.name_input import AdminTrainerNameInput
        from bot.handlers.admin.trainers.telegram_id_input import AdminTrainerTelegramIdInput

        assert self._update.message is not None
        assert self._update.effective_user is not None
        assert self._context.user_data is not None
        message_text = (self._update.message.text or '').strip()
        admin_state = self._context.user_data.get('admin_state')
        user_id = self._update.effective_user.id
        if admin_state and _is_admin(user_id, self._deps):
            if admin_state == 'awaiting_location_name':
                await AdminLocationNameInput(self._update, self._context, self._deps, message_text).handle()
                return
            elif admin_state == 'awaiting_location_maps_link':
                await AdminLocationMapsLinkInput(self._update, self._context, self._deps, message_text).handle()
                return
            elif admin_state == 'awaiting_edit_location_name':
                await AdminEditLocationNameInput(self._update, self._context, self._deps, message_text).handle()
                return
            elif admin_state == 'awaiting_edit_location_maps_link':
                await AdminEditLocationMapsLinkInput(self._update, self._context, self._deps, message_text).handle()
                return
            elif admin_state == 'awaiting_court_name':
                await AdminCourtNameInput(self._update, self._context, self._deps, message_text).handle()
                return
            elif admin_state == 'awaiting_court_description':
                await AdminCourtDescriptionInput(self._update, self._context, self._deps, message_text).handle()
                return
            elif admin_state == 'awaiting_edit_court_name':
                await AdminEditCourtNameInput(self._update, self._context, self._deps, message_text).handle()
                return
            elif admin_state == 'awaiting_edit_court_description':
                await AdminEditCourtDescriptionInput(self._update, self._context, self._deps, message_text).handle()
                return
            elif admin_state == 'awaiting_trainer_name':
                await AdminTrainerNameInput(self._update, self._context, self._deps, message_text).handle()
                return
            elif admin_state == 'awaiting_trainer_telegram_id':
                await AdminTrainerTelegramIdInput(self._update, self._context, self._deps, message_text).handle()
                return
            elif admin_state == 'awaiting_trainer_description':
                await AdminTrainerDescriptionInput(self._update, self._context, self._deps, message_text).handle()
                return
            elif admin_state == 'awaiting_edit_trainer_name':
                await AdminEditTrainerNameInput(self._update, self._context, self._deps, message_text).handle()
                return
            elif admin_state == 'awaiting_edit_trainer_telegram_id':
                await AdminEditTrainerTelegramIdInput(self._update, self._context, self._deps, message_text).handle()
                return
            elif admin_state == 'awaiting_edit_trainer_description':
                await AdminEditTrainerDescriptionInput(self._update, self._context, self._deps, message_text).handle()
                return
            elif admin_state == 'awaiting_student_name':
                await AdminStudentNameInput(self._update, self._context, self._deps, message_text).handle()
                return
            elif admin_state == 'awaiting_student_phone':
                await AdminStudentPhoneInput(self._update, self._context, self._deps, message_text).handle()
                return
            elif admin_state == 'awaiting_edit_student_name':
                await AdminEditStudentNameInput(self._update, self._context, self._deps, message_text).handle()
                return
            elif admin_state == 'awaiting_edit_student_phone':
                await AdminEditStudentPhoneInput(self._update, self._context, self._deps, message_text).handle()
                return
        await self._update.message.reply_text(
            self._messages.unknown_command,
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton(self._messages.btn_main_menu, callback_data='main_menu')]],
            ),
        )
