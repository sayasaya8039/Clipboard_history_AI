"""
クリップボード履歴 + AI整理アプリ

コピーした内容を自動でカテゴリ分けして保存するアプリケーション
"""
import sys
from pathlib import Path

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt

# アプリケーションディレクトリをパスに追加
sys.path.insert(0, str(Path(__file__).parent))

from config import APP_NAME
from database import init_database, get_setting
from clipboard_monitor import ClipboardMonitor
from ui.styles import get_stylesheet, is_dark_mode
from ui.tray_icon import TrayIcon
from ui.main_window import MainWindow
from ui.settings_dialog import SettingsDialog


class Application:
    """アプリケーションクラス"""

    def __init__(self):
        # QApplication作成
        self.app = QApplication(sys.argv)
        self.app.setApplicationName(APP_NAME)
        self.app.setQuitOnLastWindowClosed(False)  # ウィンドウを閉じても終了しない

        # データベース初期化
        init_database()

        # テーマ適用
        self._apply_theme()

        # コンポーネント初期化
        self._init_components()

        # シグナル接続
        self._connect_signals()

    def _init_components(self) -> None:
        """コンポーネントを初期化"""
        # クリップボード監視
        self.monitor = ClipboardMonitor()
        self._update_ai_settings()

        # メインウィンドウ
        self.main_window = MainWindow()

        # 設定ダイアログ（メインウィンドウを親に設定）
        self.settings_dialog = SettingsDialog(self.main_window)

        # システムトレイ
        self.tray_icon = TrayIcon()

    def _connect_signals(self) -> None:
        """シグナルを接続"""
        # トレイアイコン
        self.tray_icon.show_window_requested.connect(self._show_main_window)
        self.tray_icon.settings_requested.connect(self._show_settings)
        self.tray_icon.quit_requested.connect(self._quit)

        # メインウィンドウ
        self.main_window.copy_requested.connect(self._on_copy_requested)
        self.main_window.settings_requested.connect(self._show_settings)

        # クリップボード監視
        self.monitor.history_added.connect(self._on_history_added)

        # 設定ダイアログ
        self.settings_dialog.settings_changed.connect(self._on_settings_changed)

    def _apply_theme(self) -> None:
        """テーマを適用"""
        theme_setting = get_setting("theme", "system")

        if theme_setting == "system":
            dark = is_dark_mode()
        elif theme_setting == "dark":
            dark = True
        else:
            dark = False

        self.app.setStyleSheet(get_stylesheet(dark))

    def _update_ai_settings(self) -> None:
        """AI設定を更新"""
        provider = get_setting("ai_provider", "none")
        self.monitor.set_use_ai(provider != "none")

    def _show_main_window(self) -> None:
        """メインウィンドウを表示"""
        self.main_window.show()
        self.main_window.raise_()
        self.main_window.activateWindow()

    def _show_settings(self) -> None:
        """設定ダイアログを表示"""
        self.settings_dialog.exec()

    def _on_copy_requested(self, content_type: str, content: str, image_path: str) -> None:
        """コピーリクエスト時"""
        self.monitor.copy_to_clipboard(content_type, content, image_path)

    def _on_history_added(self, history_id: int) -> None:
        """履歴追加時"""
        # メインウィンドウが表示されている場合は更新
        if self.main_window.isVisible():
            self.main_window.refresh_history()

    def _on_settings_changed(self) -> None:
        """設定変更時"""
        self._apply_theme()
        self._update_ai_settings()

    def _quit(self) -> None:
        """アプリケーションを終了"""
        self.monitor.stop()
        self.tray_icon.hide()
        self.app.quit()

    def run(self) -> int:
        """アプリケーションを実行"""
        # クリップボード監視開始
        self.monitor.start()

        # トレイアイコン表示
        self.tray_icon.show()
        self.tray_icon.show_message(
            APP_NAME,
            "クリップボード監視を開始しました",
        )

        return self.app.exec()


def main():
    """エントリーポイント"""
    app = Application()
    sys.exit(app.run())


if __name__ == "__main__":
    main()
