"""
クリップボード履歴アプリ

コピーした内容を自動でカテゴリ分けして保存するアプリケーション
"""
import sys
from pathlib import Path

from PyQt6.QtCore import QTimer
from PyQt6.QtGui import QFont, QIcon
from PyQt6.QtWidgets import QApplication

# アプリケーションディレクトリをパスに追加
sys.path.insert(0, str(Path(__file__).parent))

from datetime import datetime

from config import APP_NAME, RESOURCES_DIR, STORAGE_DIR
from database import init_database, get_setting
from clipboard_monitor import ClipboardMonitor
from foreground_tracker import ForegroundTracker, activate_window, window_title
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
        # 前面ウィンドウ追跡（貼り付け時にフォーカス復元するため）
        self.foreground_tracker = ForegroundTracker()

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
        self.main_window.paste_requested.connect(self._on_paste_requested)
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

    def _on_paste_requested(self, content_type: str, content: str, image_path: str) -> None:
        """貼り付けリクエスト時: クリップボードにコピーし、直前のアプリに Ctrl+V を送信。"""
        target_hwnd = int(getattr(self.foreground_tracker, "last_other_hwnd", 0) or 0)
        self._paste_log(
            f"paste_request content_type={content_type} "
            f"target_hwnd=0x{target_hwnd:x} title={window_title(target_hwnd)!r}"
        )

        was_visible = self.main_window.isVisible()
        if was_visible:
            self.main_window.hide()

        if not self.monitor.copy_to_clipboard(content_type, content, image_path):
            self._paste_log("clipboard copy failed — abort")
            if was_visible:
                self.main_window.show()
            return

        # 対象ウィンドウへフォーカスを戻してから Ctrl+V を送る
        QTimer.singleShot(100, lambda: self._restore_and_paste(target_hwnd))

    def _restore_and_paste(self, target_hwnd: int) -> None:
        """対象ウィンドウを前面化して Ctrl+V を送出する。"""
        activated = False
        if target_hwnd:
            activated = activate_window(target_hwnd)

        fg_after = 0
        try:
            if sys.platform == "win32":
                import ctypes
                fg_after = int(ctypes.windll.user32.GetForegroundWindow() or 0)
        except Exception:
            pass
        self._paste_log(
            f"activate target=0x{target_hwnd:x} success={activated} "
            f"fg_now=0x{fg_after:x} title={window_title(fg_after)!r}"
        )

        QTimer.singleShot(80, self._send_paste_keystroke)

    def _paste_log(self, message: str) -> None:
        """貼り付け関連のデバッグログを書き出す。"""
        try:
            STORAGE_DIR.mkdir(parents=True, exist_ok=True)
            log_path = STORAGE_DIR / "paste.log"
            with open(log_path, "a", encoding="utf-8") as f:
                f.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} {message}\n")
        except Exception:
            pass

    def _send_paste_keystroke(self) -> None:
        """Win32 API で Ctrl+V を送信する。"""
        if sys.platform != "win32":
            return
        try:
            import ctypes

            VK_CONTROL = 0x11
            VK_V = 0x56
            KEYEVENTF_KEYUP = 0x0002
            user32 = ctypes.windll.user32
            user32.keybd_event(VK_CONTROL, 0, 0, 0)
            user32.keybd_event(VK_V, 0, 0, 0)
            user32.keybd_event(VK_V, 0, KEYEVENTF_KEYUP, 0)
            user32.keybd_event(VK_CONTROL, 0, KEYEVENTF_KEYUP, 0)
        except Exception as exc:
            print(f"貼り付け送信に失敗: {exc}")

    def _on_history_added(self, history_id: int) -> None:
        """履歴追加時"""
        # メインウィンドウが表示されている場合は更新
        if self.main_window.isVisible():
            self.main_window.refresh_history()

    def _on_settings_changed(self) -> None:
        """設定変更時"""
        self._apply_theme()
        self.main_window.set_always_on_top(get_setting("show_in_dock", "1") == "1")
        self.main_window.refresh_history()
        self.main_window.refresh_snippets()

    def _quit(self) -> None:
        """アプリケーションを終了"""
        self.monitor.stop()
        if hasattr(self, "foreground_tracker"):
            self.foreground_tracker.stop()
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
