# Week 4 — Day 1: Hash Maps (Dicts)
**Date:** 2026-03-06
**Status:** ✅ Complete

---

## What is a HashMap?

> *"A HashMap is a key-value data structure that uses a hash function to map keys to array indices — giving O(1) average lookup, insert, and delete."*

```python
# Pure hashmap (key → single value)
{"Alice": 95000, "Bob": 87000}

# Hashmap of lists (grouping pattern)
{"birds": ["crow", "hen", "sparrow"], "pets": ["cat", "dog"]}
```

---

## How it Works Internally

```
dict["Alice"] = 95000

Step 1: hash("Alice")      → 48293    (hash function)
Step 2: 48293 % array_size → index 7  (find slot)
Step 3: store 95000 at index 7

Lookup:
dict["Alice"] → hash → index 7 → 95000 in O(1)!
```

**Collision** — two keys hash to same index → Python handles with chaining (linked list at that slot)

---

## Complexity — Why it Beats List Every Time

| Operation | Dict | List | Why |
|---|---|---|---|
| Lookup by key | O(1) | O(n) | Dict hashes → direct index |
| Insert | O(1) | O(1) append | Dict hashes key → slot |
| Delete | O(1) | O(n) | Dict unlinks, List shifts |
| Membership check | O(1) | O(n) | `x in dict` = hash, `x in list` = scan |

---

## The 3 Core Patterns

### Pattern 1 — Frequency Count
```python
from collections import Counter

words = ["apple", "banana", "apple", "cherry"]
freq = Counter(words)
# {'apple': 2, 'banana': 1, 'cherry': 1}

# Top k most common:
freq.most_common(2)
# [('apple', 2), ('banana', 1)]
```

### Pattern 2 — Two Sum (O(n) lookup)
```python
def two_sum(nums, target):
    seen = {}                          # {value: index}
    for i, n in enumerate(nums):
        complement = target - n        # what do I NEED?
        if complement in seen:         # have I SEEN it? O(1)!
            return [seen[complement], i]
        seen[n] = i                    # store for future

# Mental model:
# "For every number, ask: have I already seen its perfect partner?"
```

### Pattern 3 — Grouping (Python GROUP BY)
```python
from collections import defaultdict

data = [
    {"name": "Alice", "dept": "Engineering"},
    {"name": "Bob",   "dept": "Marketing"},
    {"name": "Carol", "dept": "Engineering"},
]

groups = defaultdict(list)
for item in data:
    groups[item["dept"]].append(item["name"])
# {"Engineering": ["Alice", "Carol"], "Marketing": ["Bob"]}
# This is exactly SQL GROUP BY — in Python!
```

---

## Key Built-ins to Memorize

```python
# Safe get with default (never KeyError)
dict.get(key, 0)          # returns 0 if key missing
dict.get(key, [])         # returns [] if key missing

# defaultdict — auto-creates default value
defaultdict(list)         # auto-creates [] for new keys
defaultdict(int)          # auto-creates 0 for new keys

# Counter
Counter("aabbc")          # {'a':2, 'b':2, 'c':1}
Counter.most_common(k)    # top k elements in O(n log k)

# Safe counter update pattern
dict[key] = dict.get(key, 0) + 1

# Sort dict by values
max(d, key=d.get)                          # key with max value
sorted(d.items(), key=lambda x: x[1])     # sort by value ASC
sorted(d.items(), key=lambda x: -x[1])    # sort by value DESC
{k: len(v) for k, v in d.items()}         # count list lengths
```

---

## Common Mistakes

| Mistake | What happens | Fix |
|---|---|---|
| `dict[key]` on missing key | KeyError crashes | `dict.get(key, default)` |
| `dict.get[key]` square brackets | TypeError | `dict.get(key)` parentheses! |
| `i.split(':')` result not saved | Split ignored | `parts = i.split(':')` |
| `i[0]` on string = first char | Wrong value | `parts[0]` after split |
| Modifying dict while iterating | RuntimeError | `list(dict.keys())` |
| Using list as dict key | TypeError unhashable | Convert to `tuple` |
| Counter on dict of lists | Counts keys not lengths | `{k: len(v) for k,v in d.items()}` |

---

## Boss Problem 1 — Leaderboard

```python
class Leaderboard:
    def __init__(self):
        self.scores = {}

    def add_score(self, player, score):
        # Safe update — add to existing or start from 0
        self.scores[player] = self.scores.get(player, 0) + score

    def top(self, k):
        # Sort by score descending, take first k
        return sorted(self.scores.values(), reverse=True)[:k]

# Complexity:
# add_score → O(1)
# top(k)    → O(n log n)
```

---

## Boss Problem 2 — Log Analyzer

```python
import collections
from collections import Counter

class LogManager:
    def __init__(self):
        self.logsd = collections.defaultdict(list)

    def add_log(self, key, value):
        self.logsd[key].append(value)

    def get_counts(self):
        for key, messages in self.logsd.items():
            print(f"{key}: {len(messages)}")

    def most_frequent(self):
        return max(self.logsd, key=lambda k: len(self.logsd[k]))

    def get_errors(self):
        return self.logsd.get("ERROR")

if __name__ == '__main__':
    manager = LogManager()
    logs = [
        "ERROR: database connection failed",
        "INFO: user logged in",
        "ERROR: timeout exceeded",
        "WARNING: disk space low",
        "INFO: request completed",
        "ERROR: null pointer exception",
        "INFO: cache refreshed"
    ]
    for i in logs:
        parts = i.split(':')
        manager.add_log(parts[0], parts[1].strip())  # .strip() removes spaces!

    print(manager.logsd)
    manager.get_counts()
    print(manager.most_frequent())
    print(manager.get_errors())
```

---

## LeetCode Solutions

### LC 1 — Two Sum ✅ 10/10
```python
class Solution:
    def twoSum(self, nums, target):
        seen = {}
        for i, n in enumerate(nums):
            complement = target - n
            if complement in seen:
                return [seen[complement], i]
            seen[n] = i
# Time: O(n) | Space: O(n)
```

### LC 49 — Group Anagrams ✅ 10/10
```python
from collections import defaultdict
class Solution:
    def groupAnagrams(self, strs):
        groups = defaultdict(list)
        for s in strs:
            key = ''.join(sorted(s))
            groups[key].append(s)
        return list(groups.values())
# Time: O(n × k log k) | Space: O(n × k)
```

### LC 383 — Ransom Note ✅ 10/10
```python
from collections import Counter
class Solution:
    def canConstruct(self, ransomNote, magazine):
        mag = Counter(magazine)
        for char in ransomNote:
            mag[char] -= 1
            if mag[char] < 0:
                return False
        return True
# Time: O(n) | Space: O(1) — only 26 letters
```

---

## The Golden Rule

> *"Every time you see an O(n²) nested loop — ask yourself: can a hashmap solve this in O(n)? Pre-load the data you'll need to look up, then scan once."*

---

## DE Connection

HashMap = how **Spark shuffle** works internally. When Spark does a GROUP BY or JOIN, it hashes the key column to distribute rows across partitions — exactly the same concept as Python dicts. Understanding hashmaps = understanding distributed data processing at scale.

---

## Commit

```bash
git add .
git commit -m "week-04: day 1 complete - hashmaps, two sum, log analyzer, ransom note"
git push
```
