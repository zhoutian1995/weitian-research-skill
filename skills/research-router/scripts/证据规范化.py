#!/usr/bin/env python3
"""Normalize platform search rows into a shared, auditable evidence shape.

This tool does not fetch pages. It converts rows collected by Ego Lite or an
upstream engine into stable fields while preserving incomplete-record status.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


WORK_ROOT = Path(os.environ.get("资料搜索运行目录", "/Volumes/1TB-SSD/WilleSpace-Work/scratch/资料搜索")).expanduser()


def ensure_external_storage() -> None:
    if not Path("/Volumes/1TB-SSD/WilleSpace-Work").is_dir() or not Path("/Volumes/1TB-SSD/.wille-work-storage").exists():
        raise SystemExit("外接 SSD 不可用，不向内置盘回退。")


def first(row: dict[str, Any], *keys: str) -> Any:
    for key in keys:
        value = row.get(key)
        if value not in (None, "", [], {}):
            return value
    return None


def normalize_status(row: dict[str, Any]) -> str:
    raw = str(first(row, "status", "抓取状态", "状态") or "ok").lower()
    if raw == "auth_check_required":
        return raw
    if "explicit_auth" in raw or "明确授权" in raw:
        return "requires_explicit_auth"
    if any(token in raw for token in ("login", "登录", "auth", "授权")):
        return "requires_login"
    if any(token in raw for token in ("rate", "限流", "captcha", "验证", "blocked", "受限")):
        return "rate-limited"
    if any(token in raw for token in ("no-results", "无结果")):
        return "no-results"
    if any(token in raw for token in ("error", "失败", "unreachable", "不可达")):
        return "unreachable"
    return raw if raw in {"ok", "partial"} else "partial"


def normalize_row(row: dict[str, Any], default_platform: str | None = None) -> dict[str, Any]:
    platform = first(row, "platform", "平台", "source") or default_platform
    title = first(row, "title", "标题", "name")
    url = first(row, "url", "链接", "link")
    record = {
        "platform": platform,
        "title": title,
        "author": first(row, "author", "作者", "uploader", "账号", "account"),
        "published_at": first(row, "published_at", "发布时间", "日期", "date"),
        "engagement": first(row, "engagement", "互动量", "metrics", "stats"),
        "url": url,
        "evidence_type": first(row, "evidence_type", "证据类型") or "discovery",
        "status": normalize_status(row),
        "retrieved_at": first(row, "retrieved_at", "采集时间", "captured_at") or datetime.now(timezone.utc).isoformat(),
    }
    # Preserve observed provenance without promoting discovery dates to article dates.
    for key in ("visible_text", "published_at_raw", "published_at_source",
                "published_date_from_search", "original_url", "final_url",
                "canonical_url", "url_status", "body_status", "limitations",
                "discovery", "query", "search_elapsed_ms"):
        if key in row:
            record[key] = row[key]
    if not platform or not title or not url:
        record["status"] = "partial" if record["status"] == "ok" else record["status"]
        record["missing_fields"] = [key for key, value in (("platform", platform), ("title", title), ("url", url)) if not value]
    source_key = f"{platform or ''}|{url or ''}|{title or ''}"
    record["source_key"] = hashlib.sha256(source_key.encode("utf-8")).hexdigest()[:16]
    return record


def load_rows(path: Path) -> list[dict[str, Any]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(payload, list):
        return [row for row in payload if isinstance(row, dict)]
    for key in ("items", "results", "evidence", "rows"):
        value = payload.get(key) if isinstance(payload, dict) else None
        if isinstance(value, list):
            return [row for row in value if isinstance(row, dict)]
    if isinstance(payload, dict) and first(payload, "title", "标题", "name") and first(payload, "url", "链接", "link"):
        return [payload]
    raise SystemExit("输入JSON需要证据数组、items/results/evidence/rows 数组或包含标题和链接的单条记录。")


def main() -> int:
    parser = argparse.ArgumentParser(description="规范化多平台搜索证据记录")
    parser.add_argument("input", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--platform", help="输入行未提供平台时使用的默认平台")
    args = parser.parse_args()
    ensure_external_storage()
    rows = [normalize_row(row, args.platform) for row in load_rows(args.input)]
    output = args.output or WORK_ROOT / f"证据规范化-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    envelope = {
        "schema_version": "research-evidence/v1",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "source_file": str(args.input.resolve()),
        "read_only": True,
        "items": rows,
        "stats": {"total": len(rows), "complete": sum(not row.get("missing_fields") for row in rows), "by_status": {status: sum(row["status"] == status for row in rows) for status in sorted({row["status"] for row in rows})}},
    }
    output.write_text(json.dumps(envelope, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(output), "stats": envelope["stats"]}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
