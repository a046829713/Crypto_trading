import numpy as np
from numba import njit

@njit
def col_map_nb(col_arr, n_cols):
    col_idxs_out = np.empty((n_cols, len(col_arr)), dtype=np.int_)
    print(col_idxs_out.shape)
    col_ns_out = np.full((n_cols,), 0, dtype=np.int_)

    for r in range(col_arr.shape[0]):
        col = col_arr[r]
        col_idxs_out[col, col_ns_out[col]] = r
        col_ns_out[col] += 1
    return col_idxs_out[:, :np.max(col_ns_out)], col_ns_out

col_map_nb(np.repeat(np.arange(10000), 50), 10000)