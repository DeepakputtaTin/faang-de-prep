# Week 4 Day 4 — Heaps / Priority Queues
**FAANG DE Prep | 13-Week Plan**

---

## 🧠 Core Theory

### What is a Heap?
- A **Complete Binary Tree** stored as a **flat array** (no pointers, no Node objects)
- Two types: **Min-Heap** (smallest at root) and **Max-Heap** (largest at root)
- Python's `heapq` module gives **min-heap only** by default

### Index Math (Critical!)
```
Parent at index i
Left child  → 2i + 1
Right child → 2i + 2
Parent of i → (i - 1) // 2
```

**Example:** `[1, 5, 3, 7, 9, 11, 13]`
```
           1          ← index 0
         /   \
        5     3       ← index 1, 2
       / \   / \
      7   9 11  13    ← index 3, 4, 5, 6
```
- 11 and 13 are children of 3 (index 2) ✅
- Position in list IS the structure — no pointers needed

### Min-Heap vs Max-Heap
| | Min-Heap | Max-Heap |
|---|---|---|
| Root | Smallest element | Largest element |
| Parent rule | Parent ≤ children | Parent ≥ children |
| Python | `heapq` default | Negate values trick |

### Max-Heap in Python (Negation Trick)
```python
# Insert: negate the value
heapq.heappush(heap, -value)

# Pop: negate back
max_val = -heapq.heappop(heap)
```

---

## ⚙️ Key Operations

```python
import heapq

heap = []

# 1. INSERT — O(log N) — appends then bubbles up
heapq.heappush(heap, 5)
heapq.heappush(heap, 1)
heapq.heappush(heap, 3)
# heap = [1, 5, 3]

# 2. POP MINIMUM — O(log N) — swaps root with last, bubbles down
min_val = heapq.heappop(heap)  # returns 1

# 3. PEEK MINIMUM — O(1)
min_val = heap[0]  # no pop, just index

# 4. HEAPIFY (list → heap) — O(N)
nums = [5, 3, 1, 7, 9]
heapq.heapify(nums)
# nums = [1, 3, 5, 7, 9]
```

### Why O(log N) for push/pop?
- Tree height = log N
- Bubble up/down traverses at most one path root → leaf

---

## 🎯 Core Pattern — Top-K

### Why MIN-heap for K LARGEST?
- Min-heap keeps the **smallest of the K largest** at the top (the "bouncer")
- Any new element smaller than `heap[0]` → rejected immediately
- Memory stays **O(K)** instead of O(N) — critical for streaming data
- Time: **O(N log K)** vs sort's O(N log N)

```python
# Top-K Largest Template
heap = []
for num in nums:
    heapq.heappush(heap, num)
    if len(heap) > k:
        heapq.heappop(heap)  # evicts smallest
# heap contains K largest elements
# heap[0] = Kth largest
```

### Sort vs Heap — When it matters
| | Sort | Heap |
|---|---|---|
| Time | O(N log N) | O(N log K) |
| Space | O(1) | O(K) |
| Best for | Small N | Large N, small K |
| Streaming? | ❌ | ✅ |

**Interview line:** "Sort works but heap is O(N log K) — critical when K << N, especially in streaming pipelines."

---

## 💻 Problems Solved

### Problem 1 — LC 347: Top K Frequent Elements
```python
import heapq
from collections import Counter

def topKFrequent(nums, k):
    frequency = Counter(nums)
    
    heap = []
    for num, freq in frequency.items():
        heapq.heappush(heap, (freq, num))  # (freq, value) tuple
        if len(heap) > k:
            heapq.heappop(heap)
    
    return [num for freq, num in heap]

# Time: O(N log K) | Space: O(N) for counter + O(K) for heap
```

**Key insight:** Push `(freq, num)` tuples — heap sorts by first element (frequency).

---

### Boss Problem — Amazon Robot Monitor (Real-time Top-K with Lazy Deletion)

**Scenario:** Millions of warehouse robot sensor readings per second. Return K most overheating robots at any time. Robots send multiple readings — use latest temperature only.

```python
import heapq

class RobotMonitor:
    def __init__(self, k: int):
        self.k = k
        self.heap = []        # min-heap of (temp, robot_id)
        self.latest = {}      # {robot_id: latest_temp} — for lazy deletion

    def add_reading(self, robot_id: str, temperature: float):
        self.latest[robot_id] = temperature          # update latest
        heapq.heappush(self.heap, (temperature, robot_id))
        if len(self.heap) > self.k:
            heapq.heappop(self.heap)                 # evict smallest temp

    def get_top_k(self) -> list:
        result = []
        for temp, rid in self.heap:
            if temp == self.latest[rid]:             # skip stale entries
                result.append((temp, rid))
        return sorted(result, reverse=True)          # highest → lowest

# Time: O(N log K) add | O(K log K) get_top_k
# Space: O(K) heap + O(N) latest dict
```

**Lazy Deletion Pattern:**
- Don't remove stale entries from heap immediately (expensive)
- Instead, track `latest{}` hashmap
- On read, skip any heap entry where `temp != latest[robot_id]`
- Used in: real-time leaderboards (Amazon, Netflix, Uber)

**Test cases:**
```python
monitor = RobotMonitor(k=2)
monitor.add_reading("R1", 95.0)
monitor.add_reading("R2", 87.0)
monitor.add_reading("R3", 99.0)
monitor.add_reading("R4", 78.0)
monitor.add_reading("R5", 102.0)
monitor.add_reading("R1", 110.0)
print(monitor.get_top_k())  # [(110.0, 'R1'), (102.0, 'R5')] ✅

monitor2 = RobotMonitor(k=2)
monitor2.add_reading("R1", 95.0)
monitor2.add_reading("R2", 87.0)
monitor2.add_reading("R1", 20.0)  # R1 drops — stale entry filtered
print(monitor2.get_top_k())  # [(87.0, 'R2')] ✅
```

---

### LC 215 — Kth Largest Element in Array
```python
import heapq

class Solution:
    def findKthLargest(self, nums, k):
        heap = []
        for i in nums:
            heapq.heappush(heap, i)
            if len(heap) > k:
                heapq.heappop(heap)
        return heap[0]  # root = Kth largest

# Time: O(N log K) | Space: O(K)
# heap[0] after loop = smallest of K largest = Kth largest ✅
```

---

## 🔗 DE Connections

| Heap Use Case | Real System |
|---|---|
| Top-K frequent errors | Log monitoring (Datadog, CloudWatch) |
| Merge K sorted Parquet files | S3 data lake compaction |
| Priority task scheduling | Spark task scheduler |
| Real-time leaderboards | Amazon, Netflix, Uber |
| Streaming Top-K | Kafka consumer + Redis sorted sets |

---

## 🐛 Common Mistakes

1. **Negating for max-heap then using for Top-K** — negated values make min-heap evict your HIGHEST values ❌
2. **Sorting by wrong tuple element** — always put the comparison key FIRST in tuple `(key, value)`
3. **Heap logic in wrong method** — push/pop in `add()`, not in `get()`
4. **Using sort() instead of heap for streaming** — sort can't handle continuous data

---

## ⚡ Complexity Cheatsheet

| Operation | Time | Notes |
|---|---|---|
| heappush | O(log N) | Bubble up |
| heappop | O(log N) | Bubble down |
| heap[0] peek | O(1) | Just index 0 |
| heapify | O(N) | Better than N pushes |
| Top-K pattern | O(N log K) | K = heap size |
| Sort approach | O(N log N) | Worse when K << N |

---

## 📝 Warm-Up Recall (for tomorrow)

1. What is the index formula for left/right child of node at index `i`?
2. Why do we use a MIN-heap to find K LARGEST elements?
3. What is lazy deletion and when do you need it?
4. What's the time complexity difference between heap Top-K and sort?

---
*Week 4 Day 4 Complete ✅ | Commit: `week-04: day 4 complete - heaps/priority queues, LC347, LC215, robot monitor boss problem`*
