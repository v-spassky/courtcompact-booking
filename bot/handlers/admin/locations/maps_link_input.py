import logging

from bot.handlers.admin.locations._save import _save_location
from bot.handlers.base import TextInputHandler

logger = logging.getLogger(__name__)


class AdminLocationMapsLinkInput(TextInputHandler):
    async def _authorize(self) -> bool:
        return True

    async def _process(self) -> None:
        assert self._context.user_data is not None
        if self._text.strip() == '-':
            self._context.user_data['admin_location_maps_link'] = None
        else:
            self._context.user_data['admin_location_maps_link'] = self._text.strip()
        await _save_location(self._update, self._context)
