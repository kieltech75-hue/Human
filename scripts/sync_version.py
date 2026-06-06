#!/usr/bin/env python3
"""Sync package.json version with human_language.__version__"""
import re
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
INIT = ROOT / "human_language" / "__init__.py"
PKG = ROOT / "package.json"

text = INIT.read_text(encoding="utf-8")
m = re.search(r"^__version__\s*=\s*['\"]([^'\"]+)['\"]", text, re.M)
if not m:
    print("Error: could not find __version__ in human_language/__init__.py", file=sys.stderr)
    sys.exit(1)
ver = m.group(1)

data = json.loads(PKG.read_text(encoding="utf-8"))
old = data.get("version")
if old != ver:
    data["version"] = ver
    PKG.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    print(f"Updated package.json version: {old} -> {ver}")
else:
    print(f"package.json already at {ver}")

print(f"version: {ver}")
