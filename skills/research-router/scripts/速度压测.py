#!/usr/bin/env python3
"""Run a small latency smoke test for the project-local research router.

The default mode measures routing only (no platform writes and no network
search). ``--run`` additionally invokes the upstream engine for cases that
have public engine sources. Results are written to the external SSD scratch
area so a benchmark never pollutes the source checkout.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path


SKILL_DIR = Path(__file__).resolve().parents[1]
ROOT = SKILL_DIR
ROUTER = SKILL_DIR / "scripts" / "资料搜索.py"
WORK_ROOT = Path(os.environ.get(
    "资料搜索运行目录",
    "/Volumes/1TB-SSD/WilleSpace-Work/scratch/资料搜索",
)).expanduser()


def ensure_external_storage() -> None:
    required_root = Path("/Volumes/1TB-SSD/WilleSpace-Work")
    sentinel = Path("/Volumes/1TB-SSD/.wille-work-storage")
    if not required_root.is_dir() or not sentinel.exists():
        raise SystemExit(
            "外接 SSD 不可用：请确认 /Volumes/1TB-SSD 已挂载且存在 .wille-work-storage；"
            "不会回退到 Mac 内置盘。"
        )


def run_case(topic: str, task: str, region: str, speed: str, execute: bool) -> dict:
    command = [
        sys.executable,
        str(ROUTER),
        topic,
        "--task",
        task,
        "--region",
        region,
        "--speed",
        speed,
    ]
    if execute:
        command.append("--run")
    started = time.perf_counter()
    completed = subprocess.run(
        command,
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    elapsed = round(time.perf_counter() - started, 3)
    stdout = completed.stdout.strip()
    manifest = None
    # The router prints a JSON manifest before any upstream engine output.
    try:
        manifest = json.loads(stdout)
    except json.JSONDecodeError:
        pass
    return {
        "topic": topic,
        "task": task,
        "region": region,
        "speed": speed,
        "executed": execute,
        "elapsed_seconds": elapsed,
        "return_code": completed.returncode,
        "engine_sources": manifest.get("engine_sources", []) if manifest else [],
        "browser_spaces": manifest.get("browser_spaces", []) if manifest else [],
        "status": "ok" if completed.returncode == 0 else "error",
        "stdout_tail": stdout[-1200:],
        "stderr_tail": completed.stderr.strip()[-1200:],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="资料搜索路由速度压测")
    parser.add_argument("topic", nargs="?", default="1688 电商痛点")
    parser.add_argument("--task", default="pain_points")
    parser.add_argument("--region", default="domestic")
    parser.add_argument(
        "--speeds",
        nargs="+",
        choices=["fast", "balanced", "deep"],
        default=["fast"],
        help="要压测的延迟档位，默认只测 fast",
    )
    parser.add_argument(
        "--run",
        action="store_true",
        help="调用上游公开搜索引擎；默认只压测路由，不联网搜索",
    )
    args = parser.parse_args()

    ensure_external_storage()
    WORK_ROOT.mkdir(parents=True, exist_ok=True)
    started_at = datetime.now(timezone.utc)
    cases = [
        run_case(args.topic, args.task, args.region, speed, args.run)
        for speed in args.speeds
    ]
    report = {
        "schema_version": "research-benchmark/v1",
        "created_at": started_at.isoformat(),
        "router": str(ROUTER),
        "read_only": True,
        "network_search": args.run,
        "cases": cases,
    }
    output = WORK_ROOT / f"速度压测-{started_at.strftime('%Y%m%dT%H%M%SZ')}.json"
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(output), "cases": cases}, ensure_ascii=False, indent=2))
    return 0 if all(case["status"] == "ok" for case in cases) else 1


if __name__ == "__main__":
    raise SystemExit(main())
