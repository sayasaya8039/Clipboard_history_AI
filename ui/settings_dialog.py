"""設定ダイアログモジュール"""
from typing import Optional

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLabel, QLineEdit, QPushButton, QComboBox,
    QGroupBox, QCheckBox, QMessageBox
)
from PyQt6.QtCore import pyqtSignal, Qt

from database import get_setting, set_setting
from ai_client import test_api_connection


class SettingsDialog(QDialog):
    """設定ダイアログクラス"""

    settings_changed = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("設定")
        self.setMinimumWidth(450)
        self.setModal(True)
        # メインウィンドウより前面に表示
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)

        self._setup_ui()
        self._load_settings()

    def _setup_ui(self) -> None:
        """UIをセットアップ"""
        layout = QVBoxLayout(self)
        layout.setSpacing(16)

        # AI設定グループ
        ai_group = QGroupBox("AI カテゴリ分類")
        ai_layout = QVBoxLayout(ai_group)

        # プロバイダー選択
        provider_layout = QFormLayout()

        self._provider_combo = QComboBox()
        self._provider_combo.addItem("無効（ルールベースのみ）", "none")
        self._provider_combo.addItem("OpenAI (GPT)", "openai")
        self._provider_combo.addItem("Google Gemini", "gemini")
        self._provider_combo.currentIndexChanged.connect(self._on_provider_changed)
        provider_layout.addRow("AIプロバイダー:", self._provider_combo)

        ai_layout.addLayout(provider_layout)

        # OpenAI設定
        self._openai_group = QGroupBox("OpenAI 設定")
        openai_layout = QFormLayout(self._openai_group)

        self._openai_key_input = QLineEdit()
        self._openai_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        self._openai_key_input.setPlaceholderText("sk-...")
        openai_layout.addRow("APIキー:", self._openai_key_input)

        openai_test_btn = QPushButton("接続テスト")
        openai_test_btn.clicked.connect(lambda: self._test_connection("openai"))
        openai_layout.addRow("", openai_test_btn)

        ai_layout.addWidget(self._openai_group)

        # Gemini設定
        self._gemini_group = QGroupBox("Google Gemini 設定")
        gemini_layout = QFormLayout(self._gemini_group)

        self._gemini_key_input = QLineEdit()
        self._gemini_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        self._gemini_key_input.setPlaceholderText("AIza...")
        gemini_layout.addRow("APIキー:", self._gemini_key_input)

        gemini_test_btn = QPushButton("接続テスト")
        gemini_test_btn.clicked.connect(lambda: self._test_connection("gemini"))
        gemini_layout.addRow("", gemini_test_btn)

        ai_layout.addWidget(self._gemini_group)

        layout.addWidget(ai_group)

        # 表示設定グループ
        display_group = QGroupBox("表示設定")
        display_layout = QVBoxLayout(display_group)

        # テーマ設定
        theme_layout = QFormLayout()

        self._theme_combo = QComboBox()
        self._theme_combo.addItem("システム設定に従う", "system")
        self._theme_combo.addItem("ライトモード", "light")
        self._theme_combo.addItem("ダークモード", "dark")
        theme_layout.addRow("テーマ:", self._theme_combo)

        display_layout.addLayout(theme_layout)

        layout.addWidget(display_group)

        # ボタン
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        cancel_btn = QPushButton("キャンセル")
        cancel_btn.setProperty("class", "secondary")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)

        save_btn = QPushButton("保存")
        save_btn.clicked.connect(self._save_settings)
        button_layout.addWidget(save_btn)

        layout.addLayout(button_layout)

    def _on_provider_changed(self, index: int) -> None:
        """プロバイダー変更時"""
        provider = self._provider_combo.currentData()
        self._openai_group.setVisible(provider == "openai")
        self._gemini_group.setVisible(provider == "gemini")
        self.adjustSize()

    def _load_settings(self) -> None:
        """設定を読み込む"""
        # プロバイダー
        provider = get_setting("ai_provider", "none")
        index = self._provider_combo.findData(provider)
        if index >= 0:
            self._provider_combo.setCurrentIndex(index)

        # APIキー
        self._openai_key_input.setText(get_setting("openai_api_key", ""))
        self._gemini_key_input.setText(get_setting("gemini_api_key", ""))

        # テーマ
        theme = get_setting("theme", "system")
        theme_index = self._theme_combo.findData(theme)
        if theme_index >= 0:
            self._theme_combo.setCurrentIndex(theme_index)

        # 初期表示状態を更新
        self._on_provider_changed(self._provider_combo.currentIndex())

    def _save_settings(self) -> None:
        """設定を保存"""
        # プロバイダー
        provider = self._provider_combo.currentData()
        set_setting("ai_provider", provider)

        # APIキー
        set_setting("openai_api_key", self._openai_key_input.text())
        set_setting("gemini_api_key", self._gemini_key_input.text())

        # テーマ
        theme = self._theme_combo.currentData()
        set_setting("theme", theme)

        self.settings_changed.emit()
        self.accept()

    def _test_connection(self, provider: str) -> None:
        """API接続をテスト"""
        if provider == "openai":
            api_key = self._openai_key_input.text()
        elif provider == "gemini":
            api_key = self._gemini_key_input.text()
        else:
            return

        if not api_key:
            QMessageBox.warning(self, "エラー", "APIキーを入力してください")
            return

        success, message = test_api_connection(provider, api_key)

        if success:
            QMessageBox.information(self, "成功", message)
        else:
            QMessageBox.warning(self, "エラー", message)

    def get_theme_setting(self) -> str:
        """現在のテーマ設定を取得"""
        return get_setting("theme", "system")

    def get_ai_provider(self) -> str:
        """現在のAIプロバイダー設定を取得"""
        return get_setting("ai_provider", "none")

    def get_openai_key(self) -> str:
        """OpenAI APIキーを取得"""
        return get_setting("openai_api_key", "")

    def get_gemini_key(self) -> str:
        """Gemini APIキーを取得"""
        return get_setting("gemini_api_key", "")
