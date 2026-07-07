import time

def timer(func, *args, **kwargs):
    start = time.perf_counter()
    result = func(*args, **kwargs)
    elapsed = 1000 * (time.perf_counter() - start)
    print(f"{func.__name__} took {elapsed:.0f} ms")
    return result
