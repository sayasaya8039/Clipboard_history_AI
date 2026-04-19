"""UI で使うアイコン文字とフォントの共通定義。"""
from __future__ import annotations

from functools import lru_cache

from PyQt6.QtGui import QFont, QFontDatabase

_FLUENT_FAMILY = "Segoe Fluent Icons"
_LEGACY_FAMILY = "Segoe UI Symbol"

_FLUENT_GLYPHS = {
    "add": "\uE710",
    "clock": "\uE917",
    "code": "\uE943",
    "copy": "\uE8C8",
    "delete": "\uE74D",
    "document": "\uE8A5",
    "edit": "\uE70F",
    "favorite": "\uE734",
    "favorite_fill": "\uE735",
    "history": "\uE81C",
    "image": "\uE8B9",
    "link": "\uE71B",
    "list": "\uEA37",
    "mail": "\uE715",
    "page": "\uE7C3",
    "paste": "\uE77F",
    "pin": "\uE718",
    "pinned": "\uE840",
    "picture": "\uE8B9",
    "phone": "\uE717",
    "search": "\uE721",
    "settings": "\uE713",
    "unpin": "\uE77A",
}

_LEGACY_GLYPHS = {
    "add": "＋",
    "clock": "◷",
    "code": "<>",
    "copy": "⧉",
    "delete": "⌦",
    "document": "▣",
    "edit": "✎",
    "favorite": "☆",
    "favorite_fill": "★",
    "history": "◷",
    "image": "▣",
    "link": "🔗",
    "list": "▣",
    "mail": "✉",
    "page": "▣",
    "paste": "📋",
    "pin": "⌖",
    "pinned": "⌖",
    "picture": "▣",
    "phone": "☎",
    "search": "⌕",
    "settings": "⚙",
    "unpin": "⌖",
}


@lru_cache(maxsize=1)
def _use_fluent_icons() -> bool:
    try:
        return _FLUENT_FAMILY in QFontDatabase.families()
    except Exception:
        return False


def icon_glyph(name: str, fallback: str = "") -> str:
    """アイコン名に対応する文字を返す。"""
    if _use_fluent_icons():
        return _FLUENT_GLYPHS.get(name, fallback)
    return _LEGACY_GLYPHS.get(name, fallback)


def icon_font(size: int = 11, weight: QFont.Weight = QFont.Weight.Normal) -> QFont:
    """アイコン用フォントを返す。"""
    family = _FLUENT_FAMILY if _use_fluent_icons() else _LEGACY_FAMILY
    font = QFont(family, size)
    font.setWeight(weight)
    return font
