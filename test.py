import random

a = {i: 0 for i in range(100)}
for _ in range(1000):
    k = int(random.expovariate(100) * 100)
    if k < 100:
        a[k] += 1

print(a)
