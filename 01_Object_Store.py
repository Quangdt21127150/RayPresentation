import ray
import numpy as np
import psutil, os


process = psutil.Process(os.getpid())


def mem_mb():
    return process.memory_info().rss / 1024**2


@ray.remote
def read_array_sum(arr):
    return float(arr.sum())


n = 1_310_720
arr = np.random.rand(n).astype(np.float32)

ray.init()


print(f"Array size: {arr.nbytes / 1024**2:5f} MB")
print(f"Object store: {mem_mb() / 1024**2:5f} MB")

before = mem_mb()
arr_ref = ray.put(arr)
results = ray.get([read_array_sum.remote(arr_ref) for _ in range(4)])
after = mem_mb()
print(results)
print(f"Memory change (object store read): {after - before} MB")

before = mem_mb()
results = ray.get([read_array_sum.remote(arr) for _ in range(4)])
after = mem_mb()
print(results)
print(f"Memory change (direct object read): {after - before} MB")

ray.shutdown()
