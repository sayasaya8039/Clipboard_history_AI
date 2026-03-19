"""macOS 風設定ダイアログ。"""
from __future__ import annotations

from pathlib import Path
from typing import Optional

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor, QIntValidator, QPainter, QPaintEvent
from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QFileDialog,
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

from config import DATABASE_PATH
from csv_transfer import (
    export_history_csv,
    export_snippets_csv,
    import_history_csv,
    import_snippets_csv,
)
from database import get_setting, set_setting
from startup import (
    StartupRegistrationError,
    is_launch_at_startup_enabled,
    set_launch_at_startup_enabled,
)


_DEFAULTS: dict[str, str] = {
    "theme": "dark",
    "launch_at_startup": "0",
    "show_in_menubar": "1",
    "show_in_dock": "1",
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


def _normalize_non_negative_int(value: str, default: str) -> str:
    stripped = (value or "").strip()
    return stripped if stripped.isdigit() else default


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
        thumb_rect = track_rect.adjusted(
            thumb_x - track_rect.left(),
            2,
            -(track_rect.width() - (thumb_x - track_rect.left()) - 16),
            -2,
        )
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
        self._build_transfer_tab()

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

        self._launch_toggle = self._create_toggle("launchAtStartupToggle")
        layout.addWidget(
            self._create_toggle_row(
                "システム起動時に開始",
                "次回の Windows サインイン時から自動的に Coppy を開始します。",
                self._launch_toggle,
            )
        )

        self._menubar_toggle = self._create_toggle("showInMenuBarToggle")
        layout.addWidget(
            self._create_toggle_row(
                "通知領域に表示",
                "タスクトレイにアプリケーションアイコンを表示します。",
                self._menubar_toggle,
            )
        )

        self._dock_toggle = self._create_toggle("showInDockToggle")
        layout.addWidget(
            self._create_toggle_row(
                "最前面に表示",
                "ウィンドウを常に手前に表示します。",
                self._dock_toggle,
            )
        )

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
        layout.addWidget(
            self._create_field_block("通知", "通知バナーの表示レベル。", self._notification_combo)
        )

        layout.addWidget(self._create_separator())

        self._monitor_toggle = self._create_toggle("monitorClipboardToggle")
        layout.addWidget(
            self._create_toggle_row(
                "クリップボードを監視",
                "クリップボード変更を自動で検出します。",
                self._monitor_toggle,
            )
        )

        self._confirm_delete_toggle = self._create_toggle("confirmBeforeDeleteToggle")
        layout.addWidget(
            self._create_toggle_row(
                "確認ダイアログを表示",
                "アイテム削除時に確認ダイアログを出します。",
                self._confirm_delete_toggle,
            )
        )

        layout.addStretch(1)
        self._tabs.addTab(page, "一般")

    def _build_history_tab(self) -> None:
        page, layout = self._create_tab_page("履歴")

        self._max_history_input = self._create_number_edit("maxHistoryItemsInput", "200")
        layout.addWidget(
            self._create_field_block(
                "最大保存アイテム数",
                "履歴に保持する件数。0 で無制限。",
                self._max_history_input,
            )
        )

        self._retention_days_input = self._create_number_edit("retentionDaysInput", "0")
        layout.addWidget(
            self._create_field_block(
                "保存期間（日）",
                "指定日数を超えたアイテムを自動削除。0 で無期限。",
                self._retention_days_input,
            )
        )

        layout.addWidget(self._create_separator())

        self._save_history_toggle = self._create_toggle("saveHistoryOnExitToggle")
        layout.addWidget(
            self._create_toggle_row(
                "終了時に履歴を保存",
                "アプリ終了時に履歴をディスクへ保存します。",
                self._save_history_toggle,
            )
        )

        self._restore_history_toggle = self._create_toggle("restoreHistoryOnLaunchToggle")
        layout.addWidget(
            self._create_toggle_row(
                "起動時に履歴を復元",
                "前回の履歴を起動時に復元します。",
                self._restore_history_toggle,
            )
        )

        layout.addWidget(self._create_separator())

        self._database_path_input = self._create_line_edit("databasePathInput", str(DATABASE_PATH))
        self._database_path_input.setReadOnly(True)
        layout.addWidget(
            self._create_field_block(
                "データベースパス",
                "クリップボード履歴の保存場所。",
                self._database_path_input,
            )
        )

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

        self._max_image_size_input = self._create_number_edit("maxImageSizeInput", "10")
        layout.addWidget(
            self._create_field_block(
                "最大画像サイズ（MB）",
                "保存する画像の最大サイズ。0 で無制限。",
                self._max_image_size_input,
            )
        )

        layout.addWidget(self._create_separator())

        self._exclude_duplicates_toggle = self._create_toggle("excludeDuplicatesToggle")
        layout.addWidget(
            self._create_toggle_row(
                "重複を除外",
                "同じ内容のアイテムは 1 件だけ保持します。",
                self._exclude_duplicates_toggle,
            )
        )

        self._exclude_empty_toggle = self._create_toggle("excludeEmptyToggle")
        layout.addWidget(
            self._create_toggle_row(
                "空のアイテムを除外",
                "空白のみのアイテムを保存しません。",
                self._exclude_empty_toggle,
            )
        )

        self._exclude_passwords_toggle = self._create_toggle("excludePasswordsToggle")
        layout.addWidget(
            self._create_toggle_row(
                "パスワードを除外",
                "パスワードマネージャー由来のコピーを無視します。",
                self._exclude_passwords_toggle,
            )
        )

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
        layout.addWidget(
            self._create_field_block(
                "フォント",
                "設定画面とリスト表示の基準フォント。",
                self._font_family_combo,
            )
        )

        self._font_size_combo = self._create_combo(
            "fontSizeCombo",
            [("小（11px）", "11"), ("中（13px）", "13"), ("大（15px）", "15")],
        )
        layout.addWidget(
            self._create_field_block(
                "フォントサイズ",
                "UI に適用する基本フォントサイズ。",
                self._font_size_combo,
            )
        )

        layout.addWidget(self._create_separator())

        self._preview_line_combo = self._create_combo(
            "previewLineCountCombo",
            [("1 行", "1"), ("2 行", "2"), ("3 行", "3"), ("4 行", "4")],
        )
        layout.addWidget(
            self._create_field_block(
                "リストの行数",
                "各アイテムのプレビュー表示行数。",
                self._preview_line_combo,
            )
        )

        layout.addWidget(self._create_separator())

        self._show_item_numbers_toggle = self._create_toggle("showItemNumbersToggle")
        layout.addWidget(
            self._create_toggle_row(
                "アイテム番号を表示",
                "リストにアイテム番号を表示します。",
                self._show_item_numbers_toggle,
            )
        )

        self._show_timestamps_toggle = self._create_toggle("showTimestampsToggle")
        layout.addWidget(
            self._create_toggle_row(
                "タイムスタンプを表示",
                "各アイテムのコピー日時を表示します。",
                self._show_timestamps_toggle,
            )
        )

        self._show_app_names_toggle = self._create_toggle("showAppNamesToggle")
        layout.addWidget(
            self._create_toggle_row(
                "アプリ名を表示",
                "コピー元アプリケーション名を表示します。",
                self._show_app_names_toggle,
            )
        )

        self._show_type_icons_toggle = self._create_toggle("showTypeIconsToggle")
        layout.addWidget(
            self._create_toggle_row(
                "アイコンを表示",
                "アイテム種別アイコンを表示します。",
                self._show_type_icons_toggle,
            )
        )

        layout.addStretch(1)
        self._tabs.addTab(page, "外観")

    def _build_transfer_tab(self) -> None:
        page, layout = self._create_tab_page("出力取込")

        layout.addWidget(self._create_section_heading("履歴データ"))
        self._history_export_path_input = self._create_line_edit("historyExportPathInput", "history.csv")
        self._history_export_path_input.setReadOnly(True)
        self._history_export_encoding_combo = self._create_encoding_combo("historyExportEncodingCombo")
        layout.addWidget(
            self._create_transfer_block(
                "CSV出力",
                "履歴データを CSV に保存します。",
                self._history_export_path_input,
                lambda: self._browse_save_path(self._history_export_path_input, "履歴 CSV の保存先", "history.csv"),
                self._history_export_encoding_combo,
                "出力",
                self._export_history_csv,
            )
        )

        self._history_import_path_input = self._create_line_edit("historyImportPathInput", "history.csv")
        self._history_import_path_input.setReadOnly(True)
        self._history_import_encoding_combo = self._create_encoding_combo("historyImportEncodingCombo")
        layout.addWidget(
            self._create_transfer_block(
                "CSV取込",
                "履歴データを CSV から追加取込します。",
                self._history_import_path_input,
                lambda: self._browse_open_path(self._history_import_path_input, "履歴 CSV を選択"),
                self._history_import_encoding_combo,
                "取込",
                self._import_history_csv,
            )
        )

        layout.addWidget(self._create_separator())

        layout.addWidget(self._create_section_heading("定型文データ"))
        self._snippet_export_path_input = self._create_line_edit("snippetExportPathInput", "snippets.csv")
        self._snippet_export_path_input.setReadOnly(True)
        self._snippet_export_encoding_combo = self._create_encoding_combo("snippetExportEncodingCombo")
        layout.addWidget(
            self._create_transfer_block(
                "CSV出力",
                "定型文データを CSV に保存します。",
                self._snippet_export_path_input,
                lambda: self._browse_save_path(self._snippet_export_path_input, "定型文 CSV の保存先", "snippets.csv"),
                self._snippet_export_encoding_combo,
                "出力",
                self._export_snippets_csv,
            )
        )

        self._snippet_import_path_input = self._create_line_edit("snippetImportPathInput", "snippets.csv")
        self._snippet_import_path_input.setReadOnly(True)
        self._snippet_import_encoding_combo = self._create_encoding_combo("snippetImportEncodingCombo")
        layout.addWidget(
            self._create_transfer_block(
                "CSV取込",
                "定型文データを CSV から追加取込します。",
                self._snippet_import_path_input,
                lambda: self._browse_open_path(self._snippet_import_path_input, "定型文 CSV を選択"),
                self._snippet_import_encoding_combo,
                "取込",
                self._import_snippets_csv,
            )
        )

        layout.addStretch(1)
        self._tabs.addTab(page, "出力/取込")

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

    def _create_encoding_combo(self, object_name: str) -> QComboBox:
        combo = self._create_combo(
            object_name,
            [("Shift_JIS", "shift_jis"), ("UTF-8", "utf-8")],
        )
        self._set_combo_value(combo, "shift_jis")
        return combo

    def _create_number_edit(self, object_name: str, placeholder: str) -> QLineEdit:
        line_edit = self._create_line_edit(object_name, placeholder)
        line_edit.setValidator(QIntValidator(0, 999999, line_edit))
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

    def _create_transfer_block(
        self,
        title: str,
        description: str,
        path_input: QLineEdit,
        browse_handler,
        encoding_combo: QComboBox,
        action_text: str,
        action_handler,
    ) -> QFrame:
        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(10)

        path_row = QHBoxLayout()
        path_row.setContentsMargins(0, 0, 0, 0)
        path_row.setSpacing(10)
        path_row.addWidget(path_input, 1)
        browse_button = QPushButton("参照")
        browse_button.setObjectName("settingsSecondaryButton")
        browse_button.clicked.connect(browse_handler)
        path_row.addWidget(browse_button)
        content_layout.addLayout(path_row)

        action_row = QHBoxLayout()
        action_row.setContentsMargins(0, 0, 0, 0)
        action_row.setSpacing(10)
        label = QLabel("文字コード")
        label.setObjectName("settingsRowTitle")
        action_row.addWidget(label)
        action_row.addWidget(encoding_combo, 1)
        action_button = QPushButton(action_text)
        action_button.setObjectName("settingsPrimaryButton")
        action_button.clicked.connect(action_handler)
        action_row.addWidget(action_button)
        content_layout.addLayout(action_row)

        return self._create_field_block(title, description, content)

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
        self._set_combo_value(self._theme_combo, get_setting("theme", _DEFAULTS["theme"]))

        self._launch_toggle.setChecked(self._load_launch_at_startup_setting())
        self._menubar_toggle.setChecked(_is_truthy(get_setting("show_in_menubar", _DEFAULTS["show_in_menubar"])))
        self._dock_toggle.setChecked(_is_truthy(get_setting("show_in_dock", _DEFAULTS["show_in_dock"])))
        self._set_combo_value(self._language_combo, get_setting("language", _DEFAULTS["language"]))
        self._set_combo_value(
            self._notification_combo,
            get_setting("notification_level", _DEFAULTS["notification_level"]),
        )
        self._monitor_toggle.setChecked(_is_truthy(get_setting("monitor_clipboard", _DEFAULTS["monitor_clipboard"])))
        self._confirm_delete_toggle.setChecked(
            _is_truthy(get_setting("confirm_before_delete", _DEFAULTS["confirm_before_delete"]))
        )

        self._max_history_input.setText(get_setting("max_history_items", _DEFAULTS["max_history_items"]) or "")
        self._retention_days_input.setText(get_setting("retention_days", _DEFAULTS["retention_days"]) or "")
        self._save_history_toggle.setChecked(
            _is_truthy(get_setting("save_history_on_exit", _DEFAULTS["save_history_on_exit"]))
        )
        self._restore_history_toggle.setChecked(
            _is_truthy(get_setting("restore_history_on_launch", _DEFAULTS["restore_history_on_launch"]))
        )
        self._database_path_input.setText(get_setting("database_path", _DEFAULTS["database_path"]) or "")

        self._save_text_toggle.setChecked(_is_truthy(get_setting("save_text", _DEFAULTS["save_text"])))
        self._save_html_toggle.setChecked(_is_truthy(get_setting("save_html", _DEFAULTS["save_html"])))
        self._save_images_toggle.setChecked(_is_truthy(get_setting("save_images", _DEFAULTS["save_images"])))
        self._save_files_toggle.setChecked(_is_truthy(get_setting("save_files", _DEFAULTS["save_files"])))
        self._max_image_size_input.setText(get_setting("max_image_size_mb", _DEFAULTS["max_image_size_mb"]) or "")
        self._exclude_duplicates_toggle.setChecked(
            _is_truthy(get_setting("exclude_duplicates", _DEFAULTS["exclude_duplicates"]))
        )
        self._exclude_empty_toggle.setChecked(
            _is_truthy(get_setting("exclude_empty_items", _DEFAULTS["exclude_empty_items"]))
        )
        self._exclude_passwords_toggle.setChecked(
            _is_truthy(
                get_setting("exclude_password_manager", _DEFAULTS["exclude_password_manager"])
            )
        )

        self._set_combo_value(self._font_family_combo, get_setting("font_family", _DEFAULTS["font_family"]))
        self._set_combo_value(self._font_size_combo, get_setting("font_size", _DEFAULTS["font_size"]))
        self._set_combo_value(
            self._preview_line_combo,
            get_setting("preview_line_count", _DEFAULTS["preview_line_count"]),
        )
        self._show_item_numbers_toggle.setChecked(
            _is_truthy(get_setting("show_item_numbers", _DEFAULTS["show_item_numbers"]))
        )
        self._show_timestamps_toggle.setChecked(
            _is_truthy(get_setting("show_timestamps", _DEFAULTS["show_timestamps"]))
        )
        self._show_app_names_toggle.setChecked(
            _is_truthy(get_setting("show_app_names", _DEFAULTS["show_app_names"]))
        )
        self._show_type_icons_toggle.setChecked(
            _is_truthy(get_setting("show_type_icons", _DEFAULTS["show_type_icons"]))
        )

    def _save_settings(self) -> None:
        try:
            set_launch_at_startup_enabled(self._launch_toggle.isChecked())
        except StartupRegistrationError as exc:
            QMessageBox.warning(self, "自動起動の設定に失敗しました", str(exc))
            return

        set_setting("theme", self._theme_combo.currentData())

        self._save_bool("launch_at_startup", self._launch_toggle)
        set_setting("launch_at_startup_migrated", "1")
        self._save_bool("show_in_menubar", self._menubar_toggle)
        self._save_bool("show_in_dock", self._dock_toggle)
        set_setting("language", self._language_combo.currentData())
        set_setting("notification_level", self._notification_combo.currentData())
        self._save_bool("monitor_clipboard", self._monitor_toggle)
        self._save_bool("confirm_before_delete", self._confirm_delete_toggle)

        set_setting(
            "max_history_items",
            _normalize_non_negative_int(self._max_history_input.text(), _DEFAULTS["max_history_items"]),
        )
        set_setting(
            "retention_days",
            _normalize_non_negative_int(self._retention_days_input.text(), _DEFAULTS["retention_days"]),
        )
        self._save_bool("save_history_on_exit", self._save_history_toggle)
        self._save_bool("restore_history_on_launch", self._restore_history_toggle)
        set_setting("database_path", self._database_path_input.text().strip() or _DEFAULTS["database_path"])

        self._save_bool("save_text", self._save_text_toggle)
        self._save_bool("save_html", self._save_html_toggle)
        self._save_bool("save_images", self._save_images_toggle)
        self._save_bool("save_files", self._save_files_toggle)
        set_setting(
            "max_image_size_mb",
            _normalize_non_negative_int(self._max_image_size_input.text(), _DEFAULTS["max_image_size_mb"]),
        )
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

    def _load_launch_at_startup_setting(self) -> bool:
        try:
            return is_launch_at_startup_enabled()
        except StartupRegistrationError:
            return _is_truthy(get_setting("launch_at_startup", _DEFAULTS["launch_at_startup"]))

    def get_theme_setting(self) -> str:
        return get_setting("theme", _DEFAULTS["theme"]) or _DEFAULTS["theme"]

    def _browse_save_path(self, target: QLineEdit, title: str, default_name: str) -> None:
        selected, _ = QFileDialog.getSaveFileName(
            self,
            title,
            str(Path.cwd() / default_name),
            "CSV Files (*.csv)",
        )
        if selected:
            target.setText(selected)

    def _browse_open_path(self, target: QLineEdit, title: str) -> None:
        selected, _ = QFileDialog.getOpenFileName(
            self,
            title,
            str(Path.cwd()),
            "CSV Files (*.csv)",
        )
        if selected:
            target.setText(selected)

    def _resolve_output_path(self, target: QLineEdit, title: str, default_name: str) -> Optional[Path]:
        current = target.text().strip()
        if current:
            return Path(current)
        self._browse_save_path(target, title, default_name)
        current = target.text().strip()
        return Path(current) if current else None

    def _resolve_input_path(self, target: QLineEdit, title: str) -> Optional[Path]:
        current = target.text().strip()
        if current:
            return Path(current)
        self._browse_open_path(target, title)
        current = target.text().strip()
        return Path(current) if current else None

    def _export_history_csv(self) -> None:
        self._run_export(
            self._history_export_path_input,
            "履歴 CSV の保存先",
            "history.csv",
            self._history_export_encoding_combo.currentData(),
            export_history_csv,
            "履歴データを",
        )

    def _import_history_csv(self) -> None:
        self._run_import(
            self._history_import_path_input,
            "履歴 CSV を選択",
            self._history_import_encoding_combo.currentData(),
            import_history_csv,
            "履歴データ",
        )

    def _export_snippets_csv(self) -> None:
        self._run_export(
            self._snippet_export_path_input,
            "定型文 CSV の保存先",
            "snippets.csv",
            self._snippet_export_encoding_combo.currentData(),
            export_snippets_csv,
            "定型文データを",
        )

    def _import_snippets_csv(self) -> None:
        self._run_import(
            self._snippet_import_path_input,
            "定型文 CSV を選択",
            self._snippet_import_encoding_combo.currentData(),
            import_snippets_csv,
            "定型文データ",
        )

    def _run_export(
        self,
        target: QLineEdit,
        title: str,
        default_name: str,
        encoding: str,
        export_handler,
        subject: str,
    ) -> None:
        path = self._resolve_output_path(target, title, default_name)
        if path is None:
            return
        try:
            count = export_handler(path, encoding=encoding)
        except (OSError, UnicodeError, ValueError) as exc:
            QMessageBox.warning(self, "CSV 出力に失敗しました", str(exc))
            return

        target.setText(str(path))
        QMessageBox.information(
            self,
            "CSV 出力",
            f"{subject}{count}件出力しました。\n{path}",
        )

    def _run_import(
        self,
        target: QLineEdit,
        title: str,
        encoding: str,
        import_handler,
        subject: str,
    ) -> None:
        path = self._resolve_input_path(target, title)
        if path is None:
            return
        try:
            result = import_handler(path, encoding=encoding)
        except (OSError, UnicodeError, ValueError) as exc:
            QMessageBox.warning(self, "CSV 取込に失敗しました", str(exc))
            return

        target.setText(str(path))
        QMessageBox.information(
            self,
            "CSV 取込",
            (
                f"{subject}の取込が完了しました。\n"
                f"追加: {result.added_count} 件\n"
                f"更新: {result.updated_count} 件\n"
                f"スキップ: {result.skipped_count} 件"
            ),
        )
        self.settings_changed.emit()
