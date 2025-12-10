"""データベース操作モジュール"""
import sqlite3
from datetime import datetime
from typing import Optional
from pathlib import Path

from config import DATABASE_PATH


def get_connection() -> sqlite3.Connection:
    """データベース接続を取得"""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_database() -> None:
    """データベースを初期化"""
    conn = get_connection()
    cursor = conn.cursor()

    # 履歴テーブル
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS clipboard_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content_type TEXT NOT NULL,
            content TEXT,
            image_path TEXT,
            content_hash TEXT NOT NULL UNIQUE,
            category TEXT NOT NULL,
            is_favorite BOOLEAN DEFAULT FALSE,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # インデックス作成
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_category ON clipboard_history(category)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_created_at ON clipboard_history(created_at)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_content_hash ON clipboard_history(content_hash)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_is_favorite ON clipboard_history(is_favorite)")

    # 設定テーブル
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    """)

    conn.commit()
    conn.close()


def add_history(
    content_type: str,
    content_hash: str,
    category: str,
    content: Optional[str] = None,
    image_path: Optional[str] = None,
) -> Optional[int]:
    """履歴を追加（重複時はNoneを返す）"""
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            INSERT INTO clipboard_history (content_type, content, image_path, content_hash, category)
            VALUES (?, ?, ?, ?, ?)
            """,
            (content_type, content, image_path, content_hash, category),
        )
        conn.commit()
        return cursor.lastrowid
    except sqlite3.IntegrityError:
        # 重複エントリ（content_hashがUNIQUE制約に違反）
        return None
    finally:
        conn.close()


def get_history(
    limit: int = 100,
    offset: int = 0,
    category: Optional[str] = None,
    search_query: Optional[str] = None,
    favorites_only: bool = False,
) -> list[dict]:
    """履歴を取得"""
    conn = get_connection()
    cursor = conn.cursor()

    query = "SELECT * FROM clipboard_history WHERE 1=1"
    params = []

    if category:
        query += " AND category = ?"
        params.append(category)

    if search_query:
        query += " AND content LIKE ?"
        params.append(f"%{search_query}%")

    if favorites_only:
        query += " AND is_favorite = TRUE"

    query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
    params.extend([limit, offset])

    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()

    return [dict(row) for row in rows]


def get_history_by_id(history_id: int) -> Optional[dict]:
    """IDで履歴を取得"""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM clipboard_history WHERE id = ?", (history_id,))
    row = cursor.fetchone()
    conn.close()

    return dict(row) if row else None


def delete_history(history_id: int) -> bool:
    """履歴を削除"""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM clipboard_history WHERE id = ?", (history_id,))
    affected = cursor.rowcount
    conn.commit()
    conn.close()

    return affected > 0


def toggle_favorite(history_id: int) -> bool:
    """お気に入り状態をトグル"""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE clipboard_history SET is_favorite = NOT is_favorite WHERE id = ?",
        (history_id,),
    )
    affected = cursor.rowcount
    conn.commit()
    conn.close()

    return affected > 0


def clear_all_history() -> int:
    """全履歴を削除（お気に入り以外）"""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM clipboard_history WHERE is_favorite = FALSE")
    affected = cursor.rowcount
    conn.commit()
    conn.close()

    return affected


def get_setting(key: str, default: Optional[str] = None) -> Optional[str]:
    """設定値を取得"""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT value FROM settings WHERE key = ?", (key,))
    row = cursor.fetchone()
    conn.close()

    return row["value"] if row else default


def set_setting(key: str, value: str) -> None:
    """設定値を保存"""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)",
        (key, value),
    )
    conn.commit()
    conn.close()


def get_category_counts() -> dict[str, int]:
    """カテゴリごとの件数を取得"""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT category, COUNT(*) as count FROM clipboard_history GROUP BY category"
    )
    rows = cursor.fetchall()
    conn.close()

    return {row["category"]: row["count"] for row in rows}


def check_hash_exists(content_hash: str) -> bool:
    """ハッシュが既に存在するか確認"""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT 1 FROM clipboard_history WHERE content_hash = ?",
        (content_hash,),
    )
    exists = cursor.fetchone() is not None
    conn.close()

    return exists
