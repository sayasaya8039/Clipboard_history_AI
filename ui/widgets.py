"""Figma 風 UI の共通ウィジェット群"""
from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from PyQt6.QtCore import QPoint, Qt, pyqtSignal
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QButtonGroup,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from ui.sample_data import format_relative_time, normalize_preview


def _repolish(widget: QWidget) -> None:
    """ダイナミックプロパティ変更後に再描画する。"""
    style = widget.style()
    style.unpolish(widget)
    style.polish(widget)
    widget.update()


def _make_glyph_font(size: int = 11, weight: int = QFont.Weight.Normal) -> QFont:
    font = QFont("Segoe UI Symbol", size)
    font.setWeight(weight)
    return font


def _make_button(
    text: str,
    tooltip: str,
    *,
    object_name: str = "ghostButton",
    fixed_size: tuple[int, int] | None = None,
    checkable: bool = False,
    checked: bool = False,
) -> QPushButton:
    button = QPushButton(text)
    button.setObjectName(object_name)
    button.setToolTip(tooltip)
    button.setCheckable(checkable)
    button.setChecked(checked)
    button.setCursor(Qt.CursorShape.PointingHandCursor)
    button.setFont(_make_glyph_font(11))
    if fixed_size:
        button.setFixedSize(*fixed_size)
    return button


def _clear_layout(layout: QVBoxLayout | QHBoxLayout) -> None:
    while layout.count():
        item = layout.takeAt(0)
        widget = item.widget()
        child_layout = item.layout()
        if widget is not None:
            widget.setParent(None)
            widget.deleteLater()
        elif child_layout is not None:
            _clear_layout(child_layout)  # type: ignore[arg-type]


class TitleBarWidget(QWidget):
    """Figma 風のカスタムタイトルバー。"""

    new_requested = pyqtSignal()
    settings_requested = pyqtSignal()

    def __init__(self, title: str, version_text: str, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._title = title
        self._version_text = version_text
        self._drag_origin: QPoint | None = None
        self._build_ui()

    def _build_ui(self) -> None:
        self.setObjectName("titleBar")
        self.setFixedHeight(52)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 0, 16, 0)
        layout.setSpacing(12)

        traffic = QHBoxLayout()
        traffic.setSpacing(8)
        for color in ("#ff5f57", "#febc2e", "#28c840"):
            dot = QFrame()
            dot.setFixedSize(12, 12)
            dot.setStyleSheet(f"border-radius: 6px; background: {color};")
            traffic.addWidget(dot)
        layout.addLayout(traffic)

        title_block = QHBoxLayout()
        title_block.setSpacing(8)

        title = QLabel(self._title)
        title.setObjectName("titleLabel")
        title_block.addWidget(title)

        version = QLabel(self._version_text)
        version.setObjectName("versionLabel")
        title_block.addWidget(version)

        layout.addLayout(title_block)
        layout.addStretch(1)

        new_button = _make_button("＋ 新規", "新しいアイテムを追加", fixed_size=(96, 30))
        new_button.clicked.connect(self.new_requested.emit)
        layout.addWidget(new_button)

        settings_button = _make_button("⚙", "設定", object_name="iconButton", fixed_size=(30, 30))
        settings_button.clicked.connect(self.settings_requested.emit)
        layout.addWidget(settings_button)

    def mousePressEvent(self, event) -> None:  # noqa: N802
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_origin = event.globalPosition().toPoint()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event) -> None:  # noqa: N802
        if self._drag_origin is None:
            return
        if event.buttons() & Qt.MouseButton.LeftButton:
            delta = event.globalPosition().toPoint() - self._drag_origin
            window = self.window()
            if window is not None:
                window.move(window.pos() + delta)
            self._drag_origin = event.globalPosition().toPoint()
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event) -> None:  # noqa: N802
        self._drag_origin = None
        super().mouseReleaseEvent(event)


class SegmentedTabs(QWidget):
    """履歴/定型文の切り替えタブ。"""

    tab_changed = pyqtSignal(str)

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self) -> None:
        self.setObjectName("tabSwitcher")

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        group = QButtonGroup(self)
        group.setExclusive(True)
        self._buttons: dict[str, QPushButton] = {}

        for key, text in (("history", "◷ 履歴"), ("snippets", "▣ 定型文")):
            button = QPushButton(text)
            button.setObjectName("segmentedButton")
            button.setCheckable(True)
            button.setCursor(Qt.CursorShape.PointingHandCursor)
            button.setFont(_make_glyph_font(10))
            button.clicked.connect(lambda checked=False, tab=key: self.set_active(tab))
            group.addButton(button)
            self._buttons[key] = button
            layout.addWidget(button)

        self.set_active("history", emit=False)

    def set_active(self, tab: str, emit: bool = True) -> None:
        if tab not in self._buttons:
            return

        for key, button in self._buttons.items():
            button.setChecked(key == tab)

        if emit:
            self.tab_changed.emit(tab)

    def active_tab(self) -> str:
        for key, button in self._buttons.items():
            if button.isChecked():
                return key
        return "history"


class SearchField(QFrame):
    """検索入力。"""

    text_changed = pyqtSignal(str)

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self) -> None:
        self.setObjectName("searchFrame")

        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 0, 12, 0)
        layout.setSpacing(8)

        icon = QLabel("⌕")
        icon.setObjectName("searchIcon")
        icon.setFont(_make_glyph_font(12))
        layout.addWidget(icon)

        self._line_edit = QLineEdit()
        self._line_edit.setObjectName("searchInput")
        self._line_edit.setPlaceholderText("検索")
        self._line_edit.textChanged.connect(self.text_changed.emit)
        layout.addWidget(self._line_edit, 1)

        self.setFixedHeight(40)

    def set_text(self, text: str) -> None:
        self._line_edit.setText(text)

    def text(self) -> str:
        return self._line_edit.text()


class BaseCard(QFrame):
    """選択可能なカードの共通基底。"""

    clicked = pyqtSignal(str)

    def __init__(self, item_id: str, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.item_id = item_id
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setProperty("selected", False)

    def set_selected(self, selected: bool) -> None:
        self.setProperty("selected", selected)
        _repolish(self)

    def mousePressEvent(self, event) -> None:  # noqa: N802
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self.item_id)
        super().mousePressEvent(event)


class HistoryCard(BaseCard):
    """履歴一覧のカード。"""

    def __init__(self, item: dict[str, Any], parent: Optional[QWidget] = None):
        super().__init__(str(item.get("id")), parent)
        self.setObjectName("historyCard")
        self._item = item
        self._build_ui()
        self.update_item(item)

    def _build_ui(self) -> None:
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(12)

        self._icon = QLabel()
        self._icon.setObjectName("cardIcon")
        self._icon.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)
        self._icon.setFont(_make_glyph_font(12, QFont.Weight.DemiBold))
        self._icon.setFixedWidth(24)
        layout.addWidget(self._icon)

        content = QVBoxLayout()
        content.setSpacing(8)

        self._preview = QLabel()
        self._preview.setObjectName("cardPreview")
        self._preview.setWordWrap(True)
        self._preview.setMaximumHeight(42)
        self._preview.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        content.addWidget(self._preview)

        meta = QHBoxLayout()
        meta.setSpacing(6)

        self._time = QLabel()
        self._time.setProperty("role", "muted")
        self._time.setFont(_make_glyph_font(10))
        meta.addWidget(self._time)

        self._bullet = QLabel("•")
        self._bullet.setProperty("role", "muted")
        meta.addWidget(self._bullet)

        self._app = QLabel()
        self._app.setProperty("role", "muted")
        self._app.setFont(_make_glyph_font(10))
        meta.addWidget(self._app)

        meta.addStretch(1)
        content.addLayout(meta)

        layout.addLayout(content, 1)

    def update_item(self, item: dict[str, Any]) -> None:
        self._item = item
        content_type = str(item.get("content_type") or item.get("type") or "text")
        self._icon.setText(self._glyph_for_type(content_type))
        self._preview.setText(str(item.get("preview") or normalize_preview(str(item.get("content", "")))))
        self._time.setText(format_relative_time(item.get("created_at") or datetime.now()))
        app = str(item.get("app") or "").strip()
        self._app.setText(app if app else "")
        self._bullet.setVisible(bool(app))

    @staticmethod
    def _glyph_for_type(content_type: str) -> str:
        return {
            "code": "<>",
            "html": "</>",
            "image": "▣",
        }.get(content_type, "⧉")


class SnippetCard(BaseCard):
    """定型文一覧のカード。"""

    def __init__(self, item: dict[str, Any], parent: Optional[QWidget] = None):
        super().__init__(str(item.get("id")), parent)
        self.setObjectName("snippetCard")
        self._item = item
        self._build_ui()
        self.update_item(item)

    def _build_ui(self) -> None:
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(12)

        self._icon = QLabel("▣")
        self._icon.setObjectName("cardIcon")
        self._icon.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)
        self._icon.setFont(_make_glyph_font(12, QFont.Weight.DemiBold))
        self._icon.setFixedWidth(24)
        layout.addWidget(self._icon)

        content = QVBoxLayout()
        content.setSpacing(7)

        title_row = QHBoxLayout()
        title_row.setSpacing(8)

        self._name = QLabel()
        self._name.setObjectName("cardTitle")
        self._name.setWordWrap(False)
        self._name.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        title_row.addWidget(self._name, 1)

        self._favorite = QLabel("★")
        self._favorite.setFont(_make_glyph_font(10, QFont.Weight.Bold))
        title_row.addWidget(self._favorite)

        content.addLayout(title_row)

        self._description = QLabel()
        self._description.setObjectName("cardDescription")
        self._description.setWordWrap(True)
        self._description.setMaximumHeight(20)
        content.addWidget(self._description)

        self._tags_row = QHBoxLayout()
        self._tags_row.setSpacing(6)
        self._tags_row.addStretch(1)
        content.addLayout(self._tags_row)

        layout.addLayout(content, 1)

    def update_item(self, item: dict[str, Any]) -> None:
        self._item = item
        self._name.setText(str(item.get("name", "")))
        description = str(item.get("description") or "")
        self._description.setVisible(bool(description))
        self._description.setText(description)

        favorite = bool(item.get("favorite"))
        self._favorite.setVisible(True)
        self._favorite.setText("★" if favorite else "☆")
        self._favorite.setStyleSheet("color: #f59e0b;" if favorite else "color: #6f6f6f;")

        _clear_layout(self._tags_row)
        tags = list(item.get("tags") or [])
        if tags:
            for tag in tags:
                pill = QLabel(str(tag))
                pill.setObjectName("tagPill")
                pill.setFont(_make_glyph_font(9))
                self._tags_row.addWidget(pill)
        self._tags_row.addStretch(1)
