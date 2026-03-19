import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PyQt6.QtWidgets import QApplication, QCheckBox, QComboBox, QLineEdit, QTabWidget

from database import get_setting, init_database
from ui.settings_dialog import SettingsDialog


class SettingsDialogTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self) -> None:
        self._tempdir = tempfile.TemporaryDirectory()
        self.addCleanup(self._tempdir.cleanup)
        self._db_path = Path(self._tempdir.name) / "settings-test.db"

        self._db_patch = patch("config.DATABASE_PATH", self._db_path)
        self._db_patch.start()
        self.addCleanup(self._db_patch.stop)

        self._db_patch_2 = patch("database.DATABASE_PATH", self._db_path)
        self._db_patch_2.start()
        self.addCleanup(self._db_patch_2.stop)

        init_database()

    def test_load_settings_populates_figma_tabs_and_existing_keys(self) -> None:
        self._seed_settings(
            {
                "ai_provider": "gemini",
                "openai_api_key": "sk-load-openai",
                "gemini_api_key": "gm-load-gemini",
                "theme": "light",
                "launch_at_startup": "1",
                "show_in_dock": "1",
                "language": "en",
                "notification_level": "errors",
            }
        )

        dialog = SettingsDialog()
        self.addCleanup(dialog.deleteLater)

        tab_widget = dialog.findChild(QTabWidget, "settingsTabs")
        self.assertIsNotNone(tab_widget)
        self.assertEqual(tab_widget.count(), 5)
        self.assertEqual(
            [tab_widget.tabText(index) for index in range(tab_widget.count())],
            ["一般", "履歴", "アイテム", "ショートカット", "外観"],
        )

        provider_combo = dialog.findChild(QComboBox, "aiProviderCombo")
        theme_combo = dialog.findChild(QComboBox, "themeCombo")
        openai_input = dialog.findChild(QLineEdit, "openaiKeyInput")
        gemini_input = dialog.findChild(QLineEdit, "geminiKeyInput")
        dock_toggle = dialog.findChild(QCheckBox, "showInDockToggle")
        startup_toggle = dialog.findChild(QCheckBox, "launchAtStartupToggle")
        language_combo = dialog.findChild(QComboBox, "languageCombo")

        self.assertIsNotNone(provider_combo)
        self.assertEqual(provider_combo.currentData(), "gemini")
        self.assertIsNotNone(theme_combo)
        self.assertEqual(theme_combo.currentData(), "light")
        self.assertEqual(openai_input.text(), "sk-load-openai")
        self.assertEqual(gemini_input.text(), "gm-load-gemini")
        self.assertTrue(dock_toggle.isChecked())
        self.assertTrue(startup_toggle.isChecked())
        self.assertEqual(language_combo.currentData(), "en")

    def test_provider_change_toggles_api_groups(self) -> None:
        dialog = SettingsDialog()
        self.addCleanup(dialog.deleteLater)
        dialog.show()
        self.app.processEvents()

        provider_combo = dialog.findChild(QComboBox, "aiProviderCombo")
        openai_group = dialog.findChild(QLineEdit, "openaiKeyInput").parentWidget()
        gemini_group = dialog.findChild(QLineEdit, "geminiKeyInput").parentWidget()

        provider_combo.setCurrentIndex(provider_combo.findData("openai"))
        self.app.processEvents()
        self.assertTrue(openai_group.isVisible())
        self.assertFalse(gemini_group.isVisible())

        provider_combo.setCurrentIndex(provider_combo.findData("gemini"))
        self.app.processEvents()
        self.assertFalse(openai_group.isVisible())
        self.assertTrue(gemini_group.isVisible())

        provider_combo.setCurrentIndex(provider_combo.findData("none"))
        self.app.processEvents()
        self.assertFalse(openai_group.isVisible())
        self.assertFalse(gemini_group.isVisible())

    def test_dialog_keeps_figma_sized_frame_when_provider_changes(self) -> None:
        dialog = SettingsDialog()
        self.addCleanup(dialog.deleteLater)
        dialog.show()
        self.app.processEvents()

        self.assertGreaterEqual(dialog.width(), 700)
        self.assertGreaterEqual(dialog.height(), 700)

        provider_combo = dialog.findChild(QComboBox, "aiProviderCombo")
        provider_combo.setCurrentIndex(provider_combo.findData("openai"))
        self.app.processEvents()

        self.assertGreaterEqual(dialog.width(), 700)
        self.assertGreaterEqual(dialog.height(), 700)

    def test_save_settings_persists_existing_and_additional_keys(self) -> None:
        dialog = SettingsDialog()
        self.addCleanup(dialog.deleteLater)

        self._set_combo(dialog, "aiProviderCombo", "openai")
        self._set_text(dialog, "openaiKeyInput", "sk-save-openai")
        self._set_text(dialog, "geminiKeyInput", "gm-save-gemini")
        self._set_combo(dialog, "themeCombo", "dark")
        self._set_check(dialog, "launchAtStartupToggle", True)
        self._set_check(dialog, "showInDockToggle", True)
        self._set_combo(dialog, "languageCombo", "ko")
        self._set_combo(dialog, "notificationLevelCombo", "none")
        self._set_text(dialog, "maxHistoryItemsInput", "400")
        self._set_text(dialog, "retentionDaysInput", "30")
        self._set_check(dialog, "saveHistoryOnExitToggle", True)
        self._set_check(dialog, "restoreHistoryOnLaunchToggle", False)
        self._set_check(dialog, "saveTextToggle", True)
        self._set_check(dialog, "saveHtmlToggle", False)
        self._set_check(dialog, "saveImagesToggle", True)
        self._set_check(dialog, "saveFilesToggle", True)
        self._set_text(dialog, "maxImageSizeInput", "12")
        self._set_check(dialog, "excludeDuplicatesToggle", True)
        self._set_check(dialog, "excludeEmptyToggle", False)
        self._set_check(dialog, "excludePasswordsToggle", True)
        self._set_combo(dialog, "previewLineCountCombo", "3")
        self._set_check(dialog, "showItemNumbersToggle", True)
        self._set_check(dialog, "showTimestampsToggle", False)
        self._set_check(dialog, "showAppNamesToggle", False)
        self._set_check(dialog, "showTypeIconsToggle", True)

        dialog._save_settings()

        self.assertEqual(get_setting("ai_provider"), "openai")
        self.assertEqual(get_setting("openai_api_key"), "sk-save-openai")
        self.assertEqual(get_setting("gemini_api_key"), "gm-save-gemini")
        self.assertEqual(get_setting("theme"), "dark")
        self.assertEqual(get_setting("launch_at_startup"), "1")
        self.assertEqual(get_setting("show_in_dock"), "1")
        self.assertEqual(get_setting("language"), "ko")
        self.assertEqual(get_setting("notification_level"), "none")
        self.assertEqual(get_setting("max_history_items"), "400")
        self.assertEqual(get_setting("retention_days"), "30")
        self.assertEqual(get_setting("save_history_on_exit"), "1")
        self.assertEqual(get_setting("restore_history_on_launch"), "0")
        self.assertEqual(get_setting("save_html"), "0")
        self.assertEqual(get_setting("save_files"), "1")
        self.assertEqual(get_setting("max_image_size_mb"), "12")
        self.assertEqual(get_setting("exclude_duplicates"), "1")
        self.assertEqual(get_setting("exclude_empty_items"), "0")
        self.assertEqual(get_setting("exclude_password_manager"), "1")
        self.assertEqual(get_setting("preview_line_count"), "3")
        self.assertEqual(get_setting("show_item_numbers"), "1")
        self.assertEqual(get_setting("show_timestamps"), "0")
        self.assertEqual(get_setting("show_app_names"), "0")
        self.assertEqual(get_setting("show_type_icons"), "1")

    def test_save_settings_normalizes_invalid_numeric_values(self) -> None:
        dialog = SettingsDialog()
        self.addCleanup(dialog.deleteLater)

        self._set_text(dialog, "maxHistoryItemsInput", "abc")
        self._set_text(dialog, "retentionDaysInput", "-10")
        self._set_text(dialog, "maxImageSizeInput", "12mb")

        dialog._save_settings()

        self.assertEqual(get_setting("max_history_items"), "200")
        self.assertEqual(get_setting("retention_days"), "0")
        self.assertEqual(get_setting("max_image_size_mb"), "10")

    def _seed_settings(self, values: dict[str, str]) -> None:
        from database import set_setting

        for key, value in values.items():
            set_setting(key, value)

    def _set_combo(self, dialog: SettingsDialog, object_name: str, value: str) -> None:
        combo = dialog.findChild(QComboBox, object_name)
        combo.setCurrentIndex(combo.findData(value))

    def _set_text(self, dialog: SettingsDialog, object_name: str, value: str) -> None:
        dialog.findChild(QLineEdit, object_name).setText(value)

    def _set_check(self, dialog: SettingsDialog, object_name: str, value: bool) -> None:
        dialog.findChild(QCheckBox, object_name).setChecked(value)


if __name__ == "__main__":
    unittest.main()
