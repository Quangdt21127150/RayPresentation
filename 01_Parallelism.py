import ray
import time


# ====================== 1. Sequential vs Parallel ======================
# === Sequential ===
def square(x):
    time.sleep(1)
    return x * x


start = time.time()
results = [square(i) for i in range(8)]
duration = time.time() - start
print(f"Sequential: {results} | {duration:.2f}s")


# === Parallelism ===
@ray.remote
def square_remote(x):
    time.sleep(1)
    return x * x


ray.init(ignore_reinit_error=True)

start = time.time()
refs = [square_remote.remote(i) for i in range(8)]  # Submit 8 tasks song song
results = ray.get(refs)
duration = time.time() - start
print(f"Parallel Ray: {results} | {duration:.2f}s")

# start = time.time()
# results = [ray.get(square_remote.remote(i)) for i in range(8)]
# duration = time.time() - start
# print(f"Ray: {results} | {duration:.2f}s")


# ====================== 2. Nhận kết quả từng phần (Progressive results) ======================
print("=" * 70)
print("⏳ Progressive Results")


all_results = []
remaining_refs = refs[:]

while remaining_refs:
    ready_refs, remaining_refs = ray.wait(remaining_refs, num_returns=2, timeout=10.0)

    results = ray.get(ready_refs)
    print(f"✅ Đã xong {len(results)} tasks → {results}")

    all_results.extend(results)

print(f"Các kết quả: {all_results}")

ray.shutdown()
