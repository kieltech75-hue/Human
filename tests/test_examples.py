import subprocess
import sys
import ast
import re


def run_example():
    cmd = [sys.executable, '-m', 'human_language', 'examples/numby_test.hm']
    out = subprocess.check_output(cmd, stderr=subprocess.STDOUT, text=True, timeout=30)
    return out


def parse_output(out: str):
    # Extract the last JSON line emitted by the example (if any)
    last_json = None
    for line in out.splitlines()[::-1]:
        line = line.strip()
        if not line:
            continue
        # naive check for JSON object
        if line.startswith('{') and line.endswith('}'):
            last_json = line
            break
    if last_json is None:
        # fallback to previous parsing strategy
        results = {}
        for line in out.splitlines():
            m = re.match(r"^\s*([^\s].*?)\s*->\s*(.+)$", line)
            if m:
                key = m.group(1).strip()
                val = m.group(2).strip()
                try:
                    value = ast.literal_eval(val)
                except Exception:
                    value = val
                results[key] = value
        return results

    import json
    try:
        return json.loads(last_json)
    except Exception:
        return {}


def test_numby_example_outputs():
    out = run_example()
    results = parse_output(out)

    # Basic scalar checks
    assert 'np_sum ->' in out or 'np_sum' in results
    assert results.get('np_sum') == 10
    assert results.get('np_mean') == 2.5

    # Matrix checks
    matmul = results.get('matmul')
    assert isinstance(matmul, list)
    assert matmul == [[19, 22], [43, 50]]

    dot = results.get('dot')
    # dot may be scalar
    assert dot == 32

    transpose = results.get('transpose')
    assert transpose == [[1, 3], [2, 4]]