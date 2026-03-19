"""カテゴリ分類モジュール。"""
import re
from pathlib import Path
from typing import Optional
from urllib.parse import unquote


IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp", ".ico", ".tiff", ".tif"}


PATTERNS = {
    "url": re.compile(
        r"^(?:https?://|file:///|ftp://)[^\s]+$|"
        r"^(?:www\.)?[a-zA-Z0-9][-a-zA-Z0-9]*\.[a-zA-Z]{2,}(?:/[^\s]*)?$",
        re.IGNORECASE,
    ),
    "email": re.compile(
        r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$",
        re.IGNORECASE,
    ),
    "phone": re.compile(r"^[\d\-\(\)\+\s]{10,}$"),
    "filepath": re.compile(
        r"^(?:[a-zA-Z]:\\|/(?:home|usr|var|etc|opt|tmp|mnt|media)|~/)[\w\\/\-\.\s]+$",
    ),
    "code": re.compile(
        r"(?:"
        r"^\s*(def|class|function|const|let|var|import|from|export|public|private|protected)\s+"
        r"|[{}\[\]];$"
        r"|^\s*[#//]"
        r"|=>\s*[{(]"
        r"|^\s*@\w+"
        r"|<[a-zA-Z][^>]*/?>"
        r")",
        re.MULTILINE,
    ),
}


def is_image_file(path_or_url: str) -> bool:
    """画像ファイルかどうかを判定。"""
    try:
        if path_or_url.startswith("file:///"):
            path = unquote(path_or_url[8:])
            ext = Path(path).suffix.lower()
            return ext in IMAGE_EXTENSIONS

        ext = Path(path_or_url).suffix.lower()
        return ext in IMAGE_EXTENSIONS
    except Exception:
        return False


def extract_file_path(text: str) -> Optional[str]:
    """file:/// 形式の URL からファイルパスを抽出。"""
    if text.startswith("file:///"):
        return unquote(text[8:])
    return None


def categorize_text_rule_based(text: str) -> str:
    """ルールベースでテキストをカテゴリ分類。"""
    text = text.strip()
    if not text:
        return "text"

    if is_image_file(text):
        return "image"

    if PATTERNS["url"].match(text):
        return "url"

    if PATTERNS["email"].match(text):
        return "email"

    digits_only = text.replace("-", "").replace(" ", "").replace("(", "").replace(")", "").replace("+", "")
    if PATTERNS["phone"].match(text) and digits_only.isdigit():
        return "phone"

    if PATTERNS["filepath"].match(text):
        return "filepath"

    lines = text.split("\n")
    if len(lines) > 1:
        indented_lines = sum(1 for line in lines if line.startswith(("  ", "\t")))
        if indented_lines >= len(lines) * 0.3:
            return "code"

    if PATTERNS["code"].search(text):
        return "code"

    return "text"


def categorize(text: str) -> str:
    """テキストをカテゴリ分類。"""
    return categorize_text_rule_based(text)


def get_category_icon(category: str) -> str:
    """カテゴリに対応するアイコン文字を取得。"""
    icons = {
        "url": "🔗",
        "email": "📧",
        "code": "💻",
        "phone": "📞",
        "filepath": "📁",
        "image": "🖼️",
        "text": "📝",
    }
    return icons.get(category, "📄")


def get_category_display_name(category: str) -> str:
    """カテゴリの表示名を取得。"""
    names = {
        "url": "URL",
        "email": "メールアドレス",
        "code": "コード",
        "phone": "電話番号",
        "filepath": "ファイルパス",
        "image": "画像",
        "text": "テキスト",
    }
    return names.get(category, category)
