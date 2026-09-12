#!/usr/bin/env python3
"""Project-local router for multi-platform research.

The browser-only domestic sources are emitted as a manifest. The upstream
last30days engine is invoked only for its explicit overseas/technical sources.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


SKILL_DIR = Path(__file__).resolve().parents[1]
ROOT = SKILL_DIR
ENGINE = SKILL_DIR / "vendor" / "last30days-runtime" / "scripts" / "last30days.py"
# Research output is high-churn data. Keep it on the external SSD instead of
# the source checkout or the Mac's internal disk.
RUNS = Path(os.environ.get(
    "资料搜索运行目录",
    "/Volumes/1TB-SSD/WilleSpace-Work/scratch/资料搜索",
)).expanduser()

PROFILES = {
    "domestic_ecommerce": {
        "browser_spaces": ["douyin", "bilibili", "xiaohongshu_manual", "wechat_public"],
        "engine_sources": [],
        "forbidden_defaults": ["github"],
    },
    "overseas": {
        "browser_spaces": [],
        "engine_sources": ["reddit", "x", "youtube", "web"],
        "forbidden_defaults": [],
    },
    "technical": {
        "browser_spaces": [],
        "engine_sources": ["web", "github", "reddit", "youtube"],
        "forbidden_defaults": [],
    },
    "general": {
        "browser_spaces": [],
        "engine_sources": ["web"],
        "forbidden_defaults": ["github"],
    },
    "global": {
        "browser_spaces": ["douyin", "bilibili", "xiaohongshu_manual", "wechat_public"],
        "engine_sources": ["reddit", "x", "web"],
        "forbidden_defaults": ["github"],
    },
}

TASK_PROFILE = {
    ("pain_points", "domestic"): "domestic_ecommerce",
    ("pain_points", "overseas"): "overseas",
    ("trends", "overseas"): "overseas",
    ("competitor", "overseas"): "overseas",
    ("technical", "global"): "technical",
    ("technical", "overseas"): "technical",
    ("verify", "global"): "technical",
    ("video_deep_dive", "global"): "global",
}

SESSION_SPLIT = {
    "domestic_ecommerce": ["domestic_discovery", "domestic_verification"],
    "overseas": ["overseas_research"],
    "technical": ["technical_research"],
    "global": ["domestic_discovery", "overseas_research"],
    "general": ["overseas_research"],
}


def resolve_profile(profile: str | None, task: str | None, region: str) -> str:
    if profile:
        return profile
    if task:
        if region == "auto":
            region = "domestic" if any(word in task for word in ("pain", "用户", "电商")) else "global"
        return TASK_PROFILE.get((task, region), "global" if region == "global" else "general")
    return "general"


def engine_sources(profile: str, speed: str) -> list[str]:
    """Return the source set for the requested latency tier."""
    base = PROFILES[profile]["engine_sources"]
    if speed == "fast" and profile in {"overseas", "technical", "global"}:
        return [source for source in base if source != "youtube"]
    return list(base)


def ensure_external_storage() -> None:
    """Refuse durable run output when the external SSD is not mounted."""
    required_root = Path("/Volumes/1TB-SSD/WilleSpace-Work")
    sentinel = Path("/Volumes/1TB-SSD/.wille-work-storage")
    if not required_root.is_dir() or not sentinel.exists():
        raise SystemExit(
            "外接 SSD 不可用：请确认 /Volumes/1TB-SSD 已挂载且存在 .wille-work-storage；"
            "不会回退到 Mac 内置盘。"
        )


def build_manifest(topic: str, profile: str, speed: str) -> dict:
    route = PROFILES[profile]
    sources = engine_sources(profile, speed)
    status = {source: "pending" for source in route["browser_spaces"]}
    if profile in {"overseas", "technical"}:
        status.update({source: "configured_check_required" for source in sources})
        if "x" in sources and not (
            os.environ.get("X_BEARER_TOKEN") or os.environ.get("XAI_API_KEY")
        ):
            status["x"] = "requires_explicit_auth"
    return {
        "schema_version": "research-run/v1",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "topic": topic,
        "profile": profile,
        "mode": "read_only",
        "browser_spaces": route["browser_spaces"],
        "engine_sources": sources,
        "forbidden_defaults": route["forbidden_defaults"],
        "status": status,
        "session_plan": SESSION_SPLIT[profile],
        "handoff_contract": {
            "discovery_to_verification": "只传递结构化候选清单和证据文件；不传递Cookie或临时页面状态。",
            "verification_to_transcription": "只传递已选中的视频URL或本地文件路径；转写输出必须写外置SSD。",
        },
        "notes": [
            "国内登录平台由 Ego Lite 独立会话执行，需人工处理登录/验证码。",
            "本清单不保存 Cookie、访问令牌或平台写操作。",
        ],
    }


def run_engine(topic: str, profile: str, speed: str) -> int:
    selected_sources = engine_sources(profile, speed)
    sources = ",".join(selected_sources)
    if not sources:
        print("该路由只有浏览器平台，已生成 Ego Lite 任务清单；没有调用上游引擎。")
        return 0
    # The bundled last30days runtime uses Python 3.12+ (the router itself is
    # also written for modern Python). Fail before spawning it so Python 3.9
    # installations get an actionable status instead of a traceback.
    if sys.version_info < (3, 12):
        print(
            "当前海外/技术路由需要 Python 3.12+；"
            f"检测到 {sys.version_info.major}.{sys.version_info.minor}。"
            "请用 python3.12（或更新版本）重新运行。"
        )
        return 2
    intent = {
        "domestic_ecommerce": "opinion",
        "overseas": "opinion",
        "technical": "how_to",
        "global": "opinion",
        "general": "opinion",
    }[profile]
    plan = {
        "intent": intent,
        "freshness_mode": "recent",
        "cluster_mode": "story",
        "subqueries": [{
            "label": "primary",
            "search_query": topic,
            "ranking_query": f"What are people saying about {topic}?",
            "sources": selected_sources,
            "weight": 1.0,
        }],
        "source_weights": {source: 1.0 for source in selected_sources},
    }
    plan_path = RUNS / "当前查询计划.json"
    plan_path.write_text(json.dumps(plan, ensure_ascii=False, indent=2), encoding="utf-8")
    env = os.environ.copy()
    env.setdefault("LAST30DAYS_MEMORY_DIR", str(RUNS))
    # Never silently read browser cookies from this project. X authentication
    # can be enabled explicitly by the user through the upstream setup flow.
    env.setdefault("BIRD_DISABLE_BROWSER_COOKIES", "1")
    depth_flag = "--quick" if speed == "fast" else "--deep" if speed == "deep" else None
    cmd = [sys.executable, str(ENGINE), topic]
    if depth_flag:
        cmd.append(depth_flag)
    cmd += ["--emit=compact", f"--search={sources}", "--plan", str(plan_path), "--save-dir", str(RUNS)]
    return subprocess.call(cmd, cwd=ROOT, env=env)


def main() -> int:
    parser = argparse.ArgumentParser(description="按平台路由资料搜索任务")
    parser.add_argument("topic")
    parser.add_argument("--profile", choices=sorted(PROFILES), default=None)
    parser.add_argument("--task", choices=["pain_points", "trends", "competitor", "technical", "verify", "video_deep_dive"])
    parser.add_argument("--region", choices=["auto", "domestic", "overseas", "global"], default="auto")
    parser.add_argument("--speed", "--depth", dest="speed", choices=["fast", "balanced", "deep"], default="fast", help="首轮延迟档位；balanced 加入 YouTube，deep 使用高召回")
    parser.add_argument("--dry-run", action="store_true", help="只输出清单，不调用上游引擎")
    parser.add_argument("--run", action="store_true", help="运行允许的海外/技术公开来源")
    args = parser.parse_args()

    profile = resolve_profile(args.profile, args.task, args.region)
    manifest = build_manifest(args.topic, profile, args.speed)
    ensure_external_storage()
    RUNS.mkdir(parents=True, exist_ok=True)
    manifest_path = RUNS / "当前搜索任务.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, ensure_ascii=False, indent=2))
    if args.run and not args.dry_run:
        return run_engine(args.topic, profile, args.speed)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
