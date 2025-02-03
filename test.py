import random
import math

def is_square(n: int):
    return math.isqrt(n) ** 2 == n

def grouping_better(arr: list[int]):
    n = len(arr)
    left = [0 for _ in range(n)]
    left_count = 0
    right = [0 for _ in range(n)]
    right_count = 0
    for n in arr:
        if is_square(n):
            left[left_count] = n
            left_count += 1
        else:
            right[right_count] = n
            right_count += 1
    for i in range(left_count):
        arr[i] = left[i]
    for i in range(right_count):
        arr[left_count + i] = right[i]
    return arr

arr = [random.randint(0, 16) for _ in range(32)]
print(arr)
print(grouping_better(arr))
