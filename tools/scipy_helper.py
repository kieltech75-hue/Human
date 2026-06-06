import scipy.linalg as la

def eig_json(mat):
    import numpy as _np
    arr = _np.array(mat)
    w, v = la.eig(arr)
    return {'w': _np.real(w).tolist(), 'v': _np.real(v).tolist()}
