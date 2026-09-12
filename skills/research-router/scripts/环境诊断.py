#!/usr/bin/env python3
"""Read-only cross-platform preflight for the research Skill."""

from __future__ import annotations

import json
import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path


def command_output(command: list[str]) -> str | None:
    try:
        result = subprocess.run(command, capture_output=True, text=True, timeout=5)
    except (OSError, subprocess.SubprocessError):
        return None
    return result.stdout.strip() if result.returncode == 0 else None


def main() -> int:
    system = platform.system()
    checks: dict[str, object] = {
        "os": f"{system} {platform.release()}",
        "architecture": platform.machine(),
        "python": platform.python_version(),
        "python_executable": sys.executable,
        "ffmpeg": shutil.which("ffmpeg") is not None,
        "external_ssd_work_root": Path("/Volumes/1TB-SSD/WilleSpace-Work").is_dir(),
    }
    if system == "Windows":
        gpu = command_output(["nvidia-smi", "--query-gpu=name,memory.total,driver_version", "--format=csv,noheader"])
        checks["nvidia_gpu"] = gpu or "not_detected"
        checks["cuda_visible"] = bool(os.environ.get("CUDA_PATH") or os.environ.get("CUDA_HOME"))
        checks["windows_transcription"] = "use RTX GPU when nvidia-smi and CUDA are available"
    elif system == "Darwin":
        checks["chip"] = command_output(["sysctl", "-n", "machdep.cpu.brand_string"]) or platform.processor()
        checks["memory"] = command_output(["sysctl", "-n", "hw.memsize"])
        checks["browser_automation"] = "use Ego Lite / local browser session"
    else:
        checks["gpu"] = command_output(["nvidia-smi", "--query-gpu=name,memory.total,driver_version", "--format=csv,noheader"]) or "not_detected"

    checks["faster_whisper_installed"] = importable("faster_whisper")
    checks["recommendation"] = recommendation(system, checks)
    print(json.dumps({"schema_version": "research-environment/v1", "checks": checks}, ensure_ascii=False, indent=2))
    return 0


def importable(name: str) -> bool:
    try:
        __import__(name)
    except Exception:
        return False
    return True


def recommendation(system: str, checks: dict[str, object]) -> str:
    if system == "Windows":
        if checks.get("nvidia_gpu") == "not_detected":
            return "可做网页资料搜索；视频转写前请安装 NVIDIA 驱动并确认 nvidia-smi 可用。"
        return "可在 Windows GPU 上运行 faster-whisper；先确认 faster-whisper 和 CUDA 环境。"
    if system == "Darwin":
        return "Mac 适合运行路由、浏览器会话和证据整理；视频转写可交给 Windows GPU。"
    return "可运行网页和文本路由；视频转写能力取决于本机 GPU 与 CUDA。"


if __name__ == "__main__":
    raise SystemExit(main())
