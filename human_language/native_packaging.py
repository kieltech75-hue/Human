from __future__ import annotations

from pathlib import Path

from .pyinstaller_packaging import BundledPackagingError, build_bundled_executable


def build_executable(
    script_path: Path,
    output_dir: Path,
    format: str = "native",
    gui: bool = False,
    bundle_python: bool = False,
    name: str | None = None,
) -> None:
    if format != "native":
        raise BundledPackagingError(f"Unsupported packaging format: {format}")

    if not bundle_python:
        raise BundledPackagingError("Bundled native packaging requires --bundle-python")

    build_bundled_executable(
        script_path=script_path,
        output_dir=output_dir,
        gui=gui,
        exe_name=name,
    )
