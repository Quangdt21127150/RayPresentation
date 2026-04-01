import random

import ray
import numpy as np
import time
import os


@ray.remote
def create_data():
    pid = os.getpid()
    print(f"[{pid}] Task đang chạy...")
    return np.ones(100)


@ray.remote
def cal_sum(arr):
    time.sleep(1)
    if random.random() <= 0.7:
        os._exit(1)
    return arr.sum()


ray.init(ignore_reinit_error=True)
obj_ref = cal_sum.remote(create_data.remote())


print(f"Kết quả: {ray.get(obj_ref)}")


ray.shutdown()
