import funcs

if __name__ == "__main__":
    n = int(input())
    a, b = funcs.read_ndarray(n), funcs.read_ndarray(n)
    res = funcs.strassen(funcs.make_even(a), funcs.make_even(b),
                         funcs.bigger_two(n))[:n, :n]
    for s in list(res):
        print(*list(s))
