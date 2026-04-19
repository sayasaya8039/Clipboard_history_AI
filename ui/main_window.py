"""メインウィンドウモジュール"""
from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, Optional

from PyQt6.QtCore import QTimer, Qt, QRectF, pyqtSignal
from PyQt6.QtGui import QIcon, QPainterPath, QRegion, QCursor
from PyQt6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QScrollArea,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
    QDialog,
)

from config import APP_NAME, APP_VERSION, RESOURCES_DIR
from database import (
    create_snippet,
    delete_history,
    delete_snippet,
    get_history,
    get_setting,
    list_snippets,
    toggle_favorite,
    toggle_snippet_favorite,
    update_snippet,
)
from ui.detail_panels import HistoryDetailPanel, SnippetDetailPanel
from ui.dialogs import NewItemDialog, NewSnippetDialog
from ui.sample_data import (
    build_history_samples,
    normalize_preview,
    parse_datetime,
)
from ui.widgets import (
    HistoryCard,
    SegmentedTabs,
    SearchField,
    SnippetCard,
    TitleBarWidget,
    _clear_layout,
)


class MainWindow(QMainWindow):
    """Figma Make の見た目を再現したメインウィンドウ。"""

    close_requested = pyqtSignal()
    minimize_requested = pyqtSignal()
    copy_requested = pyqtSignal(str, str, str)
    paste_requested = pyqtSignal(str, str, str)
    settings_requested = pyqtSignal()

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)

        self._always_on_top = self._load_always_on_top_setting()

        self.setWindowTitle(APP_NAME)
        self.setWindowIcon(QIcon(str(RESOURCES_DIR / "icon.ico")))
        self.setMinimumSize(1200, 760)
        self.resize(1440, 900)
        self.setWindowFlags(self._build_window_flags())
        self._corner_radius = 18

        self._resize_margin = 8  # ウィンドウ端からのリサイズ判定幅(px)

        self._has_centered_once = False
        self._search_query = ""
        self._active_tab = "history"
        self._selected_history_id: str | None = None
        self._selected_snippet_id: str | None = None
        self._manual_history_items: list[dict[str, Any]] = []
        self._history_seed = build_history_samples()

        self._search_timer = QTimer(self)
        self._search_timer.setSingleShot(True)
        self._search_timer.timeout.connect(self._refresh_visible_content)

        self._build_ui()
        self._connect_signals()
        self._refresh_visible_content()

    def _build_ui(self) -> None:
        central = QWidget()
        self.setCentralWidget(central)

        root = QVBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        self._title_bar = TitleBarWidget("Coppy", f"v{APP_VERSION}")
        root.addWidget(self._title_bar)

        body = QHBoxLayout()
        body.setContentsMargins(0, 0, 0, 0)
        body.setSpacing(0)
        root.addLayout(body, 1)

        self._sidebar = QFrame()
        self._sidebar.setObjectName("sidebar")
        self._sidebar.setFixedWidth(280)
        sidebar_layout = QVBoxLayout(self._sidebar)
        sidebar_layout.setContentsMargins(16, 16, 16, 16)
        sidebar_layout.setSpacing(12)

        self._tabs = SegmentedTabs()
        sidebar_layout.addWidget(self._tabs)

        self._sidebar_content_panel = QFrame()
        self._sidebar_content_panel.setObjectName("sidebarContentPanel")
        content_layout = QVBoxLayout(self._sidebar_content_panel)
        content_layout.setContentsMargins(12, 12, 12, 0)
        content_layout.setSpacing(12)

        self._search = SearchField()
        content_layout.addWidget(self._search)

        self._list_scroll = QScrollArea()
        self._list_scroll.setObjectName("listScroll")
        self._list_scroll.setFrameShape(QFrame.Shape.NoFrame)
        self._list_scroll.setWidgetResizable(True)
        self._list_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self._list_host = QWidget()
        self._list_layout = QVBoxLayout(self._list_host)
        self._list_layout.setContentsMargins(0, 0, 8, 0)
        self._list_layout.setSpacing(10)
        self._list_layout.addStretch(1)
        self._list_scroll.setWidget(self._list_host)
        content_layout.addWidget(self._list_scroll, 1)

        self._sidebar_footer = QFrame()
        self._sidebar_footer.setObjectName("sidebarFooter")
        footer_layout = QHBoxLayout(self._sidebar_footer)
        footer_layout.setContentsMargins(0, 12, 0, 14)
        self._count_label = QLabel("0 アイテム")
        self._count_label.setObjectName("footerText")
        footer_layout.addWidget(self._count_label)
        footer_layout.addStretch(1)
        content_layout.addWidget(self._sidebar_footer)

        sidebar_layout.addWidget(self._sidebar_content_panel, 1)

        body.addWidget(self._sidebar)

        self._detail_stack = QStackedWidget()
        self._detail_stack.setObjectName("detailStack")
        self._history_detail = HistoryDetailPanel()
        self._snippet_detail = SnippetDetailPanel()
        self._detail_stack.addWidget(self._history_detail)
        self._detail_stack.addWidget(self._snippet_detail)
        body.addWidget(self._detail_stack, 1)

        self._install_edge_grips()

    @staticmethod
    def _load_always_on_top_setting() -> bool:
        return str(get_setting("show_in_dock", "1") or "").strip().lower() in {"1", "true", "yes", "on"}

    def _build_window_flags(self) -> Qt.WindowType:
        flags = Qt.WindowType.Window | Qt.WindowType.FramelessWindowHint
        if self._always_on_top:
            flags |= Qt.WindowType.WindowStaysOnTopHint
        return flags

    def _connect_signals(self) -> None:
        self._title_bar.close_requested.connect(self.close_requested.emit)
        self._title_bar.minimize_requested.connect(self.minimize_requested.emit)
        self._title_bar.maximize_requested.connect(self.toggle_maximize)
        self._title_bar.new_requested.connect(self._open_new_dialog)
        self._title_bar.settings_requested.connect(self.settings_requested.emit)

        self._tabs.tab_changed.connect(self._on_tab_changed)
        self._search.text_changed.connect(self._on_search_changed)

        self._history_detail.copy_requested.connect(self._copy_selected_history)
        self._history_detail.paste_requested.connect(self._paste_selected_history)
        self._history_detail.delete_requested.connect(self._delete_selected_history)
        self._history_detail.pin_requested.connect(self._toggle_selected_history_pin)

        self._snippet_detail.copy_requested.connect(self._copy_selected_snippet)
        self._snippet_detail.paste_requested.connect(self._paste_selected_snippet)
        self._snippet_detail.delete_requested.connect(self._delete_selected_snippet)
        self._snippet_detail.edit_requested.connect(self._edit_selected_snippet)
        self._snippet_detail.favorite_requested.connect(self._toggle_selected_snippet_favorite)

    def _on_tab_changed(self, tab: str) -> None:
        self._active_tab = tab
        self._refresh_visible_content()

    def _on_search_changed(self, text: str) -> None:
        self._search_query = text
        self._search_timer.start(220)

    def _refresh_visible_content(self) -> None:
        if self._active_tab == "history":
            self._refresh_history_view()
            self._detail_stack.setCurrentWidget(self._history_detail)
        else:
            self._refresh_snippet_view()
            self._detail_stack.setCurrentWidget(self._snippet_detail)

    def refresh_history(self) -> None:
        """外部更新時に履歴一覧だけ再描画する。"""
        if self._active_tab != "history":
            return

        self._refresh_history_view()

    def refresh_snippets(self) -> None:
        """外部更新時に定型文一覧だけ再描画する。"""
        if self._active_tab != "snippets":
            return

        self._refresh_snippet_view()

    def _refresh_history_view(self) -> None:
        items = self._filter_history_items(self._history_items())
        if not any(str(item["id"]) == self._selected_history_id for item in items):
            self._selected_history_id = str(items[0]["id"]) if items else None

        self._populate_cards(items, self._selected_history_id, kind="history")
        self._count_label.setText(f"{len(items)} アイテム")
        selected = next((item for item in items if str(item["id"]) == self._selected_history_id), None)
        self._history_detail.set_item(selected)

    def _refresh_snippet_view(self) -> None:
        items = self._filter_snippet_items(self._snippet_items())
        if not any(str(item["id"]) == self._selected_snippet_id for item in items):
            self._selected_snippet_id = str(items[0]["id"]) if items else None

        self._populate_cards(items, self._selected_snippet_id, kind="snippet")
        self._count_label.setText(f"{len(items)} 定型文")
        selected = next((item for item in items if str(item["id"]) == self._selected_snippet_id), None)
        self._snippet_detail.set_item(selected)

    def _populate_cards(
        self,
        items: list[dict[str, Any]],
        selected_id: str | None,
        *,
        kind: str,
    ) -> None:
        _clear_layout(self._list_layout)

        if not items:
            self._list_layout.addStretch(1)
            empty = QLabel("検索結果がありません")
            empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
            empty.setObjectName("emptyStateLabel")
            self._list_layout.addWidget(empty)
            self._list_layout.addStretch(1)
            return

        for item in items:
            card = HistoryCard(item) if kind == "history" else SnippetCard(item)
            card.clicked.connect(self._on_card_clicked)
            card.set_selected(str(item.get("id")) == selected_id)
            self._list_layout.addWidget(card)

        self._list_layout.addStretch(1)

    def _on_card_clicked(self, item_id: str) -> None:
        if self._active_tab == "history":
            self._selected_history_id = item_id
        else:
            self._selected_snippet_id = item_id
        self._refresh_visible_content()

    def _history_items(self) -> list[dict[str, Any]]:
        db_rows = get_history(limit=200, category=None, search_query=None, favorites_only=False)
        items = [self._normalize_history_row(row) for row in db_rows]
        items = [*self._manual_history_items, *items]

        if not items:
            items = [dict(sample) for sample in self._history_seed]

        return self._sort_by_timestamp(items, "created_at")

    def _snippet_items(self) -> list[dict[str, Any]]:
        rows = list_snippets()
        items = [self._normalize_snippet_row(row) for row in rows]
        return self._sort_by_timestamp(items, "created_at")

    def _filter_history_items(self, items: list[dict[str, Any]]) -> list[dict[str, Any]]:
        query = self._search_query.strip().lower()
        if not query:
            return items

        result = []
        for item in items:
            haystack = " ".join(
                str(value)
                for value in (
                    item.get("content"),
                    item.get("preview"),
                    item.get("app"),
                    item.get("content_type"),
                    item.get("category"),
                )
                if value
            ).lower()
            if query in haystack:
                result.append(item)
        return result

    def _filter_snippet_items(self, items: list[dict[str, Any]]) -> list[dict[str, Any]]:
        query = self._search_query.strip().lower()
        if not query:
            return items

        result = []
        for item in items:
            tags = ", ".join(str(tag) for tag in item.get("tags") or [])
            haystack = " ".join(
                str(value)
                for value in (
                    item.get("name"),
                    item.get("content"),
                    item.get("preview"),
                    item.get("description"),
                    tags,
                )
                if value
            ).lower()
            if query in haystack:
                result.append(item)
        return result

    def _sort_by_timestamp(self, items: list[dict[str, Any]], key: str) -> list[dict[str, Any]]:
        return sorted(
            items,
            key=lambda item: parse_datetime(item.get(key)) or datetime.min,
            reverse=True,
        )

    def _normalize_history_row(self, row: dict[str, Any]) -> dict[str, Any]:
        storage_id = row.get("id")
        content_type = str(row.get("content_type") or row.get("type") or "text")
        content = str(row.get("content") or "")
        preview = str(row.get("preview") or normalize_preview(content))
        created_at = parse_datetime(row.get("created_at")) or datetime.now()
        return {
            "id": f"db-history-{storage_id}",
            "storage_id": storage_id,
            "content_type": content_type,
            "type": content_type,
            "content": content,
            "preview": preview,
            "app": row.get("app") or None,
            "category": row.get("category") or content_type,
            "is_favorite": bool(row.get("is_favorite")),
            "image_path": row.get("image_path") or "",
            "created_at": created_at,
        }

    def _open_new_dialog(self) -> None:
        if self._active_tab == "history":
            dialog = NewItemDialog(self)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                payload = dialog.get_payload()
                if payload:
                    self._add_manual_history_item(payload)
        else:
            dialog = NewSnippetDialog(self)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                payload = dialog.get_payload()
                if payload:
                    self._add_manual_snippet(payload)

    def _add_manual_history_item(self, payload: dict[str, Any]) -> None:
        item_id = f"manual-history-{uuid.uuid4().hex[:8]}"
        content = str(payload.get("content") or "")
        item = {
            "id": item_id,
            "content_type": payload.get("content_type") or "text",
            "type": payload.get("type") or payload.get("content_type") or "text",
            "content": content,
            "preview": str(payload.get("preview") or normalize_preview(content)),
            "app": payload.get("app") or None,
            "category": payload.get("category") or payload.get("content_type") or "text",
            "is_favorite": bool(payload.get("is_favorite", False)),
            "image_path": payload.get("image_path") or "",
            "created_at": datetime.now(),
        }
        self._manual_history_items = [item, *self._manual_history_items]
        self._selected_history_id = item_id
        self._refresh_history_view()

    def _add_manual_snippet(self, payload: dict[str, Any]) -> None:
        snippet_id = create_snippet(
            name=str(payload.get("name") or ""),
            content=str(payload.get("content") or ""),
            description=payload.get("description") or None,
            tags=list(payload.get("tags") or []),
            favorite=bool(payload.get("favorite", False)),
        )
        self._selected_snippet_id = f"db-snippet-{snippet_id}"
        self._refresh_snippet_view()

    def _current_history_item(self) -> dict[str, Any] | None:
        selected = self._selected_history_id
        for item in self._history_items():
            if str(item.get("id")) == selected:
                return item
        return None

    def _current_snippet_item(self) -> dict[str, Any] | None:
        selected = self._selected_snippet_id
        for item in self._snippet_items():
            if str(item.get("id")) == selected:
                return item
        return None

    def _copy_selected_history(self) -> None:
        item = self._current_history_item()
        if not item:
            return
        self.copy_requested.emit(
            str(item.get("content_type") or "text"),
            str(item.get("content") or ""),
            str(item.get("image_path") or ""),
        )

    def _copy_selected_snippet(self) -> None:
        item = self._current_snippet_item()
        if not item:
            return
        self.copy_requested.emit("text", str(item.get("content") or ""), "")

    def _paste_selected_history(self) -> None:
        item = self._current_history_item()
        if not item:
            return
        self.paste_requested.emit(
            str(item.get("content_type") or "text"),
            str(item.get("content") or ""),
            str(item.get("image_path") or ""),
        )

    def _paste_selected_snippet(self) -> None:
        item = self._current_snippet_item()
        if not item:
            return
        self.paste_requested.emit("text", str(item.get("content") or ""), "")

    def _delete_selected_history(self) -> None:
        item = self._current_history_item()
        if not item:
            return

        item_id = str(item.get("id"))
        if item_id.startswith("manual-history-"):
            self._manual_history_items = [
                history_item for history_item in self._manual_history_items if str(history_item.get("id")) != item_id
            ]
        else:
            storage_id = item.get("storage_id")
            if storage_id is not None:
                delete_history(int(storage_id))

        self._selected_history_id = None
        self._refresh_history_view()

    def _delete_selected_snippet(self) -> None:
        item = self._current_snippet_item()
        if not item:
            return

        storage_id = item.get("storage_id")
        if storage_id is not None:
            delete_snippet(int(storage_id))
        self._selected_snippet_id = None
        self._refresh_snippet_view()

    def _edit_selected_snippet(self) -> None:
        item = self._current_snippet_item()
        if not item:
            return

        dialog = NewSnippetDialog(self, item)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            payload = dialog.get_payload()
            if payload:
                self._update_snippet_item(payload)

    def _toggle_selected_snippet_favorite(self) -> None:
        item = self._current_snippet_item()
        if not item:
            return

        storage_id = item.get("storage_id")
        if storage_id is not None:
            toggle_snippet_favorite(int(storage_id))

        self._refresh_snippet_view()

    def _toggle_selected_history_pin(self) -> None:
        item = self._current_history_item()
        if not item:
            return

        item_id = str(item.get("id"))
        if item_id.startswith("manual-history-"):
            for history_item in self._manual_history_items:
                if str(history_item.get("id")) == item_id:
                    history_item["is_favorite"] = not bool(history_item.get("is_favorite"))
                    break
        else:
            storage_id = item.get("storage_id")
            if storage_id is not None:
                toggle_favorite(int(storage_id))

        self._refresh_history_view()

    def _update_snippet_item(self, payload: dict[str, Any]) -> None:
        item_id = str(payload.get("id") or "")
        storage_id = self._extract_storage_id(item_id, "db-snippet-")
        if storage_id is None:
            return

        updated = update_snippet(
            storage_id,
            name=str(payload.get("name") or ""),
            content=str(payload.get("content") or ""),
            description=payload.get("description") or None,
            tags=list(payload.get("tags") or []),
            favorite=bool(payload.get("favorite", False)),
            created_at=self._format_datetime_value(payload.get("created_at")),
        )
        if updated:
            self._selected_snippet_id = item_id
            self._refresh_snippet_view()

    def _normalize_snippet_row(self, row: dict[str, Any]) -> dict[str, Any]:
        storage_id = row.get("id")
        content = str(row.get("content") or "")
        created_at = parse_datetime(row.get("created_at")) or datetime.now()
        return {
            "id": f"db-snippet-{storage_id}",
            "storage_id": storage_id,
            "name": row.get("name") or "",
            "content": content,
            "description": row.get("description") or None,
            "tags": list(row.get("tags") or []),
            "favorite": bool(row.get("favorite")),
            "created_at": created_at,
            "preview": str(row.get("preview") or normalize_preview(content)),
        }

    def _extract_storage_id(self, item_id: str, prefix: str) -> int | None:
        if not item_id.startswith(prefix):
            return None
        raw_value = item_id.removeprefix(prefix)
        return int(raw_value) if raw_value.isdigit() else None

    def _format_datetime_value(self, value: Any) -> str | None:
        if value is None:
            return None
        if isinstance(value, datetime):
            return value.strftime("%Y-%m-%d %H:%M:%S")
        return str(value)

    def showEvent(self, event) -> None:  # noqa: N802
        super().showEvent(event)
        self._refresh_visible_content()
        self._update_window_mask()
        if not self._has_centered_once:
            self._center_on_screen()
            self._has_centered_once = True

    def resizeEvent(self, event) -> None:  # noqa: N802
        super().resizeEvent(event)
        self._update_window_mask()
        if hasattr(self, "_edge_grips"):
            self._layout_edge_grips()

    def _center_on_screen(self) -> None:
        screen = self.screen()
        if not screen:
            return
        geometry = screen.availableGeometry()
        x = geometry.x() + (geometry.width() - self.width()) // 2
        y = geometry.y() + (geometry.height() - self.height()) // 2
        self.move(max(geometry.x(), x), max(geometry.y(), y))

    def _update_window_mask(self) -> None:
        if self.width() <= 0 or self.height() <= 0:
            return

        if self.isMaximized() or self.isFullScreen():
            self.clearMask()
            return

        path = QPainterPath()
        path.addRoundedRect(QRectF(self.rect()), self._corner_radius, self._corner_radius)
        self.setMask(QRegion(path.toFillPolygon().toPolygon()))

    def set_always_on_top(self, enabled: bool) -> None:
        enabled = bool(enabled)
        if self._always_on_top == enabled:
            return

        was_visible = self.isVisible()
        was_maximized = self.isMaximized()
        geometry = self.geometry()

        self._always_on_top = enabled
        self.setWindowFlags(self._build_window_flags())

        if was_maximized:
            self.showMaximized()
        elif was_visible:
            self.show()
            self.setGeometry(geometry)
            self.raise_()
            self.activateWindow()

        QTimer.singleShot(0, self._update_window_mask)

    def toggle_maximize(self) -> None:
        if self.isMaximized():
            self.showNormal()
        else:
            self.showMaximized()
        QTimer.singleShot(0, self._update_window_mask)

    # ── リサイズ処理 (エッジグリップ) ───────────────────────────

    def _install_edge_grips(self) -> None:
        """ウィンドウの4辺＋4隅に透明なグリップウィジェットを配置する。"""
        edges = {
            "left": Qt.CursorShape.SizeHorCursor,
            "right": Qt.CursorShape.SizeHorCursor,
            "top": Qt.CursorShape.SizeVerCursor,
            "bottom": Qt.CursorShape.SizeVerCursor,
            "top-left": Qt.CursorShape.SizeFDiagCursor,
            "top-right": Qt.CursorShape.SizeBDiagCursor,
            "bottom-left": Qt.CursorShape.SizeBDiagCursor,
            "bottom-right": Qt.CursorShape.SizeFDiagCursor,
        }
        self._edge_grips: list[_EdgeGrip] = []
        for name, cursor in edges.items():
            grip = _EdgeGrip(name, cursor, self)
            self._edge_grips.append(grip)

    def _layout_edge_grips(self) -> None:
        """ウィンドウサイズに合わせてグリップの位置を更新する。"""
        m = self._resize_margin
        w, h = self.width(), self.height()
        for grip in self._edge_grips:
            name = grip.edge_name
            if name == "left":
                grip.setGeometry(0, m, m, h - 2 * m)
            elif name == "right":
                grip.setGeometry(w - m, m, m, h - 2 * m)
            elif name == "top":
                grip.setGeometry(m, 0, w - 2 * m, m)
            elif name == "bottom":
                grip.setGeometry(m, h - m, w - 2 * m, m)
            elif name == "top-left":
                grip.setGeometry(0, 0, m, m)
            elif name == "top-right":
                grip.setGeometry(w - m, 0, m, m)
            elif name == "bottom-left":
                grip.setGeometry(0, h - m, m, m)
            elif name == "bottom-right":
                grip.setGeometry(w - m, h - m, m, m)
            grip.raise_()

    # ── /リサイズ処理 ─────────────────────────────────────────

    def closeEvent(self, event) -> None:  # noqa: N802
        event.ignore()
        self.hide()


class _EdgeGrip(QWidget):
    """ウィンドウ端に配置する透明なリサイズグリップ。"""

    _EDGE_FLAGS: dict[str, Qt.Edge] = {
        "left": Qt.Edge.LeftEdge,
        "right": Qt.Edge.RightEdge,
        "top": Qt.Edge.TopEdge,
        "bottom": Qt.Edge.BottomEdge,
        "top-left": Qt.Edge(Qt.Edge.TopEdge | Qt.Edge.LeftEdge),
        "top-right": Qt.Edge(Qt.Edge.TopEdge | Qt.Edge.RightEdge),
        "bottom-left": Qt.Edge(Qt.Edge.BottomEdge | Qt.Edge.LeftEdge),
        "bottom-right": Qt.Edge(Qt.Edge.BottomEdge | Qt.Edge.RightEdge),
    }

    def __init__(self, edge_name: str, cursor_shape: Qt.CursorShape, parent: QWidget):
        super().__init__(parent)
        self.edge_name = edge_name
        self._qt_edges = self._EDGE_FLAGS[edge_name]
        self.setCursor(QCursor(cursor_shape))
        self.setMouseTracking(True)
        self.setStyleSheet("background: transparent;")

    def mousePressEvent(self, event) -> None:  # noqa: N802
        if event.button() == Qt.MouseButton.LeftButton:
            window = self.window()
            if window and not window.isMaximized() and not window.isFullScreen():
                handle = window.windowHandle()
                if handle:
                    handle.startSystemResize(self._qt_edges)
                    return
        super().mousePressEvent(event)
