from abc import ABC, abstractmethod


class Messages(ABC):
    @classmethod
    def get_for_language(cls, language_code: str) -> 'Messages':
        from localization.ru import RussianMessages

        return RussianMessages()

    # -------------------------------------------------------------------------
    # Navigation buttons (reused everywhere)
    # -------------------------------------------------------------------------

    @property
    @abstractmethod
    def btn_main_menu(self) -> str: ...

    @property
    @abstractmethod
    def btn_back(self) -> str: ...

    @property
    @abstractmethod
    def btn_back_to_main_menu(self) -> str: ...

    @property
    @abstractmethod
    def btn_select_other_location(self) -> str: ...

    # -------------------------------------------------------------------------
    # Auth
    # -------------------------------------------------------------------------

    @property
    @abstractmethod
    def welcome_start(self) -> str: ...

    @property
    @abstractmethod
    def welcome_after_auth(self) -> str: ...

    @property
    @abstractmethod
    def auth_request(self) -> str: ...

    @property
    @abstractmethod
    def btn_share_phone(self) -> str: ...

    @property
    @abstractmethod
    def auth_wrong_contact(self) -> str: ...

    @property
    @abstractmethod
    def auth_phone_not_found(self) -> str: ...

    @abstractmethod
    def auth_success(self, name: str) -> str: ...

    @property
    @abstractmethod
    def unknown_command(self) -> str: ...

    # -------------------------------------------------------------------------
    # Main menu buttons
    # -------------------------------------------------------------------------

    @property
    @abstractmethod
    def btn_schedule_by_date(self) -> str: ...

    @property
    @abstractmethod
    def btn_schedule_weekly(self) -> str: ...

    @property
    @abstractmethod
    def btn_trainer_schedule(self) -> str: ...

    @property
    @abstractmethod
    def btn_book_court(self) -> str: ...

    @property
    @abstractmethod
    def btn_my_bookings(self) -> str: ...

    @property
    @abstractmethod
    def btn_cancel_booking(self) -> str: ...

    @property
    @abstractmethod
    def btn_admin_panel(self) -> str: ...

    # -------------------------------------------------------------------------
    # Booking flow
    # -------------------------------------------------------------------------

    @property
    @abstractmethod
    def btn_no_trainer(self) -> str: ...

    @abstractmethod
    def booking_select_trainer(self, court_name: str) -> str: ...

    @abstractmethod
    def booking_select_date(self, court_name: str, trainer_name: str | None) -> str: ...

    @abstractmethod
    def booking_select_slot(self, court_name: str, date: str, trainer_name: str | None) -> str: ...

    @property
    @abstractmethod
    def booking_no_slots_for_date(self) -> str: ...

    @property
    @abstractmethod
    def slot_occupied(self) -> str: ...

    @abstractmethod
    def booking_confirmed(
        self,
        court_name: str,
        date: str,
        time: str,
        trainer_name: str | None,
        booking_id: str,
    ) -> str: ...

    @abstractmethod
    def booking_new_notification(self, student_name: str, court_name: str, date: str, time: str) -> str: ...

    @property
    @abstractmethod
    def booking_failed(self) -> str: ...

    @property
    @abstractmethod
    def booking_slot_unavailable(self) -> str: ...

    @property
    @abstractmethod
    def booking_generic_error(self) -> str: ...

    @property
    @abstractmethod
    def my_bookings_empty(self) -> str: ...

    @property
    @abstractmethod
    def my_bookings_no_upcoming(self) -> str: ...

    @property
    @abstractmethod
    def my_bookings_title(self) -> str: ...

    @property
    @abstractmethod
    def my_bookings_error(self) -> str: ...

    @property
    @abstractmethod
    def cancel_booking_no_upcoming(self) -> str: ...

    @property
    @abstractmethod
    def cancel_booking_select(self) -> str: ...

    @property
    @abstractmethod
    def cancel_booking_load_error(self) -> str: ...

    @property
    @abstractmethod
    def booking_not_found(self) -> str: ...

    @property
    @abstractmethod
    def booking_cancelled(self) -> str: ...

    @abstractmethod
    def booking_cancelled_notification(self, court_name: str, date: str, time: str) -> str: ...

    @abstractmethod
    def booking_cancelled_by_student(self, student_name: str) -> str: ...

    @abstractmethod
    def booking_cancelled_by_trainer(self, trainer_name: str) -> str: ...

    @property
    @abstractmethod
    def cancel_booking_failed(self) -> str: ...

    @property
    @abstractmethod
    def cancel_booking_error(self) -> str: ...

    # Book court — location/court selection

    @property
    @abstractmethod
    def book_select_location(self) -> str: ...

    @abstractmethod
    def book_no_courts(self, location_name: str | None) -> str: ...

    @abstractmethod
    def book_select_court(self, location_name: str | None, maps_link: str | None) -> str: ...

    # -------------------------------------------------------------------------
    # Schedule
    # -------------------------------------------------------------------------

    @abstractmethod
    def schedule_select_location(self, date: str) -> str: ...

    @abstractmethod
    def schedule_no_courts(self, location_name: str | None) -> str: ...

    @abstractmethod
    def schedule_select_court(self, date: str, location_name: str | None, maps_link: str | None) -> str: ...

    @abstractmethod
    def schedule_court_day(
        self,
        court_name: str,
        date: str,
        location_name: str | None,
        maps_link: str | None,
    ) -> str: ...

    @property
    @abstractmethod
    def schedule_no_slots(self) -> str: ...

    @abstractmethod
    def schedule_slots_summary(self, available: int, total: int) -> str: ...

    @property
    @abstractmethod
    def schedule_no_slots_for_day(self) -> str: ...

    @property
    @abstractmethod
    def schedule_court_error(self) -> str: ...

    @abstractmethod
    def schedule_weekly_select_location(self, start: str, end: str) -> str: ...

    @abstractmethod
    def schedule_weekly_no_courts(self, location_name: str | None) -> str: ...

    @abstractmethod
    def schedule_weekly_select_court(
        self,
        start: str,
        end: str,
        location_name: str | None,
        maps_link: str | None,
    ) -> str: ...

    @abstractmethod
    def schedule_weekly_court(
        self,
        court_name: str,
        start: str,
        end: str,
        location_name: str | None,
        maps_link: str | None,
    ) -> str: ...

    @abstractmethod
    def schedule_weekly_day_row(
        self,
        day_name: str,
        date: str,
        available: int,
        total: int,
        trainer_count: int,
    ) -> str: ...

    @property
    @abstractmethod
    def schedule_weekly_day_empty(self) -> str: ...

    @property
    @abstractmethod
    def schedule_weekly_error(self) -> str: ...

    @property
    @abstractmethod
    def trainer_schedule_no_trainers(self) -> str: ...

    @property
    @abstractmethod
    def trainer_schedule_select(self) -> str: ...

    @abstractmethod
    def trainer_schedule_header(self, name: str, description: str | None) -> str: ...

    @property
    @abstractmethod
    def trainer_schedule_no_upcoming(self) -> str: ...

    @property
    @abstractmethod
    def trainer_schedule_upcoming_title(self) -> str: ...

    @property
    @abstractmethod
    def btn_back_to_trainers(self) -> str: ...

    @property
    @abstractmethod
    def trainer_schedule_error(self) -> str: ...

    @property
    @abstractmethod
    def generic_error(self) -> str: ...

    # -------------------------------------------------------------------------
    # Shared / Navigation extras
    # -------------------------------------------------------------------------

    @property
    @abstractmethod
    def day_names(self) -> list[str]: ...

    @property
    @abstractmethod
    def btn_menu(self) -> str: ...

    @property
    @abstractmethod
    def unknown_court(self) -> str: ...

    @property
    @abstractmethod
    def unknown_entity(self) -> str: ...

    @property
    @abstractmethod
    def fallback_student_name(self) -> str: ...

    @property
    @abstractmethod
    def fallback_trainer_name(self) -> str: ...

    @property
    @abstractmethod
    def not_specified(self) -> str: ...

    @property
    @abstractmethod
    def schedule_select_date(self) -> str: ...

    @abstractmethod
    def booking_detail_trainer(self, name: str) -> str: ...

    @abstractmethod
    @abstractmethod
    def booking_detail_court(self, name: str) -> str: ...

    # -------------------------------------------------------------------------
    # Admin — shared
    # -------------------------------------------------------------------------

    @property
    @abstractmethod
    def admin_no_access(self) -> str: ...

    @property
    @abstractmethod
    def admin_menu_title(self) -> str: ...

    @property
    @abstractmethod
    def btn_admin_locations(self) -> str: ...

    @property
    @abstractmethod
    def btn_admin_courts(self) -> str: ...

    @property
    @abstractmethod
    def btn_admin_trainers(self) -> str: ...

    @property
    @abstractmethod
    def btn_admin_students(self) -> str: ...

    @property
    @abstractmethod
    def btn_create(self) -> str: ...

    @property
    @abstractmethod
    def btn_edit(self) -> str: ...

    @property
    @abstractmethod
    def btn_delete(self) -> str: ...

    @property
    @abstractmethod
    def btn_cancel(self) -> str: ...

    @property
    @abstractmethod
    def btn_confirm_delete(self) -> str: ...

    @property
    @abstractmethod
    def btn_back_to_courts(self) -> str: ...

    @property
    @abstractmethod
    def btn_back_to_trainers_list(self) -> str: ...

    @property
    @abstractmethod
    def btn_back_to_locations(self) -> str: ...

    @property
    @abstractmethod
    def btn_back_to_students(self) -> str: ...

    @property
    @abstractmethod
    def btn_create_another(self) -> str: ...

    @property
    @abstractmethod
    def btn_edit_another(self) -> str: ...

    @property
    @abstractmethod
    def btn_retry(self) -> str: ...

    @property
    @abstractmethod
    def btn_add_student(self) -> str: ...

    @property
    @abstractmethod
    def btn_edit_student(self) -> str: ...

    @property
    @abstractmethod
    def btn_delete_student(self) -> str: ...

    @property
    @abstractmethod
    def btn_admin_create_court(self) -> str: ...

    @property
    @abstractmethod
    def btn_admin_edit_court(self) -> str: ...

    @property
    @abstractmethod
    def btn_admin_delete_court(self) -> str: ...

    @property
    @abstractmethod
    def btn_admin_create_trainer(self) -> str: ...

    @property
    @abstractmethod
    def btn_admin_edit_trainer(self) -> str: ...

    @property
    @abstractmethod
    def btn_admin_delete_trainer(self) -> str: ...

    @property
    @abstractmethod
    def btn_admin_create_location(self) -> str: ...

    @property
    @abstractmethod
    def btn_admin_edit_location(self) -> str: ...

    @property
    @abstractmethod
    def btn_admin_delete_location(self) -> str: ...

    # -------------------------------------------------------------------------
    # Admin — courts
    # -------------------------------------------------------------------------

    @abstractmethod
    def admin_courts_menu(self, count: int) -> str: ...

    @property
    @abstractmethod
    def admin_court_select_location(self) -> str: ...

    @property
    @abstractmethod
    def admin_court_enter_name(self) -> str: ...

    @property
    @abstractmethod
    def admin_court_enter_description(self) -> str: ...

    @property
    @abstractmethod
    def admin_court_skip_description(self) -> str: ...

    @abstractmethod
    def admin_court_created(self, name: str) -> str: ...

    @property
    @abstractmethod
    def admin_court_create_error(self) -> str: ...

    @property
    @abstractmethod
    def admin_court_no_courts(self) -> str: ...

    @property
    @abstractmethod
    def admin_court_select_to_edit(self) -> str: ...

    @property
    @abstractmethod
    def admin_court_enter_new_name(self) -> str: ...

    @property
    @abstractmethod
    def admin_court_enter_new_description(self) -> str: ...

    @abstractmethod
    def admin_court_updated(self, name: str) -> str: ...

    @property
    @abstractmethod
    def admin_court_update_error(self) -> str: ...

    @property
    @abstractmethod
    def admin_court_select_to_delete(self) -> str: ...

    @abstractmethod
    def admin_court_confirm_delete(self, name: str) -> str: ...

    @abstractmethod
    def admin_court_deleted(self, name: str) -> str: ...

    @property
    @abstractmethod
    def admin_court_delete_error(self) -> str: ...

    @property
    @abstractmethod
    def admin_court_no_locations(self) -> str: ...

    @property
    @abstractmethod
    def btn_create_location(self) -> str: ...

    @property
    @abstractmethod
    def admin_court_not_found(self) -> str: ...

    @property
    @abstractmethod
    def admin_court_location_not_found(self) -> str: ...

    @property
    @abstractmethod
    def admin_court_name_too_long(self) -> str: ...

    @property
    @abstractmethod
    def admin_court_name_too_long_edit(self) -> str: ...

    @abstractmethod
    def admin_court_create_step2(self, location_name: str) -> str: ...

    @abstractmethod
    def admin_court_create_step3(self, location_name: str, court_name: str) -> str: ...

    @abstractmethod
    def admin_court_edit_step1(self, name: str, description: str | None) -> str: ...

    @abstractmethod
    def admin_court_edit_step2(self, name: str, description: str | None) -> str: ...

    @abstractmethod
    def admin_court_location_line(self, name: str) -> str: ...

    @abstractmethod
    def admin_court_description_line(self, desc: str) -> str: ...

    # -------------------------------------------------------------------------
    # Admin — trainers
    # -------------------------------------------------------------------------

    @abstractmethod
    def admin_trainers_menu(self, count: int) -> str: ...

    @property
    @abstractmethod
    def admin_trainer_enter_name(self) -> str: ...

    @property
    @abstractmethod
    def admin_trainer_enter_telegram_id(self) -> str: ...

    @property
    @abstractmethod
    def admin_trainer_enter_description(self) -> str: ...

    @property
    @abstractmethod
    def admin_trainer_skip_description(self) -> str: ...

    @abstractmethod
    def admin_trainer_created(self, name: str) -> str: ...

    @property
    @abstractmethod
    def admin_trainer_create_error(self) -> str: ...

    @property
    @abstractmethod
    def admin_trainer_no_trainers(self) -> str: ...

    @property
    @abstractmethod
    def admin_trainer_select_to_edit(self) -> str: ...

    @property
    @abstractmethod
    def admin_trainer_enter_new_name(self) -> str: ...

    @property
    @abstractmethod
    def admin_trainer_enter_new_telegram_id(self) -> str: ...

    @property
    @abstractmethod
    def admin_trainer_enter_new_description(self) -> str: ...

    @abstractmethod
    def admin_trainer_updated(self, name: str) -> str: ...

    @property
    @abstractmethod
    def admin_trainer_update_error(self) -> str: ...

    @property
    @abstractmethod
    def admin_trainer_select_to_delete(self) -> str: ...

    @abstractmethod
    def admin_trainer_confirm_delete(self, name: str) -> str: ...

    @abstractmethod
    def admin_trainer_deleted(self, name: str) -> str: ...

    @property
    @abstractmethod
    def admin_trainer_delete_error(self) -> str: ...

    @property
    @abstractmethod
    def admin_trainer_not_found(self) -> str: ...

    @property
    @abstractmethod
    def admin_trainer_name_too_long(self) -> str: ...

    @property
    @abstractmethod
    def admin_trainer_name_too_long_edit(self) -> str: ...

    @property
    @abstractmethod
    def admin_trainer_id_not_a_number(self) -> str: ...

    @property
    @abstractmethod
    def admin_trainer_id_not_a_number_edit(self) -> str: ...

    @abstractmethod
    def admin_trainer_id_exists(self, telegram_id: int, name: str) -> str: ...

    @abstractmethod
    def admin_trainer_id_taken(self, name: str) -> str: ...

    @abstractmethod
    def admin_trainer_description_line(self, desc: str) -> str: ...

    @abstractmethod
    def admin_trainer_create_step1(self) -> str: ...

    @abstractmethod
    def admin_trainer_create_step2(self, name: str) -> str: ...

    @abstractmethod
    def admin_trainer_create_step3(self, name: str, telegram_id: int) -> str: ...

    @abstractmethod
    def admin_trainer_edit_step1(self, name: str, telegram_id: int, description: str | None) -> str: ...

    @abstractmethod
    def admin_trainer_edit_step2(self, new_name: str, telegram_id: int) -> str: ...

    @abstractmethod
    def admin_trainer_edit_step3(self, new_name: str, new_telegram_id: int, description: str | None) -> str: ...

    # -------------------------------------------------------------------------
    # Admin — locations
    # -------------------------------------------------------------------------

    @abstractmethod
    def admin_locations_menu(self, count: int) -> str: ...

    @property
    @abstractmethod
    def admin_location_enter_name(self) -> str: ...

    @property
    @abstractmethod
    def admin_location_enter_maps_link(self) -> str: ...

    @property
    @abstractmethod
    def admin_location_skip_maps_link(self) -> str: ...

    @abstractmethod
    def admin_location_created(self, name: str) -> str: ...

    @property
    @abstractmethod
    def admin_location_create_error(self) -> str: ...

    @property
    @abstractmethod
    def admin_location_no_locations(self) -> str: ...

    @property
    @abstractmethod
    def admin_location_select_to_edit(self) -> str: ...

    @property
    @abstractmethod
    def admin_location_enter_new_name(self) -> str: ...

    @property
    @abstractmethod
    def admin_location_enter_new_maps_link(self) -> str: ...

    @abstractmethod
    def admin_location_updated(self, name: str) -> str: ...

    @property
    @abstractmethod
    def admin_location_update_error(self) -> str: ...

    @property
    @abstractmethod
    def admin_location_select_to_delete(self) -> str: ...

    @abstractmethod
    def admin_location_confirm_delete(self, name: str) -> str: ...

    @abstractmethod
    def admin_location_deleted(self, name: str) -> str: ...

    @property
    @abstractmethod
    def admin_location_delete_error(self) -> str: ...

    @property
    @abstractmethod
    def admin_location_not_found(self) -> str: ...

    @property
    @abstractmethod
    def admin_location_name_too_long(self) -> str: ...

    @property
    @abstractmethod
    def admin_location_name_too_long_edit(self) -> str: ...

    @abstractmethod
    def admin_location_courts_warning(self, count: int) -> str: ...

    @abstractmethod
    def admin_location_create_step1(self) -> str: ...

    @abstractmethod
    def admin_location_create_step2(self, name: str) -> str: ...

    @abstractmethod
    def admin_location_edit_step1(self, name: str, maps_link: str | None) -> str: ...

    @abstractmethod
    def admin_location_edit_step2(self, new_name: str, maps_link: str | None) -> str: ...

    # -------------------------------------------------------------------------
    # Admin — students
    # -------------------------------------------------------------------------

    @abstractmethod
    def admin_students_menu(self, total: int, authorized: int) -> str: ...

    @property
    @abstractmethod
    def admin_student_enter_name(self) -> str: ...

    @property
    @abstractmethod
    def admin_student_enter_phone(self) -> str: ...

    @abstractmethod
    def admin_student_created(self, name: str) -> str: ...

    @property
    @abstractmethod
    def admin_student_phone_exists(self) -> str: ...

    @property
    @abstractmethod
    def admin_student_create_error(self) -> str: ...

    @property
    @abstractmethod
    def admin_student_no_students(self) -> str: ...

    @property
    @abstractmethod
    def admin_student_select_to_edit(self) -> str: ...

    @property
    @abstractmethod
    def admin_student_enter_new_name(self) -> str: ...

    @property
    @abstractmethod
    def admin_student_enter_new_phone(self) -> str: ...

    @abstractmethod
    def admin_student_updated(self, name: str) -> str: ...

    @property
    @abstractmethod
    def admin_student_update_error(self) -> str: ...

    @property
    @abstractmethod
    def admin_student_select_to_delete(self) -> str: ...

    @abstractmethod
    def admin_student_confirm_delete(self, name: str) -> str: ...

    @abstractmethod
    def admin_student_deleted(self, name: str) -> str: ...

    @property
    @abstractmethod
    def admin_student_delete_error(self) -> str: ...

    @property
    @abstractmethod
    def admin_student_not_found(self) -> str: ...

    @property
    @abstractmethod
    def admin_student_name_empty(self) -> str: ...

    @property
    @abstractmethod
    def admin_student_phone_required(self) -> str: ...

    @abstractmethod
    def admin_student_phone_taken(self, name: str) -> str: ...

    @abstractmethod
    def admin_student_phone_line(self, phone: str) -> str: ...

    @property
    @abstractmethod
    def student_status_authorized(self) -> str: ...

    @property
    @abstractmethod
    def student_status_unauthorized(self) -> str: ...

    @abstractmethod
    def admin_student_create_step1(self) -> str: ...

    @abstractmethod
    def admin_student_create_step2(self, name: str) -> str: ...

    @abstractmethod
    def admin_student_edit_step1(self, name: str, phone: str, status: str) -> str: ...

    @abstractmethod
    def admin_student_edit_step2(self, new_name: str, phone: str) -> str: ...
