import sys
import json

# Simple wrapper around numpy for demo purposes. Uses JSON for input/output.
# Usage: python tools/np_wrapper.py <op> <json-data>

op = sys.argv[1] if len(sys.argv) > 1 else ''
data_raw = sys.argv[2] if len(sys.argv) > 2 else 'null'
try:
    data = json.loads(data_raw)
except Exception:
    # try to eval simple Python literal as fallback
    try:
        data = eval(data_raw)
    except Exception:
        data = None

result = None

try:
    import numpy as np
except Exception:
    np = None

if op == 'sum':
    if isinstance(data, list):
        result = sum(data) if np is None else int(np.sum(data))
    else:
        result = None

elif op == 'mean':
    if isinstance(data, list):
        if np is None:
            result = sum(data)/len(data) if data else None
        else:
            result = float(np.mean(data))
    else:
        result = None

elif op == 'array':
    # return list representation
    if np is None:
        result = data
    else:
        arr = np.array(data)
        result = arr.tolist()

elif op == 'matmul':
    # data expected [[a],[b]] or [matrix1, matrix2]
    if isinstance(data, list) and len(data) == 2:
        a, b = data[0], data[1]
        if np is None:
            # naive python matmul for 2D lists
            result = [[sum(x*y for x,y in zip(row,col)) for col in zip(*b)] for row in a]
        else:
            result = np.matmul(np.array(a), np.array(b)).tolist()
    else:
        result = None

elif op == 'reshape':
    # args can be [data, shape] or {'data':..., 'shape':...}
    payload = data
    if isinstance(data, dict) and 'data' in data:
        payload = data
    # Normalize
    if isinstance(payload, list) and len(payload) == 2 and not isinstance(payload[1], dict):
        src = payload[0]
        shape = payload[1]
    elif isinstance(payload, dict):
        src = payload.get('data')
        shape = payload.get('shape')
    else:
        src = payload
        shape = None

    try:
        if np is None:
            # Best-effort reshape without numpy
            if shape is None:
                result = src
            else:
                # flatten source
                flat = []
                def _flatten(x):
                    if isinstance(x, list):
                        for y in x:
                            _flatten(y)
                    else:
                        flat.append(x)
                _flatten(src)
                total = 1
                for dim in shape:
                    total *= int(dim)
                if len(flat) != total:
                    result = {'error': 'cannot reshape: size mismatch'}
                else:
                    # build nested lists
                    def build(flat, shape):
                        if not shape:
                            return flat.pop(0)
                        size = int(shape[0])
                        return [build(flat, shape[1:]) for _ in range(size)]
                    flat_copy = list(flat)
                    result = build(flat_copy, [int(d) for d in shape])
        else:
            arr = np.array(src)
            if shape is None:
                result = arr.tolist()
            else:
                result = arr.reshape(tuple(int(s) for s in shape)).tolist()
    except Exception as e:
        result = {'error': str(e)}

elif op == 'dot':
    # data: [a, b]
    if isinstance(data, list) and len(data) == 2:
        a, b = data[0], data[1]
        try:
            if np is None:
                # naive dot for vectors
                if isinstance(a, list) and isinstance(b, list):
                    if len(a) != len(b):
                        result = {'error': 'size mismatch'}
                    else:
                        result = sum(x*y for x,y in zip(a,b))
                else:
                    result = None
            else:
                result = np.dot(np.array(a), np.array(b)).tolist()
        except Exception as e:
            result = {'error': str(e)}
    else:
        result = None

elif op == 'transpose':
    # data: matrix/list
    try:
        if np is None:
            if isinstance(data, list):
                result = [list(x) for x in zip(*data)]
            else:
                result = None
        else:
            result = np.transpose(np.array(data)).tolist()
    except Exception as e:
        result = {'error': str(e)}

else:
    result = {'error': f'unknown op: {op}'}

print(json.dumps(result))
