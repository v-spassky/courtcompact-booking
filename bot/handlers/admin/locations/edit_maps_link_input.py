import logging
from uuid import UUID

from bot.handlers.admin._utils import _clear_admin_state
from bot.handlers.admin.locations._save_edited import _save_edited_location
from bot.handlers.base import TextInputHandler

logger = logging.getLogger(__name__)


class AdminEditLocationMapsLinkInput(TextInputHandler):
    async def _authorize(self) -> bool:
        return True

    async def _process(self) -> None:
        assert self._context.user_data is not None
        location_id = self._context.user_data.get('admin_location_id')
        if not location_id:
            _clear_admin_state(self._context)
            return
        location = self._deps.location_repo.get(UUID(location_id))
        if not location:
            _clear_admin_state(self._context)
            return
        if self._text.strip() == '--':
            self._context.user_data['admin_location_maps_link'] = None
        elif self._text.strip() == '-':
            self._context.user_data['admin_location_maps_link'] = location.maps_link
        else:
            self._context.user_data['admin_location_maps_link'] = self._text.strip()
        await _save_edited_location(self._update, self._context)
