from __future__ import annotations

import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path


class InstallError(Exception):
    pass


def _is_bundled() -> bool:
    return getattr(sys, "frozen", False) and hasattr(sys, "executable")


def _install_dir() -> Path:
    if os.name == "nt":
        local_app_data = os.environ.get("LOCALAPPDATA") or str(Path.home() / "AppData" / "Local")
        return Path(local_app_data) / "Programs" / "Human"
    return Path.home() / ".local" / "bin"


def _target_path() -> Path:
    install_dir = _install_dir()
    if os.name == "nt":
        return install_dir / "human.exe"
    return install_dir / "human"


def _add_to_user_path(path: Path) -> None:
    if os.name == "nt":
        current = os.environ.get("PATH", "")
        paths = [p for p in current.split(";") if p]
        if str(path) not in paths:
            new_path = ";".join(paths + [str(path)])
            subprocess.run(
                ["powershell", "-NoProfile", "-Command", f"[Environment]::SetEnvironmentVariable('Path', '{new_path}', 'User')"],
                check=True,
                capture_output=True,
                text=True,
            )
        return

    profile_candidates = [Path.home() / ".bashrc", Path.home() / ".zshrc", Path.home() / ".profile"]
    export_line = f'export PATH="{path}:$PATH"\n'
    for profile in profile_candidates:
        if profile.exists() and export_line.strip() in profile.read_text(encoding="utf-8"):
            return

    target_profile = Path.home() / ".profile"
    if not target_profile.exists():
        target_profile.write_text("", encoding="utf-8")
    target_profile.write_text(target_profile.read_text(encoding="utf-8") + export_line, encoding="utf-8")


def ensure_self_installed() -> bool:
    if not _is_bundled():
        return False

    source = Path(sys.executable).resolve()
    target = _target_path().resolve()
    install_dir = target.parent

    if not target.exists() or target.resolve() != source.resolve():
        install_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
        if os.name == "nt":
            shim_path = install_dir / "human.cmd"
            shim_path.write_text('@echo off\r\n"%~dp0human.exe" %*\r\n', encoding="cp1252")

    _add_to_user_path(install_dir)
    return True
