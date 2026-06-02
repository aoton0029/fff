"""Create an initial admin user.

Usage:
    uv run python scripts/create_admin.py
    uv run python scripts/create_admin.py --username admin --password secret
"""
import argparse
import sys
from pathlib import Path

# Ensure project root is on sys.path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.main import create_app
from app.extensions import db
from app.models.mst_user import User
from sqlalchemy import select


def create_admin(username: str, password: str) -> None:
    app = create_app()
    with app.app_context():
        db.create_all()

        existing = db.session.scalar(select(User).filter_by(username=username))
        if existing:
            print(f'[SKIP] ユーザー "{username}" は既に存在します。')
            return

        user = User(username=username)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        print(f'[OK] ユーザー "{username}" を作成しました (id={user.id})。')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='初期管理者ユーザーを作成します。')
    parser.add_argument('--username', default='admin', help='ユーザー名 (デフォルト: admin)')
    parser.add_argument('--password', default=None, help='パスワード (省略時は対話入力)')
    args = parser.parse_args()

    password = args.password
    if password is None:
        import getpass
        password = getpass.getpass(f'パスワードを入力してください ({args.username}): ')
        confirm = getpass.getpass('確認のため再入力してください: ')
        if password != confirm:
            print('[ERROR] パスワードが一致しません。')
            sys.exit(1)

    if not password:
        print('[ERROR] パスワードを入力してください。')
        sys.exit(1)

    create_admin(args.username, password)
