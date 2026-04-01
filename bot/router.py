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
from bot.handlers.auth import ShowAuthorizationRequest, ShowMainMenu, _create_calendar, _is_authorized, _log_user_action
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
from bot.handlers.callback_args import (
    AdminConfirmDeleteCourtArg,
    AdminConfirmDeleteLocationArg,
    AdminConfirmDeleteStudentArg,
    AdminConfirmDeleteTrainerArg,
    AdminCourtLocationArg,
    AdminDeleteCourtArg,
    AdminDeleteLocationArg,
    AdminDeleteStudentArg,
    AdminDeleteTrainerArg,
    AdminEditCourtArg,
    AdminEditLocationArg,
    AdminEditStudentArg,
    AdminEditTrainerArg,
    BookCalArg,
    BookDateArg,
    BookLocationArg,
    BookSlotArg,
    CalendarNavArg,
    CancelBookingArg,
    CourtDayArg,
    CourtWeekArg,
    ScheduleDateArg,
    ScheduleLocationArg,
    SelectCourtArg,
    SelectTrainerArg,
    ViewTrainerArg,
    WeeklyLocationArg,
)
from bot.handlers.schedule.by_date import ScheduleForDate
from bot.handlers.schedule.by_date_courts import ScheduleForDateShowCourts
from bot.handlers.schedule.court_day import CourtScheduleForDay
from bot.handlers.schedule.court_week import CourtScheduleForWeek
from bot.handlers.schedule.trainer_menu import TrainerScheduleMenu
from bot.handlers.schedule.trainer_view import ViewTrainerSchedule
from bot.handlers.schedule.weekly import ScheduleWeekly
from bot.handlers.schedule.weekly_courts import ScheduleWeeklyShowCourts
from config.settings import now_kiev
from localization.base import Messages

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
        await ShowAuthorizationRequest(update, context, deps).handle()
        return
    msgs = Messages.get_for_language(update.effective_user.language_code or '')
    if callback_data == 'main_menu':
        await ShowMainMenu(update, context, deps, edit_message=True).handle()
    elif callback_data == 'ignore':
        await update.callback_query.answer()
        return
    elif callback_data == 'select_date_schedule':
        now = now_kiev()
        calendar_markup = _create_calendar(now.year, now.month)
        await update.callback_query.edit_message_text(msgs.schedule_select_date, reply_markup=calendar_markup)
    elif callback_data.startswith('cal_'):
        cal_args = CalendarNavArg.from_callback_data(callback_data)
        calendar_markup = _create_calendar(cal_args.year, cal_args.month)
        await update.callback_query.edit_message_text(msgs.schedule_select_date, reply_markup=calendar_markup)
    elif callback_data.startswith('date_'):
        date_args = ScheduleDateArg.from_callback_data(callback_data)
        await ScheduleForDate(update, context, deps, datetime(date_args.year, date_args.month, date_args.day)).handle()
    elif callback_data.startswith('schedule_location_'):
        sched_loc_args = ScheduleLocationArg.from_callback_data(callback_data)
        await ScheduleForDateShowCourts(
            update,
            context,
            deps,
            datetime(sched_loc_args.year, sched_loc_args.month, sched_loc_args.day),
            sched_loc_args.location_id,
        ).handle()
    elif callback_data.startswith('court_day_'):
        court_day_args = CourtDayArg.from_callback_data(callback_data)
        await CourtScheduleForDay(
            update,
            context,
            deps,
            court_day_args.court_id,
            datetime(court_day_args.year, court_day_args.month, court_day_args.day),
        ).handle()
    elif callback_data.startswith('court_week_'):
        court_week_args = CourtWeekArg.from_callback_data(callback_data)
        await CourtScheduleForWeek(
            update,
            context,
            deps,
            court_week_args.court_id,
            datetime(court_week_args.year, court_week_args.month, court_week_args.day),
        ).handle()
    elif callback_data == 'schedule_weekly':
        await ScheduleWeekly(update, context, deps).handle()
    elif callback_data.startswith('weekly_location_'):
        weekly_loc_args = WeeklyLocationArg.from_callback_data(callback_data)
        await ScheduleWeeklyShowCourts(
            update,
            context,
            deps,
            datetime(weekly_loc_args.year, weekly_loc_args.month, weekly_loc_args.day),
            weekly_loc_args.location_id,
        ).handle()
    elif callback_data == 'trainer_schedule':
        await TrainerScheduleMenu(update, context, deps).handle()
    elif callback_data.startswith('view_trainer_'):
        await ViewTrainerSchedule(update, context, deps, ViewTrainerArg.from_callback_data(callback_data)).handle()
    elif callback_data.startswith('book_cal_'):
        await BookingCalendarNavigation(update, context, deps, BookCalArg.from_callback_data(callback_data)).handle()
    elif callback_data.startswith('book_date_'):
        await BookingDateSelection(update, context, deps, BookDateArg.from_callback_data(callback_data)).handle()
    elif callback_data.startswith('book_slot_'):
        await BookingSlotSelection(
            update,
            context,
            deps,
            BookSlotArg.from_callback_data(callback_data),
            update.effective_user.id,
        ).handle()
    elif callback_data == 'book_court':
        await BookCourtSelectLocation(update, context, deps).handle()
    elif callback_data.startswith('book_location_'):
        await BookCourt(update, context, deps, BookLocationArg.from_callback_data(callback_data)).handle()
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
        await AdminEditLocationStart(
            update,
            context,
            deps,
            AdminEditLocationArg.from_callback_data(callback_data),
        ).handle()
    elif callback_data == 'admin_delete_location':
        await AdminDeleteLocationList(update, context, deps).handle()
    elif callback_data.startswith('admin_delete_location_'):
        await AdminDeleteLocationConfirm(
            update,
            context,
            deps,
            AdminDeleteLocationArg.from_callback_data(callback_data),
        ).handle()
    elif callback_data.startswith('admin_confirm_delete_location_'):
        await AdminDeleteLocationExecute(
            update,
            context,
            deps,
            AdminConfirmDeleteLocationArg.from_callback_data(callback_data),
        ).handle()
    elif callback_data == 'admin_create_court':
        await AdminCreateCourtSelectLocation(update, context, deps).handle()
    elif callback_data.startswith('admin_court_location_'):
        await AdminCreateCourtStart(
            update,
            context,
            deps,
            AdminCourtLocationArg.from_callback_data(callback_data),
        ).handle()
    elif callback_data == 'admin_edit_court':
        await AdminEditCourtList(update, context, deps).handle()
    elif callback_data.startswith('admin_edit_court_'):
        await AdminEditCourtStart(update, context, deps, AdminEditCourtArg.from_callback_data(callback_data)).handle()
    elif callback_data == 'admin_delete_court':
        await AdminDeleteCourtList(update, context, deps).handle()
    elif callback_data.startswith('admin_delete_court_'):
        await AdminDeleteCourtConfirm(
            update,
            context,
            deps,
            AdminDeleteCourtArg.from_callback_data(callback_data),
        ).handle()
    elif callback_data.startswith('admin_confirm_delete_court_'):
        await AdminDeleteCourtExecute(
            update,
            context,
            deps,
            AdminConfirmDeleteCourtArg.from_callback_data(callback_data),
        ).handle()
    elif callback_data == 'admin_create_trainer':
        await AdminCreateTrainerStart(update, context, deps).handle()
    elif callback_data == 'admin_edit_trainer':
        await AdminEditTrainerList(update, context, deps).handle()
    elif callback_data.startswith('admin_edit_trainer_'):
        await AdminEditTrainerStart(
            update,
            context,
            deps,
            AdminEditTrainerArg.from_callback_data(callback_data),
        ).handle()
    elif callback_data == 'admin_delete_trainer':
        await AdminDeleteTrainerList(update, context, deps).handle()
    elif callback_data.startswith('admin_delete_trainer_'):
        await AdminDeleteTrainerConfirm(
            update,
            context,
            deps,
            AdminDeleteTrainerArg.from_callback_data(callback_data),
        ).handle()
    elif callback_data.startswith('admin_confirm_delete_trainer_'):
        await AdminDeleteTrainerExecute(
            update,
            context,
            deps,
            AdminConfirmDeleteTrainerArg.from_callback_data(callback_data),
        ).handle()
    elif callback_data == 'admin_students':
        await AdminStudentsMenu(update, context, deps).handle()
    elif callback_data == 'admin_create_student':
        await AdminCreateStudentStart(update, context, deps).handle()
    elif callback_data == 'admin_edit_student':
        await AdminEditStudentList(update, context, deps).handle()
    elif callback_data.startswith('admin_edit_student_'):
        await AdminEditStudentStart(
            update,
            context,
            deps,
            AdminEditStudentArg.from_callback_data(callback_data),
        ).handle()
    elif callback_data == 'admin_delete_student':
        await AdminDeleteStudentList(update, context, deps).handle()
    elif callback_data.startswith('admin_delete_student_'):
        await AdminDeleteStudentConfirm(
            update,
            context,
            deps,
            AdminDeleteStudentArg.from_callback_data(callback_data),
        ).handle()
    elif callback_data.startswith('admin_confirm_delete_student_'):
        await AdminDeleteStudentExecute(
            update,
            context,
            deps,
            AdminConfirmDeleteStudentArg.from_callback_data(callback_data),
        ).handle()
    elif callback_data.startswith('select_court_'):
        await CourtSelectionForBooking(
            update,
            context,
            deps,
            SelectCourtArg.from_callback_data(callback_data),
            update.effective_user.id,
        ).handle()
    elif callback_data.startswith('select_trainer_'):
        await TrainerSelectionForBooking(
            update,
            context,
            deps,
            SelectTrainerArg.from_callback_data(callback_data),
            update.effective_user.id,
        ).handle()
    elif callback_data.startswith('cancel_booking_'):
        await BookingCancellation(
            update,
            context,
            deps,
            CancelBookingArg.from_callback_data(callback_data),
            update.effective_user.id,
        ).handle()
