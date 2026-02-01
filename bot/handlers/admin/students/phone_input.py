import logging
from uuid import uuid4

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from bot.deps import get_deps
from bot.handlers.admin._utils import _clear_admin_state
from bot.handlers.auth import _log_user_action
from db.models import Student
from localization import get_messages

logger = logging.getLogger(__name__)


async def _handle_admin_student_phone_input(update: Update, context: ContextTypes.DEFAULT_TYPE, phone: str) -> None:
    assert update.message is not None
    assert context.user_data is not None
    msgs = get_messages()
    deps = get_deps(context)
    student_name = context.user_data.get('admin_student_name', '')
    if not student_name:
        _clear_admin_state(context)
        return

    if not phone or phone == '-':
        context.user_data.pop('admin_state', None)
        text = '❌ Номер телефона обязателен для ученика.'
        keyboard = [
            [InlineKeyboardButton('🔄 Попробовать снова', callback_data='admin_create_student')],
            [InlineKeyboardButton(msgs.btn_cancel, callback_data='admin_students')],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(text, reply_markup=reply_markup)
        return

    existing = deps.student_repo.get_by_phone(phone)
    if existing:
        _clear_admin_state(context)
        keyboard = [
            [InlineKeyboardButton('🔄 Попробовать снова', callback_data='admin_create_student')],
            [InlineKeyboardButton(msgs.btn_cancel, callback_data='admin_students')],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(msgs.admin_student_phone_exists, reply_markup=reply_markup)
        return

    _clear_admin_state(context)

    try:
        student = Student(
            id=str(uuid4()),
            name=student_name,
            phone=phone,
            telegram_user_id=None,
        )
        deps.student_repo.save(student)

        if update.effective_user:
            _log_user_action(update.effective_user, f'created student: {student_name}')

        text = msgs.admin_student_created(name=student_name)
        text += f'\n📱 Телефон: {phone}'

        keyboard = [
            [InlineKeyboardButton('➕ Создать ещё', callback_data='admin_create_student')],
            [InlineKeyboardButton('◀️ К ученикам', callback_data='admin_students')],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(text, reply_markup=reply_markup)

    except Exception:
        logger.exception('Failed to create student')
        keyboard = [[InlineKeyboardButton('◀️ К ученикам', callback_data='admin_students')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(msgs.admin_student_create_error, reply_markup=reply_markup)
