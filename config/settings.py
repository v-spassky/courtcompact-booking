from datetime import datetime, timedelta, timezone, tzinfo

from dateutil import tz as dateutil_tz
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    telegram_bot_token: str
    db_url: str
    log_level: str = 'INFO'
    timezone: tzinfo

    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='ignore')

    @field_validator('timezone', mode='before')
    @classmethod
    def _parse_timezone(cls, raw_value: str) -> tzinfo:
        tz_str = str(raw_value).strip()
        if not tz_str:
            raise ValueError('Timezone string cannot be empty')
        if '/' in tz_str or tz_str == 'UTC':
            tz = dateutil_tz.gettz(tz_str)
            if tz is None:
                raise ValueError(f'Unknown timezone: {tz_str}')
            return tz
        sign = 1
        if tz_str.startswith('-'):
            sign = -1
            tz_str = tz_str[1:]
        elif tz_str.startswith('+'):
            tz_str = tz_str[1:]
        if ':' in tz_str:
            parts = tz_str.split(':')
            hours, minutes = int(parts[0]), int(parts[1])
        else:
            hours, minutes = int(tz_str), 0
        return timezone(timedelta(hours=sign * hours, minutes=sign * minutes))


settings = Settings()  # type: ignore[call-arg]


def now_kiev() -> datetime:
    return datetime.now(settings.timezone).replace(tzinfo=None)
