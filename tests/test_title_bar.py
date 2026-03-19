import os
import unittest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PyQt6.QtWidgets import QApplication, QPushButton

from ui.iconography import icon_font
from ui.styles import get_stylesheet
from ui.widgets import TitleBarWidget


class TitleBarTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.app = QApplication.instance() or QApplication([])

    def test_new_button_uses_plain_plus_instead_of_icon_glyph_font(self) -> None:
        title_bar = TitleBarWidget("Coppy", "v1.0.0")
        self.addCleanup(title_bar.deleteLater)

        new_button = next(
            button
            for button in title_bar.findChildren(QPushButton)
            if button.toolTip() == "新しいアイテムを追加"
        )

        self.assertEqual(new_button.text(), "＋ 新規")
        self.assertNotEqual(new_button.font().family(), icon_font().family())

    def test_settings_button_keeps_icon_font(self) -> None:
        title_bar = TitleBarWidget("Coppy", "v1.0.0")
        self.addCleanup(title_bar.deleteLater)

        settings_button = next(
            button
            for button in title_bar.findChildren(QPushButton)
            if button.toolTip() == "設定"
        )

        self.assertEqual(settings_button.font().family(), icon_font().family())

    def test_stylesheet_targets_title_bar_and_tab_switcher_widgets(self) -> None:
        stylesheet = get_stylesheet(True)

        self.assertIn("QWidget#titleBar {", stylesheet)
        self.assertIn("QWidget#tabSwitcher {", stylesheet)
        self.assertNotIn("QFrame#titleBar {", stylesheet)
        self.assertNotIn("QFrame#tabSwitcher {", stylesheet)


if __name__ == "__main__":
    unittest.main()
