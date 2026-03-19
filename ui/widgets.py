"""Figma 風 UI の共通ウィジェット群"""
from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any, Optional
from urllib.parse import urlparse

from PyQt6.QtCore import QPoint, Qt, pyqtSignal
from PyQt6.QtCore import QTimer
from PyQt6.QtGui import QFont, QFontMetrics, QPixmap, QTextLayout, QTextOption
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

from config import RESOURCES_DIR
from ui.iconography import icon_font, icon_glyph
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
    use_icon_font: bool = False,
) -> QPushButton:
    button = QPushButton(text)
    button.setObjectName(object_name)
    button.setToolTip(tooltip)
    button.setCheckable(checkable)
    button.setChecked(checked)
    button.setCursor(Qt.CursorShape.PointingHandCursor)
    if use_icon_font:
        button.setFont(icon_font(11))
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

    close_requested = pyqtSignal()
    minimize_requested = pyqtSignal()
    maximize_requested = pyqtSignal()
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
        self._close_button = _make_button(
            "",
            "閉じる",
            object_name="trafficCloseButton",
            fixed_size=(12, 12),
        )
        self._close_button.clicked.connect(self.close_requested.emit)
        traffic.addWidget(self._close_button)

        self._minimize_button = _make_button(
            "",
            "システムトレイに最小化",
            object_name="trafficMinimizeButton",
            fixed_size=(12, 12),
        )
        self._minimize_button.clicked.connect(self.minimize_requested.emit)
        traffic.addWidget(self._minimize_button)

        self._maximize_button = _make_button(
            "",
            "最大化 / 復元",
            object_name="trafficMaximizeButton",
            fixed_size=(12, 12),
        )
        self._maximize_button.clicked.connect(self.maximize_requested.emit)
        traffic.addWidget(self._maximize_button)
        layout.addLayout(traffic)

        title_block = QHBoxLayout()
        title_block.setSpacing(8)

        app_icon = QLabel()
        app_icon.setObjectName("appIcon")
        app_icon.setFixedSize(18, 18)
        app_icon.setPixmap(self._load_app_icon_pixmap(18))
        title_block.addWidget(app_icon)

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

        settings_button = _make_button(
            icon_glyph("settings"),
            "設定",
            object_name="iconButton",
            fixed_size=(30, 30),
            use_icon_font=True,
        )
        settings_button.clicked.connect(self.settings_requested.emit)
        layout.addWidget(settings_button)

    def _load_app_icon_pixmap(self, size: int) -> QPixmap:
        for candidate in (RESOURCES_DIR / "icon.ico", RESOURCES_DIR / "icon.png"):
            if not candidate.exists():
                continue
            pixmap = QPixmap(str(candidate))
            if not pixmap.isNull():
                return pixmap.scaled(
                    size,
                    size,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                )

        fallback = QPixmap(size, size)
        fallback.fill(Qt.GlobalColor.transparent)
        return fallback

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

        for key, text in (("history", f"{icon_glyph('clock')} 履歴"), ("snippets", f"{icon_glyph('list')} 定型文")):
            button = QPushButton(text)
            button.setObjectName("segmentedButton")
            button.setCheckable(True)
            button.setCursor(Qt.CursorShape.PointingHandCursor)
            button.setFont(icon_font(10))
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

        icon = QLabel(icon_glyph("search"))
        icon.setObjectName("searchIcon")
        icon.setFont(icon_font(12))
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


class ClampedTextLabel(QLabel):
    """指定行数で文字列を収めるラベル。"""

    def __init__(self, max_lines: int = 2, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._max_lines = max(1, max_lines)
        self._raw_text = ""
        self._refresh_scheduled = False
        self.setTextFormat(Qt.TextFormat.PlainText)
        self.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        self.setWordWrap(False)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

    def setText(self, text: str) -> None:  # noqa: N802
        self._raw_text = text or ""
        self.setToolTip(self._raw_text)
        self._refresh_text()

    def resizeEvent(self, event) -> None:  # noqa: N802
        super().resizeEvent(event)
        if not self._refresh_scheduled:
            self._refresh_scheduled = True
            QTimer.singleShot(0, self._apply_pending_refresh)

    def showEvent(self, event) -> None:  # noqa: N802
        super().showEvent(event)
        if not self._refresh_scheduled:
            self._refresh_scheduled = True
            QTimer.singleShot(0, self._apply_pending_refresh)

    def _apply_pending_refresh(self) -> None:
        self._refresh_scheduled = False
        self._refresh_text()

    def _refresh_text(self) -> None:
        if not self._raw_text:
            if self.text():
                super().setText("")
            if self.height() != 0:
                self.setFixedHeight(0)
            self.updateGeometry()
            return

        available_width = max(1, self.contentsRect().width())
        metrics = QFontMetrics(self.font())
        lines = self._layout_lines(self._raw_text, available_width, metrics)
        display_text = "\n".join(lines)
        if display_text != self.text():
            super().setText(display_text)
        target_height = metrics.lineSpacing() * min(len(lines), self._max_lines)
        if self.height() != target_height:
            self.setFixedHeight(target_height)
        self.updateGeometry()

    def _layout_lines(self, text: str, width: int, metrics: QFontMetrics) -> list[str]:
        layout = QTextLayout(text, self.font())
        option = QTextOption()
        option.setWrapMode(QTextOption.WrapMode.WrapAtWordBoundaryOrAnywhere)
        layout.setTextOption(option)

        lines: list[str] = []
        layout.beginLayout()
        try:
            while len(lines) < self._max_lines:
                line = layout.createLine()
                if not line.isValid():
                    break

                line.setLineWidth(width)
                start = line.textStart()
                length = line.textLength()
                segment = text[start : start + length].strip()

                if len(lines) == self._max_lines - 1:
                    remaining = text[start:].strip()
                    if remaining and remaining != segment:
                        segment = metrics.elidedText(remaining, Qt.TextElideMode.ElideRight, width)

                lines.append(segment)
        finally:
            layout.endLayout()

        return lines or [text]


class BaseCard(QFrame):
    """選択可能なカードの共通基底。"""

    clicked = pyqtSignal(str)

    def __init__(self, item_id: str, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.item_id = item_id
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setProperty("selected", False)
        self.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Preferred)

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
        self._icon.setFont(icon_font(12, QFont.Weight.DemiBold))
        self._icon.setFixedWidth(24)
        layout.addWidget(self._icon)

        content = QVBoxLayout()
        content.setSpacing(8)

        self._preview = ClampedTextLabel(2)
        self._preview.setObjectName("cardPreview")
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

        self._source = QLabel()
        self._source.setObjectName("cardSource")
        self._source.setProperty("role", "muted")
        meta.addWidget(self._source)

        meta.addStretch(1)
        content.addLayout(meta)

        layout.addLayout(content, 1)

    def update_item(self, item: dict[str, Any]) -> None:
        self._item = item
        content_type = str(item.get("content_type") or item.get("type") or "text")
        self._icon.setText(self._glyph_for_type(content_type))
        self._preview.setText(str(item.get("preview") or normalize_preview(str(item.get("content", "")))))
        self._time.setText(format_relative_time(item.get("created_at") or datetime.now()))
        source = self._source_label_for_item(item)
        self._source.setText(source)
        self._source.setVisible(bool(source))
        self._bullet.setVisible(bool(source))

    @staticmethod
    def _glyph_for_type(content_type: str) -> str:
        return {
            "code": icon_glyph("code"),
            "html": icon_glyph("code"),
            "image": icon_glyph("picture"),
            "url": icon_glyph("link"),
            "email": icon_glyph("mail"),
            "phone": icon_glyph("phone"),
            "filepath": icon_glyph("page"),
            "text": icon_glyph("page"),
        }.get(content_type, icon_glyph("page"))

    @staticmethod
    def _source_label_for_item(item: dict[str, Any]) -> str:
        source = str(item.get("app") or item.get("source") or "").strip()
        if source:
            return source

        content = str(item.get("content") or "").strip()
        content_type = str(item.get("content_type") or item.get("type") or "").lower()
        category = str(item.get("category") or "").lower()

        if content_type == "image" or category == "image":
            return "画像"
        if content_type in {"code", "html"} or category == "code":
            return "Code"
        if content_type == "email" or "@" in content:
            return "Mail"
        if content_type == "phone":
            return "Phone"
        if content.startswith(("http://", "https://")):
            host = urlparse(content).netloc.lower()
            if host.startswith("www."):
                host = host[4:]
            return host or "URL"
        if content.startswith("file:///"):
            local_path = Path(content[8:])
            return local_path.name or local_path.parent.name or "File"
        if any(sep in content for sep in ("\\", "/")):
            local_path = Path(content.replace("file:///", ""))
            return local_path.name or local_path.parent.name or "File"
        if content.lower().startswith(("python ", "npm ", "cargo ", "git ", "select ", "insert ", "update ", "delete ")):
            return "Terminal"
        return category.capitalize() if category and category != "text" else ""


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

        self._icon = QLabel(icon_glyph("page"))
        self._icon.setObjectName("cardIcon")
        self._icon.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)
        self._icon.setFont(icon_font(12, QFont.Weight.DemiBold))
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

        self._favorite = QLabel(icon_glyph("favorite"))
        self._favorite.setFont(icon_font(10, QFont.Weight.Bold))
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
