#!/usr/bin/env python3
"""Small release gate for checking a copied Skill package."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


PACKAGE = Path(__file__).resolve().parents[1]


def run(args: list[str]) -> None:
    result = subprocess.run(args, cwd=PACKAGE, text=True, capture_output=True)
    if result.returncode != 0:
        sys.stderr.write(result.stdout)
        sys.stderr.write(result.stderr)
        raise SystemExit(result.returncode)


def main() -> int:
    required = [
        PACKAGE / "SKILL.md",
        PACKAGE / "agents/openai.yaml",
        PACKAGE / "scripts/资料搜索.py",
        PACKAGE / "scripts/证据规范化.py",
        PACKAGE / "vendor/last30days-runtime/scripts/last30days.py",
        PACKAGE / "vendor/LICENSE",
    ]
    missing = [str(path.relative_to(PACKAGE)) for path in required if not path.is_file()]
    if missing:
        print(json.dumps({"status": "missing", "files": missing}, ensure_ascii=False))
        return 2

    run([sys.executable, str(PACKAGE / "scripts/资料搜索.py"), "1688 电商痛点",
         "--task", "pain_points", "--region", "domestic", "--dry-run"])
    run([sys.executable, str(PACKAGE / "scripts/证据规范化.py"), "--help"])
    print(json.dumps({"status": "ok", "package": str(PACKAGE)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
