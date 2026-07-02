from __future__ import annotations

import importlib.util
import os
import shutil
import subprocess
import sys
import tempfile
import textwrap
from pathlib import Path


class BundledPackagingError(Exception):
    pass


def _find_project_venv() -> Path | None:
    current = Path.cwd()
    while True:
        candidate = current / ".venv"
        if candidate.exists():
            return candidate
        if current.parent == current:
            return None
        current = current.parent


def _find_pyinstaller() -> str:
    if shutil.which("pyinstaller"):
        return "pyinstaller"

    spec = importlib.util.find_spec("PyInstaller")
    if spec is not None:
        return sys.executable

    venv_path = _find_project_venv()
    if venv_path is not None:
        venv_bin = venv_path / ("Scripts" if os.name == "nt" else "bin")
        pyinstaller_bin = venv_bin / ("pyinstaller.exe" if os.name == "nt" else "pyinstaller")
        if pyinstaller_bin.exists():
            return str(pyinstaller_bin)
        venv_python = venv_bin / ("python.exe" if os.name == "nt" else "python")
        if venv_python.exists():
            return str(venv_python)

    raise BundledPackagingError(
        "PyInstaller is required to build a bundled executable. Install it with `pip install pyinstaller` in the active environment or in the project .venv."
    )


def build_bundled_executable(script_path: Path, output_dir: Path, gui: bool = False, exe_name: str | None = None) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    script_path = script_path.resolve()
    if not script_path.exists():
        raise BundledPackagingError(f"Human script not found: {script_path}")

    exe_name = exe_name or script_path.stem
    pyinstaller_cmd = _find_pyinstaller()
    use_executable = shutil.which("pyinstaller") is not None

    script_text = script_path.read_text(encoding="utf-8")
    launcher_name = f"{script_path.stem}_bundle_launcher.py"

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_dir_path = Path(temp_dir)
        launcher_path = temp_dir_path / launcher_name
        launcher_path.write_text(
            textwrap.dedent(
                f"""\
                import sys
                import tempfile
                from pathlib import Path
                from human_language.interpreter import run_file

                SCRIPT_CONTENT = {script_text!r}

                def write_script() -> Path:
                    target_dir = Path(tempfile.gettempdir()) / "human_bundle"
                    target_dir.mkdir(parents=True, exist_ok=True)
                    target_file = target_dir / {script_path.name!r}
                    target_file.write_text(SCRIPT_CONTENT, encoding="utf-8")
                    return target_file

                def main() -> int:
                    target_file = write_script()
                    run_file(str(target_file))
                    return 0

                if __name__ == "__main__":
                    sys.exit(main())
                """
            ),
            encoding="utf-8",
        )

        dist_path = output_dir.resolve()
        work_path = temp_dir_path / "build"
        spec_path = temp_dir_path
        cmd: list[str]
        if use_executable:
            cmd = [pyinstaller_cmd]
        else:
            pyinstaller_path = Path(pyinstaller_cmd)
            if pyinstaller_path.name.lower().startswith("python") or pyinstaller_path.name.lower().startswith("python"):
                cmd = [pyinstaller_cmd, "-m", "PyInstaller"]
            else:
                cmd = [pyinstaller_cmd]

        cmd.extend([
            "--clean",
            "--onefile",
            "--name",
            exe_name,
            "--distpath",
            str(dist_path),
            "--workpath",
            str(work_path),
            "--specpath",
            str(spec_path),
            "--paths",
            str(Path.cwd()),
            "--hidden-import",
            "human_language",
        ])

        if gui:
            if os.name == "nt":
                cmd.append("--windowed")
            else:
                cmd.append("--windowed")

        cmd.append(str(launcher_path))

        try:
            subprocess.run(cmd, check=True)
        except subprocess.CalledProcessError as exc:
            raise BundledPackagingError(
                f"PyInstaller packaging failed with exit code {exc.returncode}."
            ) from exc

        print(f"Bundled executable written to {dist_path / (exe_name + ('.exe' if os.name == 'nt' else ''))}")
