from unittest.mock import AsyncMock, MagicMock

from telegram import Message, Update
from telegram.ext import ContextTypes

from bot.deps import Deps
from bot.router import handle_callback_query
from localization.base import Messages


async def test_unauthorized_user_sees_auth_prompt(deps: Deps) -> None:
    msg = MagicMock(spec=Message)
    msg.reply_text = AsyncMock()

    callback_query = MagicMock()
    callback_query.answer = AsyncMock()
    callback_query.data = 'main_menu'
    callback_query.message = msg

    update = MagicMock(spec=Update)
    update.callback_query = callback_query
    update.message = None
    update.effective_user = MagicMock()
    update.effective_user.id = 999999  # not in DB
    update.effective_user.username = 'stranger'
    update.effective_user.full_name = 'Stranger'

    context = MagicMock(spec=ContextTypes.DEFAULT_TYPE)
    context.bot_data = {'deps': deps}

    await handle_callback_query(update, context)

    msgs = Messages.get_for_language('')
    msg.reply_text.assert_called_once()
    assert msg.reply_text.call_args.args[0] == msgs.auth_request
