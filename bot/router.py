import logging
from datetime import datetime

from telegram import Update
from telegram.ext import ContextTypes

from bot.deps import get_deps
from bot.handlers.admin.courts.create_select_location import AdminCreateCourtSelectLocation
from bot.handlers.admin.courts.create_start import AdminCreateCourtStart
from bot.handlers.admin.courts.delete_confirm import AdminDeleteCourtConfirm
from bot.handlers.admin.courts.delete_execute import AdminDeleteCourtExecute
from bot.handlers.admin.courts.delete_list import AdminDeleteCourtList
from bot.handlers.admin.courts.edit_list import AdminEditCourtList
from bot.handlers.admin.courts.edit_start import AdminEditCourtStart
from bot.handlers.admin.locations.create_start import AdminCreateLocationStart
from bot.handlers.admin.locations.delete_confirm import AdminDeleteLocationConfirm
from bot.handlers.admin.locations.delete_execute import AdminDeleteLocationExecute
from bot.handlers.admin.locations.delete_list import AdminDeleteLocationList
from bot.handlers.admin.locations.edit_list import AdminEditLocationList
from bot.handlers.admin.locations.edit_start import AdminEditLocationStart
from bot.handlers.admin.menu import AdminCourtsMenu, AdminLocationsMenu, AdminMenu, AdminStudentsMenu, AdminTrainersMenu
from bot.handlers.admin.students.create_start import AdminCreateStudentStart
from bot.handlers.admin.students.delete_confirm import AdminDeleteStudentConfirm
from bot.handlers.admin.students.delete_execute import AdminDeleteStudentExecute
from bot.handlers.admin.students.delete_list import AdminDeleteStudentList
from bot.handlers.admin.students.edit_list import AdminEditStudentList
from bot.handlers.admin.students.edit_start import AdminEditStudentStart
from bot.handlers.admin.trainers.create_start import AdminCreateTrainerStart
from bot.handlers.admin.trainers.delete_confirm import AdminDeleteTrainerConfirm
from bot.handlers.admin.trainers.delete_execute import AdminDeleteTrainerExecute
from bot.handlers.admin.trainers.delete_list import AdminDeleteTrainerList
from bot.handlers.admin.trainers.edit_list import AdminEditTrainerList
from bot.handlers.admin.trainers.edit_start import AdminEditTrainerStart
from bot.handlers.auth import (
    _create_calendar,
    _is_authorized,
    _log_user_action,
    _show_authorization_request,
    show_main_menu,
)
from bot.handlers.booking.calendar_nav import BookingCalendarNavigation
from bot.handlers.booking.cancel_menu import CancelBookingMenu
from bot.handlers.booking.cancellation import BookingCancellation
from bot.handlers.booking.court_selection import CourtSelectionForBooking
from bot.handlers.booking.date_selection import BookingDateSelection
from bot.handlers.booking.my_bookings import MyBookings
from bot.handlers.booking.select_court import BookCourt
from bot.handlers.booking.select_location import BookCourtSelectLocation
from bot.handlers.booking.slot_selection import BookingSlotSelection
from bot.handlers.booking.trainer_selection import TrainerSelectionForBooking
from bot.handlers.schedule.by_date import ScheduleForDate
from bot.handlers.schedule.by_date_courts import ScheduleForDateShowCourts
from bot.handlers.schedule.court_day import CourtScheduleForDay
from bot.handlers.schedule.court_week import CourtScheduleForWeek
from bot.handlers.schedule.trainer_menu import TrainerScheduleMenu
from bot.handlers.schedule.trainer_view import ViewTrainerSchedule
from bot.handlers.schedule.weekly import ScheduleWeekly
from bot.handlers.schedule.weekly_courts import ScheduleWeeklyShowCourts
from config.settings import now_kiev
from localization import get_messages

logger = logging.getLogger(__name__)


async def handle_callback_query(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.callback_query or not update.effective_user:
        return
    await update.callback_query.answer()
    callback_data = update.callback_query.data
    if callback_data is None:
        return
    deps = get_deps(context)
    if callback_data != 'ignore':
        _log_user_action(update.effective_user, f'clicked button: {callback_data}')
    if callback_data != 'ignore' and not _is_authorized(update.effective_user.id, deps):
        await _show_authorization_request(update, context)
        return
    msgs = get_messages()
    if callback_data == 'main_menu':
        await show_main_menu(update, context, edit_message=True)
    elif callback_data == 'ignore':
        await update.callback_query.answer()
        return
    elif callback_data == 'select_date_schedule':
        now = now_kiev()
        calendar_markup = _create_calendar(now.year, now.month)
        await update.callback_query.edit_message_text(msgs.schedule_select_date, reply_markup=calendar_markup)
    elif callback_data.startswith('cal_'):
        parts = callback_data.split('_')
        year, month = int(parts[1]), int(parts[2])
        calendar_markup = _create_calendar(year, month)
        await update.callback_query.edit_message_text(msgs.schedule_select_date, reply_markup=calendar_markup)
    elif callback_data.startswith('date_'):
        parts = callback_data.split('_')
        year, month, day = int(parts[1]), int(parts[2]), int(parts[3])
        selected_date = datetime(year, month, day)
        await ScheduleForDate(update, context, deps, selected_date).handle()
    elif callback_data.startswith('schedule_location_'):
        parts = callback_data.split('_')
        location_id = int(parts[2])
        year, month, day = int(parts[3]), int(parts[4]), int(parts[5])
        selected_date = datetime(year, month, day)
        await ScheduleForDateShowCourts(update, context, deps, selected_date, location_id).handle()
    elif callback_data.startswith('court_day_'):
        parts = callback_data.split('_')
        court_id = int(parts[2])
        year, month, day = int(parts[3]), int(parts[4]), int(parts[5])
        selected_date = datetime(year, month, day)
        await CourtScheduleForDay(update, context, deps, court_id, selected_date).handle()
    elif callback_data.startswith('court_week_'):
        parts = callback_data.split('_')
        court_id = int(parts[2])
        year, month, day = int(parts[3]), int(parts[4]), int(parts[5])
        start_of_week = datetime(year, month, day)
        await CourtScheduleForWeek(update, context, deps, court_id, start_of_week).handle()
    elif callback_data == 'schedule_weekly':
        await ScheduleWeekly(update, context, deps).handle()
    elif callback_data.startswith('weekly_location_'):
        parts = callback_data.split('_')
        location_id = int(parts[2])
        year, month, day = int(parts[3]), int(parts[4]), int(parts[5])
        start_of_week = datetime(year, month, day)
        await ScheduleWeeklyShowCourts(update, context, deps, start_of_week, location_id).handle()
    elif callback_data == 'trainer_schedule':
        await TrainerScheduleMenu(update, context, deps).handle()
    elif callback_data.startswith('view_trainer_'):
        await ViewTrainerSchedule(update, context, deps, callback_data).handle()
    elif callback_data.startswith('book_cal_'):
        await BookingCalendarNavigation(update, context, deps, callback_data).handle()
    elif callback_data.startswith('book_date_'):
        await BookingDateSelection(update, context, deps, callback_data).handle()
    elif callback_data.startswith('book_slot_'):
        await BookingSlotSelection(update, context, deps, callback_data, update.effective_user.id).handle()
    elif callback_data == 'book_court':
        await BookCourtSelectLocation(update, context, deps).handle()
    elif callback_data.startswith('book_location_'):
        await BookCourt(update, context, deps, callback_data).handle()
    elif callback_data == 'my_bookings':
        await MyBookings(update, context, deps).handle()
    elif callback_data == 'cancel_booking':
        await CancelBookingMenu(update, context, deps).handle()
    elif callback_data == 'admin_menu':
        await AdminMenu(update, context, deps).handle()
    elif callback_data == 'admin_courts':
        await AdminCourtsMenu(update, context, deps).handle()
    elif callback_data == 'admin_trainers':
        await AdminTrainersMenu(update, context, deps).handle()
    elif callback_data == 'admin_locations':
        await AdminLocationsMenu(update, context, deps).handle()
    elif callback_data == 'admin_create_location':
        await AdminCreateLocationStart(update, context, deps).handle()
    elif callback_data == 'admin_edit_location':
        await AdminEditLocationList(update, context, deps).handle()
    elif callback_data.startswith('admin_edit_location_'):
        await AdminEditLocationStart(update, context, deps, callback_data).handle()
    elif callback_data == 'admin_delete_location':
        await AdminDeleteLocationList(update, context, deps).handle()
    elif callback_data.startswith('admin_delete_location_'):
        await AdminDeleteLocationConfirm(update, context, deps, callback_data).handle()
    elif callback_data.startswith('admin_confirm_delete_location_'):
        await AdminDeleteLocationExecute(update, context, deps, callback_data).handle()
    elif callback_data == 'admin_create_court':
        await AdminCreateCourtSelectLocation(update, context, deps).handle()
    elif callback_data.startswith('admin_court_location_'):
        await AdminCreateCourtStart(update, context, deps, callback_data).handle()
    elif callback_data == 'admin_edit_court':
        await AdminEditCourtList(update, context, deps).handle()
    elif callback_data.startswith('admin_edit_court_'):
        await AdminEditCourtStart(update, context, deps, callback_data).handle()
    elif callback_data == 'admin_delete_court':
        await AdminDeleteCourtList(update, context, deps).handle()
    elif callback_data.startswith('admin_delete_court_'):
        await AdminDeleteCourtConfirm(update, context, deps, callback_data).handle()
    elif callback_data.startswith('admin_confirm_delete_court_'):
        await AdminDeleteCourtExecute(update, context, deps, callback_data).handle()
    elif callback_data == 'admin_create_trainer':
        await AdminCreateTrainerStart(update, context, deps).handle()
    elif callback_data == 'admin_edit_trainer':
        await AdminEditTrainerList(update, context, deps).handle()
    elif callback_data.startswith('admin_edit_trainer_'):
        await AdminEditTrainerStart(update, context, deps, callback_data).handle()
    elif callback_data == 'admin_delete_trainer':
        await AdminDeleteTrainerList(update, context, deps).handle()
    elif callback_data.startswith('admin_delete_trainer_'):
        await AdminDeleteTrainerConfirm(update, context, deps, callback_data).handle()
    elif callback_data.startswith('admin_confirm_delete_trainer_'):
        await AdminDeleteTrainerExecute(update, context, deps, callback_data).handle()
    elif callback_data == 'admin_students':
        await AdminStudentsMenu(update, context, deps).handle()
    elif callback_data == 'admin_create_student':
        await AdminCreateStudentStart(update, context, deps).handle()
    elif callback_data == 'admin_edit_student':
        await AdminEditStudentList(update, context, deps).handle()
    elif callback_data.startswith('admin_edit_student_'):
        await AdminEditStudentStart(update, context, deps, callback_data).handle()
    elif callback_data == 'admin_delete_student':
        await AdminDeleteStudentList(update, context, deps).handle()
    elif callback_data.startswith('admin_delete_student_'):
        await AdminDeleteStudentConfirm(update, context, deps, callback_data).handle()
    elif callback_data.startswith('admin_confirm_delete_student_'):
        await AdminDeleteStudentExecute(update, context, deps, callback_data).handle()
    elif callback_data.startswith('select_court_'):
        await CourtSelectionForBooking(update, context, deps, callback_data, update.effective_user.id).handle()
    elif callback_data.startswith('select_trainer_'):
        await TrainerSelectionForBooking(update, context, deps, callback_data, update.effective_user.id).handle()
    elif callback_data.startswith('cancel_booking_'):
        await BookingCancellation(update, context, deps, callback_data, update.effective_user.id).handle()
