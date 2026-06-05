
# python環境構築手順
1. uv をインストール
[](https://pypi.org/project/uv/)からインストーラーをダウンロードして実行

2. プロジェクトルートで以下のコマンドを実行して、仮想環境を構築
```bash
uv sync
```

3. 仮想環境をアクティベート
```bash
.venv\Scripts\activate
```


# テスト(development)環境構築手順
テスト用DBはローカルのsqliteを使用するため、特別な環境構築は不要です。上記のpython環境構築手順を実行後、以下のコマンドでテストを実行できます。
```bash
# テーブル生成と初期マスタデータの投入
uv run scripts\init_app_db.py
# テスト用に管理者ユーザーを作成(本番では、ユーザーは手動で作成する)
uv run scripts\create_admin.py
```

# 本番環境構築手順
本番環境では、SQLServerを使用するため、以下の環境構築が必要です。