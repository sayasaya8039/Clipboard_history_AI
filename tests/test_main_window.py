import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication

from database import init_database
from ui.main_window import MainWindow


class MainWindowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self) -> None:
        self._tempdir = tempfile.TemporaryDirectory()
        self.addCleanup(self._tempdir.cleanup)
        self._db_path = Path(self._tempdir.name) / "main-window-test.db"

        self._db_patch = patch("config.DATABASE_PATH", self._db_path)
        self._db_patch.start()
        self.addCleanup(self._db_patch.stop)

        self._db_patch_2 = patch("database.DATABASE_PATH", self._db_path)
        self._db_patch_2.start()
        self.addCleanup(self._db_patch_2.stop)

        init_database()

    def test_window_starts_on_top_when_setting_enabled(self) -> None:
        from database import set_setting

        set_setting("show_in_dock", "1")
        window = MainWindow()
        self.addCleanup(window.deleteLater)

        self.assertTrue(bool(window.windowFlags() & Qt.WindowType.WindowStaysOnTopHint))

    def test_window_can_toggle_always_on_top_flag(self) -> None:
        from database import set_setting

        set_setting("show_in_dock", "0")
        window = MainWindow()
        self.addCleanup(window.deleteLater)

        self.assertFalse(bool(window.windowFlags() & Qt.WindowType.WindowStaysOnTopHint))

        window.set_always_on_top(True)
        self.assertTrue(bool(window.windowFlags() & Qt.WindowType.WindowStaysOnTopHint))

        window.set_always_on_top(False)
        self.assertFalse(bool(window.windowFlags() & Qt.WindowType.WindowStaysOnTopHint))

    def test_window_reads_persisted_snippets_from_database(self) -> None:
        from database import create_snippet

        create_snippet(
            name="署名",
            content="よろしくお願いします。",
            description="メール用",
            tags=["mail"],
            favorite=True,
            created_at="2026-03-20 10:00:00",
        )

        window = MainWindow()
        self.addCleanup(window.deleteLater)

        snippet_names = [item["name"] for item in window._snippet_items()]
        self.assertIn("署名", snippet_names)


if __name__ == "__main__":
    unittest.main()
