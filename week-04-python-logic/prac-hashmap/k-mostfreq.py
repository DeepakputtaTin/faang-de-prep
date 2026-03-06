from collections import Counter


def count(nums, k):
    c = Counter(nums)
    print(c)
    print([n for n, freq in c.most_common(k)])
    return c.most_common(k)

nums = [1,1,1,2,2,3]
k = 2
print(count(nums, k))
