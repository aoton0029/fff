# flask汎用プロジェクトベース

# 概要
Flaskを使用した汎用的なプロジェクトのベースコードです。基本的な機能や構成が含まれており、プロジェクトの立ち上げを迅速に行うことができます。

# 技術スタック
- Python 3.14
- Flask
- SQLAlchemy
- SQLServer
- bootstrap 5
- htmx

# ライブラリ
- Flask-htmx
- Flask-SQLAlchemy
- pyodbc
- Flask-wtf
- Flask-Login
- SQLAlchemy

# ディレクトリ構成
``` 
flask_project/
├─app
│  ├─api
│  ├─config
│  ├─forms
│  ├─models
│  ├─services
│  ├─static
│  ├─templates
│  ├─utils
│  └─views
└─tests
```

# 主要な機能
- ユーザー認証(ユーザーIDとパスワード, Flask-Loginを使用, セッション管理)
- データベース操作(SQLAlchemyを使用)
- フォーム処理(Flask-WTFを使用)
- 静的ファイルの管理(CSS, JavaScript, 画像など)
- APIエンドポイントの作成(Flask-htmxを使用)
- エラーハンドリング
- logging(出力先はコンソール)
- コンポーネントベースのUI構築(bootstrap 5を使用)
- 複数ファイルアップロード機能
- セッション管理
- テーブルのソート、フィルタリング、ページネーション機能、およびCSVエクスポート機能を備えたテーブルコンポーネント

# 画面構成(template)
- ログイン画面
- ベース画面
    - ナビゲーションサイドバー
        - メニュー
        - ユーザー名
        - ロゴ
    - コンテンツ表示エリア
    - アラート
- エラー画面
- セッションアウト画面

# コンポーネント
- コンファームモーダル
- アラートモーダル
- ファイルアップロードコンポーネント
- テーブルコンポーネント
- フォームコンポーネント