import os
import re
import unittest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PyQt6.QtWidgets import QApplication

from ui.detail_panels import HistoryDetailPanel, SnippetDetailPanel
from ui.styles import FIGMA_DARK, FIGMA_LIGHT, get_stylesheet
from ui.widgets import SnippetCard


class ThemeStyleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.app = QApplication.instance() or QApplication([])

    def test_segmented_button_checked_uses_theme_specific_colors(self) -> None:
        dark_rule = self._rule_body(get_stylesheet(True), "QPushButton#segmentedButton:checked")
        light_rule = self._rule_body(get_stylesheet(False), "QPushButton#segmentedButton:checked")

        self.assertIsNotNone(dark_rule)
        self.assertIsNotNone(light_rule)
        self.assertIn(
            f'background-color: {FIGMA_DARK["segmented_checked_bg"]};',
            dark_rule,
        )
        self.assertIn(
            f'color: {FIGMA_DARK["segmented_checked_text"]};',
            dark_rule,
        )
        self.assertIn(
            f'background-color: {FIGMA_LIGHT["segmented_checked_bg"]};',
            light_rule,
        )
        self.assertIn(
            f'color: {FIGMA_LIGHT["segmented_checked_text"]};',
            light_rule,
        )
        self.assertNotIn("background-color: #f1f1f1;", dark_rule)

    def test_blue_tag_pill_uses_theme_tokens(self) -> None:
        dark_rule = self._rule_body(get_stylesheet(True), "QLabel#tagPillBlue")
        light_rule = self._rule_body(get_stylesheet(False), "QLabel#tagPillBlue")

        self.assertIsNotNone(dark_rule)
        self.assertIsNotNone(light_rule)
        self.assertIn(FIGMA_DARK["tag_blue_bg"], dark_rule)
        self.assertIn(FIGMA_DARK["tag_blue_text"], dark_rule)
        self.assertIn(FIGMA_LIGHT["tag_blue_bg"], light_rule)
        self.assertIn(FIGMA_LIGHT["tag_blue_text"], light_rule)

    def test_history_detail_pin_button_uses_dynamic_property(self) -> None:
        panel = HistoryDetailPanel()
        self.addCleanup(panel.deleteLater)

        panel._update_pin_button(True)
        self.assertTrue(panel._pin_button.property("pinned"))
        self.assertEqual(panel._pin_button.styleSheet(), "")

        panel._update_pin_button(False)
        self.assertFalse(panel._pin_button.property("pinned"))
        self.assertEqual(panel._pin_button.styleSheet(), "")

    def test_snippet_favorite_indicators_use_dynamic_properties(self) -> None:
        panel = SnippetDetailPanel()
        self.addCleanup(panel.deleteLater)
        panel.set_item(
            {
                "name": "定型文",
                "content": "print('hello')",
                "description": "説明",
                "tags": ["python"],
                "favorite": True,
            }
        )
        self.assertTrue(panel._favorite_badge.property("favorite"))
        self.assertTrue(panel._favorite_button.property("favorite"))
        self.assertEqual(panel._favorite_badge.styleSheet(), "")

        card = SnippetCard(
            {
                "id": "snippet-1",
                "name": "定型文",
                "description": "説明",
                "favorite": False,
                "tags": ["python"],
            }
        )
        self.addCleanup(card.deleteLater)
        self.assertFalse(card._favorite.property("favorite"))

        card.update_item(
            {
                "id": "snippet-1",
                "name": "定型文",
                "description": "説明",
                "favorite": True,
                "tags": ["python"],
            }
        )
        self.assertTrue(card._favorite.property("favorite"))
        self.assertEqual(card._favorite.styleSheet(), "")

    def _rule_body(self, stylesheet: str, selector: str) -> str | None:
        pattern = re.compile(rf"{re.escape(selector)}\s*\{{(.*?)\}}", re.DOTALL)
        match = pattern.search(stylesheet)
        if match is None:
            return None
        return match.group(1)


if __name__ == "__main__":
    unittest.main()
