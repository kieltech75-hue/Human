from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def run(cmd: list[str], cwd: Path | None = None) -> None:
    print("+", " ".join(cmd))
    subprocess.run(cmd, cwd=str(cwd or ROOT), check=True)


def build_native_binary(platform: str, output_dir: Path, output_name: str) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    script = ROOT / "examples" / "hello_world.hm"
    if not script.exists():
        raise SystemExit(f"Missing sample script: {script}")

    cmd = [
        sys.executable,
        "main.py",
        "--package-native",
        str(script),
        "--dist",
        str(output_dir),
        "--bundle-python",
        "--name",
        output_name,
    ]
    run(cmd, ROOT)

    binary_path = output_dir / output_name
    if os.name == "nt" and not binary_path.exists():
        binary_path = output_dir / f"{output_name}.exe"
    if not binary_path.exists():
        raise SystemExit(f"Expected packaged binary was not created: {binary_path}")

    if platform in {"linux", "macos"}:
        binary_path.chmod(0o755)


def main() -> None:
    parser = argparse.ArgumentParser(description="Build a platform-native Human executable for release")
    parser.add_argument("--platform", required=True, choices=["windows", "linux", "macos"])
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--name", required=True)
    args = parser.parse_args()

    output_dir = Path(args.output_dir).resolve()
    build_native_binary(args.platform, output_dir, args.name)


if __name__ == "__main__":
    main()
