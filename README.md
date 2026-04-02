Telegram bot for managing tennis court bookings.

## Requirements

- Python 3.13
- [uv](https://docs.astral.sh/uv/)

## Setup

Create a `.env` file and add set app configurations (at minimum set `TELEGRAM_BOT_TOKEN`):

```
cp .env.example .env
```

Install dependencies:

```
uv sync
```

Run DB  migrations:

```
uv run alembic upgrade head
```

## Running

```
uv run python main.py
```

## Docker

Build and run with Docker:

```
docker build -t courtcompact-booking .
```

```
docker run --env-file .env -v $(pwd)/.data:/app/.data courtcompact-booking
```

Note: run DB migrations before starting the bot (or against the same DB the container will use):

```
uv run alembic upgrade head
```

## Scripts

### `scripts/create_admin.py`

Creates an admin user by Telegram ID. If the Telegram user doesn't exist in the database yet, a new user record is
created. If the user already exists, it is reused. Exits without making changes if the user is already an admin.

```
uv run python scripts/create_admin.py --telegram-id <id> --name "<name>"
```

Arguments:

- `--telegram-id` — Telegram user ID of the new admin (integer, required)
- `--name` — display name for the user record (string, required)

## CI checks

Install pre-commit hooks:

```
uv run pre-commit install
```

Run them:

```
uv run pre-commit run --all-files
```
