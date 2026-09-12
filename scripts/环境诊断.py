#!/usr/bin/env python3
"""Backward-compatible wrapper for the packaged environment diagnostic."""
from pathlib import Path
import runpy

runpy.run_path(str(Path(__file__).resolve().parents[1] / "skills/research-router/scripts/环境诊断.py"), run_name="__main__")
