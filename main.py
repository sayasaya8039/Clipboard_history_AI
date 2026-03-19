"""
クリップボード履歴アプリ

コピーした内容を自動でカテゴリ分けして保存するアプリケーション
"""
import sys
from pathlib import Path

from PyQt6.QtGui import QFont, QIcon
from PyQt6.QtWidgets import QApplication

# アプリケーションディレクトリをパスに追加
sys.path.insert(0, str(Path(__file__).parent))

from config import APP_NAME, RESOURCES_DIR
from database import init_database, get_setting
from clipboard_monitor import ClipboardMonitor
from startup import is_startup_launch, set_launch_at_startup_enabled
from ui.styles import get_stylesheet, is_dark_mode
from ui.tray_icon import TrayIcon
from ui.main_window import MainWindow
from ui.settings_dialog import SettingsDialog


class Application:
    """アプリケーションクラス"""

    def __init__(self):
        self._started_from_startup = is_startup_launch(sys.argv[1:])

        # QApplication作成
        self.app = QApplication(sys.argv)
        self.app.setApplicationName(APP_NAME)
        self.app.setStyle("Fusion")
        self.app.setFont(QFont("Segoe UI", 9))
        self.app.setWindowIcon(QIcon(str(RESOURCES_DIR / "icon.ico")))
        self.app.setQuitOnLastWindowClosed(False)  # ウィンドウを閉じても終了しない

        # データベース初期化
        init_database()
        self._sync_launch_at_startup_setting()

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
        self.main_window.close_requested.connect(self._quit)
        self.main_window.minimize_requested.connect(self._minimize_to_tray)

        # クリップボード監視
        self.monitor.history_added.connect(self._on_history_added)

        # 設定ダイアログ
        self.settings_dialog.settings_changed.connect(self._on_settings_changed)

    def _apply_theme(self) -> None:
        """テーマを適用"""
        theme_setting = get_setting("theme", "dark")

        if theme_setting == "system":
            dark = is_dark_mode()
        elif theme_setting == "dark":
            dark = True
        else:
            dark = False

        self.app.setStyleSheet(get_stylesheet(dark))

    def _show_main_window(self) -> None:
        """メインウィンドウを表示"""
        self.main_window.show()
        self.main_window.raise_()
        self.main_window.activateWindow()

    def _sync_launch_at_startup_setting(self) -> None:
        """保存済みの自動起動設定を OS に反映する。"""
        if get_setting("launch_at_startup_migrated", "0") != "1":
            return

        try:
            set_launch_at_startup_enabled(get_setting("launch_at_startup", "0") == "1")
        except OSError as exc:
            print(f"自動起動の同期に失敗: {exc}")

    def _show_settings(self) -> None:
        """設定ダイアログを表示"""
        self.settings_dialog.exec()

    def _minimize_to_tray(self) -> None:
        """メインウィンドウをシステムトレイに格納する。"""
        self.main_window.hide()

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

    def _quit(self) -> None:
        """アプリケーションを終了"""
        self.monitor.stop()
        self.main_window.hide()
        self.tray_icon.hide()
        self.app.quit()

    def run(self) -> int:
        """アプリケーションを実行"""
        # クリップボード監視開始
        self.monitor.start()

        # トレイアイコン表示
        self.tray_icon.show()
        if not self._started_from_startup:
            self.tray_icon.show_message(
                APP_NAME,
                "クリップボード監視を開始しました",
            )

        if not self._started_from_startup:
            self._show_main_window()

        return self.app.exec()


def main():
    """エントリーポイント"""
    app = Application()
    sys.exit(app.run())


if __name__ == "__main__":
    main()
