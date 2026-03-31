from typing import Any

from telegram import Update
from telegram.ext import Application, CallbackQueryHandler, CommandHandler, ContextTypes, MessageHandler, filters

from bot import router
from bot.deps import Deps, get_deps
from bot.handlers.auth import HandleContact, HandleUnknownMessage, StartCommand


async def _handle_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.effective_user:
        return
    await StartCommand(update, context, get_deps(context)).handle()


async def _handle_contact(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await HandleContact(update, context, get_deps(context)).handle()


async def _handle_unknown_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message or not update.effective_user:
        return
    await HandleUnknownMessage(update, context, get_deps(context)).handle()


def setup_application(deps: Deps) -> Application[Any, Any, Any, Any, Any, Any]:
    app = Application.builder().token(deps.settings.telegram_bot_token).build()
    app.bot_data['deps'] = deps
    app.add_handler(CommandHandler('start', _handle_start))
    app.add_handler(CallbackQueryHandler(router.handle_callback_query))
    app.add_handler(MessageHandler(filters.CONTACT, _handle_contact))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, _handle_unknown_message))
    return app
