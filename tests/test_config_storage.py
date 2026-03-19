import tempfile
import unittest
from pathlib import Path


class ConfigStorageTests(unittest.TestCase):
    def test_build_runtime_paths_uses_appdata_for_persistent_storage(self) -> None:
        from config import build_runtime_paths

        with tempfile.TemporaryDirectory() as tempdir:
            package_dir = Path(tempdir) / "package"
            appdata_root = Path(tempdir) / "AppData" / "Roaming"

            paths = build_runtime_paths(
                package_dir=package_dir,
                appdata_root=appdata_root,
                app_storage_name="Coppy",
            )

        self.assertEqual(paths.data_dir, appdata_root / "Coppy" / "data")
        self.assertEqual(paths.images_dir, appdata_root / "Coppy" / "images")
        self.assertEqual(paths.database_path, appdata_root / "Coppy" / "data" / "clipboard_history.db")
        self.assertEqual(paths.resources_dir, package_dir / "resources")

    def test_migrate_legacy_storage_copies_database_and_images(self) -> None:
        from config import build_runtime_paths, migrate_legacy_storage

        with tempfile.TemporaryDirectory() as tempdir:
            package_dir = Path(tempdir) / "package"
            legacy_data_dir = package_dir / "data"
            legacy_images_dir = package_dir / "images"
            legacy_data_dir.mkdir(parents=True)
            legacy_images_dir.mkdir(parents=True)
            legacy_db = legacy_data_dir / "clipboard_history.db"
            legacy_db.write_text("legacy-db", encoding="utf-8")
            legacy_image = legacy_images_dir / "sample.png"
            legacy_image.write_bytes(b"png")

            paths = build_runtime_paths(
                package_dir=package_dir,
                appdata_root=Path(tempdir) / "AppData" / "Roaming",
                app_storage_name="Coppy",
            )

            migrate_legacy_storage(paths)

            self.assertEqual(paths.database_path.read_text(encoding="utf-8"), "legacy-db")
            self.assertEqual((paths.images_dir / "sample.png").read_bytes(), b"png")
