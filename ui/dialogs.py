"""Figma 風の新規追加ダイアログ"""
from __future__ import annotations

from typing import Any

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QComboBox,
    QTextEdit,
    QVBoxLayout,
)


class NewItemDialog(QDialog):
    """履歴アイテムを手入力で追加するダイアログ。"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._payload: dict[str, Any] | None = None

        self.setWindowTitle("新しいアイテムを追加")
        self.setModal(True)
        self.setMinimumWidth(520)
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)

        self._build_ui()

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(20, 20, 20, 20)
        root.setSpacing(16)

        title = QLabel("新しいアイテムを追加")
        title.setObjectName("DialogTitle")
        root.addWidget(title)

        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)
        form.setFormAlignment(Qt.AlignmentFlag.AlignTop)
        form.setHorizontalSpacing(14)
        form.setVerticalSpacing(12)

        self._type_combo = QComboBox()
        self._type_combo.addItem("テキスト", "text")
        self._type_combo.addItem("コード", "code")
        self._type_combo.addItem("HTML", "html")
        self._type_combo.addItem("画像URL", "image")
        form.addRow("タイプ", self._type_combo)

        self._content_edit = QTextEdit()
        self._content_edit.setPlaceholderText("内容を入力...")
        self._content_edit.setMinimumHeight(160)
        form.addRow("内容", self._content_edit)

        self._app_input = QLineEdit()
        self._app_input.setPlaceholderText("Safari, VS Code など")
        form.addRow("アプリ名（オプション）", self._app_input)

        root.addLayout(form)

        footer = QHBoxLayout()
        footer.addStretch(1)

        cancel = QPushButton("キャンセル")
        cancel.setObjectName("ghostButton")
        cancel.clicked.connect(self.reject)
        footer.addWidget(cancel)

        submit = QPushButton("追加")
        submit.setObjectName("primaryButton")
        submit.clicked.connect(self._accept_form)
        footer.addWidget(submit)

        root.addLayout(footer)

    def _accept_form(self) -> None:
        content = self._content_edit.toPlainText().strip()
        if not content:
            return

        content_type = self._type_combo.currentData()
        app = self._app_input.text().strip() or None
        preview = content.replace("\n", " ")
        if len(preview) > 96:
            preview = preview[:95].rstrip() + "…"

        self._payload = {
            "content_type": content_type,
            "type": content_type,
            "content": content,
            "preview": preview,
            "app": app,
            "category": content_type,
            "image_path": "",
            "is_favorite": False,
        }
        self.accept()

    def get_payload(self) -> dict[str, Any] | None:
        return self._payload


class NewSnippetDialog(QDialog):
    """定型文を追加・編集するダイアログ。"""

    def __init__(self, parent=None, snippet: dict[str, Any] | None = None):
        super().__init__(parent)
        self._snippet = snippet
        self._payload: dict[str, Any] | None = None

        self.setModal(True)
        self.setMinimumWidth(560)
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)
        self.setWindowTitle("定型文を編集" if snippet else "新しい定型文を追加")

        self._build_ui()
        self._load_data()

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(20, 20, 20, 20)
        root.setSpacing(16)

        title = QLabel("定型文を編集" if self._snippet else "新しい定型文を追加")
        title.setObjectName("DialogTitle")
        root.addWidget(title)

        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)
        form.setFormAlignment(Qt.AlignmentFlag.AlignTop)
        form.setHorizontalSpacing(14)
        form.setVerticalSpacing(12)

        self._name_input = QLineEdit()
        self._name_input.setPlaceholderText("例: メールの署名")
        form.addRow("名前", self._name_input)

        self._content_edit = QTextEdit()
        self._content_edit.setPlaceholderText("定型文の内容を入力...")
        self._content_edit.setMinimumHeight(160)
        form.addRow("内容", self._content_edit)

        self._description_input = QLineEdit()
        self._description_input.setPlaceholderText("この定型文の用途")
        form.addRow("説明（オプション）", self._description_input)

        self._tags_input = QLineEdit()
        self._tags_input.setPlaceholderText("タグをカンマ区切りで入力: 仕事, メール")
        form.addRow("タグ（オプション）", self._tags_input)

        root.addLayout(form)

        self._favorite_button = QPushButton("お気に入り")
        self._favorite_button.setCheckable(True)
        self._favorite_button.setObjectName("favoriteToggleButton")
        self._favorite_button.toggled.connect(self._sync_favorite_button)
        favorite_row = QHBoxLayout()
        favorite_row.addWidget(self._favorite_button)
        favorite_row.addStretch(1)
        root.addLayout(favorite_row)

        footer = QHBoxLayout()
        footer.addStretch(1)

        cancel = QPushButton("キャンセル")
        cancel.setObjectName("ghostButton")
        cancel.clicked.connect(self.reject)
        footer.addWidget(cancel)

        submit = QPushButton("保存" if self._snippet else "追加")
        submit.setObjectName("primaryButton")
        submit.clicked.connect(self._accept_form)
        footer.addWidget(submit)

        root.addLayout(footer)

    def _load_data(self) -> None:
        if not self._snippet:
            self._sync_favorite_button(False)
            return

        self._name_input.setText(str(self._snippet.get("name", "")))
        self._content_edit.setPlainText(str(self._snippet.get("content", "")))
        self._description_input.setText(str(self._snippet.get("description", "")))
        tags = self._snippet.get("tags") or []
        self._tags_input.setText(", ".join(tags))
        self._favorite_button.setChecked(bool(self._snippet.get("favorite", False)))

    def _sync_favorite_button(self, checked: bool) -> None:
        self._favorite_button.setText("★ お気に入り" if checked else "☆ お気に入り")

    def _accept_form(self) -> None:
        name = self._name_input.text().strip()
        content = self._content_edit.toPlainText().strip()
        if not name or not content:
            return

        tags_raw = self._tags_input.text().strip()
        tags = [tag.strip() for tag in tags_raw.split(",") if tag.strip()] if tags_raw else []

        description = self._description_input.text().strip() or None
        preview = content.replace("\n", " ")
        if len(preview) > 96:
            preview = preview[:95].rstrip() + "…"

        self._payload = {
            "name": name,
            "content": content,
            "description": description,
            "tags": tags,
            "favorite": self._favorite_button.isChecked(),
            "preview": preview,
        }
        if self._snippet and "id" in self._snippet:
            self._payload["id"] = self._snippet["id"]
            self._payload["created_at"] = self._snippet.get("created_at")

        self.accept()

    def get_payload(self) -> dict[str, Any] | None:
        return self._payload
