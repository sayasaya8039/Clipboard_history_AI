"""設定管理モジュール"""
from __future__ import annotations

import os
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path

# アプリケーション設定
APP_NAME = "クリップボード履歴"
APP_STORAGE_NAME = "Coppy"
APP_VERSION = "1.1.1"


@dataclass(frozen=True)
class RuntimePaths:
    package_dir: Path
    storage_dir: Path
    data_dir: Path
    images_dir: Path
    resources_dir: Path
    database_path: Path
    legacy_data_dir: Path
    legacy_images_dir: Path


def build_runtime_paths(
    package_dir: Path | None = None,
    appdata_root: Path | None = None,
    app_storage_name: str = APP_STORAGE_NAME,
) -> RuntimePaths:
    """実行環境ごとのリソース / 永続データパスを組み立てる。"""
    resolved_package_dir = Path(package_dir) if package_dir is not None else _resolve_package_dir()
    resolved_appdata_root = Path(appdata_root) if appdata_root is not None else _resolve_appdata_root()
    storage_dir = resolved_appdata_root / app_storage_name
    data_dir = storage_dir / "data"
    images_dir = storage_dir / "images"
    resources_dir = resolved_package_dir / "resources"
    database_path = data_dir / "clipboard_history.db"
    legacy_data_dir = resolved_package_dir / "data"
    legacy_images_dir = resolved_package_dir / "images"
    return RuntimePaths(
        package_dir=resolved_package_dir,
        storage_dir=storage_dir,
        data_dir=data_dir,
        images_dir=images_dir,
        resources_dir=resources_dir,
        database_path=database_path,
        legacy_data_dir=legacy_data_dir,
        legacy_images_dir=legacy_images_dir,
    )


def ensure_storage_dirs(paths: RuntimePaths) -> None:
    """永続ストレージ用ディレクトリを作成する。"""
    paths.storage_dir.mkdir(parents=True, exist_ok=True)
    paths.data_dir.mkdir(parents=True, exist_ok=True)
    paths.images_dir.mkdir(parents=True, exist_ok=True)


def migrate_legacy_storage(paths: RuntimePaths) -> None:
    """旧保存先から初回のみ永続データを移行する。"""
    ensure_storage_dirs(paths)

    legacy_database = paths.legacy_data_dir / "clipboard_history.db"
    if legacy_database.exists() and not paths.database_path.exists():
        shutil.copy2(legacy_database, paths.database_path)

    if not paths.legacy_images_dir.exists() or paths.legacy_images_dir == paths.images_dir:
        return

    for source in paths.legacy_images_dir.rglob("*"):
        if not source.is_file():
            continue
        relative = source.relative_to(paths.legacy_images_dir)
        destination = paths.images_dir / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        if not destination.exists():
            shutil.copy2(source, destination)


def _resolve_package_dir() -> Path:
    if getattr(sys, "frozen", False):
        bundle_dir = getattr(sys, "_MEIPASS", None)
        if bundle_dir:
            return Path(bundle_dir)
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent


def _resolve_appdata_root() -> Path:
    if os.getenv("APPDATA"):
        return Path(os.environ["APPDATA"])
    if os.getenv("XDG_DATA_HOME"):
        return Path(os.environ["XDG_DATA_HOME"])
    return Path.home() / "AppData" / "Roaming"


_RUNTIME_PATHS = build_runtime_paths()
ensure_storage_dirs(_RUNTIME_PATHS)
migrate_legacy_storage(_RUNTIME_PATHS)

# アプリケーションディレクトリ
APP_DIR = _RUNTIME_PATHS.package_dir
STORAGE_DIR = _RUNTIME_PATHS.storage_dir
DATA_DIR = _RUNTIME_PATHS.data_dir
IMAGES_DIR = _RUNTIME_PATHS.images_dir
RESOURCES_DIR = _RUNTIME_PATHS.resources_dir

# データベースパス
DATABASE_PATH = _RUNTIME_PATHS.database_path

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
