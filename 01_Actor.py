import os
import time

import ray


@ray.remote
def increment(count):
    count += 1
    return count


@ray.remote(max_restarts=5)
class Counter:
    def __init__(self):
        self.count = 0

    def increment(self):
        self.count += 1
        return self.count

    def getCount(self):
        return self.count

    def crash(self):
        os._exit(1)


ray.init(ignore_reinit_error=True)
print("\n=== Task Example (Stateless) ===")
count = 0
print("Count 1:", ray.get(increment.remote(count)))
print("Count 2:", ray.get(increment.remote(count)))
print("Count 3:", ray.get(increment.remote(count)))


print("\n=== Actor Example (Stateful) ===")
counter = Counter.remote()
print("Count 1:", ray.get(counter.increment.remote()))
print("Count 2:", ray.get(counter.increment.remote()))
print("Count 3:", ray.get(counter.increment.remote()))

# ray.kill(counter)
# time.sleep(1)
# print("Count:", ray.get(counter.getCount.remote()))

# for i in range(10):
#     try:
#         ray.get(counter.crash.remote())
#     except ray.exceptions.RayActorError as e:
#         print(f"Actor crashed {i + 1} times: {e}", flush=True)

#     print("Count:", ray.get(counter.getCount.remote()))


ray.shutdown()

# print("Count:", ray.get(counter.getCount.remote()))
