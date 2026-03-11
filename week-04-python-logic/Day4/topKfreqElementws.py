import heapq
from collections import Counter


def topKFrequent(nums, k):
    frequency = Counter(nums)

    heap = []
    for num, freq in frequency.items():
        print(num, freq) #check the freq
        heapq.heappush(heap,(freq, num))
        print(heap)
        if len(heap) > k:
            heapq.heappop(heap)
            print(f'if heap > {k} returns {heap}')
    return[num for freq, num in heap]

nums = [1,1,1,2,2,3,3,3,4,5]
k = 2 #find the top 2 most repeated element from nums
print(topKFrequent(nums, k))

heapq.