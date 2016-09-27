import numpy as np


def read_ndarray(n):
    return np.array([list(map(int, input().split())) for _ in range(n)],
                    dtype=np.int64)


def bigger_two(x):
    t = 1
    while 1:
        t *= 2
        if t >= x:
            break
    return t


def make_even(a):
    sz = a.shape[0]
    t = bigger_two(sz)
    col_stacked = np.column_stack((a, np.zeros((sz, t - sz), dtype=np.int64)))
    a = np.row_stack((col_stacked, np.zeros((t - sz, t), dtype=np.int64)))
    return a


def divide_ndarray(a):
    half = a.shape[0] // 2
    return a[:half, :half], a[:half, half:], a[half:, :half], a[half:, half:]


def strassen(a, b, n):
    if n == 1:
        return np.dot(a, b)
    sz = n // 2
    a_11, a_12, a_21, a_22 = divide_ndarray(a)
    b_11, b_12, b_21, b_22 = divide_ndarray(b)
    I = strassen(a_11 + a_22, b_11 + b_22, sz)
    II = strassen(a_21 + a_22, b_11, sz)
    III = strassen(a_11, b_12 - b_22, sz)
    IV = strassen(a_22, -b_11 + b_21, sz)
    V = strassen(a_11 + a_12, b_22, sz)
    VI = strassen(-a_11 + a_21, b_11 + b_12, sz)
    VII = strassen(a_12 - a_22, b_21 + b_22, sz)
    c_11 = I + IV - V + VII
    c_21 = II + IV
    c_12 = III + V
    c_22 = I + III - II + VI
    return np.column_stack((np.row_stack((c_11, c_21)),
                            np.row_stack((c_12, c_22))))
