"""履歴 / 定型文の CSV 出力・取込サービス。"""
from __future__ import annotations

import csv
import hashlib
from dataclasses import dataclass
from pathlib import Path

from database import (
    add_history,
    clear_all_snippets,
    create_snippet,
    find_snippet_by_name_and_content,
    get_all_history,
    history_entry_exists,
    list_snippets,
    update_snippet,
)

_HISTORY_HEADERS = [
    "content_type",
    "content",
    "image_path",
    "category",
    "app",
    "is_favorite",
    "created_at",
]
_SNIPPET_HEADERS = [
    "name",
    "content",
    "description",
    "tags",
    "favorite",
    "created_at",
]


@dataclass(frozen=True)
class ImportResult:
    added_count: int = 0
    updated_count: int = 0
    skipped_count: int = 0
    cleared_count: int = 0


def export_history_csv(path: str | Path, encoding: str = "utf-8") -> int:
    """履歴を CSV に出力する。"""
    rows = get_all_history()
    destination = Path(path)
    with destination.open("w", encoding=encoding, newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=_HISTORY_HEADERS)
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {
                    "content_type": row.get("content_type") or "",
                    "content": row.get("content") or "",
                    "image_path": row.get("image_path") or "",
                    "category": row.get("category") or "",
                    "app": row.get("app") or "",
                    "is_favorite": "1" if row.get("is_favorite") else "0",
                    "created_at": row.get("created_at") or "",
                }
            )
    return len(rows)


def import_history_csv(path: str | Path, encoding: str = "utf-8") -> ImportResult:
    """履歴 CSV を取り込む。"""
    source = Path(path)
    added_count = 0
    skipped_count = 0
    with source.open("r", encoding=encoding, newline="") as handle:
        reader = csv.DictReader(handle)
        _validate_headers(reader.fieldnames, _HISTORY_HEADERS)
        for row in reader:
            normalized = {key: (row.get(key) or "").strip() for key in _HISTORY_HEADERS}
            if not normalized["content_type"] or not normalized["category"]:
                skipped_count += 1
                continue

            if history_entry_exists(
                normalized["content_type"],
                normalized["content"],
                normalized["image_path"],
                normalized["category"],
                normalized["app"] or None,
            ):
                skipped_count += 1
                continue

            content_hash = _history_import_hash(
                normalized["content_type"],
                normalized["content"],
                normalized["image_path"],
                normalized["category"],
                normalized["app"],
            )
            history_id = add_history(
                content_type=normalized["content_type"],
                content=normalized["content"] or None,
                image_path=normalized["image_path"] or None,
                content_hash=content_hash,
                category=normalized["category"],
                app=normalized["app"] or None,
                is_favorite=_is_truthy_csv(normalized["is_favorite"]),
                created_at=normalized["created_at"] or None,
            )
            if history_id is None:
                skipped_count += 1
                continue
            added_count += 1
    return ImportResult(added_count=added_count, skipped_count=skipped_count)


def export_snippets_csv(path: str | Path, encoding: str = "utf-8") -> int:
    """定型文を CSV に出力する。"""
    rows = list_snippets()
    destination = Path(path)
    with destination.open("w", encoding=encoding, newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=_SNIPPET_HEADERS)
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {
                    "name": row.get("name") or "",
                    "content": row.get("content") or "",
                    "description": row.get("description") or "",
                    "tags": ",".join(row.get("tags") or []),
                    "favorite": "1" if row.get("favorite") else "0",
                    "created_at": row.get("created_at") or "",
                }
            )
    return len(rows)


def import_snippets_csv(
    path: str | Path,
    encoding: str = "utf-8",
    clear_existing: bool = False,
) -> ImportResult:
    """定型文 CSV を取り込む。"""
    source = Path(path)
    added_count = 0
    updated_count = 0
    skipped_count = 0
    cleared_count = clear_all_snippets() if clear_existing else 0
    with source.open("r", encoding=encoding, newline="") as handle:
        reader = csv.DictReader(handle)
        _validate_headers(reader.fieldnames, _SNIPPET_HEADERS)
        for row in reader:
            normalized = {key: (row.get(key) or "").strip() for key in _SNIPPET_HEADERS}
            if not normalized["name"] or not normalized["content"]:
                skipped_count += 1
                continue

            tags = [tag.strip() for tag in normalized["tags"].split(",") if tag.strip()]
            existing = find_snippet_by_name_and_content(normalized["name"], normalized["content"])
            if existing is None:
                create_snippet(
                    name=normalized["name"],
                    content=normalized["content"],
                    description=normalized["description"] or None,
                    tags=tags,
                    favorite=_is_truthy_csv(normalized["favorite"]),
                    created_at=normalized["created_at"] or None,
                )
                added_count += 1
                continue

            updated = update_snippet(
                int(existing["id"]),
                name=normalized["name"],
                content=normalized["content"],
                description=normalized["description"] or None,
                tags=tags,
                favorite=_is_truthy_csv(normalized["favorite"]),
                created_at=normalized["created_at"] or None,
            )
            if updated:
                updated_count += 1
            else:
                skipped_count += 1
    return ImportResult(
        added_count=added_count,
        updated_count=updated_count,
        skipped_count=skipped_count,
        cleared_count=cleared_count,
    )


def _validate_headers(fieldnames: list[str] | None, required_headers: list[str]) -> None:
    normalized = fieldnames or []
    missing = [header for header in required_headers if header not in normalized]
    if missing:
        raise ValueError(f"CSV に必須列がありません: {', '.join(missing)}")


def _history_import_hash(
    content_type: str,
    content: str,
    image_path: str,
    category: str,
    app: str,
) -> str:
    payload = "\x1f".join([content_type, content, image_path, category, app])
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _is_truthy_csv(value: str) -> bool:
    return str(value or "").strip().lower() in {"1", "true", "yes", "on"}
