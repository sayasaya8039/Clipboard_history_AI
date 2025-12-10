"""スタイル定義モジュール"""
import sys
from config import THEME


def is_dark_mode() -> bool:
    """システムのダークモード設定を検出"""
    if sys.platform == "win32":
        try:
            import winreg
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize"
            )
            value, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
            winreg.CloseKey(key)
            return value == 0
        except Exception:
            pass
    return False


def get_stylesheet(dark: bool = False) -> str:
    """スタイルシートを生成"""
    theme = THEME["dark"] if dark else THEME["light"]

    return f"""
        /* メインウィンドウ */
        QMainWindow, QDialog {{
            background-color: {theme["bg_main"]};
            color: {theme["text_main"]};
        }}

        /* ウィジェット全般 */
        QWidget {{
            background-color: {theme["bg_main"]};
            color: {theme["text_main"]};
            font-family: "Segoe UI", "Hiragino Sans", "Meiryo", sans-serif;
            font-size: 14px;
        }}

        /* ラベル */
        QLabel {{
            color: {theme["text_main"]};
            background-color: transparent;
        }}

        QLabel[class="subtitle"] {{
            color: {theme["text_sub"]};
            font-size: 12px;
        }}

        /* 入力フィールド */
        QLineEdit {{
            background-color: {theme["bg_sub"]};
            color: {theme["text_main"]};
            border: 1px solid {theme["border"]};
            border-radius: 4px;
            padding: 8px 12px;
            font-size: 14px;
        }}

        QLineEdit:focus {{
            border-color: {theme["accent"]};
        }}

        QLineEdit::placeholder {{
            color: {theme["text_sub"]};
        }}

        /* ボタン */
        QPushButton {{
            background-color: {theme["accent"]};
            color: {theme["bg_main"]};
            border: none;
            border-radius: 4px;
            padding: 8px 16px;
            font-size: 14px;
            font-weight: 500;
        }}

        QPushButton:hover {{
            background-color: {theme["text_sub"]};
        }}

        QPushButton:pressed {{
            background-color: {theme["text_main"]};
        }}

        QPushButton[class="secondary"] {{
            background-color: {theme["bg_sub"]};
            color: {theme["text_main"]};
            border: 1px solid {theme["border"]};
        }}

        QPushButton[class="secondary"]:hover {{
            background-color: {theme["bg_hover"]};
        }}

        QPushButton[class="icon"] {{
            background-color: transparent;
            color: {theme["text_main"]};
            border: none;
            padding: 4px;
            min-width: 32px;
            max-width: 32px;
            min-height: 32px;
            max-height: 32px;
        }}

        QPushButton[class="icon"]:hover {{
            background-color: {theme["bg_hover"]};
            border-radius: 4px;
        }}

        /* リストウィジェット */
        QListWidget {{
            background-color: {theme["bg_main"]};
            color: {theme["text_main"]};
            border: 1px solid {theme["border"]};
            border-radius: 4px;
            outline: none;
        }}

        QListWidget::item {{
            padding: 8px;
            border-bottom: 1px solid {theme["border"]};
        }}

        QListWidget::item:selected {{
            background-color: {theme["bg_hover"]};
            color: {theme["text_main"]};
        }}

        QListWidget::item:hover {{
            background-color: {theme["bg_sub"]};
        }}

        /* スクロールバー */
        QScrollBar:vertical {{
            background-color: {theme["bg_main"]};
            width: 12px;
            border: none;
        }}

        QScrollBar::handle:vertical {{
            background-color: {theme["border"]};
            border-radius: 6px;
            min-height: 30px;
            margin: 2px;
        }}

        QScrollBar::handle:vertical:hover {{
            background-color: {theme["text_sub"]};
        }}

        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            height: 0px;
        }}

        QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
            background-color: transparent;
        }}

        /* コンボボックス */
        QComboBox {{
            background-color: {theme["bg_sub"]};
            color: {theme["text_main"]};
            border: 1px solid {theme["border"]};
            border-radius: 4px;
            padding: 8px 12px;
            font-size: 14px;
        }}

        QComboBox:hover {{
            border-color: {theme["accent"]};
        }}

        QComboBox::drop-down {{
            border: none;
            width: 20px;
        }}

        QComboBox::down-arrow {{
            image: none;
            border-left: 5px solid transparent;
            border-right: 5px solid transparent;
            border-top: 5px solid {theme["text_main"]};
            margin-right: 8px;
        }}

        QComboBox QAbstractItemView {{
            background-color: {theme["bg_main"]};
            color: {theme["text_main"]};
            border: 1px solid {theme["border"]};
            selection-background-color: {theme["bg_hover"]};
        }}

        /* メニュー */
        QMenu {{
            background-color: {theme["bg_main"]};
            color: {theme["text_main"]};
            border: 1px solid {theme["border"]};
            border-radius: 4px;
            padding: 4px;
        }}

        QMenu::item {{
            padding: 8px 24px;
            border-radius: 2px;
        }}

        QMenu::item:selected {{
            background-color: {theme["bg_hover"]};
        }}

        QMenu::separator {{
            height: 1px;
            background-color: {theme["border"]};
            margin: 4px 8px;
        }}

        /* グループボックス */
        QGroupBox {{
            color: {theme["text_main"]};
            border: 1px solid {theme["border"]};
            border-radius: 4px;
            margin-top: 12px;
            padding-top: 8px;
        }}

        QGroupBox::title {{
            subcontrol-origin: margin;
            subcontrol-position: top left;
            padding: 0 8px;
            color: {theme["text_main"]};
        }}

        /* タブ */
        QTabWidget::pane {{
            border: 1px solid {theme["border"]};
            border-radius: 4px;
            background-color: {theme["bg_main"]};
        }}

        QTabBar::tab {{
            background-color: {theme["bg_sub"]};
            color: {theme["text_main"]};
            padding: 8px 16px;
            border: 1px solid {theme["border"]};
            border-bottom: none;
            border-top-left-radius: 4px;
            border-top-right-radius: 4px;
        }}

        QTabBar::tab:selected {{
            background-color: {theme["bg_main"]};
            border-bottom: 1px solid {theme["bg_main"]};
        }}

        QTabBar::tab:hover:!selected {{
            background-color: {theme["bg_hover"]};
        }}

        /* チェックボックス */
        QCheckBox {{
            color: {theme["text_main"]};
            spacing: 8px;
        }}

        QCheckBox::indicator {{
            width: 18px;
            height: 18px;
            border: 1px solid {theme["border"]};
            border-radius: 3px;
            background-color: {theme["bg_sub"]};
        }}

        QCheckBox::indicator:checked {{
            background-color: {theme["accent"]};
            border-color: {theme["accent"]};
        }}

        /* ツールチップ */
        QToolTip {{
            background-color: {theme["bg_sub"]};
            color: {theme["text_main"]};
            border: 1px solid {theme["border"]};
            border-radius: 4px;
            padding: 4px 8px;
        }}
    """
