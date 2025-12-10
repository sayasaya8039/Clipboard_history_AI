"""システムトレイアイコンモジュール"""
from typing import Optional
from PyQt6.QtWidgets import QSystemTrayIcon, QMenu, QApplication
from PyQt6.QtGui import (
    QIcon, QPixmap, QPainter, QColor, QFont, QPen,
    QLinearGradient, QRadialGradient, QPainterPath, QBrush
)
from PyQt6.QtCore import pyqtSignal, QObject, QPointF, QRectF, Qt

from config import APP_NAME, RESOURCES_DIR


def create_default_icon() -> QIcon:
    """近未来的なデフォルトアイコンを生成"""
    size = 64
    pixmap = QPixmap(size, size)
    pixmap.fill(QColor(0, 0, 0, 0))  # 透明背景

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

    center = size / 2
    radius = size / 2 - 4

    # 外側のグロー効果（シアン）
    glow = QRadialGradient(center, center, radius + 4)
    glow.setColorAt(0.0, QColor(0, 255, 255, 0))
    glow.setColorAt(0.7, QColor(0, 255, 255, 30))
    glow.setColorAt(1.0, QColor(0, 255, 255, 80))
    painter.setBrush(QBrush(glow))
    painter.setPen(Qt.PenStyle.NoPen)
    painter.drawEllipse(QRectF(0, 0, size, size))

    # メイン背景（ダークグラデーション）
    bg_gradient = QRadialGradient(center, center * 0.7, radius)
    bg_gradient.setColorAt(0.0, QColor(40, 45, 55))
    bg_gradient.setColorAt(0.5, QColor(25, 30, 40))
    bg_gradient.setColorAt(1.0, QColor(15, 18, 25))
    painter.setBrush(QBrush(bg_gradient))
    painter.setPen(Qt.PenStyle.NoPen)
    painter.drawEllipse(QRectF(4, 4, size - 8, size - 8))

    # 外側リング（シアン）
    ring_pen = QPen(QColor(0, 220, 255, 200))
    ring_pen.setWidth(2)
    painter.setPen(ring_pen)
    painter.setBrush(Qt.BrushStyle.NoBrush)
    painter.drawEllipse(QRectF(5, 5, size - 10, size - 10))

    # 内側リング（薄いシアン）
    inner_pen = QPen(QColor(0, 200, 255, 100))
    inner_pen.setWidth(1)
    painter.setPen(inner_pen)
    painter.drawEllipse(QRectF(12, 12, size - 24, size - 24))

    # クリップボードアイコン風の形状
    clip_path = QPainterPath()
    # メインボード
    board_x, board_y = center - 10, center - 6
    board_w, board_h = 20, 18
    clip_path.addRoundedRect(QRectF(board_x, board_y, board_w, board_h), 2, 2)
    # 上部クリップ
    clip_path.addRoundedRect(QRectF(center - 5, center - 10, 10, 6), 1, 1)

    # クリップボード塗りつぶし（グラデーション）
    clip_gradient = QLinearGradient(board_x, board_y, board_x, board_y + board_h)
    clip_gradient.setColorAt(0.0, QColor(0, 230, 255, 220))
    clip_gradient.setColorAt(1.0, QColor(0, 180, 220, 180))
    painter.setBrush(QBrush(clip_gradient))
    painter.setPen(QPen(QColor(0, 255, 255, 255), 1))
    painter.drawPath(clip_path)

    # データライン（ホログラム風）
    line_pen = QPen(QColor(15, 25, 35, 200))
    line_pen.setWidth(2)
    painter.setPen(line_pen)
    for i in range(3):
        y = center + i * 4
        painter.drawLine(int(center - 6), int(y), int(center + 6), int(y))

    # AIドット（パルス風）
    ai_gradient = QRadialGradient(center, center + 12, 3)
    ai_gradient.setColorAt(0.0, QColor(255, 255, 255, 255))
    ai_gradient.setColorAt(0.5, QColor(0, 255, 200, 200))
    ai_gradient.setColorAt(1.0, QColor(0, 200, 255, 0))
    painter.setBrush(QBrush(ai_gradient))
    painter.setPen(Qt.PenStyle.NoPen)
    painter.drawEllipse(QPointF(center + 6, center - 2), 2, 2)

    painter.end()

    return QIcon(pixmap)


class TrayIcon(QObject):
    """システムトレイアイコンクラス"""

    # シグナル
    show_window_requested = pyqtSignal()
    settings_requested = pyqtSignal()
    quit_requested = pyqtSignal()

    def __init__(self, parent: Optional[QObject] = None):
        super().__init__(parent)

        self._tray_icon = QSystemTrayIcon()

        # アイコン設定
        icon_path = RESOURCES_DIR / "icon.png"
        if icon_path.exists():
            self._tray_icon.setIcon(QIcon(str(icon_path)))
        else:
            self._tray_icon.setIcon(create_default_icon())

        self._tray_icon.setToolTip(APP_NAME)

        # コンテキストメニュー作成
        self._create_menu()

        # クリックイベント
        self._tray_icon.activated.connect(self._on_activated)

    def _create_menu(self) -> None:
        """コンテキストメニューを作成"""
        menu = QMenu()

        # 表示
        show_action = menu.addAction("履歴を表示")
        show_action.triggered.connect(self.show_window_requested.emit)

        menu.addSeparator()

        # 設定
        settings_action = menu.addAction("設定")
        settings_action.triggered.connect(self.settings_requested.emit)

        menu.addSeparator()

        # 終了
        quit_action = menu.addAction("終了")
        quit_action.triggered.connect(self.quit_requested.emit)

        self._tray_icon.setContextMenu(menu)

    def _on_activated(self, reason: QSystemTrayIcon.ActivationReason) -> None:
        """トレイアイコンがクリックされたとき"""
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            # 左クリック：ウィンドウ表示
            self.show_window_requested.emit()
        elif reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            # ダブルクリック：ウィンドウ表示
            self.show_window_requested.emit()

    def show(self) -> None:
        """トレイアイコンを表示"""
        self._tray_icon.show()

    def hide(self) -> None:
        """トレイアイコンを非表示"""
        self._tray_icon.hide()

    def show_message(self, title: str, message: str, icon: QSystemTrayIcon.MessageIcon = QSystemTrayIcon.MessageIcon.Information, duration: int = 3000) -> None:
        """通知メッセージを表示"""
        self._tray_icon.showMessage(title, message, icon, duration)
