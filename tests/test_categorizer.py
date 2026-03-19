import unittest

from categorizer import categorize, extract_file_path, is_image_file


class CategorizerTests(unittest.TestCase):
    def test_categorize_uses_rule_based_detection_for_common_types(self) -> None:
        self.assertEqual(categorize("https://example.com"), "url")
        self.assertEqual(categorize("hello@example.com"), "email")
        self.assertEqual(categorize("def hello():\n    return 1"), "code")

    def test_categorize_detects_image_file_paths(self) -> None:
        self.assertTrue(is_image_file(r"C:\Temp\image.png"))
        self.assertEqual(categorize(r"C:\Temp\image.png"), "image")

    def test_extract_file_path_decodes_file_url(self) -> None:
        self.assertEqual(
            extract_file_path("file:///C:/Users/Owner/Pictures/test%20image.png"),
            "C:/Users/Owner/Pictures/test image.png",
        )


if __name__ == "__main__":
    unittest.main()
