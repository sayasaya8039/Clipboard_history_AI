"""カテゴリ分類モジュール"""
import re
from typing import Optional
from pathlib import Path
from urllib.parse import unquote

from database import get_setting
from ai_client import categorize_with_ai


# 画像ファイルの拡張子
IMAGE_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp', '.ico', '.tiff', '.tif'}


# カテゴリ判定用の正規表現パターン
PATTERNS = {
    # URL: http://, https://, file:// または ドメイン形式
    "url": re.compile(
        r"^(?:https?://|file:///|ftp://)[^\s]+$|"  # プロトコル付き
        r"^(?:www\.)?[a-zA-Z0-9][-a-zA-Z0-9]*\.[a-zA-Z]{2,}(?:/[^\s]*)?$",  # ドメイン形式
        re.IGNORECASE,
    ),
    "email": re.compile(
        r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$",
        re.IGNORECASE,
    ),
    "phone": re.compile(
        r"^[\d\-\(\)\+\s]{10,}$",
    ),
    # ファイルパス: Windows形式、Unix形式
    "filepath": re.compile(
        r"^(?:[a-zA-Z]:\\|/(?:home|usr|var|etc|opt|tmp|mnt|media)|~/)[\w\\/\-\.\s]+$",
    ),
    "code": re.compile(
        r"(?:"
        r"^\s*(def|class|function|const|let|var|import|from|export|public|private|protected)\s+"  # キーワード
        r"|[{}\[\]];$"  # ブレース・ブラケット
        r"|^\s*[#//]"  # コメント
        r"|=>\s*[{(]"  # アロー関数
        r"|^\s*@\w+"  # デコレータ
        r"|<[a-zA-Z][^>]*/?>"  # HTMLタグ
        r")",
        re.MULTILINE,
    ),
}


def is_image_file(path_or_url: str) -> bool:
    """画像ファイルかどうかを判定"""
    try:
        # file:/// 形式の場合
        if path_or_url.startswith("file:///"):
            # URLデコードしてパスを取得
            path = unquote(path_or_url[8:])  # "file:///" を除去
            ext = Path(path).suffix.lower()
            return ext in IMAGE_EXTENSIONS

        # 通常のファイルパスの場合
        ext = Path(path_or_url).suffix.lower()
        return ext in IMAGE_EXTENSIONS
    except Exception:
        return False


def extract_file_path(text: str) -> Optional[str]:
    """file:///形式のURLからファイルパスを抽出"""
    if text.startswith("file:///"):
        # URLデコードしてパスを取得
        path = unquote(text[8:])  # "file:///" を除去
        return path
    return None


def categorize_text_rule_based(text: str) -> str:
    """ルールベースでテキストをカテゴリ分類"""
    text = text.strip()

    # 空文字チェック
    if not text:
        return "text"

    # 画像ファイルパス判定（file:/// または ローカルパス）
    if is_image_file(text):
        return "image"

    # URL判定
    if PATTERNS["url"].match(text):
        return "url"

    # メールアドレス判定
    if PATTERNS["email"].match(text):
        return "email"

    # 電話番号判定（数字とハイフンのみで構成）
    if PATTERNS["phone"].match(text) and text.replace("-", "").replace(" ", "").replace("(", "").replace(")", "").replace("+", "").isdigit():
        return "phone"

    # ファイルパス判定
    if PATTERNS["filepath"].match(text):
        return "filepath"

    # コード判定（複数行または特定パターンを含む）
    lines = text.split("\n")
    if len(lines) > 1:
        # 複数行でインデントがある場合
        indented_lines = sum(1 for line in lines if line.startswith(("  ", "\t")))
        if indented_lines >= len(lines) * 0.3:
            return "code"

    # コードパターンに一致
    if PATTERNS["code"].search(text):
        return "code"

    return "text"


def categorize(
    text: str,
    use_ai: bool = False,
) -> str:
    """テキストをカテゴリ分類"""
    # まずルールベースで判定
    rule_category = categorize_text_rule_based(text)

    # AI分類が有効でない場合、またはルールで明確に判定できた場合
    ai_provider = get_setting("ai_provider", "none")
    if not use_ai or ai_provider == "none":
        return rule_category

    # ルールベースで「text」と判定された場合のみAIを使用
    if rule_category == "text":
        ai_category = categorize_with_ai(text)
        if ai_category:
            return ai_category

    return rule_category


def get_category_icon(category: str) -> str:
    """カテゴリに対応するアイコン文字を取得"""
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
    """カテゴリの表示名を取得"""
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
