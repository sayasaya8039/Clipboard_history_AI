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
    "bg": "#151618",
    "surface": "#1b1d21",
    "panel": "#21242a",
    "panel_alt": "#262a31",
    "panel_soft": "#2d323a",
    "topbar": "#191b1f",
    "border": "#373c45",
    "border_soft": "#4a515c",
    "text": "#f5f7fa",
    "text_soft": "#b3bcc8",
    "text_dim": "#7d8794",
    "accent": "#4a84e8",
    "accent_hover": "#6197f5",
    "accent_soft": "rgba(74, 132, 232, 0.24)",
    "accent_soft_2": "rgba(74, 132, 232, 0.10)",
    "hover": "rgba(255, 255, 255, 0.055)",
    "segmented_checked_bg": "#eceff4",
    "segmented_checked_text": "#14181f",
    "segmented_checked_border": "rgba(255, 255, 255, 0.08)",
    "selected_text": "#ffffff",
    "selected_text_soft": "rgba(255, 255, 255, 0.86)",
    "tag_blue_bg": "rgba(74, 132, 232, 0.20)",
    "tag_blue_text": "#b7ceff",
    "favorite_active": "#f6b84b",
    "favorite_inactive": "#768090",
    "danger": "#ff5d57",
    "warning": "#f59e0b",
}

FIGMA_LIGHT = {
    "bg": "#f6f4ef",
    "surface": "#fcfbf8",
    "panel": "#f2efe8",
    "panel_alt": "#ece8df",
    "panel_soft": "#e3ddd2",
    "topbar": "#f9f7f2",
    "border": "#d6d0c5",
    "border_soft": "#c7c0b4",
    "text": "#1c1f24",
    "text_soft": "#565f6d",
    "text_dim": "#7e8794",
    "accent": "#2f6fd6",
    "accent_hover": "#255fc2",
    "accent_soft": "rgba(47, 111, 214, 0.16)",
    "accent_soft_2": "rgba(47, 111, 214, 0.08)",
    "hover": "rgba(28, 31, 36, 0.045)",
    "segmented_checked_bg": "#ffffff",
    "segmented_checked_text": "#15181e",
    "segmented_checked_border": "#dcd6cb",
    "selected_text": "#ffffff",
    "selected_text_soft": "rgba(255, 255, 255, 0.88)",
    "tag_blue_bg": "rgba(47, 111, 214, 0.12)",
    "tag_blue_text": "#2c5fb0",
    "favorite_active": "#d98a14",
    "favorite_inactive": "#8e96a0",
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

        QPushButton#trafficCloseButton,
        QPushButton#trafficMinimizeButton,
        QPushButton#trafficMaximizeButton {{
            background-color: transparent;
            border: none;
            border-radius: 6px;
            min-width: 12px;
            max-width: 12px;
            min-height: 12px;
            max-height: 12px;
            padding: 0;
        }}

        QPushButton#trafficCloseButton {{
            background-color: #ff5f57;
        }}

        QPushButton#trafficMinimizeButton {{
            background-color: #febc2e;
        }}

        QPushButton#trafficMaximizeButton {{
            background-color: #28c840;
        }}

        QPushButton#trafficCloseButton:hover {{
            background-color: #ff7a73;
        }}

        QPushButton#trafficMinimizeButton:hover {{
            background-color: #ffd05a;
        }}

        QPushButton#trafficMaximizeButton:hover {{
            background-color: #4dde58;
        }}

        QPushButton#trafficCloseButton:pressed {{
            background-color: #e24a43;
        }}

        QPushButton#trafficMinimizeButton:pressed {{
            background-color: #e9b427;
        }}

        QPushButton#trafficMaximizeButton:pressed {{
            background-color: #23aa35;
        }}

        QFrame#sidebar {{
            background-color: {t["surface"]};
            border-right: 1px solid {t["border"]};
        }}

        QFrame#sidebarContentPanel {{
            background-color: {t["panel_alt"]};
            border: 1px solid {t["border"]};
            border-radius: 18px;
        }}

        QFrame#sidebarFooter {{
            background-color: transparent;
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
            font-family: "Segoe Fluent Icons", "Segoe UI Symbol";
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
            color: {t["text_soft"]};
            font-size: 11px;
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
            font-family: "Segoe Fluent Icons", "Segoe UI Symbol";
            color: {t["text_soft"]};
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
            font-family: "Segoe Fluent Icons", "Segoe UI Symbol";
            color: {t["text_soft"]};
            font-size: 12px;
        }}

        QLabel#cardSource {{
            color: {t["text_soft"]};
            font-size: 10px;
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
            background-color: {t["tag_blue_bg"]};
            color: {t["tag_blue_text"]};
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
            background-color: {t["hover"]};
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
            background-color: {t["hover"]};
        }}

        QPushButton#iconButton {{
            font-family: "Segoe Fluent Icons", "Segoe UI Symbol";
            background-color: transparent;
            border-radius: 8px;
            min-width: 30px;
            max-width: 30px;
            min-height: 30px;
            max-height: 30px;
            padding: 0;
            font-size: 12px;
            color: {t["text_soft"]};
        }}

        QPushButton#iconButton:hover {{
            background-color: {t["hover"]};
        }}

        QPushButton#iconButton[pinned="true"] {{
            color: {t["accent"]};
        }}

        QPushButton#iconButton[favorite="true"] {{
            color: {t["favorite_active"]};
        }}

        QPushButton#dangerIconButton {{
            font-family: "Segoe Fluent Icons", "Segoe UI Symbol";
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
            font-family: "Segoe Fluent Icons", "Segoe UI Symbol", "Segoe UI", "Yu Gothic UI", "Hiragino Sans", "Meiryo", sans-serif;
            background-color: transparent;
            border-radius: 14px;
            padding: 0 16px;
            min-height: 36px;
            color: {t["text_soft"]};
            font-size: 12px;
        }}

        QPushButton#segmentedButton:hover {{
            background-color: {t["hover"]};
        }}

        QPushButton#segmentedButton:checked {{
            background-color: {t["segmented_checked_bg"]};
            color: {t["segmented_checked_text"]};
            border: 1px solid {t["segmented_checked_border"]};
        }}

        QPushButton#favoriteToggleButton {{
            font-family: "Segoe Fluent Icons", "Segoe UI Symbol", "Segoe UI", "Yu Gothic UI", "Hiragino Sans", "Meiryo", sans-serif;
        }}

        QFrame#tabSwitcher {{
            background-color: {t["panel"]};
            border: 1px solid {t["border"]};
            border-radius: 20px;
            padding: 3px;
        }}

        QFrame#historyCard,
        QFrame#snippetCard {{
            background-color: transparent;
            border-radius: 12px;
        }}

        QFrame#historyCard:hover,
        QFrame#snippetCard:hover {{
            background-color: {t["hover"]};
        }}

        QFrame#historyCard[selected="true"],
        QFrame#snippetCard[selected="true"] {{
            background-color: {t["accent"]};
        }}

        QFrame#historyCard[selected="true"] QLabel,
        QFrame#snippetCard[selected="true"] QLabel {{
            color: {t["selected_text"]};
        }}

        QFrame#historyCard[selected="true"] QLabel#cardIcon,
        QFrame#snippetCard[selected="true"] QLabel#cardIcon {{
            color: {t["selected_text"]};
        }}

        QFrame#historyCard[selected="true"] QLabel#cardPreview,
        QFrame#snippetCard[selected="true"] QLabel#cardDescription,
        QFrame#historyCard[selected="true"] QLabel#cardDescription,
        QFrame#historyCard[selected="true"] QLabel#cardSource,
        QFrame#snippetCard[selected="true"] QLabel#cardSource,
        QFrame#historyCard[selected="true"] QLabel[role="muted"] {{
            color: {t["selected_text_soft"]};
        }}

        QFrame#snippetCard[selected="true"] QLabel#tagPill {{
            background-color: rgba(255, 255, 255, 0.18);
            color: {t["selected_text"]};
        }}

        QFrame#snippetCard[selected="true"] QLabel#tagPillBlue {{
            background-color: rgba(255, 255, 255, 0.18);
            color: {t["selected_text"]};
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

        QDialog#settingsDialog {{
            background-color: {t["surface"]};
            border: 1px solid {t["border"]};
            border-radius: 18px;
        }}

        QLabel#settingsDialogTitle {{
            color: {t["text"]};
            font-size: 15px;
            font-weight: 600;
        }}

        QTabWidget#settingsTabs::pane {{
            border: none;
            background: transparent;
            margin-top: 12px;
        }}

        QTabBar#settingsTabBar {{
            background: {t["panel"]};
            border: 1px solid {t["border"]};
            border-radius: 10px;
            padding: 3px;
        }}

        QTabBar#settingsTabBar::tab {{
            background: transparent;
            color: {t["text_soft"]};
            border: none;
            border-radius: 8px;
            padding: 8px 12px;
            margin: 0 2px 0 0;
            min-width: 88px;
        }}

        QTabBar#settingsTabBar::tab:selected {{
            background-color: {t["surface"]};
            color: {t["text"]};
            font-weight: 600;
        }}

        QTabBar#settingsTabBar::tab:hover:!selected {{
            background-color: {t["hover"]};
        }}

        QScrollArea#settingsScrollArea {{
            background: transparent;
            border: none;
        }}

        QFrame#settingsSection {{
            background-color: {t["panel"]};
            border: 1px solid {t["border"]};
            border-radius: 14px;
        }}

        QFrame#settingsSeparator {{
            background-color: {t["border"]};
            min-height: 1px;
            max-height: 1px;
            border: none;
        }}

        QLabel#settingsSectionHeading {{
            color: {t["text"]};
            font-size: 13px;
            font-weight: 600;
        }}

        QLabel#settingsFieldTitle,
        QLabel#settingsRowTitle {{
            color: {t["text"]};
            font-size: 13px;
            font-weight: 600;
        }}

        QLabel#settingsDescription {{
            color: {t["text_soft"]};
            font-size: 11px;
        }}

        QFrame#settingsShortcutRow {{
            border-bottom: 1px solid {t["border"]};
        }}

        QLabel#shortcutKeycap {{
            background-color: {t["panel_alt"]};
            border: 1px solid {t["border"]};
            border-radius: 8px;
            color: {t["text_soft"]};
            font-family: Consolas, "SF Mono", monospace;
            font-size: 11px;
            padding: 6px 10px;
            min-width: 96px;
        }}

        QPushButton#settingsPrimaryButton {{
            background-color: {t["accent"]};
            color: #ffffff;
            border-radius: 10px;
            padding: 0 16px;
            min-height: 34px;
        }}

        QPushButton#settingsPrimaryButton:hover {{
            background-color: {t["accent_hover"]};
        }}

        QPushButton#settingsSecondaryButton {{
            background-color: {t["panel"]};
            border: 1px solid {t["border"]};
            border-radius: 10px;
            padding: 0 16px;
            min-height: 34px;
        }}

        QPushButton#settingsSecondaryButton:hover {{
            background-color: {t["hover"]};
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
            background-color: {t["hover"]};
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
            background-color: {t["hover"]};
        }}

        QMenu::separator {{
            height: 1px;
            background-color: {t["border"]};
            margin: 4px 8px;
        }}

        QLabel#favoriteBadge[favorite="true"],
        QLabel#cardFavoriteBadge[favorite="true"] {{
            color: {t["favorite_active"]};
        }}

        QLabel#favoriteBadge[favorite="false"],
        QLabel#cardFavoriteBadge[favorite="false"] {{
            color: {t["favorite_inactive"]};
        }}

        QToolTip {{
            background-color: {t["panel"]};
            color: {t["text"]};
            border: 1px solid {t["border"]};
            border-radius: 8px;
            padding: 4px 8px;
        }}
    """
