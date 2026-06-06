"""
Health check for Human's Python interop environment.

- Verifies required modules (from requirements.txt by default) can be imported in-process.
- Reads optional env var `HUMAN_PY_FALLBACK` - comma-separated module names allowed to fallback.
- Exits with code 0 when all required modules import successfully or are allowed to fallback.
- Exits with non-zero code when required modules fail and are NOT allowed to fallback.

Outputs a short report to stdout with actionable commands to recreate venv or set fallback env.
"""
import importlib
import os
import sys
from typing import List

REQ_FILE = os.path.join(os.path.dirname(__file__), '..', 'requirements.txt')


def parse_requirements(path: str) -> List[str]:
    modules = []
    try:
        with open(path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                # take package name before any extras or version spec
                pkg = line.split()[0]
                pkg = pkg.split('==')[0].split('>=')[0].split('<=')[0].split('~=')[0]
                modules.append(pkg)
    except FileNotFoundError:
        return []
    return modules


def check_modules(modules: List[str], fallback_set: List[str]):
    ok = []
    failed = []
    for mod in modules:
        name = mod
        # Some packages map to different import names (basic heuristic)
        import_name = mod
        if mod.lower() == 'pandas':
            import_name = 'pandas'
        try:
            importlib.import_module(import_name)
            ok.append(mod)
        except Exception as e:
            if mod in fallback_set:
                failed.append((mod, str(e), True))
            else:
                failed.append((mod, str(e), False))
    return ok, failed


def main():
    fallback_env = os.environ.get('HUMAN_PY_FALLBACK', '')
    fallback_set = [m.strip() for m in fallback_env.split(',') if m.strip()]

    modules = parse_requirements(REQ_FILE)
    if not modules:
        print('No requirements.txt found or it contains no modules.')
        sys.exit(0)

    print('Checking imports for:', ', '.join(modules))
    ok, failed = check_modules(modules, fallback_set)

    if ok:
        print('\nImported successfully:')
        for m in ok:
            print(' -', m)

    if failed:
        print('\nImport failures:')
        for (m, err, allowed) in failed:
            if allowed:
                print(f" - {m}: FAILED (allowed fallback). error: {err}")
            else:
                print(f" - {m}: FAILED (not allowed to fallback). error: {err}")

    # Summary and actionable commands
    if any(not a for (_, _, a) in failed):
        print('\nAction: Some modules failed to import in-process.')
        print(' - To recreate a clean venv and install dependencies, run:')
        print('   scripts\\setup_venv.ps1')
        print('\n - Alternatively, add modules to HUMAN_PY_FALLBACK to allow subprocess fallbacks:')
        print('   (PowerShell) $env:HUMAN_PY_FALLBACK = "' + ','.join(fallback_set) + ',<module>"')
        sys.exit(2)

    # Optionally run example tests to verify end-to-end behavior. Set HUMAN_SKIP_EXAMPLE_CHECK=1 to skip.
    if os.environ.get('HUMAN_SKIP_EXAMPLE_CHECK', '') != '1':
        examples = [
            {
                'cmd': [sys.executable, '-m', 'human_language', 'examples/numby_test.hm'],
                'expect': [
                    'np_sum -> 10',
                    'np_mean -> 2.5'
                ]
            }
        ]

        for ex in examples:
            print(f"\nRunning example check: {' '.join(ex['cmd'])}")
            try:
                import subprocess
                out = subprocess.check_output(ex['cmd'], stderr=subprocess.STDOUT, text=True, timeout=30)
            except Exception as e:
                print(f"Example run failed: {e}")
                print('Output (if any):')
                try:
                    print(e.output)
                except Exception:
                    pass
                sys.exit(3)

            missing = [s for s in ex['expect'] if s not in out]
            if missing:
                print('Example output did not contain expected lines:')
                for m in missing:
                    print(' -', m)
                print('Full output:')
                print(out)
                sys.exit(4)

    print('\nAll checks passed (or failures are allowed to fallback).')
    sys.exit(0)


if __name__ == '__main__':
    main()
