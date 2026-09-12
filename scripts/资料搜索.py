#!/usr/bin/env python3
"""Backward-compatible wrapper for the packaged research-router skill."""
from pathlib import Path
import runpy

runpy.run_path(str(Path(__file__).resolve().parents[1] / "skills" / "research-router" / "scripts" / "资料搜索.py"), run_name="__main__")
