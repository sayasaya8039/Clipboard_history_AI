"""設定管理モジュール"""
from pathlib import Path

# アプリケーションディレクトリ
APP_DIR = Path(__file__).parent
DATA_DIR = APP_DIR / "data"
IMAGES_DIR = APP_DIR / "images"
RESOURCES_DIR = APP_DIR / "resources"

# ディレクトリが存在しない場合は作成
DATA_DIR.mkdir(exist_ok=True)
IMAGES_DIR.mkdir(exist_ok=True)
RESOURCES_DIR.mkdir(exist_ok=True)

# データベースパス
DATABASE_PATH = DATA_DIR / "clipboard_history.db"

# アプリケーション設定
APP_NAME = "クリップボード履歴"
APP_VERSION = "1.1.0"

# カテゴリ定義
CATEGORIES = {
    "url": "URL",
    "email": "メールアドレス",
    "code": "コード",
    "phone": "電話番号",
    "filepath": "ファイルパス",
    "image": "画像",
    "text": "テキスト",
}

# テーマ色定義
THEME = {
    "light": {
        "bg_main": "#FCFBF8",
        "bg_sub": "#F2EFE8",
        "bg_hover": "#E3DDD2",
        "text_main": "#1C1F24",
        "text_sub": "#565F6D",
        "border": "#D6D0C5",
        "accent": "#2F6FD6",
        "success": "#4CAF50",
        "error": "#F44336",
        "warning": "#FF9800",
        "info": "#2196F3",
    },
    "dark": {
        "bg_main": "#151618",
        "bg_sub": "#21242A",
        "bg_hover": "#2D323A",
        "text_main": "#F5F7FA",
        "text_sub": "#B3BCC8",
        "border": "#373C45",
        "accent": "#4A84E8",
        "success": "#4CAF50",
        "error": "#F44336",
        "warning": "#FF9800",
        "info": "#2196F3",
    },
}
