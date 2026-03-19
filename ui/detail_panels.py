"""履歴と定型文の詳細ペイン"""
from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QPixmap
from PyQt6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPlainTextEdit,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from ui.iconography import icon_font, icon_glyph
from ui.sample_data import format_japanese_datetime
from ui.widgets import _clear_layout, _make_button, _make_glyph_font


class HistoryDetailPanel(QFrame):
    """履歴の詳細ペイン。"""

    copy_requested = pyqtSignal()
    delete_requested = pyqtSignal()
    pin_requested = pyqtSignal()

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setObjectName("detailPane")
        self._item: dict[str, Any] | None = None
        self._build_ui()
        self.set_empty_state()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        header = QFrame()
        header.setObjectName("detailHeader")
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(24, 18, 24, 18)
        header_layout.setSpacing(12)

        left = QHBoxLayout()
        left.setSpacing(10)

        self._type_label = QLabel("")
        self._type_label.setObjectName("detailType")
        self._type_label.setFont(_make_glyph_font(10))
        left.addWidget(self._type_label)

        self._dot_label = QLabel("•")
        self._dot_label.setObjectName("detailDot")
        left.addWidget(self._dot_label)

        self._app_label = QLabel("")
        self._app_label.setObjectName("detailApp")
        self._app_label.setFont(_make_glyph_font(10))
        left.addWidget(self._app_label)

        left.addStretch(1)
        header_layout.addLayout(left, 1)

        actions = QHBoxLayout()
        actions.setSpacing(8)

        self._pin_button = _make_button(icon_glyph("pin"), "ピン", object_name="iconButton", fixed_size=(30, 30))
        self._pin_button.clicked.connect(self.pin_requested.emit)
        actions.addWidget(self._pin_button)

        self._copy_button = _make_button(icon_glyph("copy"), "コピー", object_name="iconButton", fixed_size=(30, 30))
        self._copy_button.clicked.connect(self.copy_requested.emit)
        actions.addWidget(self._copy_button)

        self._delete_button = _make_button(icon_glyph("delete"), "削除", object_name="dangerIconButton", fixed_size=(30, 30))
        self._delete_button.clicked.connect(self.delete_requested.emit)
        actions.addWidget(self._delete_button)

        header_layout.addLayout(actions)
        layout.addWidget(header)

        self._content_host = QFrame()
        self._content_host.setObjectName("detailContentHost")
        self._content_layout = QVBoxLayout(self._content_host)
        self._content_layout.setContentsMargins(24, 24, 24, 24)
        self._content_layout.setSpacing(0)
        layout.addWidget(self._content_host, 1)

        footer = QFrame()
        footer.setObjectName("detailFooter")
        footer_layout = QHBoxLayout(footer)
        footer_layout.setContentsMargins(24, 12, 24, 12)
        footer_layout.addWidget(QLabel(" "))
        footer_layout.addStretch(1)

        self._footer_label = QLabel("")
        self._footer_label.setObjectName("footerText")
        self._footer_label.setFont(_make_glyph_font(10))
        footer_layout.addWidget(self._footer_label)
        layout.addWidget(footer)

    def set_empty_state(self) -> None:
        self._item = None
        self._type_label.setText("")
        self._type_label.setVisible(False)
        self._dot_label.setVisible(False)
        self._app_label.setText("")
        self._app_label.setVisible(False)
        self._footer_label.setText("")
        self._set_content_widget(self._empty_widget("クリップボードアイテムを選択してください"))
        self._update_pin_button(False)
        self._toggle_controls(False)

    def set_item(self, item: dict[str, Any] | None) -> None:
        self._item = item
        if item is None:
            self.set_empty_state()
            return

        content_type = str(item.get("content_type") or item.get("type") or "text")
        self._type_label.setText(content_type.upper())
        self._type_label.setVisible(True)
        app = str(item.get("app") or "").strip()
        self._app_label.setText(app)
        self._dot_label.setVisible(bool(app))
        self._app_label.setVisible(bool(app))
        self._footer_label.setText(format_japanese_datetime(item.get("created_at") or datetime.now()))
        self._update_pin_button(bool(item.get("is_favorite")))
        self._toggle_controls(True)
        self._set_content_widget(self._build_content_widget(item))

    def _toggle_controls(self, enabled: bool) -> None:
        self._pin_button.setEnabled(enabled)
        self._copy_button.setEnabled(enabled)
        self._delete_button.setEnabled(enabled)

    def _update_pin_button(self, pinned: bool) -> None:
        self._pin_button.setText(icon_glyph("pinned" if pinned else "pin"))
        self._pin_button.setStyleSheet("color: #2d7ff9;" if pinned else "color: #f3f3f3;")

    def _empty_widget(self, text: str) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addStretch(1)

        label = QLabel(text)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setObjectName("emptyStateLabel")
        label.setFont(_make_glyph_font(10))
        layout.addWidget(label)
        layout.addStretch(1)
        return widget

    def _build_content_widget(self, item: dict[str, Any]) -> QWidget:
        content_type = str(item.get("content_type") or item.get("type") or "text")
        content = str(item.get("content") or "")
        image_path = str(item.get("image_path") or "")

        if content_type == "image":
            if image_path and Path(image_path).exists():
                pixmap = QPixmap(image_path)
                if not pixmap.isNull():
                    label = QLabel()
                    label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                    label.setPixmap(
                        pixmap.scaledToWidth(960, Qt.TransformationMode.SmoothTransformation)
                    )
                    label.setObjectName("detailImage")
                    return self._wrap_widget(label)

            label = QLabel(content or "画像を表示できません")
            label.setWordWrap(True)
            label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
            label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
            label.setObjectName("detailPlainText")
            return self._wrap_widget(label)

        if content_type in {"code", "html"}:
            editor = QPlainTextEdit()
            editor.setPlainText(content)
            editor.setReadOnly(True)
            editor.setFrameShape(QFrame.Shape.NoFrame)
            editor.setObjectName("detailCode")
            editor.setFont(QFont("Consolas", 11))
            editor.setLineWrapMode(QPlainTextEdit.LineWrapMode.WidgetWidth)
            return self._wrap_widget(editor)

        label = QLabel(content)
        label.setWordWrap(True)
        label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        label.setObjectName("detailPlainText")
        return self._wrap_widget(label)

    def _wrap_widget(self, widget: QWidget) -> QWidget:
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(widget)
        layout.addStretch(1)
        return container

    def _set_content_widget(self, widget: QWidget) -> None:
        _clear_layout(self._content_layout)
        self._content_layout.addWidget(widget, 1)

    def current_item(self) -> dict[str, Any] | None:
        return self._item


class SnippetDetailPanel(QFrame):
    """定型文の詳細ペイン。"""

    copy_requested = pyqtSignal()
    delete_requested = pyqtSignal()
    edit_requested = pyqtSignal()
    favorite_requested = pyqtSignal()

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setObjectName("detailPane")
        self._item: dict[str, Any] | None = None
        self._build_ui()
        self.set_empty_state()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        header = QFrame()
        header.setObjectName("detailHeader")
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(24, 18, 24, 18)
        header_layout.setSpacing(12)

        title_box = QHBoxLayout()
        title_box.setSpacing(12)

        self._name_label = QLabel("")
        self._name_label.setObjectName("detailTitle")
        self._name_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        title_box.addWidget(self._name_label, 1)

        self._favorite_badge = QLabel(icon_glyph("favorite"))
        self._favorite_badge.setObjectName("favoriteBadge")
        self._favorite_badge.setFont(icon_font(11, QFont.Weight.Bold))
        title_box.addWidget(self._favorite_badge)

        title_box.addStretch(1)
        header_layout.addLayout(title_box, 1)

        actions = QHBoxLayout()
        actions.setSpacing(8)

        self._favorite_button = _make_button(icon_glyph("favorite"), "お気に入り", object_name="iconButton", fixed_size=(30, 30))
        self._favorite_button.clicked.connect(self.favorite_requested.emit)
        actions.addWidget(self._favorite_button)

        self._edit_button = _make_button(icon_glyph("edit"), "編集", object_name="iconButton", fixed_size=(30, 30))
        self._edit_button.clicked.connect(self.edit_requested.emit)
        actions.addWidget(self._edit_button)

        self._copy_button = _make_button(icon_glyph("copy"), "コピー", object_name="iconButton", fixed_size=(30, 30))
        self._copy_button.clicked.connect(self.copy_requested.emit)
        actions.addWidget(self._copy_button)

        self._delete_button = _make_button(icon_glyph("delete"), "削除", object_name="dangerIconButton", fixed_size=(30, 30))
        self._delete_button.clicked.connect(self.delete_requested.emit)
        actions.addWidget(self._delete_button)

        header_layout.addLayout(actions)
        layout.addWidget(header)

        self._meta_frame = QFrame()
        self._meta_frame.setObjectName("snippetMetaFrame")
        meta_layout = QVBoxLayout(self._meta_frame)
        meta_layout.setContentsMargins(24, 14, 24, 14)
        meta_layout.setSpacing(10)

        self._description_label = QLabel("")
        self._description_label.setObjectName("detailMuted")
        self._description_label.setWordWrap(True)
        meta_layout.addWidget(self._description_label)

        self._tags_row = QHBoxLayout()
        self._tags_row.setSpacing(6)
        self._tags_row.addStretch(1)
        meta_layout.addLayout(self._tags_row)

        layout.addWidget(self._meta_frame)

        self._content_host = QFrame()
        self._content_host.setObjectName("detailContentHost")
        self._content_layout = QVBoxLayout(self._content_host)
        self._content_layout.setContentsMargins(24, 24, 24, 24)
        self._content_layout.setSpacing(0)
        layout.addWidget(self._content_host, 1)

        footer = QFrame()
        footer.setObjectName("detailFooter")
        footer_layout = QHBoxLayout(footer)
        footer_layout.setContentsMargins(24, 12, 24, 12)
        footer_layout.addWidget(QLabel(" "))
        footer_layout.addStretch(1)

        self._footer_label = QLabel("")
        self._footer_label.setObjectName("footerText")
        self._footer_label.setFont(_make_glyph_font(10))
        footer_layout.addWidget(self._footer_label)
        layout.addWidget(footer)

    def set_empty_state(self) -> None:
        self._item = None
        self._name_label.setText("")
        self._description_label.setText("")
        self._description_label.setVisible(False)
        self._footer_label.setText("")
        self._favorite_badge.setVisible(False)
        self._meta_frame.setVisible(False)
        self._set_tags([])
        self._toggle_controls(False)
        self._set_content_widget(self._empty_widget("定型文を選択してください"))

    def set_item(self, item: dict[str, Any] | None) -> None:
        self._item = item
        if item is None:
            self.set_empty_state()
            return

        self._name_label.setText(str(item.get("name", "")))
        description = str(item.get("description") or "")
        tags = list(item.get("tags") or [])
        self._description_label.setVisible(bool(description))
        self._description_label.setText(description)
        self._footer_label.setText(f"作成日: {format_japanese_datetime(item.get('created_at') or datetime.now())}")

        favorite = bool(item.get("favorite"))
        self._favorite_badge.setVisible(True)
        self._favorite_badge.setText(icon_glyph("favorite_fill" if favorite else "favorite"))
        self._favorite_badge.setStyleSheet("color: #f59e0b;" if favorite else "color: #6f6f6f;")
        self._favorite_button.setText(icon_glyph("favorite_fill" if favorite else "favorite"))

        self._toggle_controls(True)
        self._set_tags(tags)
        self._meta_frame.setVisible(bool(description or tags))
        self._set_content_widget(self._build_content_widget(str(item.get("content") or "")))

    def _toggle_controls(self, enabled: bool) -> None:
        self._favorite_button.setEnabled(enabled)
        self._edit_button.setEnabled(enabled)
        self._copy_button.setEnabled(enabled)
        self._delete_button.setEnabled(enabled)

    def _empty_widget(self, text: str) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addStretch(1)

        label = QLabel(text)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setObjectName("emptyStateLabel")
        label.setFont(_make_glyph_font(10))
        layout.addWidget(label)
        layout.addStretch(1)
        return widget

    def _build_content_widget(self, content: str) -> QWidget:
        editor = QPlainTextEdit()
        editor.setPlainText(content)
        editor.setReadOnly(True)
        editor.setFrameShape(QFrame.Shape.NoFrame)
        editor.setObjectName("detailCode")
        editor.setFont(QFont("Consolas", 11))
        editor.setLineWrapMode(QPlainTextEdit.LineWrapMode.WidgetWidth)
        return self._wrap_widget(editor)

    def _wrap_widget(self, widget: QWidget) -> QWidget:
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(widget)
        layout.addStretch(1)
        return container

    def _set_tags(self, tags: list[str]) -> None:
        _clear_layout(self._tags_row)
        if tags:
            for tag in tags:
                pill = QLabel(tag)
                pill.setObjectName("tagPillBlue")
                pill.setFont(_make_glyph_font(9))
                self._tags_row.addWidget(pill)
        self._tags_row.addStretch(1)

    def _set_content_widget(self, widget: QWidget) -> None:
        _clear_layout(self._content_layout)
        self._content_layout.addWidget(widget, 1)

    def current_item(self) -> dict[str, Any] | None:
        return self._item
