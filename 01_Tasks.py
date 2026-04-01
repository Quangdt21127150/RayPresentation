import ray
import time


@ray.remote
def slow_task(x):
    time.sleep(1)
    return x * x


# ray.init()
# ray.init()
ray.init(ignore_reinit_error=True)


n = 12
print(f"Running {n} tasks...")
refs = [slow_task.remote(i) for i in range(n)]
results = ray.get(refs)
print("Object Refs:", refs)
print("Kết quả:", results)

print("Resource: ", ray.cluster_resources())
print("Remaining Resource: ", ray.available_resources())

ray.shutdown()
