"""データベース操作モジュール"""
import sqlite3
from typing import Optional
from pathlib import Path

from config import DATABASE_PATH

_LEGACY_SETTING_KEYS = ("ai_provider", "openai_api_key", "gemini_api_key")


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
    _ensure_column(cursor, "clipboard_history", "app", "TEXT")

    # インデックス作成
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_category ON clipboard_history(category)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_created_at ON clipboard_history(created_at)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_content_hash ON clipboard_history(content_hash)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_is_favorite ON clipboard_history(is_favorite)")

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS snippets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            content TEXT NOT NULL,
            description TEXT,
            tags TEXT NOT NULL DEFAULT '',
            favorite BOOLEAN DEFAULT FALSE,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_snippets_created_at ON snippets(created_at)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_snippets_name_content ON snippets(name, content)")

    # 設定テーブル
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    """)
    # 使われなくなった AI 関連設定は起動時に掃除する。
    cursor.executemany(
        "DELETE FROM settings WHERE key = ?",
        [(key,) for key in _LEGACY_SETTING_KEYS],
    )

    conn.commit()
    conn.close()


def _ensure_column(cursor: sqlite3.Cursor, table: str, column: str, column_type: str) -> None:
    """テーブルに列がなければ追加する。"""
    cursor.execute(f"PRAGMA table_info({table})")
    columns = {row[1] for row in cursor.fetchall()}
    if column not in columns:
        cursor.execute(f"ALTER TABLE {table} ADD COLUMN {column} {column_type}")


def add_history(
    content_type: str,
    content_hash: str,
    category: str,
    content: Optional[str] = None,
    image_path: Optional[str] = None,
    app: Optional[str] = None,
    is_favorite: bool = False,
    created_at: Optional[str] = None,
) -> Optional[int]:
    """履歴を追加（重複時はNoneを返す）"""
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            """
            INSERT INTO clipboard_history (
                content_type,
                content,
                image_path,
                content_hash,
                category,
                app,
                is_favorite,
                created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, COALESCE(?, CURRENT_TIMESTAMP))
            """,
            (
                content_type,
                content,
                image_path,
                content_hash,
                category,
                app,
                bool(is_favorite),
                created_at,
            ),
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


def get_all_history() -> list[dict]:
    """全履歴を取得"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM clipboard_history ORDER BY created_at DESC")
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

    cursor.execute("SELECT image_path FROM clipboard_history WHERE id = ?", (history_id,))
    row = cursor.fetchone()
    image_path = row["image_path"] if row else None

    cursor.execute("DELETE FROM clipboard_history WHERE id = ?", (history_id,))
    affected = cursor.rowcount
    conn.commit()
    conn.close()

    if affected > 0 and image_path:
        try:
            path = Path(image_path)
            if path.exists():
                path.unlink()
        except Exception:
            pass

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

    cursor.execute("SELECT image_path FROM clipboard_history WHERE is_favorite = FALSE AND image_path IS NOT NULL")
    image_paths = [row["image_path"] for row in cursor.fetchall()]

    cursor.execute("DELETE FROM clipboard_history WHERE is_favorite = FALSE")
    affected = cursor.rowcount
    conn.commit()
    conn.close()

    for image_path in image_paths:
        try:
            path = Path(image_path)
            if path.exists():
                path.unlink()
        except Exception:
            pass

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


def history_entry_exists(
    content_type: str,
    content: Optional[str],
    image_path: Optional[str],
    category: str,
    app: Optional[str],
) -> bool:
    """同一内容の履歴が存在するか確認する。"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT 1
        FROM clipboard_history
        WHERE content_type = ?
          AND COALESCE(content, '') = ?
          AND COALESCE(image_path, '') = ?
          AND category = ?
          AND COALESCE(app, '') = ?
        LIMIT 1
        """,
        (
            content_type,
            content or "",
            image_path or "",
            category,
            app or "",
        ),
    )
    exists = cursor.fetchone() is not None
    conn.close()
    return exists


def list_snippets() -> list[dict]:
    """定型文を取得"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM snippets ORDER BY created_at DESC")
    rows = cursor.fetchall()
    conn.close()
    return [_normalize_snippet_row(dict(row)) for row in rows]


def create_snippet(
    name: str,
    content: str,
    description: Optional[str] = None,
    tags: Optional[list[str]] = None,
    favorite: bool = False,
    created_at: Optional[str] = None,
) -> int:
    """定型文を追加"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO snippets (name, content, description, tags, favorite, created_at)
        VALUES (?, ?, ?, ?, ?, COALESCE(?, CURRENT_TIMESTAMP))
        """,
        (
            name,
            content,
            description,
            _serialize_tags(tags),
            bool(favorite),
            created_at,
        ),
    )
    conn.commit()
    snippet_id = cursor.lastrowid
    conn.close()
    return snippet_id


def update_snippet(
    snippet_id: int,
    name: str,
    content: str,
    description: Optional[str] = None,
    tags: Optional[list[str]] = None,
    favorite: bool = False,
    created_at: Optional[str] = None,
) -> bool:
    """定型文を更新"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        UPDATE snippets
        SET name = ?,
            content = ?,
            description = ?,
            tags = ?,
            favorite = ?,
            created_at = COALESCE(?, created_at)
        WHERE id = ?
        """,
        (
            name,
            content,
            description,
            _serialize_tags(tags),
            bool(favorite),
            created_at,
            snippet_id,
        ),
    )
    affected = cursor.rowcount
    conn.commit()
    conn.close()
    return affected > 0


def delete_snippet(snippet_id: int) -> bool:
    """定型文を削除"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM snippets WHERE id = ?", (snippet_id,))
    affected = cursor.rowcount
    conn.commit()
    conn.close()
    return affected > 0


def toggle_snippet_favorite(snippet_id: int) -> bool:
    """定型文のお気に入り状態をトグル"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE snippets SET favorite = NOT favorite WHERE id = ?",
        (snippet_id,),
    )
    affected = cursor.rowcount
    conn.commit()
    conn.close()
    return affected > 0


def find_snippet_by_name_and_content(name: str, content: str) -> Optional[dict]:
    """名前と内容で定型文を検索"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM snippets WHERE name = ? AND content = ? LIMIT 1",
        (name, content),
    )
    row = cursor.fetchone()
    conn.close()
    return _normalize_snippet_row(dict(row)) if row else None


def _serialize_tags(tags: Optional[list[str]]) -> str:
    return ",".join(tag.strip() for tag in tags or [] if str(tag).strip())


def _deserialize_tags(value: Optional[str]) -> list[str]:
    if not value:
        return []
    return [tag.strip() for tag in str(value).split(",") if tag.strip()]


def _normalize_snippet_row(row: dict) -> dict:
    row["favorite"] = bool(row.get("favorite"))
    row["tags"] = _deserialize_tags(row.get("tags"))
    return row
