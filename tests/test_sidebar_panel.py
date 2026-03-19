import os
import re
import unittest
from datetime import datetime

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PyQt6.QtWidgets import QApplication, QFrame

from ui.main_window import MainWindow
from ui.styles import get_stylesheet
from ui.widgets import HistoryCard


class SidebarPanelTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.app = QApplication.instance() or QApplication([])

    def test_sidebar_rule_does_not_round_outer_edge(self) -> None:
        stylesheet = get_stylesheet(dark=True)

        sidebar_rule = self._rule_body(stylesheet, "QFrame#sidebar")
        self.assertIsNotNone(sidebar_rule)
        self.assertNotIn("border-top-right-radius", sidebar_rule)
        self.assertNotIn("border-bottom-right-radius", sidebar_rule)

    def test_sidebar_uses_inner_rounded_panel_without_sidebar_mask(self) -> None:
        stylesheet = get_stylesheet(dark=True)
        content_panel_rule = self._rule_body(stylesheet, "QFrame#sidebarContentPanel")
        self.assertIsNotNone(content_panel_rule)
        self.assertIn("border-radius: 18px", content_panel_rule)

        window = MainWindow()
        self.addCleanup(window.deleteLater)

        content_panel = window.findChild(QFrame, "sidebarContentPanel")
        self.assertIsNotNone(content_panel)

        window.show()
        self.app.processEvents()
        self.assertTrue(window._sidebar.mask().isEmpty())

    def test_selected_history_card_keeps_right_side_space_for_rounded_corner(self) -> None:
        self.app.setStyle("Fusion")
        self.app.setStyleSheet(get_stylesheet(True))

        window = MainWindow()
        self.addCleanup(window.deleteLater)
        window._manual_history_items = [
            {
                "id": "manual-test",
                "content": r"D:\NEXTCLOUD\Windows_app\ZWG\very\long\folder\name\with\deep\structure\and\final.txt",
                "preview": r"D:\NEXTCLOUD\Windows_app\ZWG\very\long\folder\name\with\deep\structure\and\final.txt",
                "content_type": "filepath",
                "type": "filepath",
                "created_at": datetime.now(),
                "app": "Explorer",
                "is_favorite": False,
                "image_path": "",
                "category": "filepath",
            }
        ]
        window._selected_history_id = "manual-test"
        window._refresh_history_view()
        window.show()
        self.app.processEvents()

        card = window.findChild(HistoryCard, "historyCard")
        self.assertIsNotNone(card)
        self.assertGreater(window._list_layout.contentsMargins().right(), 0)
        self.assertLess(card.width(), window._list_scroll.viewport().width())

    def _rule_body(self, stylesheet: str, selector: str) -> str | None:
        pattern = re.compile(rf"{re.escape(selector)}\s*\{{(.*?)\}}", re.DOTALL)
        match = pattern.search(stylesheet)
        if match is None:
            return None
        return match.group(1)


if __name__ == "__main__":
    unittest.main()
