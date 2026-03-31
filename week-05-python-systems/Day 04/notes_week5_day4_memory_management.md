# Week 5 Day 4 — Memory Management & Linked Lists
**FAANG DE Prep | 13-Week Plan**

---

## 🧠 Core Theory

### sys.getsizeof()
- Returns size of a Python object in **bytes**
- Critical for DE — measure before choosing data structure

```python
from sys import getsizeof

my_list = [x for x in range(100_000)]
my_gen  = (x for x in range(100_000))

print(getsizeof(my_list))  # ~800,984 bytes (800KB)
print(getsizeof(my_gen))   # 192 bytes (always flat!)
```

### List vs Generator vs Tuple

| Structure | Memory | Use Case |
|---|---|---|
| List | O(N) ~800KB/100k | Small data, random access needed |
| Generator | O(1) ~192 bytes | Large/streaming data |
| Tuple | O(N) but smaller than list | Fixed, immutable data |

**Why tuple < list?**
- List pre-allocates extra buffer for future `.append()` (over-allocation)
- Tuple is fixed size — no buffer needed

**Generator is 4,000x+ smaller than list for 100k elements!**

### Interview Answer — List vs Generator
> "A list of 100k elements takes ~800KB. A generator takes 192 bytes — 4,000x smaller — because it yields one value at a time. For large DE pipelines, generators keep memory at O(1) vs O(N)."

---

## 💻 Problems Solved

### LC 141 — Linked List Cycle (Floyd's Algorithm)

```python
class Solution(object):
    def hasCycle(self, head):
        slow = head    # NOT self.head ← common mistake
        fast = head
        while fast and fast.next:
            slow = slow.next
            fast = fast.next.next
            if slow == fast:    # they met → cycle exists
                return True
        return False            # fast hit None → no cycle

# Time: O(N) | Space: O(1)
```

### LC 876 — Middle of Linked List

```python
class Solution(object):
    def middleNode(self, head):
        slow = head
        fast = head
        while fast and fast.next:
            slow = slow.next
            fast = fast.next.next
        return slow  # when fast hits end, slow is at middle

# Time: O(N) | Space: O(1)
# Returns node — LeetCode prints entire chain from that node
```

### LC 21 — Merge Two Sorted Lists

```python
class Solution(object):
    def mergeTwoLists(self, list1, list2):
        dummy = ListNode(0)   # placeholder start
        curr = dummy

        while list1 and list2:
            if list1.val <= list2.val:
                curr.next = list1
                list1 = list1.next
            else:
                curr.next = list2
                list2 = list2.next
            curr = curr.next      # ✅ inside loop!
        curr.next = list1 or list2  # append remaining
        return dummy.next

# Time: O(N+M) | Space: O(1)
```

---

### Boss Problem — Walgreens Rewards System

**Real-world insight:** Walgreens retrieves your rewards in split seconds using O(1) hash lookup — same as Python dict.

```python
import heapq

class RewardsSystem:
    def __init__(self):
        self.customers = {}  # phone → {name, points}

    def add_customer(self, phone, name, points):
        self.customers[phone] = {"name": name, "points": points}

    def get_customer(self, phone):
        return self.customers[phone]          # O(1) hash lookup ✅

    def add_points(self, phone, points):
        self.customers[phone]["points"] += points  # O(1) update ✅

    def top_customers(self, k):
        result = heapq.nlargest(k, self.customers.items(),
                                key=lambda x: x[1]["points"])
        return [(data["name"], data["points"]) for phone, data in result]
        # O(N log K) ✅

# Usage:
rewards = RewardsSystem()
rewards.add_customer("913-278-3519", "Deepak", 250)
rewards.add_points("913-278-3519", 100)
rewards.top_customers(2)  # → [("Deepak", 350), ("Jane", 320)]
```

**Key patterns:**
- `heapq.nlargest(k, iterable, key=...)` — cleaner than manual heap for Top-K from dict
- `heapq.heapify()` returns `None` — never assign it to a variable ⚠️

---

## 🎯 Fast/Slow Pointer Pattern

| Problem | Fast | Slow | Stop | Result |
|---|---|---|---|---|
| LC 141 Cycle | 2 steps | 1 step | fast == slow | True/False |
| LC 876 Middle | 2 steps | 1 step | fast hits None | middle node |

---

## ⚠️ Common Mistakes

1. **`self.head` in LeetCode** — head is a parameter, never `self.head` ❌
2. **`curr = curr.next` outside loop** — must be inside while loop in merge
3. **`heapq.heapify()` returns None** — never assign: `x = heapq.heapify(lst)` ❌
4. **Heapifying a dict** — only heapifies keys, use `.items()` with `key=` instead
5. **List for large data** — generator is 4,000x smaller, always prefer for streaming

---

## 🔗 Real World Connections

| Concept | Real System |
|---|---|
| O(1) hash lookup | Walgreens/CVS/Starbucks rewards |
| Dict as hash map | Redis cache, Kafka partition keys |
| Generator O(1) memory | Spark lazy evaluation, streaming ETL |
| Top-K heap | Leaderboards, monitoring dashboards |
| Linked List cycle | Detecting infinite loops in DAGs |

---

## 📝 Warm-Up Recall (for tomorrow)

1. What does `sys.getsizeof()` return for a generator of 1M elements?
2. In Floyd's cycle detection, what does it mean when slow == fast?
3. Why must `curr = curr.next` be inside the while loop in merge two lists?
4. Why does `heapq.heapify()` return None?
5. What's the correct way to use `heapq.nlargest` with a custom key?

---
*Week 5 Day 4 Complete ✅*
*Commit: `week-05: day 4 complete - memory management, LC141, LC876, LC21, rewards system`*
