"""設定管理モジュール"""
import os
from pathlib import Path
from dotenv import load_dotenv

# .envファイルを読み込み
load_dotenv()

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

# AI設定
AI_PROVIDER = os.getenv("AI_PROVIDER", "none")  # none, openai, gemini
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# アプリケーション設定
APP_NAME = "クリップボード履歴"
APP_VERSION = "1.0.0"

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
        "bg_main": "#FFFFFF",
        "bg_sub": "#F5F5F5",
        "bg_hover": "#EEEEEE",
        "text_main": "#1A1A1A",
        "text_sub": "#666666",
        "border": "#E0E0E0",
        "accent": "#333333",
        "success": "#4CAF50",
        "error": "#F44336",
        "warning": "#FF9800",
        "info": "#2196F3",
    },
    "dark": {
        "bg_main": "#1A1A1A",
        "bg_sub": "#2D2D2D",
        "bg_hover": "#3D3D3D",
        "text_main": "#F5F5F5",
        "text_sub": "#A0A0A0",
        "border": "#404040",
        "accent": "#E0E0E0",
        "success": "#4CAF50",
        "error": "#F44336",
        "warning": "#FF9800",
        "info": "#2196F3",
    },
}
