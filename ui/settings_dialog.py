"""macOS 風設定ダイアログ。"""
from __future__ import annotations

from typing import Optional

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor, QPainter, QPaintEvent
from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from ai_client import test_api_connection
from config import DATABASE_PATH
from database import get_setting, set_setting


_DEFAULTS: dict[str, str] = {
    "ai_provider": "none",
    "openai_api_key": "",
    "gemini_api_key": "",
    "theme": "dark",
    "launch_at_startup": "1",
    "show_in_menubar": "1",
    "show_in_dock": "0",
    "language": "ja",
    "notification_level": "all",
    "monitor_clipboard": "1",
    "confirm_before_delete": "1",
    "max_history_items": "200",
    "retention_days": "0",
    "save_history_on_exit": "1",
    "restore_history_on_launch": "1",
    "database_path": str(DATABASE_PATH),
    "save_text": "1",
    "save_html": "1",
    "save_images": "1",
    "save_files": "0",
    "max_image_size_mb": "10",
    "exclude_duplicates": "0",
    "exclude_empty_items": "1",
    "exclude_password_manager": "1",
    "font_family": "system",
    "font_size": "13",
    "preview_line_count": "2",
    "show_item_numbers": "0",
    "show_timestamps": "1",
    "show_app_names": "1",
    "show_type_icons": "1",
}


def _is_truthy(value: Optional[str]) -> bool:
    return str(value or "").strip().lower() in {"1", "true", "yes", "on"}


class SwitchToggle(QCheckBox):
    """QSS では表現しづらい macOS 風スイッチ。"""

    def __init__(self, object_name: str, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setObjectName(object_name)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setText("")
        self.setFixedSize(38, 22)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

    def paintEvent(self, event: QPaintEvent) -> None:  # noqa: N802
        del event
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        track_rect = self.rect().adjusted(1, 1, -1, -1)
        track_color = QColor("#2d7ff9") if self.isChecked() else QColor("#c7c9d1")
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(track_color)
        painter.drawRoundedRect(track_rect, 11, 11)

        thumb_x = track_rect.right() - 18 if self.isChecked() else track_rect.left() + 2
        thumb_rect = track_rect.adjusted(thumb_x - track_rect.left(), 2, -(track_rect.width() - (thumb_x - track_rect.left()) - 16), -2)
        painter.setBrush(QColor("#ffffff"))
        painter.drawEllipse(thumb_rect)


class SettingsDialog(QDialog):
    """Figma Make をベースにした設定ダイアログ。"""

    settings_changed = pyqtSignal()

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setObjectName("settingsDialog")
        self.setWindowTitle("設定")
        self.setMinimumSize(700, 700)
        self.resize(700, 700)
        self.setModal(True)
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)

        self._setup_ui()
        self._load_settings()

    def _setup_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(20, 18, 20, 18)
        root.setSpacing(14)

        title = QLabel("設定")
        title.setObjectName("settingsDialogTitle")
        root.addWidget(title)

        self._tabs = QTabWidget()
        self._tabs.setObjectName("settingsTabs")
        self._tabs.tabBar().setObjectName("settingsTabBar")
        self._tabs.setDocumentMode(True)
        root.addWidget(self._tabs, 1)

        self._build_general_tab()
        self._build_history_tab()
        self._build_items_tab()
        self._build_shortcuts_tab()
        self._build_appearance_tab()

        button_layout = QHBoxLayout()
        button_layout.addStretch(1)

        cancel_button = QPushButton("キャンセル")
        cancel_button.setObjectName("settingsSecondaryButton")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)

        save_button = QPushButton("保存")
        save_button.setObjectName("settingsPrimaryButton")
        save_button.clicked.connect(self._save_settings)
        button_layout.addWidget(save_button)

        root.addLayout(button_layout)

    def _build_general_tab(self) -> None:
        page, layout = self._create_tab_page("一般")

        ai_section = self._create_section("AI カテゴリ分類")
        ai_layout = ai_section.layout()
        self._provider_combo = self._create_combo(
            "aiProviderCombo",
            [
                ("無効（ルールベースのみ）", "none"),
                ("OpenAI (GPT)", "openai"),
                ("Google Gemini", "gemini"),
            ],
        )
        self._provider_combo.currentIndexChanged.connect(self._on_provider_changed)
        ai_layout.addWidget(self._create_field_block("AI プロバイダー", "既存の分類機能と接続テストを維持します。", self._provider_combo))

        self._openai_section = self._create_api_section(
            "openaiSettingsSection",
            "OpenAI 設定",
            "openaiKeyInput",
            "sk-...",
            "接続テスト",
            lambda: self._test_connection("openai"),
        )
        ai_layout.addWidget(self._openai_section)

        self._gemini_section = self._create_api_section(
            "geminiSettingsSection",
            "Google Gemini 設定",
            "geminiKeyInput",
            "AIza...",
            "接続テスト",
            lambda: self._test_connection("gemini"),
        )
        ai_layout.addWidget(self._gemini_section)
        layout.addWidget(ai_section)

        layout.addWidget(self._create_separator())

        self._launch_toggle = self._create_toggle("launchAtStartupToggle")
        layout.addWidget(self._create_toggle_row("システム起動時に開始", "Windows 起動時に自動的に Coppy を開始します。", self._launch_toggle))

        self._menubar_toggle = self._create_toggle("showInMenuBarToggle")
        layout.addWidget(self._create_toggle_row("通知領域に表示", "タスクトレイにアプリケーションアイコンを表示します。", self._menubar_toggle))

        self._dock_toggle = self._create_toggle("showInDockToggle")
        layout.addWidget(self._create_toggle_row("Dock に表示", "macOS 風表現の項目として残し、Windows では表示設定として扱います。", self._dock_toggle))

        layout.addWidget(self._create_separator())

        self._language_combo = self._create_combo(
            "languageCombo",
            [("日本語", "ja"), ("English", "en"), ("中文", "zh"), ("한국어", "ko")],
        )
        layout.addWidget(self._create_field_block("言語", "UI 表示言語。", self._language_combo))

        self._notification_combo = self._create_combo(
            "notificationLevelCombo",
            [("すべて表示", "all"), ("エラーのみ", "errors"), ("表示しない", "none")],
        )
        layout.addWidget(self._create_field_block("通知", "通知バナーの表示レベル。", self._notification_combo))

        layout.addWidget(self._create_separator())

        self._monitor_toggle = self._create_toggle("monitorClipboardToggle")
        layout.addWidget(self._create_toggle_row("クリップボードを監視", "クリップボード変更を自動で検出します。", self._monitor_toggle))

        self._confirm_delete_toggle = self._create_toggle("confirmBeforeDeleteToggle")
        layout.addWidget(self._create_toggle_row("確認ダイアログを表示", "アイテム削除時に確認ダイアログを出します。", self._confirm_delete_toggle))

        layout.addStretch(1)
        self._tabs.addTab(page, "一般")

    def _build_history_tab(self) -> None:
        page, layout = self._create_tab_page("履歴")

        self._max_history_input = self._create_line_edit("maxHistoryItemsInput", "200")
        layout.addWidget(self._create_field_block("最大保存アイテム数", "履歴に保持する件数。0 で無制限。", self._max_history_input))

        self._retention_days_input = self._create_line_edit("retentionDaysInput", "0")
        layout.addWidget(self._create_field_block("保存期間（日）", "指定日数を超えたアイテムを自動削除。0 で無期限。", self._retention_days_input))

        layout.addWidget(self._create_separator())

        self._save_history_toggle = self._create_toggle("saveHistoryOnExitToggle")
        layout.addWidget(self._create_toggle_row("終了時に履歴を保存", "アプリ終了時に履歴をディスクへ保存します。", self._save_history_toggle))

        self._restore_history_toggle = self._create_toggle("restoreHistoryOnLaunchToggle")
        layout.addWidget(self._create_toggle_row("起動時に履歴を復元", "前回の履歴を起動時に復元します。", self._restore_history_toggle))

        layout.addWidget(self._create_separator())

        self._database_path_input = self._create_line_edit("databasePathInput", str(DATABASE_PATH))
        self._database_path_input.setReadOnly(True)
        layout.addWidget(self._create_field_block("データベースパス", "クリップボード履歴の保存場所。", self._database_path_input))

        layout.addStretch(1)
        self._tabs.addTab(page, "履歴")

    def _build_items_tab(self) -> None:
        page, layout = self._create_tab_page("アイテム")

        self._save_text_toggle = self._create_toggle("saveTextToggle")
        layout.addWidget(self._create_toggle_row("テキスト", "プレーンテキストを保存します。", self._save_text_toggle))

        self._save_html_toggle = self._create_toggle("saveHtmlToggle")
        layout.addWidget(self._create_toggle_row("HTML", "リッチテキストを保存します。", self._save_html_toggle))

        self._save_images_toggle = self._create_toggle("saveImagesToggle")
        layout.addWidget(self._create_toggle_row("画像", "PNG、JPEG などの画像を保存します。", self._save_images_toggle))

        self._save_files_toggle = self._create_toggle("saveFilesToggle")
        layout.addWidget(self._create_toggle_row("ファイル", "ファイルパスを保存します。", self._save_files_toggle))

        layout.addWidget(self._create_separator())

        self._max_image_size_input = self._create_line_edit("maxImageSizeInput", "10")
        layout.addWidget(self._create_field_block("最大画像サイズ（MB）", "保存する画像の最大サイズ。0 で無制限。", self._max_image_size_input))

        layout.addWidget(self._create_separator())

        self._exclude_duplicates_toggle = self._create_toggle("excludeDuplicatesToggle")
        layout.addWidget(self._create_toggle_row("重複を除外", "同じ内容のアイテムは 1 件だけ保持します。", self._exclude_duplicates_toggle))

        self._exclude_empty_toggle = self._create_toggle("excludeEmptyToggle")
        layout.addWidget(self._create_toggle_row("空のアイテムを除外", "空白のみのアイテムを保存しません。", self._exclude_empty_toggle))

        self._exclude_passwords_toggle = self._create_toggle("excludePasswordsToggle")
        layout.addWidget(self._create_toggle_row("パスワードを除外", "パスワードマネージャー由来のコピーを無視します。", self._exclude_passwords_toggle))

        layout.addStretch(1)
        self._tabs.addTab(page, "アイテム")

    def _build_shortcuts_tab(self) -> None:
        page, layout = self._create_tab_page("ショートカット")

        layout.addWidget(self._create_section_heading("グローバルショートカット"))
        for title, description, shortcut in (
            ("メインウィンドウを表示", "Coppy のメインウィンドウを表示 / 非表示。", "Ctrl + Shift + V"),
            ("履歴メニューを表示", "クリップボード履歴のポップアップメニュー。", "Ctrl + Shift + H"),
            ("定型文メニューを表示", "保存された定型文のポップアップメニュー。", "Ctrl + Shift + S"),
        ):
            layout.addWidget(self._create_shortcut_row(title, description, shortcut))

        layout.addWidget(self._create_separator())
        layout.addWidget(self._create_section_heading("アプリ内ショートカット"))

        for title, shortcut in (
            ("検索", "Ctrl + F"),
            ("新規アイテム", "Ctrl + N"),
            ("アイテムを削除", "Delete"),
            ("履歴をクリア", "Ctrl + Shift + K"),
            ("設定を開く", "Ctrl + ,"),
            ("選択アイテムをコピー", "Ctrl + C"),
            ("選択アイテムをペースト", "Enter"),
        ):
            layout.addWidget(self._create_shortcut_row(title, "", shortcut))

        layout.addStretch(1)
        self._tabs.addTab(page, "ショートカット")

    def _build_appearance_tab(self) -> None:
        page, layout = self._create_tab_page("外観")

        self._theme_combo = self._create_combo(
            "themeCombo",
            [("ライト", "light"), ("ダーク", "dark"), ("システム設定に従う", "system")],
        )
        layout.addWidget(self._create_field_block("テーマ", "アプリ全体のテーマ。", self._theme_combo))

        layout.addWidget(self._create_separator())

        self._font_family_combo = self._create_combo(
            "fontFamilyCombo",
            [("システムフォント", "system"), ("Segoe UI", "segoe-ui"), ("Consolas", "consolas")],
        )
        layout.addWidget(self._create_field_block("フォント", "設定画面とリスト表示の基準フォント。", self._font_family_combo))

        self._font_size_combo = self._create_combo(
            "fontSizeCombo",
            [("小（11px）", "11"), ("中（13px）", "13"), ("大（15px）", "15")],
        )
        layout.addWidget(self._create_field_block("フォントサイズ", "UI に適用する基本フォントサイズ。", self._font_size_combo))

        layout.addWidget(self._create_separator())

        self._preview_line_combo = self._create_combo(
            "previewLineCountCombo",
            [("1 行", "1"), ("2 行", "2"), ("3 行", "3"), ("4 行", "4")],
        )
        layout.addWidget(self._create_field_block("リストの行数", "各アイテムのプレビュー表示行数。", self._preview_line_combo))

        layout.addWidget(self._create_separator())

        self._show_item_numbers_toggle = self._create_toggle("showItemNumbersToggle")
        layout.addWidget(self._create_toggle_row("アイテム番号を表示", "リストにアイテム番号を表示します。", self._show_item_numbers_toggle))

        self._show_timestamps_toggle = self._create_toggle("showTimestampsToggle")
        layout.addWidget(self._create_toggle_row("タイムスタンプを表示", "各アイテムのコピー日時を表示します。", self._show_timestamps_toggle))

        self._show_app_names_toggle = self._create_toggle("showAppNamesToggle")
        layout.addWidget(self._create_toggle_row("アプリ名を表示", "コピー元アプリケーション名を表示します。", self._show_app_names_toggle))

        self._show_type_icons_toggle = self._create_toggle("showTypeIconsToggle")
        layout.addWidget(self._create_toggle_row("アイコンを表示", "アイテム種別アイコンを表示します。", self._show_type_icons_toggle))

        layout.addStretch(1)
        self._tabs.addTab(page, "外観")

    def _create_tab_page(self, name: str) -> tuple[QWidget, QVBoxLayout]:
        page = QWidget()
        page_layout = QVBoxLayout(page)
        page_layout.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setObjectName("settingsScrollArea")
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        container = QWidget()
        container.setObjectName(f"{name}TabContent")
        layout = QVBoxLayout(container)
        layout.setContentsMargins(8, 14, 8, 8)
        layout.setSpacing(10)

        scroll.setWidget(container)
        page_layout.addWidget(scroll)
        return page, layout

    def _create_section(self, title: str) -> QFrame:
        section = QFrame()
        section.setObjectName("settingsSection")
        layout = QVBoxLayout(section)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(10)

        heading = QLabel(title)
        heading.setObjectName("settingsSectionHeading")
        layout.addWidget(heading)
        return section

    def _create_separator(self) -> QFrame:
        separator = QFrame()
        separator.setObjectName("settingsSeparator")
        separator.setFrameShape(QFrame.Shape.HLine)
        return separator

    def _create_section_heading(self, text: str) -> QLabel:
        label = QLabel(text)
        label.setObjectName("settingsSectionHeading")
        return label

    def _create_toggle(self, object_name: str) -> SwitchToggle:
        return SwitchToggle(object_name)

    def _create_combo(self, object_name: str, items: list[tuple[str, str]]) -> QComboBox:
        combo = QComboBox()
        combo.setObjectName(object_name)
        for label, value in items:
            combo.addItem(label, value)
        return combo

    def _create_line_edit(self, object_name: str, placeholder: str) -> QLineEdit:
        line_edit = QLineEdit()
        line_edit.setObjectName(object_name)
        line_edit.setPlaceholderText(placeholder)
        return line_edit

    def _create_field_block(self, title: str, description: str, field: QWidget) -> QFrame:
        block = QFrame()
        block.setObjectName("settingsFieldBlock")
        layout = QVBoxLayout(block)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        title_label = QLabel(title)
        title_label.setObjectName("settingsFieldTitle")
        layout.addWidget(title_label)

        if description:
            desc_label = QLabel(description)
            desc_label.setObjectName("settingsDescription")
            desc_label.setWordWrap(True)
            layout.addWidget(desc_label)

        layout.addWidget(field)
        return block

    def _create_toggle_row(self, title: str, description: str, toggle: QCheckBox) -> QFrame:
        row = QFrame()
        row.setObjectName("settingsRow")
        layout = QHBoxLayout(row)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(14)

        text_column = QVBoxLayout()
        text_column.setSpacing(2)

        title_label = QLabel(title)
        title_label.setObjectName("settingsRowTitle")
        text_column.addWidget(title_label)

        desc_label = QLabel(description)
        desc_label.setObjectName("settingsDescription")
        desc_label.setWordWrap(True)
        text_column.addWidget(desc_label)

        layout.addLayout(text_column, 1)
        layout.addWidget(toggle, 0, Qt.AlignmentFlag.AlignTop)
        return row

    def _create_api_section(
        self,
        object_name: str,
        title: str,
        input_name: str,
        placeholder: str,
        button_text: str,
        callback,
    ) -> QFrame:
        section = self._create_section(title)
        section.setObjectName(object_name)
        layout = section.layout()

        api_input = self._create_line_edit(input_name, placeholder)
        api_input.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self._create_field_block("API キー", "", api_input))

        test_button = QPushButton(button_text)
        test_button.setObjectName("settingsSecondaryButton")
        test_button.clicked.connect(callback)
        layout.addWidget(test_button, 0, Qt.AlignmentFlag.AlignLeft)
        return section

    def _create_shortcut_row(self, title: str, description: str, shortcut: str) -> QFrame:
        row = QFrame()
        row.setObjectName("settingsShortcutRow")
        layout = QHBoxLayout(row)
        layout.setContentsMargins(0, 8, 0, 8)
        layout.setSpacing(12)

        text_column = QVBoxLayout()
        text_column.setSpacing(2)

        title_label = QLabel(title)
        title_label.setObjectName("settingsRowTitle")
        text_column.addWidget(title_label)

        if description:
            desc_label = QLabel(description)
            desc_label.setObjectName("settingsDescription")
            desc_label.setWordWrap(True)
            text_column.addWidget(desc_label)

        layout.addLayout(text_column, 1)

        keycap = QLabel(shortcut)
        keycap.setObjectName("shortcutKeycap")
        keycap.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(keycap)
        return row

    def _load_settings(self) -> None:
        self._set_combo_value(self._provider_combo, get_setting("ai_provider", _DEFAULTS["ai_provider"]))
        self.findChild(QLineEdit, "openaiKeyInput").setText(get_setting("openai_api_key", _DEFAULTS["openai_api_key"]) or "")
        self.findChild(QLineEdit, "geminiKeyInput").setText(get_setting("gemini_api_key", _DEFAULTS["gemini_api_key"]) or "")
        self._set_combo_value(self._theme_combo, get_setting("theme", _DEFAULTS["theme"]))

        self._launch_toggle.setChecked(_is_truthy(get_setting("launch_at_startup", _DEFAULTS["launch_at_startup"])))
        self._menubar_toggle.setChecked(_is_truthy(get_setting("show_in_menubar", _DEFAULTS["show_in_menubar"])))
        self._dock_toggle.setChecked(_is_truthy(get_setting("show_in_dock", _DEFAULTS["show_in_dock"])))
        self._set_combo_value(self._language_combo, get_setting("language", _DEFAULTS["language"]))
        self._set_combo_value(self._notification_combo, get_setting("notification_level", _DEFAULTS["notification_level"]))
        self._monitor_toggle.setChecked(_is_truthy(get_setting("monitor_clipboard", _DEFAULTS["monitor_clipboard"])))
        self._confirm_delete_toggle.setChecked(_is_truthy(get_setting("confirm_before_delete", _DEFAULTS["confirm_before_delete"])))

        self._max_history_input.setText(get_setting("max_history_items", _DEFAULTS["max_history_items"]) or "")
        self._retention_days_input.setText(get_setting("retention_days", _DEFAULTS["retention_days"]) or "")
        self._save_history_toggle.setChecked(_is_truthy(get_setting("save_history_on_exit", _DEFAULTS["save_history_on_exit"])))
        self._restore_history_toggle.setChecked(_is_truthy(get_setting("restore_history_on_launch", _DEFAULTS["restore_history_on_launch"])))
        self._database_path_input.setText(get_setting("database_path", _DEFAULTS["database_path"]) or "")

        self._save_text_toggle.setChecked(_is_truthy(get_setting("save_text", _DEFAULTS["save_text"])))
        self._save_html_toggle.setChecked(_is_truthy(get_setting("save_html", _DEFAULTS["save_html"])))
        self._save_images_toggle.setChecked(_is_truthy(get_setting("save_images", _DEFAULTS["save_images"])))
        self._save_files_toggle.setChecked(_is_truthy(get_setting("save_files", _DEFAULTS["save_files"])))
        self._max_image_size_input.setText(get_setting("max_image_size_mb", _DEFAULTS["max_image_size_mb"]) or "")
        self._exclude_duplicates_toggle.setChecked(_is_truthy(get_setting("exclude_duplicates", _DEFAULTS["exclude_duplicates"])))
        self._exclude_empty_toggle.setChecked(_is_truthy(get_setting("exclude_empty_items", _DEFAULTS["exclude_empty_items"])))
        self._exclude_passwords_toggle.setChecked(_is_truthy(get_setting("exclude_password_manager", _DEFAULTS["exclude_password_manager"])))

        self._set_combo_value(self._font_family_combo, get_setting("font_family", _DEFAULTS["font_family"]))
        self._set_combo_value(self._font_size_combo, get_setting("font_size", _DEFAULTS["font_size"]))
        self._set_combo_value(self._preview_line_combo, get_setting("preview_line_count", _DEFAULTS["preview_line_count"]))
        self._show_item_numbers_toggle.setChecked(_is_truthy(get_setting("show_item_numbers", _DEFAULTS["show_item_numbers"])))
        self._show_timestamps_toggle.setChecked(_is_truthy(get_setting("show_timestamps", _DEFAULTS["show_timestamps"])))
        self._show_app_names_toggle.setChecked(_is_truthy(get_setting("show_app_names", _DEFAULTS["show_app_names"])))
        self._show_type_icons_toggle.setChecked(_is_truthy(get_setting("show_type_icons", _DEFAULTS["show_type_icons"])))

        self._on_provider_changed(self._provider_combo.currentIndex())

    def _save_settings(self) -> None:
        set_setting("ai_provider", self._provider_combo.currentData())
        set_setting("openai_api_key", self.findChild(QLineEdit, "openaiKeyInput").text())
        set_setting("gemini_api_key", self.findChild(QLineEdit, "geminiKeyInput").text())
        set_setting("theme", self._theme_combo.currentData())

        self._save_bool("launch_at_startup", self._launch_toggle)
        self._save_bool("show_in_menubar", self._menubar_toggle)
        self._save_bool("show_in_dock", self._dock_toggle)
        set_setting("language", self._language_combo.currentData())
        set_setting("notification_level", self._notification_combo.currentData())
        self._save_bool("monitor_clipboard", self._monitor_toggle)
        self._save_bool("confirm_before_delete", self._confirm_delete_toggle)

        set_setting("max_history_items", self._max_history_input.text().strip() or _DEFAULTS["max_history_items"])
        set_setting("retention_days", self._retention_days_input.text().strip() or _DEFAULTS["retention_days"])
        self._save_bool("save_history_on_exit", self._save_history_toggle)
        self._save_bool("restore_history_on_launch", self._restore_history_toggle)
        set_setting("database_path", self._database_path_input.text().strip() or _DEFAULTS["database_path"])

        self._save_bool("save_text", self._save_text_toggle)
        self._save_bool("save_html", self._save_html_toggle)
        self._save_bool("save_images", self._save_images_toggle)
        self._save_bool("save_files", self._save_files_toggle)
        set_setting("max_image_size_mb", self._max_image_size_input.text().strip() or _DEFAULTS["max_image_size_mb"])
        self._save_bool("exclude_duplicates", self._exclude_duplicates_toggle)
        self._save_bool("exclude_empty_items", self._exclude_empty_toggle)
        self._save_bool("exclude_password_manager", self._exclude_passwords_toggle)

        set_setting("font_family", self._font_family_combo.currentData())
        set_setting("font_size", self._font_size_combo.currentData())
        set_setting("preview_line_count", self._preview_line_combo.currentData())
        self._save_bool("show_item_numbers", self._show_item_numbers_toggle)
        self._save_bool("show_timestamps", self._show_timestamps_toggle)
        self._save_bool("show_app_names", self._show_app_names_toggle)
        self._save_bool("show_type_icons", self._show_type_icons_toggle)

        self.settings_changed.emit()
        self.accept()

    def _save_bool(self, key: str, widget: QCheckBox) -> None:
        set_setting(key, "1" if widget.isChecked() else "0")

    def _set_combo_value(self, combo: QComboBox, value: Optional[str]) -> None:
        index = combo.findData(value)
        if index >= 0:
            combo.setCurrentIndex(index)

    def _on_provider_changed(self, index: int) -> None:
        del index
        provider = self._provider_combo.currentData()
        self._openai_section.setVisible(provider == "openai")
        self._gemini_section.setVisible(provider == "gemini")

    def _test_connection(self, provider: str) -> None:
        api_key = ""
        if provider == "openai":
            api_key = self.findChild(QLineEdit, "openaiKeyInput").text()
        elif provider == "gemini":
            api_key = self.findChild(QLineEdit, "geminiKeyInput").text()

        if not api_key:
            QMessageBox.warning(self, "エラー", "APIキーを入力してください")
            return

        success, message = test_api_connection(provider, api_key)
        if success:
            QMessageBox.information(self, "成功", message)
        else:
            QMessageBox.warning(self, "エラー", message)

    def get_theme_setting(self) -> str:
        return get_setting("theme", _DEFAULTS["theme"]) or _DEFAULTS["theme"]

    def get_ai_provider(self) -> str:
        return get_setting("ai_provider", _DEFAULTS["ai_provider"]) or _DEFAULTS["ai_provider"]

    def get_openai_key(self) -> str:
        return get_setting("openai_api_key", _DEFAULTS["openai_api_key"]) or ""

    def get_gemini_key(self) -> str:
        return get_setting("gemini_api_key", _DEFAULTS["gemini_api_key"]) or ""
