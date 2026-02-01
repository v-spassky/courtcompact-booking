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

## CI checks

Install pre-commit hooks:

```
uv run pre-commit install
```

Run them:

```
uv run pre-commit run --all-files
```
