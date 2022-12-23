import numpy as np
from utils.TimeCountMsg import TimeCountMsg
import numba


@TimeCountMsg.record_timemsg
def max_rolling1(a, window, axis=1):
    max_arr = np.empty(shape=a.shape[0])
    shape = a.shape[:-1] + (a.shape[-1] - window + 1, window)
    strides = a.strides + (a.strides[-1],)
    rolling = np.lib.stride_tricks.as_strided(a, shape=shape, strides=strides)
    max_arr[window-1:] = np.roll(np.max(rolling, axis=1), 1)
    max_arr[:window] = np.nan
    return max_arr


# @TimeCountMsg.record_timemsg
# def max_rolling2(A,K):
#     rollingmax = np.array([max(A[j:j+K]) for j in range(len(A)-K)])
#     return rollingmax


A = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9])
K = 3

print(max_rolling1(A, K))
