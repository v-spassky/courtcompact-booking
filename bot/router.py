import logging
from datetime import datetime

from telegram import Update
from telegram.ext import ContextTypes

from bot.deps import get_deps
from bot.handlers import auth, booking, schedule
from bot.handlers.admin import courts, locations
from bot.handlers.admin import menu as admin_menu
from bot.handlers.admin import students, trainers
from config.settings import now_kiev

logger = logging.getLogger(__name__)


async def handle_callback_query(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.callback_query or not update.effective_user:
        return

    query = update.callback_query
    await query.answer()

    data = query.data
    if data is None:
        return
    user_id = update.effective_user.id

    deps = get_deps(context)

    if data != 'ignore':
        auth._log_user_action(update.effective_user, f'clicked button: {data}')

    if data != 'ignore' and not auth._is_authorized(user_id, deps):
        await auth._show_authorization_request(update, context)
        return

    if data == 'main_menu':
        await auth.show_main_menu(update, context, edit_message=True)
    elif data == 'ignore':
        await query.answer()
        return
    elif data == 'select_date_schedule':
        now = now_kiev()
        calendar_markup = auth._create_calendar(now.year, now.month)
        await query.edit_message_text('📅 Выберите дату для просмотра расписания:', reply_markup=calendar_markup)
    elif data.startswith('cal_'):
        parts = data.split('_')
        year, month = int(parts[1]), int(parts[2])
        calendar_markup = auth._create_calendar(year, month)
        await query.edit_message_text('📅 Выберите дату для просмотра расписания:', reply_markup=calendar_markup)
    elif data.startswith('date_'):
        parts = data.split('_')
        year, month, day = int(parts[1]), int(parts[2]), int(parts[3])
        selected_date = datetime(year, month, day)
        await schedule._handle_schedule_for_date(update, context, selected_date)
    elif data.startswith('schedule_location_'):
        parts = data.split('_')
        location_id_short = parts[2]
        year, month, day = int(parts[3]), int(parts[4]), int(parts[5])
        selected_date = datetime(year, month, day)
        locations_list = deps.location_repo.get_active()
        location_id = None
        for loc in locations_list:
            if str(loc.id).startswith(location_id_short):
                location_id = str(loc.id)
                break
        await schedule._handle_schedule_for_date_show_courts(update, context, selected_date, location_id)
    elif data.startswith('court_day_'):
        parts = data.split('_')
        court_id = parts[2]
        year, month, day = int(parts[3]), int(parts[4]), int(parts[5])
        selected_date = datetime(year, month, day)
        await schedule._handle_court_schedule_for_day(update, context, court_id, selected_date)
    elif data.startswith('court_week_'):
        parts = data.split('_')
        court_id = parts[2]
        year, month, day = int(parts[3]), int(parts[4]), int(parts[5])
        start_of_week = datetime(year, month, day)
        await schedule._handle_court_schedule_for_week(update, context, court_id, start_of_week)
    elif data == 'schedule_weekly':
        await schedule._handle_schedule_weekly(update, context)
    elif data.startswith('weekly_location_'):
        parts = data.split('_')
        location_id_short = parts[2]
        year, month, day = int(parts[3]), int(parts[4]), int(parts[5])
        start_of_week = datetime(year, month, day)
        locations_list = deps.location_repo.get_active()
        location_id = None
        for loc in locations_list:
            if str(loc.id).startswith(location_id_short):
                location_id = str(loc.id)
                break
        await schedule._handle_schedule_weekly_show_courts(update, context, start_of_week, location_id)
    elif data == 'trainer_schedule':
        await schedule._handle_trainer_schedule_menu(update, context)
    elif data.startswith('view_trainer_'):
        await schedule._handle_view_trainer_schedule(update, context, data)
    elif data.startswith('book_cal_'):
        await booking._handle_booking_calendar_navigation(update, context, data)
    elif data.startswith('book_date_'):
        await booking._handle_booking_date_selection(update, context, data)
    elif data.startswith('book_slot_'):
        await booking._handle_booking_slot_selection(update, context, data, user_id)
    elif data == 'book_court':
        await booking._handle_book_court_select_location(update, context)
    elif data.startswith('book_location_'):
        await booking._handle_book_court(update, context, data)
    elif data == 'my_bookings':
        await booking._handle_my_bookings(update, context)
    elif data == 'cancel_booking':
        await booking._handle_cancel_booking_menu(update, context)
    elif data == 'admin_menu':
        await admin_menu._handle_admin_menu(update, context)
    elif data == 'admin_courts':
        await admin_menu._handle_admin_courts_menu(update, context)
    elif data == 'admin_trainers':
        await admin_menu._handle_admin_trainers_menu(update, context)
    elif data == 'admin_locations':
        await admin_menu._handle_admin_locations_menu(update, context)
    elif data == 'admin_create_location':
        await locations._handle_admin_create_location_start(update, context)
    elif data == 'admin_edit_location':
        await locations._handle_admin_edit_location_list(update, context)
    elif data.startswith('admin_edit_location_'):
        await locations._handle_admin_edit_location_start(update, context, data)
    elif data == 'admin_delete_location':
        await locations._handle_admin_delete_location_list(update, context)
    elif data.startswith('admin_delete_location_'):
        await locations._handle_admin_delete_location_confirm(update, context, data)
    elif data.startswith('admin_confirm_delete_location_'):
        await locations._handle_admin_delete_location_execute(update, context, data)
    elif data == 'admin_create_court':
        await courts._handle_admin_create_court_select_location(update, context)
    elif data.startswith('admin_court_location_'):
        await courts._handle_admin_create_court_start(update, context, data)
    elif data == 'admin_edit_court':
        await courts._handle_admin_edit_court_list(update, context)
    elif data.startswith('admin_edit_court_'):
        await courts._handle_admin_edit_court_start(update, context, data)
    elif data == 'admin_delete_court':
        await courts._handle_admin_delete_court_list(update, context)
    elif data.startswith('admin_delete_court_'):
        await courts._handle_admin_delete_court_confirm(update, context, data)
    elif data.startswith('admin_confirm_delete_court_'):
        await courts._handle_admin_delete_court_execute(update, context, data)
    elif data == 'admin_create_trainer':
        await trainers._handle_admin_create_trainer_start(update, context)
    elif data == 'admin_edit_trainer':
        await trainers._handle_admin_edit_trainer_list(update, context)
    elif data.startswith('admin_edit_trainer_'):
        await trainers._handle_admin_edit_trainer_start(update, context, data)
    elif data == 'admin_delete_trainer':
        await trainers._handle_admin_delete_trainer_list(update, context)
    elif data.startswith('admin_delete_trainer_'):
        await trainers._handle_admin_delete_trainer_confirm(update, context, data)
    elif data.startswith('admin_confirm_delete_trainer_'):
        await trainers._handle_admin_delete_trainer_execute(update, context, data)
    elif data == 'admin_students':
        await admin_menu._handle_admin_students_menu(update, context)
    elif data == 'admin_create_student':
        await students._handle_admin_create_student_start(update, context)
    elif data == 'admin_edit_student':
        await students._handle_admin_edit_student_list(update, context)
    elif data.startswith('admin_edit_student_'):
        await students._handle_admin_edit_student_start(update, context, data)
    elif data == 'admin_delete_student':
        await students._handle_admin_delete_student_list(update, context)
    elif data.startswith('admin_delete_student_'):
        await students._handle_admin_delete_student_confirm(update, context, data)
    elif data.startswith('admin_confirm_delete_student_'):
        await students._handle_admin_delete_student_execute(update, context, data)
    elif data.startswith('select_court_'):
        await booking._handle_court_selection_for_booking(update, context, query, data, user_id)
    elif data.startswith('select_trainer_'):
        await booking._handle_trainer_selection_for_booking(update, context, query, data, user_id)
    elif data.startswith('cancel_booking_'):
        await booking._handle_booking_cancellation(update, context, query, data, user_id)
