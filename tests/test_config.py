import os
import textwrap
from pathlib import Path
import importlib

import pytest

from human_language.compiler import Bytecode
import human_language.vm as vm_module


def write_toml(path: Path, content: str):
    path.write_text(content)


def test_loads_human_toml(tmp_path, monkeypatch):
    # Ensure env vars don't interfere
    monkeypatch.delenv('HUMAN_PY_IMPORT_ENABLED', raising=False)
    monkeypatch.delenv('HUMAN_PY_IMPORT_ALLOWLIST', raising=False)
    monkeypatch.delenv('HUMAN_PY_FALLBACK', raising=False)

    toml_content = textwrap.dedent('''
    [py_import]
    enabled = false
    allowlist = ["numpy"]
    fallback = ["numpy"]
    ''')
    write_toml(tmp_path / 'human.toml', toml_content)

    monkeypatch.chdir(tmp_path)

    bc = Bytecode()
    vm = vm_module.VM(bc)

    assert vm.py_import_enabled is False
    assert vm.py_import_allowlist == {"numpy"}
    assert vm.py_fallback_modules == {"numpy"}


def test_warns_when_no_toml_parser(tmp_path, monkeypatch, caplog):
    # Simulate absence of tomllib/tomli/toml
    monkeypatch.setattr(vm_module, '_tomllib', None)
    monkeypatch.delenv('HUMAN_PY_IMPORT_ENABLED', raising=False)
    monkeypatch.delenv('HUMAN_PY_IMPORT_ALLOWLIST', raising=False)
    monkeypatch.delenv('HUMAN_PY_FALLBACK', raising=False)

    write_toml(tmp_path / 'human.toml', '[py_import]\nenabled=true\n')
    monkeypatch.chdir(tmp_path)

    caplog.clear()
    bc = Bytecode()
    vm = vm_module.VM(bc)

    # Expect a warning about missing toml parser
    found = any('human.toml found but no TOML parser available' in r.message for r in caplog.records)
    assert found, 'Expected warning when toml parser is unavailable'
