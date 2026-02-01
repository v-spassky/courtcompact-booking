from telegram.ext import ContextTypes


def _clear_admin_state(context: ContextTypes.DEFAULT_TYPE) -> None:
    keys_to_clear = [
        'admin_state',
        'admin_court_name',
        'admin_court_id',
        'admin_court_location_id',
        'admin_trainer_name',
        'admin_trainer_telegram_id',
        'admin_trainer_description',
        'admin_trainer_id',
        'admin_location_name',
        'admin_location_id',
        'admin_location_maps_link',
        'admin_student_name',
        'admin_student_phone',
        'admin_student_id',
    ]
    assert context.user_data is not None
    for key in keys_to_clear:
        context.user_data.pop(key, None)
