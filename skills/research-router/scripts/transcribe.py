#!/usr/bin/env python3
"""Local video transcription for the Windows RTX 5070 lane.

This script intentionally accepts local media only. Platform URL acquisition
stays in the browser/download layer, so cookies and login state never enter
the transcription process.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import sys
from datetime import datetime, timezone
from pathlib import Path


def work_root() -> Path:
    if os.environ.get("WILLE_WORK_ROOT"):
        return Path(os.environ["WILLE_WORK_ROOT"]).expanduser()
    return Path(r"E:\WilleSpace-Work") if platform.system() == "Windows" else Path("/Volumes/1TB-SSD/WilleSpace-Work")


def ensure_storage(root: Path) -> Path:
    # Windows keeps the sentinel in the explicitly managed work root. macOS
    # keeps it at the mounted-volume root, matching the workstation policy.
    sentinel = root / ".wille-work-storage" if platform.system() == "Windows" else root.parent / ".wille-work-storage"
    if not root.is_dir() or not sentinel.exists():
        raise SystemExit(f"外接 SSD 存储未确认：需要 {root} 和 {sentinel}。不会回退到系统盘。")
    kb = root / "KnowledgeBase"
    if not kb.is_dir():
        raise SystemExit(f"KnowledgeBase 尚未准备好：{kb}。请先创建目录后重试。")
    return kb


def safe_output_dir(kb: Path, requested: str | None) -> Path:
    default = kb / "10-raw" / "social-media" / "transcripts"
    output = Path(requested).expanduser() if requested else default
    output = output.resolve()
    kb_resolved = kb.resolve()
    if output != kb_resolved and kb_resolved not in output.parents:
        raise SystemExit(f"转写输出必须位于 KnowledgeBase 下：{kb_resolved}")
    output.mkdir(parents=True, exist_ok=True)
    return output


def output_stem(source: Path) -> str:
    digest = hashlib.sha256(f"{source.resolve()}:{source.stat().st_size}:{source.stat().st_mtime_ns}".encode()).hexdigest()[:12]
    return f"{source.stem[:80]}-{digest}"


def write_srt(segments: list[dict], path: Path) -> None:
    def ts(seconds: float) -> str:
        ms = max(0, int(round(seconds * 1000)))
        h, rem = divmod(ms, 3_600_000)
        m, rem = divmod(rem, 60_000)
        s, milli = divmod(rem, 1000)
        return f"{h:02d}:{m:02d}:{s:02d},{milli:03d}"

    lines: list[str] = []
    for i, seg in enumerate(segments, 1):
        lines.extend([str(i), f"{ts(seg['start'])} --> {ts(seg['end'])}", seg["text"].strip(), ""])
    path.write_text("\n".join(lines), encoding="utf-8")


def transcribe(source: Path, output_dir: Path, model_name: str, language: str | None) -> tuple[Path, Path, Path]:
    try:
        from faster_whisper import WhisperModel
    except ImportError as exc:
        raise SystemExit("缺少 faster-whisper：请在 Windows 上安装 requirements-windows.txt") from exc

    cache_dir = os.environ.get("FASTER_WHISPER_CACHE", str(work_root() / "models" / "faster-whisper"))
    device = os.environ.get("FASTER_WHISPER_DEVICE", "cuda")
    compute_type = os.environ.get("FASTER_WHISPER_COMPUTE_TYPE", "float16")
    model = WhisperModel(model_name, device=device, compute_type=compute_type, download_root=cache_dir)
    segments_iter, info = model.transcribe(
        str(source),
        language=language or None,
        beam_size=5,
        vad_filter=True,
        word_timestamps=True,
    )
    segments: list[dict] = []
    text_parts: list[str] = []
    for segment in segments_iter:
        text = segment.text.strip()
        if not text:
            continue
        words = []
        for word in segment.words or []:
            words.append({"start": word.start, "end": word.end, "text": word.word})
        row = {"start": segment.start, "end": segment.end, "text": text, "words": words}
        segments.append(row)
        text_parts.append(text)

    stem = output_stem(source)
    json_path = output_dir / f"{stem}_transcript.json"
    md_path = output_dir / f"{stem}_转写.md"
    srt_path = output_dir / f"{stem}_字幕.srt"
    payload = {
        "schema_version": "local-transcript/v1",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "source": str(source.resolve()),
        "model": model_name,
        "device": device,
        "compute_type": compute_type,
        "language": info.language,
        "language_probability": info.language_probability,
        "segments": segments,
    }
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    md_path.write_text(
        f"# {source.stem}\n\n"
        f"> 来源：`{source.resolve()}`\n> 模型：`{model_name}` · 设备：`{device}` · 语言：`{info.language}`\n\n"
        + "\n".join(f"[{s['start']:.2f} - {s['end']:.2f}] {s['text']}" for s in segments)
        + "\n",
        encoding="utf-8",
    )
    write_srt(segments, srt_path)
    return json_path, md_path, srt_path


def main() -> int:
    parser = argparse.ArgumentParser(description="Windows RTX 5070 本地视频转文字")
    parser.add_argument("input", help="本地视频或音频路径；不接受平台 URL")
    parser.add_argument("--output-dir", help="KnowledgeBase 下的输出目录")
    # large-v3-turbo is already cached and benchmarked on the target RTX 5070.
    # Callers can still select large-v3 when maximum accuracy matters.
    parser.add_argument("--model", default=os.environ.get("FASTER_WHISPER_MODEL", "large-v3-turbo"))
    parser.add_argument("--language", help="语言代码，例如 zh、en；默认自动识别")
    args = parser.parse_args()

    if args.input.startswith(("http://", "https://")):
        raise SystemExit("请先通过已授权的平台下载流程取得本地文件，再交给本脚本；不会在这里读取登录态。")
    source = Path(args.input).expanduser().resolve()
    if not source.is_file():
        raise SystemExit(f"找不到本地媒体文件：{source}")
    kb = ensure_storage(work_root())
    output_dir = safe_output_dir(kb, args.output_dir)
    paths = transcribe(source, output_dir, args.model, args.language)
    print(json.dumps({"ok": True, "outputs": [str(path) for path in paths]}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
