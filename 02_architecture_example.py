import ray
import numpy as np


@ray.remote
def multiply(a, b):
    return a * b


# Tạo hai object
a = 150
b = np.array([[10, 20], [30, 40]])

ray.init(ignore_reinit_error=True)

# Put vào Object Store
a_ref = ray.put(a)
b_ref = ray.put(b)

# Gửi task đến Scheduler
c_ref = multiply.remote(a_ref, b_ref)

# Lấy kết quả
c = ray.get(c_ref)

print("\nKết quả cuối cùng:")
print(c)

ray.shutdown()
