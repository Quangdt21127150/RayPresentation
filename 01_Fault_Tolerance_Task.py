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

    print(f"→ Lần #{attempt} đang chạy trên worker PID: {os.getpid()}...")
    time.sleep(0.5)

    if random.random() <= 0.9:
        print(f"Lần chạy #{attempt} → Worker crashed")
        os._exit(1)

    return f"Thành công ở lần chạy #{attempt}"


ray.init(ignore_reinit_error=True)

counter = AttemptCounter.remote()

try:
    result = ray.get(flaky_task.remote(counter))
    print("Task thành công:", result)
except Exception as e:
    print(f"{type(e).__name__}: {e}")

ray.shutdown()
