import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from database import init_database


class CsvTransferTests(unittest.TestCase):
    def setUp(self) -> None:
        self._tempdir = tempfile.TemporaryDirectory()
        self.addCleanup(self._tempdir.cleanup)
        self._db_path = Path(self._tempdir.name) / "csv-transfer-test.db"

        self._db_patch = patch("config.DATABASE_PATH", self._db_path)
        self._db_patch.start()
        self.addCleanup(self._db_patch.stop)

        self._db_patch_2 = patch("database.DATABASE_PATH", self._db_path)
        self._db_patch_2.start()
        self.addCleanup(self._db_patch_2.stop)

        init_database()

    def test_export_history_csv_writes_expected_headers(self) -> None:
        from csv_transfer import export_history_csv
        from database import add_history

        add_history(
            content_type="text",
            content="hello world",
            image_path="",
            content_hash="hash-1",
            category="text",
            app="VS Code",
        )

        export_path = Path(self._tempdir.name) / "history.csv"
        exported_count = export_history_csv(export_path, encoding="utf-8")

        self.assertEqual(exported_count, 1)
        lines = export_path.read_text(encoding="utf-8").splitlines()
        self.assertEqual(
            lines[0],
            "content_type,content,image_path,category,app,is_favorite,created_at",
        )
        self.assertIn("hello world", lines[1])

    def test_import_history_csv_skips_duplicates(self) -> None:
        from csv_transfer import import_history_csv
        from database import add_history, get_history

        add_history(
            content_type="text",
            content="duplicate row",
            image_path="",
            content_hash="hash-dup",
            category="text",
            app="Notepad",
        )

        import_path = Path(self._tempdir.name) / "history-import.csv"
        import_path.write_text(
            "\n".join(
                [
                    "content_type,content,image_path,category,app,is_favorite,created_at",
                    "text,duplicate row,,text,Notepad,0,2026-03-20 12:00:00",
                ]
            ),
            encoding="utf-8",
        )

        result = import_history_csv(import_path, encoding="utf-8")

        self.assertEqual(result.added_count, 0)
        self.assertEqual(result.skipped_count, 1)
        self.assertEqual(len(get_history(limit=10)), 1)

    def test_export_and_import_snippets_round_trip(self) -> None:
        from csv_transfer import export_snippets_csv, import_snippets_csv
        from database import create_snippet, list_snippets

        create_snippet(
            name="署名",
            content="よろしくお願いします。",
            description="メール用",
            tags=["mail", "jp"],
            favorite=True,
            created_at="2026-03-20 10:00:00",
        )

        export_path = Path(self._tempdir.name) / "snippets.csv"
        exported_count = export_snippets_csv(export_path, encoding="utf-8")
        self.assertEqual(exported_count, 1)

        second_db_path = Path(self._tempdir.name) / "csv-transfer-second.db"
        with patch("database.DATABASE_PATH", second_db_path):
            init_database()
            result = import_snippets_csv(export_path, encoding="utf-8")
            snippets = list_snippets()

        self.assertEqual(result.added_count, 1)
        self.assertEqual(len(snippets), 1)
        self.assertEqual(snippets[0]["name"], "署名")
        self.assertEqual(snippets[0]["tags"], ["mail", "jp"])

    def test_export_and_import_history_round_trip_with_shift_jis(self) -> None:
        from csv_transfer import export_history_csv, import_history_csv
        from database import add_history, get_all_history

        add_history(
            content_type="text",
            content="日本語の履歴",
            image_path="",
            content_hash="hash-jp",
            category="text",
            app="Notepad",
        )

        export_path = Path(self._tempdir.name) / "history-sjis.csv"
        exported_count = export_history_csv(export_path, encoding="shift_jis")
        self.assertEqual(exported_count, 1)

        second_db_path = Path(self._tempdir.name) / "history-roundtrip.db"
        with patch("database.DATABASE_PATH", second_db_path):
            init_database()
            result = import_history_csv(export_path, encoding="shift_jis")
            rows = get_all_history()

        self.assertEqual(result.added_count, 1)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["content"], "日本語の履歴")
