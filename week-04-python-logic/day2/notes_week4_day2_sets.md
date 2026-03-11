# Week 4 — Day 2: Sets & Deduplication
**Date:** 2026-03-06
**Status:** ✅ Complete

---

## What is a Set?

> *"A Set is an unordered collection of UNIQUE elements backed by a hash table — giving O(1) average lookup, insert, and delete. No duplicates allowed, no guaranteed order."*

---

## How Sets Work Internally

Same as HashMap — but stores only keys, no values!

```python
s = {1, 2, 3}

add(4)    → hash(4) → index → store   O(1)
remove(2) → hash(2) → index → delete  O(1)
4 in s    → hash(4) → index → check   O(1)
```

---

## Set vs List vs Dict

| Operation | Set | List | Dict |
|---|---|---|---|
| Membership `x in s` | O(1) | O(n) | O(1) |
| Add | O(1) | O(1) append | O(1) |
| Remove | O(1) | O(n) | O(1) |
| Duplicates | ❌ Never | ✅ Allowed | ❌ Keys unique |
| Order | ❌ No | ✅ Yes | ✅ Yes (3.7+) |

---

## The 4 Set Operations

```python
A = {1, 2, 3, 4}
B = {3, 4, 5, 6}

A | B   # Union          → {1,2,3,4,5,6}  everything
A & B   # Intersection   → {3,4}          overlap only
A - B   # Difference     → {1,2}          A only
A ^ B   # Symmetric diff → {1,2,5,6}      non-overlap
```

**Visual:**
```
A = [1, 2, 3, 4]
B =       [3, 4, 5, 6]

A | B = [1, 2, 3, 4, 5, 6]  ← everything
A & B =       [3, 4]         ← overlap only
A - B = [1, 2]               ← A only
A ^ B = [1, 2,       5, 6]  ← non-overlap
```

---

## The 3 Core Patterns

### Pattern 1 — Deduplication

```python
# Simple dedup (order NOT preserved)
nums = [1,2,2,3,3,3,4]
unique = list(set(nums))
# [1,2,3,4] ✅ but order not guaranteed!

# Ordered dedup (order preserved) ⭐
seen = set()
unique = []
for n in nums:
    if n not in seen:   # O(1) lookup
        unique.append(n)
        seen.add(n)
# [1,2,3,4] ✅ order preserved!
```

> *"Use a list to STORE ordered results. Use a set to CHECK membership. Never check membership against a list — O(n) vs O(1)!"*

### Pattern 2 — Fast Membership Check

```python
# ❌ Slow — O(n) per lookup
banned_list = ["spam1", "spam2", "spam3"]
if email in banned_list:   # scans entire list!

# ✅ Fast — O(1) per lookup
banned_set = {"spam1", "spam2", "spam3"}
if email in banned_set:    # instant!
```

### Pattern 3 — Missing/Extra Elements

```python
expected = {1,2,3,4,5}
actual   = {1,2,4,5}

missing = expected - actual   # {3}
extra   = actual - expected   # {}
```

---

## Extract Digits Without Strings (Interview Trick!)

```python
# ❌ String approach (interviewer might ban this!)
digits = [int(d) for d in str(n)]

# ✅ Math approach — no strings!
def get_digits(n):
    digits = []
    while n > 0:
        digits.append(n % 10)   # last digit
        n = n // 10             # remove last digit
    return digits

# Pattern to memorize:
# % 10 → last digit
# // 10 → remove last digit
# Repeat until 0
```

---

## Common Mistakes

| Mistake | Fix |
|---|---|
| `{}` creates dict not set | Use `set()` for empty set |
| `set()` loses order | Use seen set + list pattern |
| Adding dict to set → TypeError | Track dict's ID field instead |
| Assuming set is sorted | Sets have no guaranteed order |
| Sets are unhashable | Use `frozenset` as dict key |

---

## LeetCode Solutions

### LC 349 — Intersection of Two Arrays ✅ 10/10

```python
class Solution:
    def intersection(self, nums1, nums2):
        return list(set(nums1) & set(nums2))
# Time: O(n+m) | Space: O(n+m)
```

### LC 202 — Happy Number ✅ 10/10

```python
# With string conversion
def isHappy(n):
    seen = set()
    while n != 1:
        if n in seen:
            return False
        seen.add(n)
        n = sum(int(d)**2 for d in str(n))
    return True

# Without string conversion (interview hard mode!)
def get_sum(n):
    total = 0
    while n > 0:
        digit = n % 10
        total += digit ** 2
        n = n // 10
    return total

def isHappy(n):
    seen = set()
    while n != 1:
        if n in seen:
            return False
        seen.add(n)
        n = get_sum(n)
    return True

# Time: O(log n) | Space: O(log n)
```

### LC 128 — Longest Consecutive Sequence ✅ 10/10

```python
class Solution:
    def longestConsecutive(self, nums):
        s1 = set(nums)
        count = 0

        for n in s1:
            if (n-1) not in s1:      # start of sequence only!
                length = 1
                while (n+1) in s1:   # count forward
                    length += 1
                    n += 1
                count = max(count, length)

        return count

# Key insight: only start counting from sequence beginnings
# Each number visited at most twice → O(n)!
# Time: O(n) | Space: O(n)
```

---

## Boss Problem — Data Pipeline Deduplication ✅ 10/10

```python
from collections import Counter

def deduplication(mobile_events, web_events):
    # Step 1 — Deduplicate by event_id
    seen_ids = set()
    unique_events = []
    for event in mobile_events + web_events:
        if event["event_id"] not in seen_ids:
            seen_ids.add(event["event_id"])
            unique_events.append(event)
    print(f"Unique events: {len(unique_events)}")

    # Step 2 — Most active user
    user_counts = Counter([e["user_id"] for e in unique_events])
    most_active = user_counts.most_common(1)[0][0]
    print(f"Most active: {most_active}")

    # Step 3 — Users on BOTH platforms
    mobile_users = {e["user_id"] for e in mobile_events}
    web_users    = {e["user_id"] for e in web_events}
    both = mobile_users.intersection(web_users)
    print(f"Both platforms: {both}")
```

**This pattern runs in production at:**
- Kafka deduplication pipelines
- Spark streaming exactly-once processing
- AWS Lambda event dedup with DynamoDB

---

## The Golden Rules of Sets

1. **Membership check** → always use set, never list
2. **Dedup with order** → seen set + result list
3. **Overlap between streams** → intersection `&`
4. **Missing elements** → difference `-`
5. **Can't add dict to set** → track the ID field instead
6. **Empty set** → `set()` not `{}`

---

## DE Connection

> *"Sets are how Spark handles deduplication at scale — `df.distinct()` internally uses a hash set per partition, then merges across partitions. Same O(1) lookup principle, distributed across 1000 nodes. Understanding sets = understanding distributed dedup."*

---

## Commit

```bash
git add .
git commit -m "week-04: day 2 complete - sets, deduplication, happy number, longest consecutive"
git push
```
