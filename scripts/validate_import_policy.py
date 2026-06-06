"""
Validate the effective py_import policy by merging `human.toml` (if present) with environment variables,
then attempting to import modules in the allowlist and reporting results.
"""
import os
import sys

try:
    import tomllib as _tomllib
except Exception:
    _tomllib = None

import importlib


def load_project_config():
    cfg = {}
    path = os.path.join(os.getcwd(), 'human.toml')
    if os.path.exists(path) and _tomllib is not None:
        try:
            with open(path, 'rb') as f:
                cfg = _tomllib.load(f)
        except Exception:
            cfg = {}
    return cfg


def effective_policy():
    cfg = load_project_config()
    py_cfg = cfg.get('py_import', {}) if isinstance(cfg, dict) else {}

    # fallback
    fallback_env = os.environ.get('HUMAN_PY_FALLBACK', None)
    if fallback_env is not None:
        fallback = [m.strip() for m in fallback_env.split(',') if m.strip()]
    else:
        fallback = py_cfg.get('fallback', []) or []

    # allowlist
    allow_env = os.environ.get('HUMAN_PY_IMPORT_ALLOWLIST', None)
    if allow_env is not None:
        allow = [m.strip() for m in allow_env.split(',') if m.strip()]
    else:
        allow = py_cfg.get('allowlist', []) or []

    # enabled
    env_enabled = os.environ.get('HUMAN_PY_IMPORT_ENABLED', None)
    if env_enabled is not None:
        enabled = env_enabled != '0'
    elif 'enabled' in py_cfg:
        enabled = bool(py_cfg.get('enabled'))
    else:
        enabled = True

    return {'enabled': enabled, 'allowlist': allow, 'fallback': fallback}


def main():
    pol = effective_policy()
    print('Effective py_import policy:')
    print(f"  enabled: {pol['enabled']}")
    print(f"  allowlist: {pol['allowlist']}")
    print(f"  fallback: {pol['fallback']}")

    if not pol['enabled']:
        print('\npy_import is disabled. Nothing to validate.')
        return 0

    failed = []
    for m in pol['allowlist']:
        try:
            importlib.import_module(m)
            print(f"OK: imported {m}")
        except Exception as e:
            print(f"FAIL: {m} -> {e}")
            failed.append((m, str(e)))

    if failed:
        print('\nSome allowlist imports failed.')
        return 2

    print('\nAll allowlist modules imported successfully.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
