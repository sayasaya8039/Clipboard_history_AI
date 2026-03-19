"""Figma 風 UI 向けのサンプルデータと表示用ヘルパー"""
from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any


def normalize_preview(text: str, limit: int = 96) -> str:
    """1 行プレビュー用に空白と改行を整形する。"""
    collapsed = " ".join(text.strip().split())
    if len(collapsed) <= limit:
        return collapsed
    return collapsed[: max(0, limit - 1)].rstrip() + "…"


def format_relative_time(value: datetime | str) -> str:
    """Figma 風の相対時刻表記を返す。"""
    dt = parse_datetime(value)
    if dt is None:
        return ""

    diff = datetime.now() - dt
    minutes = max(0, int(diff.total_seconds() // 60))
    hours = minutes // 60
    days = minutes // (60 * 24)

    if minutes < 1:
        return "今"
    if minutes < 60:
        return f"{minutes}分前"
    if hours < 24:
        return f"{hours}時間前"
    return f"{days}日前"


def format_japanese_datetime(value: datetime | str) -> str:
    """フッター向けの日本語日時表記を返す。"""
    dt = parse_datetime(value)
    if dt is None:
        return ""

    return f"{dt.year}年{dt.month}月{dt.day}日 {dt:%H:%M:%S}"


def parse_datetime(value: datetime | str | None) -> datetime | None:
    """DB 文字列または datetime を datetime に変換する。"""
    if value is None:
        return None
    if isinstance(value, datetime):
        return value

    text = str(value).strip()
    if not text:
        return None

    try:
        return datetime.fromisoformat(text)
    except ValueError:
        pass

    for fmt in (
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d %H:%M",
        "%Y/%m/%d %H:%M:%S",
        "%Y/%m/%d %H:%M",
    ):
        try:
            return datetime.strptime(text, fmt)
        except ValueError:
            continue

    return None


def build_history_samples(reference: datetime | None = None) -> list[dict[str, Any]]:
    """Figma Make の履歴サンプルを生成する。"""
    now = reference or datetime.now()

    def ago(minutes: int) -> datetime:
        return now - timedelta(minutes=minutes)

    samples = [
        {
            "id": "sample-history-1",
            "content_type": "text",
            "type": "text",
            "content": "CopyQはクリップボード管理ツールです。テキスト、画像、その他のデータをコピーすると、自動的に履歴に保存されます。",
            "app": "Safari",
            "category": "text",
            "is_favorite": False,
            "created_at": ago(5),
        },
        {
            "id": "sample-history-2",
            "content_type": "code",
            "type": "code",
            "content": "function fibonacci(n) {\n  if (n <= 1) return n;\n  return fibonacci(n - 1) + fibonacci(n - 2);\n}\n\nconsole.log(fibonacci(10));",
            "app": "VS Code",
            "category": "code",
            "is_favorite": False,
            "created_at": ago(15),
        },
        {
            "id": "sample-history-3",
            "content_type": "text",
            "type": "text",
            "content": "hello@example.com",
            "app": "Mail",
            "category": "email",
            "is_favorite": False,
            "created_at": ago(30),
        },
        {
            "id": "sample-history-4",
            "content_type": "html",
            "type": "html",
            "content": "<div class=\"container\">\n  <h1>Hello World</h1>\n  <p>This is a sample HTML snippet</p>\n</div>",
            "app": "Chrome",
            "category": "code",
            "is_favorite": False,
            "created_at": ago(60),
        },
        {
            "id": "sample-history-5",
            "content_type": "text",
            "type": "text",
            "content": "2026年3月16日（月）",
            "app": "Calendar",
            "category": "text",
            "is_favorite": False,
            "created_at": ago(90),
        },
        {
            "id": "sample-history-6",
            "content_type": "code",
            "type": "code",
            "content": "SELECT users.name, orders.total\nFROM users\nINNER JOIN orders ON users.id = orders.user_id\nWHERE orders.total > 100\nORDER BY orders.total DESC;",
            "app": "DataGrip",
            "category": "code",
            "is_favorite": False,
            "created_at": ago(120),
        },
        {
            "id": "sample-history-7",
            "content_type": "text",
            "type": "text",
            "content": "https://www.example.com/article/how-to-use-clipboard-manager",
            "app": "Safari",
            "category": "url",
            "is_favorite": False,
            "created_at": ago(180),
        },
        {
            "id": "sample-history-8",
            "content_type": "code",
            "type": "code",
            "content": "import React from 'react';\n\nexport const Button = ({ children, onClick }) => {\n  return (\n    <button onClick={onClick} className=\"btn\">\n      {children}\n    </button>\n  );\n};",
            "app": "VS Code",
            "category": "code",
            "is_favorite": False,
            "created_at": ago(240),
        },
    ]

    for sample in samples:
        sample["preview"] = normalize_preview(str(sample["content"]))

    return samples


def build_snippet_samples(reference: datetime | None = None) -> list[dict[str, Any]]:
    """Figma Make の定型文サンプルを生成する。"""
    now = reference or datetime.now()

    def ago(days: int) -> datetime:
        return now - timedelta(days=days)

    samples = [
        {
            "id": "sample-snippet-1",
            "name": "メールの署名",
            "content": "よろしくお願いいたします。\n\n山田太郎\n〇〇株式会社 開発部\nEmail: yamada@example.com\nTel: 03-1234-5678",
            "description": "ビジネスメールの署名",
            "tags": ["メール", "仕事"],
            "favorite": True,
            "created_at": ago(7),
        },
        {
            "id": "sample-snippet-2",
            "name": "React コンポーネントテンプレート",
            "content": "import React from 'react';\n\ninterface Props {\n  // プロパティをここに定義\n}\n\nexport const ComponentName: React.FC<Props> = (props) => {\n  return (\n    <div>\n      {/* コンテンツ */}\n    </div>\n  );\n};",
            "description": "React関数コンポーネントの基本テンプレート",
            "tags": ["React", "コード", "テンプレート"],
            "favorite": True,
            "created_at": ago(5),
        },
        {
            "id": "sample-snippet-3",
            "name": "会議の議事録フォーマット",
            "content": "## 会議議事録\n\n**日時**: \n**参加者**: \n**議題**: \n\n### 決定事項\n- \n\n### 課題・TODO\n- \n\n### 次回予定\n- ",
            "description": "会議の議事録用フォーマット",
            "tags": ["会議", "ドキュメント"],
            "favorite": False,
            "created_at": ago(3),
        },
        {
            "id": "sample-snippet-4",
            "name": "住所",
            "content": "〒100-0001 東京都千代田区千代田1-1-1",
            "description": "会社の住所",
            "tags": ["住所", "仕事"],
            "favorite": False,
            "created_at": ago(10),
        },
        {
            "id": "sample-snippet-5",
            "name": "Git コミットメッセージテンプレート",
            "content": "feat: 新機能の追加\n\n- 変更内容の詳細1\n- 変更内容の詳細2\n\n関連Issue: #",
            "description": "Gitコミットメッセージの標準フォーマット",
            "tags": ["Git", "開発"],
            "favorite": False,
            "created_at": ago(2),
        },
    ]

    for sample in samples:
        sample["preview"] = normalize_preview(str(sample["content"]))

    return samples
