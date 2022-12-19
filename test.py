import numpy as np


def max_rolling1(a, window, axis=1):
    """

    Args:
        a (_type_): _description_
        window (_type_): _description_
        axis (int, optional): _description_. Defaults to 1.
    """
    shape = a.shape[:-1] + (a.shape[-1] - window + 1, window)
    strides = a.strides + (a.strides[-1],)
    rolling = np.lib.stride_tricks.as_strided(a, shape=shape, strides=strides)
    out_array = np.append(np.full((window - 1), np.nan),
                          np.max(rolling, axis=axis))
    out_array = np.roll(out_array, 1)
    out_array[:window] = np.nan
    return out_array


a = np.array([5, 4, 1, 8])
max_rolling1(a, window=3)
