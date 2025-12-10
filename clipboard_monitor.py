"""クリップボード監視モジュール"""
import hashlib
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional

from PyQt6.QtCore import QObject, pyqtSignal, QTimer, QBuffer, QIODevice
from PyQt6.QtGui import QClipboard, QImage
from PyQt6.QtWidgets import QApplication

from config import IMAGES_DIR, AI_PROVIDER
from database import add_history, check_hash_exists
from categorizer import categorize, is_image_file, extract_file_path


class ClipboardMonitor(QObject):
    """クリップボード監視クラス"""

    # 新しい履歴が追加されたときのシグナル
    history_added = pyqtSignal(int)  # 追加された履歴のID

    def __init__(self, parent: Optional[QObject] = None):
        super().__init__(parent)
        self._clipboard: Optional[QClipboard] = None
        self._last_hash: Optional[str] = None
        self._monitoring = False
        self._use_ai = AI_PROVIDER != "none"

        # タイマーベースの監視（クリップボードシグナルが不安定な場合のフォールバック）
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._check_clipboard)

    def start(self) -> None:
        """監視を開始"""
        if self._monitoring:
            return

        app = QApplication.instance()
        if app is None:
            raise RuntimeError("QApplicationが初期化されていません")

        self._clipboard = app.clipboard()
        self._clipboard.dataChanged.connect(self._on_clipboard_changed)
        self._monitoring = True

        # 初回チェック
        self._check_clipboard()

        # タイマーでも定期的にチェック（500ms間隔）
        self._timer.start(500)

    def stop(self) -> None:
        """監視を停止"""
        if not self._monitoring:
            return

        self._timer.stop()

        if self._clipboard:
            try:
                self._clipboard.dataChanged.disconnect(self._on_clipboard_changed)
            except Exception:
                pass

        self._monitoring = False

    def set_use_ai(self, use_ai: bool) -> None:
        """AI分類の使用を設定"""
        self._use_ai = use_ai

    def _on_clipboard_changed(self) -> None:
        """クリップボード変更時のコールバック"""
        self._check_clipboard()

    def _check_clipboard(self) -> None:
        """クリップボードの内容をチェック"""
        if not self._clipboard:
            return

        mime_data = self._clipboard.mimeData()
        if mime_data is None:
            return

        # 画像チェック
        if mime_data.hasImage():
            image = self._clipboard.image()
            if not image.isNull():
                self._process_image(image)
                return

        # テキストチェック
        if mime_data.hasText():
            text = mime_data.text()
            if text and text.strip():
                self._process_text(text)

    def _process_text(self, text: str) -> None:
        """テキストを処理"""
        text = text.strip()
        if not text:
            return

        # ハッシュ計算
        content_hash = hashlib.sha256(text.encode("utf-8")).hexdigest()

        # 重複チェック（最後のハッシュと比較）
        if content_hash == self._last_hash:
            return

        # データベースで重複確認
        if check_hash_exists(content_hash):
            self._last_hash = content_hash
            return

        # カテゴリ分類
        category = categorize(text, use_ai=self._use_ai)

        # 画像ファイルパスの場合は特別処理
        if category == "image" and is_image_file(text):
            # file:///形式からパスを抽出、または直接パスとして使用
            file_path = extract_file_path(text)
            if file_path is None:
                file_path = text

            # ファイルが存在するか確認
            if Path(file_path).exists():
                history_id = add_history(
                    content_type="image",
                    content=text,  # 元のURLも保存
                    image_path=file_path,
                    content_hash=content_hash,
                    category="image",
                )
            else:
                # ファイルが存在しない場合はURLとして保存
                history_id = add_history(
                    content_type="text",
                    content=text,
                    content_hash=content_hash,
                    category="url",
                )
        else:
            # 通常のテキスト保存
            history_id = add_history(
                content_type="text",
                content=text,
                content_hash=content_hash,
                category=category,
            )

        if history_id:
            self._last_hash = content_hash
            self.history_added.emit(history_id)

    def _process_image(self, image: QImage) -> None:
        """画像を処理"""
        # 画像データをバイト列に変換してハッシュ計算
        buffer = QBuffer()
        buffer.open(QIODevice.OpenModeFlag.WriteOnly)
        image.save(buffer, "PNG")
        image_data = buffer.data().data()
        buffer.close()

        content_hash = hashlib.sha256(image_data).hexdigest()

        # 重複チェック
        if content_hash == self._last_hash:
            return

        if check_hash_exists(content_hash):
            self._last_hash = content_hash
            return

        # 画像をファイルに保存
        filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}.png"
        image_path = IMAGES_DIR / filename
        image.save(str(image_path), "PNG")

        # データベースに保存
        history_id = add_history(
            content_type="image",
            image_path=str(image_path),
            content_hash=content_hash,
            category="image",
        )

        if history_id:
            self._last_hash = content_hash
            self.history_added.emit(history_id)

    def copy_to_clipboard(self, content_type: str, content: Optional[str] = None, image_path: Optional[str] = None) -> bool:
        """内容をクリップボードにコピー"""
        if not self._clipboard:
            return False

        try:
            if content_type == "text" and content:
                # テキストをコピー
                self._clipboard.setText(content)
                # コピーしたものを履歴に追加しないようにハッシュを更新
                self._last_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()
                return True

            elif content_type == "image" and image_path:
                # 画像をコピー
                image = QImage(image_path)
                if not image.isNull():
                    self._clipboard.setImage(image)
                    # ハッシュを更新
                    buffer = QBuffer()
                    buffer.open(QIODevice.OpenModeFlag.WriteOnly)
                    image.save(buffer, "PNG")
                    self._last_hash = hashlib.sha256(buffer.data().data()).hexdigest()
                    buffer.close()
                    return True

        except Exception as e:
            print(f"クリップボードへのコピーに失敗: {e}")

        return False
