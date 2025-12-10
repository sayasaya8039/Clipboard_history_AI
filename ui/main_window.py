"""メインウィンドウモジュール"""
import webbrowser
from datetime import datetime
from typing import Optional
from pathlib import Path

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLineEdit, QListWidget, QListWidgetItem, QLabel,
    QPushButton, QComboBox, QMenu, QFrame, QSizePolicy,
    QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal, QSize, QTimer
from PyQt6.QtGui import QPixmap, QIcon, QAction, QCursor

from config import APP_NAME, CATEGORIES
from database import get_history, delete_history, toggle_favorite, clear_all_history
from categorizer import get_category_icon, get_category_display_name


class HistoryItemWidget(QFrame):
    """履歴アイテムのカスタムウィジェット"""

    copy_clicked = pyqtSignal(dict)  # コピーボタンクリック
    favorite_clicked = pyqtSignal(dict)  # お気に入りボタンクリック
    delete_clicked = pyqtSignal(dict)  # 削除ボタンクリック
    open_url_clicked = pyqtSignal(dict)  # URL開くボタンクリック

    def __init__(self, data: dict, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.data = data
        self._setup_ui()

    def _setup_ui(self) -> None:
        """UIをセットアップ"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        # 左側：コンテンツ
        content_layout = QVBoxLayout()
        content_layout.setSpacing(4)

        # カテゴリとタイムスタンプ
        header_layout = QHBoxLayout()

        # カテゴリアイコンと名前
        category = self.data.get("category", "text")
        category_label = QLabel(f"{get_category_icon(category)} {get_category_display_name(category)}")
        category_label.setProperty("class", "subtitle")
        header_layout.addWidget(category_label)

        header_layout.addStretch()

        # タイムスタンプ
        created_at = self.data.get("created_at", "")
        if created_at:
            try:
                dt = datetime.fromisoformat(created_at)
                time_str = dt.strftime("%Y/%m/%d %H:%M")
            except Exception:
                time_str = created_at
        else:
            time_str = ""
        time_label = QLabel(time_str)
        time_label.setProperty("class", "subtitle")
        header_layout.addWidget(time_label)

        content_layout.addLayout(header_layout)

        # コンテンツ表示
        content_type = self.data.get("content_type", "text")

        if content_type == "image":
            # 画像サムネイル
            image_path = self.data.get("image_path", "")
            if image_path and Path(image_path).exists():
                pixmap = QPixmap(image_path)
                if not pixmap.isNull():
                    scaled = pixmap.scaled(
                        100, 60,
                        Qt.AspectRatioMode.KeepAspectRatio,
                        Qt.TransformationMode.SmoothTransformation
                    )
                    image_label = QLabel()
                    image_label.setPixmap(scaled)
                    content_layout.addWidget(image_label)
                else:
                    content_layout.addWidget(QLabel("[画像を読み込めません]"))
            else:
                content_layout.addWidget(QLabel("[画像ファイルが見つかりません]"))
        else:
            # テキストコンテンツ
            content = self.data.get("content", "")
            # 長いテキストは省略
            display_text = content[:200] + "..." if len(content) > 200 else content
            # 改行を含む場合は最初の3行まで
            lines = display_text.split("\n")
            if len(lines) > 3:
                display_text = "\n".join(lines[:3]) + "\n..."

            content_label = QLabel(display_text)
            content_label.setWordWrap(True)
            content_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)

            # URLカテゴリの場合はクリック可能にする
            if category == "url":
                content_label.setCursor(Qt.CursorShape.PointingHandCursor)
                content_label.setStyleSheet("QLabel:hover { text-decoration: underline; color: #2196F3; }")
                content_label.mousePressEvent = lambda e: self.open_url_clicked.emit(self.data)

            content_layout.addWidget(content_label)

        layout.addLayout(content_layout, 1)

        # 右側：アクションボタン
        button_layout = QVBoxLayout()
        button_layout.setSpacing(4)

        # URLの場合は「開く」ボタンを追加
        if category == "url":
            open_btn = QPushButton("🔗")
            open_btn.setProperty("class", "icon")
            open_btn.setToolTip("ブラウザで開く")
            open_btn.clicked.connect(lambda: self.open_url_clicked.emit(self.data))
            button_layout.addWidget(open_btn)

        # お気に入りボタン
        is_favorite = self.data.get("is_favorite", False)
        fav_btn = QPushButton("★" if is_favorite else "☆")
        fav_btn.setProperty("class", "icon")
        fav_btn.setToolTip("お気に入り")
        fav_btn.clicked.connect(lambda: self.favorite_clicked.emit(self.data))
        button_layout.addWidget(fav_btn)

        # コピーボタン
        copy_btn = QPushButton("📋")
        copy_btn.setProperty("class", "icon")
        copy_btn.setToolTip("コピー")
        copy_btn.clicked.connect(lambda: self.copy_clicked.emit(self.data))
        button_layout.addWidget(copy_btn)

        # 削除ボタン
        delete_btn = QPushButton("🗑")
        delete_btn.setProperty("class", "icon")
        delete_btn.setToolTip("削除")
        delete_btn.clicked.connect(lambda: self.delete_clicked.emit(self.data))
        button_layout.addWidget(delete_btn)

        button_layout.addStretch()

        layout.addLayout(button_layout)


class MainWindow(QMainWindow):
    """メインウィンドウクラス"""

    copy_requested = pyqtSignal(str, str, str)  # content_type, content, image_path
    settings_requested = pyqtSignal()

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)

        self.setWindowTitle(APP_NAME)
        self.setMinimumSize(400, 500)
        self.resize(450, 600)

        # ウィンドウフラグ設定（タスクバーに表示しない）
        self.setWindowFlags(
            Qt.WindowType.Window |
            Qt.WindowType.WindowStaysOnTopHint
        )

        self._search_timer = QTimer()
        self._search_timer.setSingleShot(True)
        self._search_timer.timeout.connect(self._do_search)

        self._current_category: Optional[str] = None
        self._current_search: str = ""
        self._favorites_only: bool = False

        self._setup_ui()

    def _setup_ui(self) -> None:
        """UIをセットアップ"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        # ヘッダー
        header_layout = QHBoxLayout()

        title_label = QLabel(APP_NAME)
        title_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        header_layout.addWidget(title_label)

        header_layout.addStretch()

        # 設定ボタン
        settings_btn = QPushButton("⚙")
        settings_btn.setProperty("class", "icon")
        settings_btn.setToolTip("設定")
        settings_btn.clicked.connect(self.settings_requested.emit)
        header_layout.addWidget(settings_btn)

        layout.addLayout(header_layout)

        # 検索バー
        search_layout = QHBoxLayout()

        self._search_input = QLineEdit()
        self._search_input.setPlaceholderText("検索...")
        self._search_input.textChanged.connect(self._on_search_changed)
        search_layout.addWidget(self._search_input)

        layout.addLayout(search_layout)

        # フィルターバー
        filter_layout = QHBoxLayout()

        # カテゴリフィルター
        self._category_combo = QComboBox()
        self._category_combo.addItem("すべて", None)
        for key, name in CATEGORIES.items():
            self._category_combo.addItem(f"{get_category_icon(key)} {name}", key)
        self._category_combo.currentIndexChanged.connect(self._on_category_changed)
        filter_layout.addWidget(self._category_combo)

        filter_layout.addStretch()

        # お気に入りフィルター
        self._fav_btn = QPushButton("☆ お気に入り")
        self._fav_btn.setProperty("class", "secondary")
        self._fav_btn.setCheckable(True)
        self._fav_btn.clicked.connect(self._on_favorites_toggled)
        filter_layout.addWidget(self._fav_btn)

        # クリアボタン
        clear_btn = QPushButton("履歴をクリア")
        clear_btn.setProperty("class", "secondary")
        clear_btn.clicked.connect(self._on_clear_clicked)
        filter_layout.addWidget(clear_btn)

        layout.addLayout(filter_layout)

        # 履歴リスト
        self._list_widget = QListWidget()
        self._list_widget.setSpacing(2)
        self._list_widget.itemDoubleClicked.connect(self._on_item_double_clicked)
        layout.addWidget(self._list_widget)

        # ステータスバー
        self._status_label = QLabel("")
        self._status_label.setProperty("class", "subtitle")
        layout.addWidget(self._status_label)

    def _on_search_changed(self, text: str) -> None:
        """検索テキスト変更時"""
        self._current_search = text
        # デバウンス（300ms後に検索実行）
        self._search_timer.start(300)

    def _do_search(self) -> None:
        """検索実行"""
        self.refresh_history()

    def _on_category_changed(self, index: int) -> None:
        """カテゴリ変更時"""
        self._current_category = self._category_combo.currentData()
        self.refresh_history()

    def _on_favorites_toggled(self, checked: bool) -> None:
        """お気に入りフィルタートグル"""
        self._favorites_only = checked
        self._fav_btn.setText("★ お気に入り" if checked else "☆ お気に入り")
        self.refresh_history()

    def _on_clear_clicked(self) -> None:
        """履歴クリアボタンクリック"""
        reply = QMessageBox.question(
            self,
            "確認",
            "お気に入り以外の履歴をすべて削除しますか？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            count = clear_all_history()
            self._status_label.setText(f"{count}件の履歴を削除しました")
            self.refresh_history()

    def _on_item_double_clicked(self, item: QListWidgetItem) -> None:
        """アイテムダブルクリック時"""
        widget = self._list_widget.itemWidget(item)
        if isinstance(widget, HistoryItemWidget):
            self._copy_item(widget.data)

    def _copy_item(self, data: dict) -> None:
        """アイテムをコピー"""
        content_type = data.get("content_type", "text")
        content = data.get("content", "")
        image_path = data.get("image_path", "")
        self.copy_requested.emit(content_type, content, image_path)
        self._status_label.setText("コピーしました")

    def _favorite_item(self, data: dict) -> None:
        """アイテムのお気に入りをトグル"""
        history_id = data.get("id")
        if history_id:
            toggle_favorite(history_id)
            self.refresh_history()

    def _delete_item(self, data: dict) -> None:
        """アイテムを削除"""
        history_id = data.get("id")
        if history_id:
            delete_history(history_id)
            self.refresh_history()

    def _open_url(self, data: dict) -> None:
        """URLをブラウザで開く"""
        content = data.get("content", "")
        if content:
            # http/https がない場合は追加
            url = content
            if not url.startswith(("http://", "https://", "file://")):
                url = "https://" + url
            try:
                webbrowser.open(url)
                self._status_label.setText("ブラウザで開きました")
            except Exception as e:
                self._status_label.setText(f"URLを開けませんでした: {e}")

    def refresh_history(self) -> None:
        """履歴を更新"""
        self._list_widget.clear()

        history = get_history(
            limit=200,
            category=self._current_category,
            search_query=self._current_search if self._current_search else None,
            favorites_only=self._favorites_only,
        )

        for item_data in history:
            item = QListWidgetItem(self._list_widget)
            widget = HistoryItemWidget(item_data)

            # シグナル接続
            widget.copy_clicked.connect(self._copy_item)
            widget.favorite_clicked.connect(self._favorite_item)
            widget.delete_clicked.connect(self._delete_item)
            widget.open_url_clicked.connect(self._open_url)

            item.setSizeHint(widget.sizeHint())
            self._list_widget.addItem(item)
            self._list_widget.setItemWidget(item, widget)

        self._status_label.setText(f"{len(history)}件の履歴")

    def showEvent(self, event) -> None:
        """ウィンドウ表示時"""
        super().showEvent(event)
        self.refresh_history()

        # 画面中央に表示
        screen = self.screen()
        if screen:
            screen_geometry = screen.availableGeometry()
            x = (screen_geometry.width() - self.width()) // 2
            y = (screen_geometry.height() - self.height()) // 2
            self.move(x, y)

    def closeEvent(self, event) -> None:
        """ウィンドウを閉じる時は非表示にする"""
        event.ignore()
        self.hide()
