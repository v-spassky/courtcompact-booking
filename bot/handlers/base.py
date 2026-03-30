import logging
from abc import ABC, abstractmethod

from telegram import Update
from telegram.ext import ContextTypes

from bot.deps import Deps
from localization.base import Messages

logger = logging.getLogger(__name__)


class Handler(ABC):
    def __init__(self, update: Update, context: ContextTypes.DEFAULT_TYPE, deps: Deps) -> None:
        self._update = update
        self._context = context
        self._deps = deps
        # TODO: add default language
        language_code = (self._update.effective_user.language_code or '') if self._update.effective_user else ''
        self._messages = Messages.get_for_language(language_code)

    async def handle(self) -> None:
        try:
            if not await self._authorize():
                return
            await self._process()
        except Exception as e:
            await self._on_error(e)

    @abstractmethod
    async def _authorize(self) -> bool: ...

    @abstractmethod
    async def _process(self) -> None: ...

    async def _on_error(self, error: Exception) -> None:
        logger.exception('Unhandled error in %s', type(self).__name__)


class TextInputHandler(Handler):
    def __init__(self, update: Update, context: ContextTypes.DEFAULT_TYPE, deps: Deps, text: str) -> None:
        super().__init__(update, context, deps)
        self._text = text
