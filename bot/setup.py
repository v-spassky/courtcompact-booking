from typing import Any

from telegram.ext import Application, CallbackQueryHandler, CommandHandler, MessageHandler, filters

from bot import router
from bot.deps import Deps
from bot.handlers import auth


def setup_application(deps: Deps) -> Application[Any, Any, Any, Any, Any, Any]:
    app = Application.builder().token(deps.settings.telegram_bot_token).build()
    app.bot_data['deps'] = deps
    app.add_handler(CommandHandler('start', auth.start_command))
    app.add_handler(CallbackQueryHandler(router.handle_callback_query))
    app.add_handler(MessageHandler(filters.CONTACT, auth.handle_contact))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, auth.handle_unknown_message))
    return app
