# Week 4 — Day 3: Sliding Window
**Date:** 2026-03-09
**Status:** ✅ Complete

---

## What is Sliding Window?

> *"Sliding window converts O(n²) nested loop problems into O(n) single pass solutions by avoiding redundant recalculation. Instead of recomputing the entire window, just add the incoming element and remove the outgoing one."*

**DE Connection:** Same concept as SQL Rolling Window — but Python version can expand AND shrink dynamically!

```
SQL Rolling Window:   fixed frame, slides over sorted data
Python Sliding Window: variable OR fixed, expands and shrinks
```

---

## Two Types of Sliding Window

### Type 1 — Fixed Size
- Window size K is given
- Always add right, remove left
- Use when: "subarray/substring of size K"

### Type 2 — Variable Size
- Window size changes based on condition
- Expand right until condition breaks
- Shrink left until condition is valid again
- Use when: "longest/shortest subarray satisfying condition"

---

## Fixed Size Template

```python
def fixed_window(arr, k):
    window_sum = sum(arr[:k])  # first window
    result = window_sum

    for i in range(k, len(arr)):
        window_sum += arr[i]      # add incoming (right)
        window_sum -= arr[i - k]  # remove outgoing (left)
        result = max(result, window_sum)

    return result

# Key formula: just add new, subtract old — no recalculation!
```

---

## Variable Size Template

```python
def variable_window(arr):
    left = 0
    result = 0
    window_state = {}  # track what's inside window

    for right in range(len(arr)):
        # Step 1 — ADD right element to window
        window_state[arr[right]] = window_state.get(arr[right], 0) + 1

        # Step 2 — SHRINK from left if condition breaks
        while window_is_invalid:
            window_state[arr[left]] -= 1
            left += 1

        # Step 3 — UPDATE result
        result = max(result, right - left + 1)

    return result

# Window size formula: right - left + 1
# Why while not if: need to keep shrinking until valid!
```

---

## Common Mistakes

| Mistake | Fix |
|---|---|
| Forgetting `left += 1` | Always increment left when shrinking |
| Wrong window size | `right - left + 1` not `right - left` |
| Using `if` instead of `while` | `while` keeps shrinking until valid |
| Not initializing first window | Sum first k elements before loop |
| `list.pop(0)` instead of `deque.popleft()` | deque = O(1), list = O(n) |

---

## Practice Problems

### Fixed Window — Max Sum Subarray of size K ✅ 9.5/10

```python
def max_sum(nums, k):
    window_sum = sum(nums[:k])
    best = window_sum

    for i in range(k, len(nums)):
        window_sum += nums[i]     # add incoming
        window_sum -= nums[i-k]   # remove outgoing
        best = max(best, window_sum)

    return best

# nums=[1,4,2,9,7,3], k=3
# [1,4,2]=7 → [4,2,9]=15 → [2,9,7]=18 → [9,7,3]=19
# Answer: 19
# Time: O(n) | Space: O(1)
```

### Variable Window — LC 3: Longest Substring Without Repeating Characters ✅ 10/10

```python
def lengthOfLongestSubstring(s):
    left = 0
    seen = {}
    result = 0

    for right in range(len(s)):
        # Add right char
        seen[s[right]] = seen.get(s[right], 0) + 1

        # Shrink left if duplicate
        while seen[s[right]] > 1:
            seen[s[left]] -= 1
            left += 1

        # Update result
        result = max(result, right - left + 1)

    return result

# "abcabcbb" → 3 ("abc")
# Time: O(n) — each char visited at most twice
# Space: O(k) — k unique chars in window
```

---

## Boss Problem — Rate Limiter ✅ 10/10

```python
from collections import defaultdict, deque

class RateLimiter:
    def __init__(self, max_requests, window_size):
        self.max_requests = max_requests  # e.g. 3
        self.window_size = window_size    # e.g. 10 seconds
        self.windows = defaultdict(deque) # each user gets own queue

    def is_allowed(self, user_id, timestamp):
        # Step 1 — Remove timestamps outside window
        while self.windows[user_id] and \
              timestamp - self.windows[user_id][0] >= self.window_size:
            self.windows[user_id].popleft()  # remove oldest ← O(1)!

        # Step 2 — Check if allowed
        if len(self.windows[user_id]) < self.max_requests:
            self.windows[user_id].append(timestamp)
            return True   # ✅ allowed

        return False      # ❌ blocked

# Test:
requests = [
    {"user_id": "u1", "timestamp": 1},
    {"user_id": "u1", "timestamp": 4},
    {"user_id": "u1", "timestamp": 8},
    {"user_id": "u1", "timestamp": 9},   # BLOCKED
    {"user_id": "u2", "timestamp": 5},
    {"user_id": "u1", "timestamp": 12},  # ALLOWED
]

limiter = RateLimiter(max_requests=3, window_size=10)
for req in requests:
    result = limiter.is_allowed(req["user_id"], req["timestamp"])
    print(f"u={req['user_id']} t={req['timestamp']} → {result}")

# Output:
# u1 t=1  → True  ✅
# u1 t=4  → True  ✅
# u1 t=8  → True  ✅
# u1 t=9  → False ❌ correctly blocked!
# u2 t=5  → True  ✅
# u1 t=12 → True  ✅ correctly allowed after window slides!
```

**Why deque over list?**
```
deque.popleft() = O(1)  ← use this!
list.pop(0)     = O(n)  ← never use for queues!
```

**This pattern runs in production at:**
- Amazon API Gateway → rate limiting per API key
- Twitter → 300 tweets per 3 hours
- Stripe → 100 requests per second
- Netflix → stream requests per user

---

## The Two Key Insights

**Insight 1 — popleft() removes OLD timestamps, not exceeded ones:**
```
popleft() fires when: timestamp - oldest >= window_size
NOT when: count exceeds limit
Two separate jobs — clean first, then check limit!
```

**Insight 2 — deque is a double-ended queue:**
```
append()    → add to RIGHT  (newest)
popleft()   → remove LEFT   (oldest)
[0]         → peek oldest   (left end)
[-1]        → peek newest   (right end)
```

---

## Interview Gold Line

> *"Sliding window converts O(n²) to O(n) by maintaining a running state — instead of recomputing the entire window each time, I add the incoming element and remove the outgoing one. For variable windows, I expand right always and shrink left only when the condition breaks."*

---

## Commit

```bash
git add .
git commit -m "week-04: day 3 complete - sliding window, rate limiter boss problem"
git push
```
