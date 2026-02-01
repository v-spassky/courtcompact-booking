from localization.base import Messages


class RussianMessages(Messages):
    # -------------------------------------------------------------------------
    # Navigation
    # -------------------------------------------------------------------------

    @property
    def btn_main_menu(self) -> str:
        return '🏠 Главное меню'

    @property
    def btn_back(self) -> str:
        return '◀️ Назад'

    @property
    def btn_back_to_main_menu(self) -> str:
        return '🏠 Вернуться в главное меню'

    @property
    def btn_select_other_location(self) -> str:
        return '◀️ Выбрать другую локацию'

    # -------------------------------------------------------------------------
    # Auth
    # -------------------------------------------------------------------------

    @property
    def welcome_start(self) -> str:
        return '🎾 Добро пожаловать в бот бронирования теннисных кортов!\n\nВыберите опцию ниже, чтобы начать:'

    @property
    def welcome_after_auth(self) -> str:
        return '🎾 Бот бронирования теннисных кортов\n\nВыберите опцию ниже:'

    @property
    def auth_request(self) -> str:
        return (
            '🔐 Для использования бота необходима авторизация.\n\n'
            'Для авторизации нажмите кнопку ниже и поделитесь своим номером телефона.\n\n'
            'Ваш номер телефона должен быть предварительно зарегистрирован администратором.'
        )

    @property
    def btn_share_phone(self) -> str:
        return '📱 Поделиться номером телефона'

    @property
    def auth_wrong_contact(self) -> str:
        return '❌ Пожалуйста, поделитесь своим номером телефона, а не контактом другого человека.'

    @property
    def auth_phone_not_found(self) -> str:
        return '❌ Ваш номер телефона не найден в системе.\n\nПожалуйста, обратитесь к администратору для регистрации.'

    def auth_success(self, name: str) -> str:
        return f'✅ Авторизация успешна!\n\nДобро пожаловать, {name}!'

    @property
    def unknown_command(self) -> str:
        return '❓ Извините, я не понимаю эту команду.'

    # -------------------------------------------------------------------------
    # Main menu buttons
    # -------------------------------------------------------------------------

    @property
    def btn_schedule_by_date(self) -> str:
        return '📅 Расписание корта по дате'

    @property
    def btn_schedule_weekly(self) -> str:
        return '📊 Расписание корта на неделю'

    @property
    def btn_trainer_schedule(self) -> str:
        return '👨‍🏫 Расписание тренеров'

    @property
    def btn_book_court(self) -> str:
        return '🎾 Забронировать корт'

    @property
    def btn_my_bookings(self) -> str:
        return '📋 Мои бронирования'

    @property
    def btn_cancel_booking(self) -> str:
        return '❌ Отменить бронирование'

    @property
    def btn_admin_panel(self) -> str:
        return '⚙️ Админ панель'

    # -------------------------------------------------------------------------
    # Booking flow
    # -------------------------------------------------------------------------

    @property
    def btn_no_trainer(self) -> str:
        return '⛔ Без тренера'

    def booking_select_trainer(self, court_name: str) -> str:
        return f'🎾 {court_name}\n\nВыберите тренера:'

    def booking_select_date(self, court_name: str, trainer_name: str | None) -> str:
        text = f'📅 Бронирование: {court_name}\n'
        if trainer_name:
            text += f'👨‍🏫 Тренер: {trainer_name}\n'
        text += '\nВыберите дату:'
        return text

    def booking_select_slot(self, court_name: str, date: str, trainer_name: str | None) -> str:
        text = f'📅 {court_name} — {date}\n'
        if trainer_name:
            text += f'👨‍🏫 Тренер: {trainer_name}\n'
        text += '\nВыберите слот:'
        return text

    @property
    def booking_no_slots_for_date(self) -> str:
        return '❌ Нет слотов на эту дату.'

    @property
    def slot_occupied(self) -> str:
        return 'Занят'

    def booking_confirmed(
        self, court_name: str, date: str, time: str, trainer_name: str | None, booking_id: str
    ) -> str:
        text = f'✅ Бронирование подтверждено!\n\n🎾 Корт: {court_name}\n📅 Дата: {date}\n🕐 Время: {time}\n'
        if trainer_name:
            text += f'👨‍🏫 Тренер: {trainer_name}\n'
        text += f'🆔 ID: {booking_id}'
        return text

    def booking_new_notification(self, student_name: str, court_name: str, date: str, time: str) -> str:
        return f'📬 Новое бронирование!\n\n👤 Студент: {student_name}\n🎾 Корт: {court_name}\n📅 Дата: {date}\n🕐 Время: {time}\n'

    @property
    def booking_failed(self) -> str:
        return '❌ Не удалось создать бронирование. Выбранный слот может быть недоступен.'

    @property
    def booking_slot_unavailable(self) -> str:
        return '❌ Не удалось создать бронирование. Выбранный слот может быть недоступен.'

    @property
    def booking_generic_error(self) -> str:
        return '❌ Не удалось создать бронирование. Пожалуйста, попробуйте снова.'

    @property
    def my_bookings_empty(self) -> str:
        return '📅 У вас нет бронирований.'

    @property
    def my_bookings_no_upcoming(self) -> str:
        return '📅 У вас нет предстоящих бронирований.'

    @property
    def my_bookings_title(self) -> str:
        return '📅 Ваши предстоящие бронирования:\n\n'

    @property
    def my_bookings_error(self) -> str:
        return '❌ Не удалось получить ваши бронирования. Пожалуйста, попробуйте снова.'

    @property
    def cancel_booking_no_upcoming(self) -> str:
        return '📅 У вас нет предстоящих бронирований для отмены.'

    @property
    def cancel_booking_select(self) -> str:
        return '❌ Выберите бронирование для отмены:'

    @property
    def cancel_booking_load_error(self) -> str:
        return '❌ Не удалось загрузить ваши бронирования. Пожалуйста, попробуйте снова.'

    @property
    def booking_not_found(self) -> str:
        return '❌ Бронирование не найдено.'

    @property
    def booking_cancelled(self) -> str:
        return '✅ Бронирование успешно отменено!'

    def booking_cancelled_notification(self, court_name: str, date: str, time: str) -> str:
        return f'❌ Бронирование отменено!\n\n🎾 Корт: {court_name}\n📅 Дата: {date}\n🕐 Время: {time}\n'

    def booking_cancelled_by_student(self, student_name: str) -> str:
        return f'\n👤 Отменил: {student_name}'

    def booking_cancelled_by_trainer(self, trainer_name: str) -> str:
        return f'\n👨‍🏫 Отменил: {trainer_name}'

    @property
    def cancel_booking_failed(self) -> str:
        return '❌ Не удалось отменить бронирование. Пожалуйста, проверьте ID бронирования.'

    @property
    def cancel_booking_error(self) -> str:
        return '❌ Не удалось отменить бронирование. Пожалуйста, попробуйте снова.'

    @property
    def book_select_location(self) -> str:
        return '📍 Выберите локацию для бронирования:\n\n'

    def book_no_courts(self, location_name: str | None) -> str:
        text = '❌ Нет доступных кортов для бронирования'
        if location_name:
            text += f' в локации "{location_name}"'
        return text + '.'

    def book_select_court(self, location_name: str | None, maps_link: str | None) -> str:
        if location_name and maps_link:
            return f'📍 <a href="{maps_link}">{location_name}</a>\n\n🎾 Выберите корт:'
        if location_name:
            return f'📍 {location_name}\n\n🎾 Выберите корт:'
        return '🎾 Выберите корт для бронирования'

    # -------------------------------------------------------------------------
    # Schedule
    # -------------------------------------------------------------------------

    def schedule_select_location(self, date: str) -> str:
        return f'📅 Расписание на {date}\n\n📍 Выберите локацию:\n\n'

    def schedule_no_courts(self, location_name: str | None) -> str:
        text = '❌ Нет доступных кортов'
        if location_name:
            text += f' в локации "{location_name}"'
        return text + '.'

    def schedule_select_court(self, date: str, location_name: str | None, maps_link: str | None) -> str:
        text = f'📅 Расписание на {date}\n'
        if location_name and maps_link:
            text += f'📍 <a href="{maps_link}">{location_name}</a>\n'
        elif location_name:
            text += f'📍 {location_name}\n'
        text += '\n🎾 Выберите корт:'
        return text

    def schedule_court_day(self, court_name: str, date: str, location_name: str | None, maps_link: str | None) -> str:
        loc = ''
        if location_name and maps_link:
            loc = f'📍 <a href="{maps_link}">{location_name}</a>\n'
        elif location_name:
            loc = f'📍 {location_name}\n'
        return f'{loc}📅 {court_name} — {date}\n\n'

    @property
    def schedule_no_slots(self) -> str:
        return 'Нет доступных слотов.'

    def schedule_slots_summary(self, available: int, total: int) -> str:
        return f'Доступно: {available}/{total}\n\n'

    @property
    def schedule_no_slots_for_day(self) -> str:
        return '❌ Нет слотов'

    @property
    def schedule_court_error(self) -> str:
        return '❌ Не удалось создать расписание. Пожалуйста, попробуйте снова.'

    def schedule_weekly_select_location(self, start: str, end: str) -> str:
        return f'📊 Недельное расписание ({start} - {end})\n\n📍 Выберите локацию:\n\n'

    def schedule_weekly_no_courts(self, location_name: str | None) -> str:
        text = '❌ Нет доступных кортов'
        if location_name:
            text += f' в локации "{location_name}"'
        return text + '.'

    def schedule_weekly_select_court(
        self, start: str, end: str, location_name: str | None, maps_link: str | None
    ) -> str:
        text = f'📊 Недельное расписание ({start} - {end})\n'
        if location_name and maps_link:
            text += f'📍 <a href="{maps_link}">{location_name}</a>\n'
        elif location_name:
            text += f'📍 {location_name}\n'
        text += '\n🎾 Выберите корт:'
        return text

    def schedule_weekly_court(
        self, court_name: str, start: str, end: str, location_name: str | None, maps_link: str | None
    ) -> str:
        loc = ''
        if location_name and maps_link:
            loc = f'📍 <a href="{maps_link}">{location_name}</a>\n'
        elif location_name:
            loc = f'📍 {location_name}\n'
        return f'{loc}📊 {court_name}\n{start} - {end}\n\n'

    def schedule_weekly_day_row(self, day_name: str, date: str, available: int, total: int, trainer_count: int) -> str:
        text = f'{day_name} {date}: '
        if total == 0:
            return text + '—\n'
        text += f'{available}/{total} слотов доступно'
        if trainer_count > 0:
            text += f' (👨‍🏫 {trainer_count})'
        return text + '\n'

    @property
    def schedule_weekly_day_empty(self) -> str:
        return '—\n'

    @property
    def schedule_weekly_error(self) -> str:
        return '❌ Не удалось создать недельное расписание. Пожалуйста, попробуйте снова.'

    @property
    def trainer_schedule_no_trainers(self) -> str:
        return '❌ Нет доступных тренеров.'

    @property
    def trainer_schedule_select(self) -> str:
        return '👨‍🏫 Выберите тренера для просмотра расписания:'

    def trainer_schedule_header(self, name: str, description: str | None) -> str:
        text = f'👨‍🏫 {name}\n'
        if description:
            text += f'{description}\n'
        return text + '\n'

    @property
    def trainer_schedule_no_upcoming(self) -> str:
        return '📅 Нет предстоящих занятий на следующие 14 дней.'

    @property
    def trainer_schedule_upcoming_title(self) -> str:
        return '📅 Предстоящие занятия (следующие 14 дней):\n\n'

    @property
    def btn_back_to_trainers(self) -> str:
        return '◀️ Назад к тренерам'

    @property
    def trainer_schedule_error(self) -> str:
        return '❌ Не удалось создать расписание тренера. Пожалуйста, попробуйте снова.'

    @property
    def generic_error(self) -> str:
        return '❌ Ошибка. Пожалуйста, попробуйте снова.'

    # -------------------------------------------------------------------------
    # Admin — shared
    # -------------------------------------------------------------------------

    @property
    def admin_no_access(self) -> str:
        return '❌ У вас нет доступа к админ панели.'

    @property
    def admin_menu_title(self) -> str:
        return '⚙️ Админ панель\n\nВыберите раздел:'

    @property
    def btn_admin_locations(self) -> str:
        return '📍 Локации'

    @property
    def btn_admin_courts(self) -> str:
        return '🎾 Корты'

    @property
    def btn_admin_trainers(self) -> str:
        return '👨‍🏫 Тренеры'

    @property
    def btn_admin_students(self) -> str:
        return '👥 Ученики'

    @property
    def btn_create(self) -> str:
        return '➕ Создать'

    @property
    def btn_edit(self) -> str:
        return '✏️ Изменить'

    @property
    def btn_delete(self) -> str:
        return '🗑️ Удалить'

    @property
    def btn_cancel(self) -> str:
        return '❌ Отмена'

    @property
    def btn_confirm_delete(self) -> str:
        return '🗑️ Да, удалить'

    # -------------------------------------------------------------------------
    # Admin — courts
    # -------------------------------------------------------------------------

    def admin_courts_menu(self, count: int) -> str:
        return f'🎾 Управление кортами\n\nВсего кортов: {count}\n\nВыберите действие:'

    @property
    def admin_court_select_location(self) -> str:
        return '📍 Выберите локацию для нового корта:'

    @property
    def admin_court_enter_name(self) -> str:
        return '🎾 Введите название корта:'

    @property
    def admin_court_enter_description(self) -> str:
        return '📝 Введите описание корта (или нажмите "Пропустить"):'

    @property
    def admin_court_skip_description(self) -> str:
        return '⏭️ Пропустить'

    def admin_court_created(self, name: str) -> str:
        return f'✅ Корт "{name}" успешно создан!'

    @property
    def admin_court_create_error(self) -> str:
        return '❌ Не удалось создать корт. Пожалуйста, попробуйте снова.'

    @property
    def admin_court_no_courts(self) -> str:
        return '❌ Нет доступных кортов.'

    @property
    def admin_court_select_to_edit(self) -> str:
        return '✏️ Выберите корт для редактирования:'

    @property
    def admin_court_enter_new_name(self) -> str:
        return '🎾 Введите новое название корта:'

    @property
    def admin_court_enter_new_description(self) -> str:
        return '📝 Введите новое описание корта (или нажмите "Пропустить"):'

    def admin_court_updated(self, name: str) -> str:
        return f'✅ Корт "{name}" успешно обновлён!'

    @property
    def admin_court_update_error(self) -> str:
        return '❌ Не удалось обновить корт. Пожалуйста, попробуйте снова.'

    @property
    def admin_court_select_to_delete(self) -> str:
        return '🗑️ Выберите корт для удаления:'

    def admin_court_confirm_delete(self, name: str) -> str:
        return f'⚠️ Вы уверены, что хотите удалить корт "{name}"?'

    def admin_court_deleted(self, name: str) -> str:
        return f'✅ Корт "{name}" успешно удалён!'

    @property
    def admin_court_delete_error(self) -> str:
        return '❌ Не удалось удалить корт. Пожалуйста, попробуйте снова.'

    # -------------------------------------------------------------------------
    # Admin — trainers
    # -------------------------------------------------------------------------

    def admin_trainers_menu(self, count: int) -> str:
        return f'👨‍🏫 Управление тренерами\n\nВсего тренеров: {count}\n\nВыберите действие:'

    @property
    def admin_trainer_enter_name(self) -> str:
        return '👨‍🏫 Введите имя тренера:'

    @property
    def admin_trainer_enter_telegram_id(self) -> str:
        return '📱 Введите Telegram ID тренера:'

    @property
    def admin_trainer_enter_description(self) -> str:
        return '📝 Введите описание тренера (или нажмите "Пропустить"):'

    @property
    def admin_trainer_skip_description(self) -> str:
        return '⏭️ Пропустить'

    def admin_trainer_created(self, name: str) -> str:
        return f'✅ Тренер "{name}" успешно создан!'

    @property
    def admin_trainer_create_error(self) -> str:
        return '❌ Не удалось создать тренера. Пожалуйста, попробуйте снова.'

    @property
    def admin_trainer_no_trainers(self) -> str:
        return '❌ Нет тренеров.'

    @property
    def admin_trainer_select_to_edit(self) -> str:
        return '✏️ Выберите тренера для редактирования:'

    @property
    def admin_trainer_enter_new_name(self) -> str:
        return '👨‍🏫 Введите новое имя тренера:'

    @property
    def admin_trainer_enter_new_telegram_id(self) -> str:
        return '📱 Введите новый Telegram ID тренера:'

    @property
    def admin_trainer_enter_new_description(self) -> str:
        return '📝 Введите новое описание тренера (или нажмите "Пропустить"):'

    def admin_trainer_updated(self, name: str) -> str:
        return f'✅ Тренер "{name}" успешно обновлён!'

    @property
    def admin_trainer_update_error(self) -> str:
        return '❌ Не удалось обновить тренера. Пожалуйста, попробуйте снова.'

    @property
    def admin_trainer_select_to_delete(self) -> str:
        return '🗑️ Выберите тренера для удаления:'

    def admin_trainer_confirm_delete(self, name: str) -> str:
        return f'⚠️ Вы уверены, что хотите удалить тренера "{name}"?'

    def admin_trainer_deleted(self, name: str) -> str:
        return f'✅ Тренер "{name}" успешно удалён!'

    @property
    def admin_trainer_delete_error(self) -> str:
        return '❌ Не удалось удалить тренера. Пожалуйста, попробуйте снова.'

    # -------------------------------------------------------------------------
    # Admin — locations
    # -------------------------------------------------------------------------

    def admin_locations_menu(self, count: int) -> str:
        return f'📍 Управление локациями\n\nВсего локаций: {count}\n\nВыберите действие:'

    @property
    def admin_location_enter_name(self) -> str:
        return '📍 Введите название локации:'

    @property
    def admin_location_enter_maps_link(self) -> str:
        return '🗺️ Введите ссылку на Google Maps (или нажмите "Пропустить"):'

    @property
    def admin_location_skip_maps_link(self) -> str:
        return '⏭️ Пропустить'

    def admin_location_created(self, name: str) -> str:
        return f'✅ Локация "{name}" успешно создана!'

    @property
    def admin_location_create_error(self) -> str:
        return '❌ Не удалось создать локацию. Пожалуйста, попробуйте снова.'

    @property
    def admin_location_no_locations(self) -> str:
        return '❌ Нет доступных локаций.'

    @property
    def admin_location_select_to_edit(self) -> str:
        return '✏️ Выберите локацию для редактирования:'

    @property
    def admin_location_enter_new_name(self) -> str:
        return '📍 Введите новое название локации:'

    @property
    def admin_location_enter_new_maps_link(self) -> str:
        return '🗺️ Введите новую ссылку на Google Maps (или нажмите "Пропустить"):'

    def admin_location_updated(self, name: str) -> str:
        return f'✅ Локация "{name}" успешно обновлена!'

    @property
    def admin_location_update_error(self) -> str:
        return '❌ Не удалось обновить локацию. Пожалуйста, попробуйте снова.'

    @property
    def admin_location_select_to_delete(self) -> str:
        return '🗑️ Выберите локацию для удаления:'

    def admin_location_confirm_delete(self, name: str) -> str:
        return f'⚠️ Вы уверены, что хотите удалить локацию "{name}"?'

    def admin_location_deleted(self, name: str) -> str:
        return f'✅ Локация "{name}" успешно удалена!'

    @property
    def admin_location_delete_error(self) -> str:
        return '❌ Не удалось удалить локацию. Пожалуйста, попробуйте снова.'

    # -------------------------------------------------------------------------
    # Admin — students
    # -------------------------------------------------------------------------

    def admin_students_menu(self, total: int, authorized: int) -> str:
        return f'👥 Управление учениками\n\nВсего учеников: {total}\nАвторизованных: {authorized}\n\nВыберите действие:'

    @property
    def admin_student_enter_name(self) -> str:
        return '👤 Введите имя ученика:'

    @property
    def admin_student_enter_phone(self) -> str:
        return '📱 Введите номер телефона ученика:'

    def admin_student_created(self, name: str) -> str:
        return f'✅ Ученик "{name}" успешно добавлен!'

    @property
    def admin_student_phone_exists(self) -> str:
        return '❌ Ученик с таким номером телефона уже существует.'

    @property
    def admin_student_create_error(self) -> str:
        return '❌ Не удалось добавить ученика. Пожалуйста, попробуйте снова.'

    @property
    def admin_student_no_students(self) -> str:
        return '❌ Нет учеников.'

    @property
    def admin_student_select_to_edit(self) -> str:
        return '✏️ Выберите ученика для редактирования:'

    @property
    def admin_student_enter_new_name(self) -> str:
        return '👤 Введите новое имя ученика:'

    @property
    def admin_student_enter_new_phone(self) -> str:
        return '📱 Введите новый номер телефона ученика:'

    def admin_student_updated(self, name: str) -> str:
        return f'✅ Данные ученика "{name}" успешно обновлены!'

    @property
    def admin_student_update_error(self) -> str:
        return '❌ Не удалось обновить данные ученика. Пожалуйста, попробуйте снова.'

    @property
    def admin_student_select_to_delete(self) -> str:
        return '🗑️ Выберите ученика для удаления:'

    def admin_student_confirm_delete(self, name: str) -> str:
        return f'⚠️ Вы уверены, что хотите удалить ученика "{name}"?'

    def admin_student_deleted(self, name: str) -> str:
        return f'✅ Ученик "{name}" успешно удалён!'

    @property
    def admin_student_delete_error(self) -> str:
        return '❌ Не удалось удалить ученика. Пожалуйста, попробуйте снова.'
