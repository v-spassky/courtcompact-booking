import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from config.settings import settings
from db.models import Admin, User, make_session_factory
from db.repositories.admin import AdminRepository
from db.repositories.user import UserRepository


def main() -> None:
    parser = argparse.ArgumentParser(description='Create an admin user')
    parser.add_argument('--telegram-id', type=int, required=True, help='Telegram user ID')
    parser.add_argument('--name', type=str, required=True, help='Display name')
    args = parser.parse_args()

    factory = make_session_factory(settings.db_url)
    user_repo = UserRepository(factory)
    admin_repo = AdminRepository(factory)

    existing_admin = admin_repo.get_by_telegram_id(args.telegram_id)
    if existing_admin:
        print(f'User {args.telegram_id} is already an admin.')
        sys.exit(0)

    user = user_repo.get_by_telegram_id(args.telegram_id)
    if user is None:
        user = User(telegram_user_id=args.telegram_id, name=args.name)
        user_repo.save(user)
        print(f'Created user: {user.name} (telegram_id={args.telegram_id})')
    else:
        print(f'Using existing user: {user.name} (telegram_id={args.telegram_id})')

    admin = Admin(user_id=user.id)
    admin_repo.save(admin)
    print(f'Admin created successfully (admin_id={admin.id})')


if __name__ == '__main__':
    main()
