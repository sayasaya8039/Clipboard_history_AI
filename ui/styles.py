"""スタイル定義モジュール"""
from __future__ import annotations

import sys


def is_dark_mode() -> bool:
    """システムのダークモード設定を検出する。"""
    if sys.platform == "win32":
        try:
            import winreg

            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize",
            )
            value, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
            winreg.CloseKey(key)
            return value == 0
        except Exception:
            pass
    return False


FIGMA_DARK = {
    "bg": "#171717",
    "surface": "#1d1d1d",
    "panel": "#202020",
    "panel_alt": "#242424",
    "panel_soft": "#262626",
    "topbar": "#1f1f1f",
    "border": "#303030",
    "border_soft": "#383838",
    "text": "#f3f3f3",
    "text_soft": "#a0a0a0",
    "text_dim": "#707070",
    "accent": "#2d7ff9",
    "accent_hover": "#3b87ff",
    "accent_soft": "rgba(45, 127, 249, 0.22)",
    "accent_soft_2": "rgba(45, 127, 249, 0.14)",
    "danger": "#ff5d57",
    "warning": "#f59e0b",
}

FIGMA_LIGHT = {
    "bg": "#f4f4f4",
    "surface": "#ffffff",
    "panel": "#f8f8f8",
    "panel_alt": "#efefef",
    "panel_soft": "#e6e6e6",
    "topbar": "#fafafa",
    "border": "#d7d7d7",
    "border_soft": "#cfcfcf",
    "text": "#181818",
    "text_soft": "#5f5f5f",
    "text_dim": "#808080",
    "accent": "#2563eb",
    "accent_hover": "#1d4ed8",
    "accent_soft": "rgba(37, 99, 235, 0.14)",
    "accent_soft_2": "rgba(37, 99, 235, 0.08)",
    "danger": "#dc2626",
    "warning": "#d97706",
}


def get_stylesheet(dark: bool = False) -> str:
    """アプリ全体に適用する Figma 風のスタイルシートを返す。"""
    t = FIGMA_DARK if dark else FIGMA_LIGHT

    return f"""
        QMainWindow, QDialog {{
            background-color: {t["bg"]};
            color: {t["text"]};
        }}

        QWidget {{
            background-color: transparent;
            color: {t["text"]};
            font-family: "Segoe UI", "Yu Gothic UI", "Hiragino Sans", "Meiryo", sans-serif;
            font-size: 13px;
        }}

        QFrame#titleBar {{
            background-color: {t["topbar"]};
            border-bottom: 1px solid {t["border"]};
        }}

        QLabel#titleLabel {{
            color: {t["text"]};
            font-size: 13px;
            font-weight: 600;
        }}

        QLabel#versionLabel {{
            color: {t["text_dim"]};
            font-size: 11px;
        }}

        QFrame#sidebar {{
            background-color: {t["surface"]};
            border-right: 1px solid {t["border"]};
        }}

        QFrame#sidebarFooter {{
            border-top: 1px solid {t["border"]};
        }}

        QFrame#detailPane {{
            background-color: {t["bg"]};
        }}

        QFrame#detailHeader {{
            background-color: {t["bg"]};
            border-bottom: 1px solid {t["border"]};
        }}

        QFrame#detailFooter {{
            background-color: {t["surface"]};
            border-top: 1px solid {t["border"]};
        }}

        QFrame#snippetMetaFrame {{
            background-color: {t["panel"]};
            border-bottom: 1px solid {t["border"]};
        }}

        QFrame#detailContentHost {{
            background-color: {t["bg"]};
        }}

        QFrame#searchFrame {{
            background-color: {t["panel"]};
            border: 1px solid {t["border"]};
            border-radius: 12px;
        }}

        QLabel#searchIcon {{
            color: {t["text_dim"]};
            font-size: 12px;
        }}

        QLineEdit#searchInput {{
            background: transparent;
            border: none;
            padding: 0;
            color: {t["text"]};
            selection-background-color: {t["accent"]};
        }}

        QLineEdit, QTextEdit, QPlainTextEdit, QComboBox, QSpinBox {{
            background-color: {t["panel"]};
            border: 1px solid {t["border"]};
            border-radius: 10px;
            color: {t["text"]};
            padding: 8px 12px;
            selection-background-color: {t["accent"]};
            selection-color: #ffffff;
        }}

        QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus, QComboBox:focus, QSpinBox:focus {{
            border-color: {t["accent"]};
        }}

        QTextEdit, QPlainTextEdit {{
            padding: 10px 12px;
        }}

        QPlainTextEdit#detailCode,
        QTextEdit#detailCode {{
            background: transparent;
            border: none;
            padding: 0;
            color: {t["text"]};
        }}

        QLabel#detailPlainText {{
            color: {t["text"]};
            font-size: 13px;
            line-height: 1.6;
        }}

        QLabel#emptyStateLabel {{
            color: {t["text_dim"]};
            font-size: 10px;
        }}

        QLabel#detailType,
        QLabel#detailApp,
        QLabel#detailDot {{
            color: {t["text_soft"]};
            font-size: 10px;
            letter-spacing: 0.08em;
        }}

        QLabel#detailTitle {{
            color: {t["text"]};
            font-size: 15px;
            font-weight: 600;
        }}

        QLabel#favoriteBadge {{
            color: {t["warning"]};
        }}

        QLabel#detailMuted {{
            color: {t["text_soft"]};
            font-size: 12px;
        }}

        QLabel#footerText {{
            color: {t["text_dim"]};
            font-size: 11px;
        }}

        QLabel#cardIcon {{
            color: {t["text_soft"]};
            font-size: 12px;
        }}

        QLabel#cardPreview,
        QLabel#cardTitle {{
            color: {t["text"]};
            font-size: 13px;
        }}

        QLabel#cardTitle {{
            font-weight: 600;
        }}

        QLabel#cardDescription {{
            color: {t["text_soft"]};
            font-size: 11px;
        }}

        QLabel#tagPill {{
            background-color: {t["panel_soft"]};
            color: {t["text_soft"]};
            border-radius: 4px;
            padding: 1px 6px;
            font-size: 10px;
        }}

        QLabel#tagPillBlue {{
            background-color: rgba(45, 127, 249, 0.18);
            color: #8cb9ff;
            border-radius: 4px;
            padding: 1px 6px;
            font-size: 10px;
        }}

        QLabel#detailImage {{
            border-radius: 12px;
        }}

        QPushButton {{
            border: none;
            border-radius: 10px;
            color: {t["text"]};
            background-color: transparent;
            padding: 0 12px;
        }}

        QPushButton:hover {{
            background-color: {t["accent_soft_2"]};
        }}

        QPushButton:disabled {{
            color: {t["text_dim"]};
        }}

        QPushButton#ghostButton {{
            background-color: transparent;
            border-radius: 8px;
            padding: 0 12px;
            font-size: 12px;
        }}

        QPushButton#ghostButton:hover {{
            background-color: {t["accent_soft_2"]};
        }}

        QPushButton#iconButton {{
            background-color: transparent;
            border-radius: 8px;
            min-width: 30px;
            max-width: 30px;
            min-height: 30px;
            max-height: 30px;
            padding: 0;
            font-size: 12px;
        }}

        QPushButton#iconButton:hover {{
            background-color: {t["accent_soft_2"]};
        }}

        QPushButton#dangerIconButton {{
            background-color: transparent;
            border-radius: 8px;
            min-width: 30px;
            max-width: 30px;
            min-height: 30px;
            max-height: 30px;
            padding: 0;
            font-size: 12px;
            color: {t["danger"]};
        }}

        QPushButton#dangerIconButton:hover {{
            background-color: rgba(255, 93, 87, 0.14);
        }}

        QPushButton#segmentedButton {{
            background-color: transparent;
            border-radius: 999px;
            padding: 0 16px;
            min-height: 36px;
            color: {t["text_soft"]};
            font-size: 12px;
        }}

        QPushButton#segmentedButton:hover {{
            background-color: {t["accent_soft_2"]};
        }}

        QPushButton#segmentedButton:checked {{
            background-color: #f1f1f1;
            color: #111111;
            border: 1px solid transparent;
        }}

        QFrame#tabSwitcher {{
            background-color: {t["panel"]};
            border: 1px solid {t["border"]};
            border-radius: 18px;
            padding: 2px;
        }}

        QFrame#historyCard,
        QFrame#snippetCard {{
            background-color: transparent;
            border-radius: 12px;
        }}

        QFrame#historyCard:hover,
        QFrame#snippetCard:hover {{
            background-color: {t["accent_soft_2"]};
        }}

        QFrame#historyCard[selected="true"],
        QFrame#snippetCard[selected="true"] {{
            background-color: {t["accent"]};
        }}

        QFrame#historyCard[selected="true"] QLabel,
        QFrame#snippetCard[selected="true"] QLabel {{
            color: #ffffff;
        }}

        QFrame#historyCard[selected="true"] QLabel#cardIcon,
        QFrame#snippetCard[selected="true"] QLabel#cardIcon {{
            color: rgba(255, 255, 255, 0.92);
        }}

        QFrame#historyCard[selected="true"] QLabel#cardPreview,
        QFrame#snippetCard[selected="true"] QLabel#cardTitle,
        QFrame#snippetCard[selected="true"] QLabel#cardDescription,
        QFrame#historyCard[selected="true"] QLabel#cardTitle,
        QFrame#historyCard[selected="true"] QLabel#cardDescription,
        QFrame#historyCard[selected="true"] QLabel[role="muted"] {{
            color: rgba(255, 255, 255, 0.78);
        }}

        QFrame#snippetCard[selected="true"] QLabel#tagPill {{
            background-color: rgba(255, 255, 255, 0.18);
            color: #ffffff;
        }}

        QFrame#snippetCard[selected="true"] QLabel#tagPillBlue {{
            background-color: rgba(255, 255, 255, 0.18);
            color: #ffffff;
        }}

        QFrame#detailPane QScrollArea {{
            background-color: transparent;
            border: none;
        }}

        QScrollArea#listScroll {{
            background-color: transparent;
            border: none;
        }}

        QScrollBar:vertical {{
            background: transparent;
            width: 10px;
            margin: 0 2px 0 2px;
        }}

        QScrollBar::handle:vertical {{
            background: {t["border_soft"]};
            min-height: 24px;
            border-radius: 5px;
        }}

        QScrollBar::handle:vertical:hover {{
            background: {t["text_dim"]};
        }}

        QScrollBar::add-line:vertical,
        QScrollBar::sub-line:vertical {{
            height: 0px;
        }}

        QScrollBar::add-page:vertical,
        QScrollBar::sub-page:vertical {{
            background: transparent;
        }}

        QGroupBox {{
            color: {t["text"]};
            border: 1px solid {t["border"]};
            border-radius: 12px;
            margin-top: 12px;
            padding-top: 10px;
        }}

        QGroupBox::title {{
            subcontrol-origin: margin;
            subcontrol-position: top left;
            padding: 0 8px;
            color: {t["text"]};
        }}

        QTabWidget::pane {{
            border: 1px solid {t["border"]};
            border-radius: 12px;
            background-color: {t["panel"]};
        }}

        QTabBar::tab {{
            background-color: {t["panel"]};
            color: {t["text_soft"]};
            border: 1px solid {t["border"]};
            border-bottom: none;
            padding: 8px 14px;
            border-top-left-radius: 12px;
            border-top-right-radius: 12px;
        }}

        QTabBar::tab:selected {{
            background-color: {t["surface"]};
            color: {t["text"]};
        }}

        QTabBar::tab:hover:!selected {{
            background-color: {t["accent_soft_2"]};
        }}

        QCheckBox {{
            color: {t["text"]};
            spacing: 8px;
        }}

        QCheckBox::indicator {{
            width: 18px;
            height: 18px;
            border: 1px solid {t["border"]};
            border-radius: 4px;
            background-color: {t["panel"]};
        }}

        QCheckBox::indicator:checked {{
            background-color: {t["accent"]};
            border-color: {t["accent"]};
        }}

        QMenu {{
            background-color: {t["panel"]};
            color: {t["text"]};
            border: 1px solid {t["border"]};
            border-radius: 10px;
            padding: 4px;
        }}

        QMenu::item {{
            padding: 8px 18px;
            border-radius: 6px;
        }}

        QMenu::item:selected {{
            background-color: {t["accent_soft_2"]};
        }}

        QMenu::separator {{
            height: 1px;
            background-color: {t["border"]};
            margin: 4px 8px;
        }}

        QToolTip {{
            background-color: {t["panel"]};
            color: {t["text"]};
            border: 1px solid {t["border"]};
            border-radius: 8px;
            padding: 4px 8px;
        }}
    """
