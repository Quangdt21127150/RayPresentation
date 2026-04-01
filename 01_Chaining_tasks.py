import ray

ray.init()


# Task 1: Nhân số với 2
@ray.remote
def multiply_by_two(x):
    return x * 2


# Task 2: Cộng 3
@ray.remote
def add_three(x):
    return x + 3


# Task 3: Chia 5
@ray.remote
def divide_by_five(x):
    return x / 5


# Task chaining:
x = 4
result = divide_by_five.remote(add_three.remote(multiply_by_two.remote(x)))

final_result = ray.get(result)
print(f"Kết quả cuối cùng: {final_result}")
print("Resource: ", ray.cluster_resources())
print("Remaining Resource: ", ray.available_resources())

ray.shutdown()
