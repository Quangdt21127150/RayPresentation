import ray
import time
import os
import random


@ray.remote
class AttemptCounter:
    def __init__(self):
        self.attempt = 0

    def increment(self):
        self.attempt += 1
        return self.attempt


@ray.remote(max_retries=5)
def flaky_task(counter_actor):
    attempt = ray.get(counter_actor.increment.remote())

    print(f"→ Lần #{attempt} đang chạy trên worker {os.getpid()}...", flush=True)
    time.sleep(0.5)

    if random.random() <= 0.9:
        os._exit(1)

    return f"thành công ở lần chạy #{attempt}"


ray.init(ignore_reinit_error=True)

counter = AttemptCounter.remote()

try:
    result = ray.get(flaky_task.remote(counter))
    print("Task", result, flush=True)
except Exception as e:
    print(f"{type(e).__name__}: {e}", flush=True)

ray.shutdown()
