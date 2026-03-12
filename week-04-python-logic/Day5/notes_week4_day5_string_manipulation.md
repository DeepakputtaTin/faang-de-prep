# Week 4 Day 5 — String Manipulation
**FAANG DE Prep | 13-Week Plan**

---

## 🧠 Core Theory

### String Operations in Python
- `strip()`, `lstrip()`, `rstrip()` — remove whitespace/chars
- `split(delimiter)` — split into list
- `''.join(list)` — join list into string
- `sorted(string)` — returns sorted list of characters
- `s[i]` — index access O(1)
- `s[start:end]` — slicing

### Key Algorithmic Patterns

| Pattern | Use Case | Key Trick |
|---|---|---|
| Sort as Hash Key | Group Anagrams | `''.join(sorted(word))` |
| Sliding Window + Counter | Find All Anagrams | Add right, remove left, compare |
| Split + Parse | Log ETL | `split('=')[1]` for key=value pairs |

---

## 🎯 Pattern 1 — Sort as Hash Key

**Insight:** Two words are anagrams if their sorted characters are identical.
```
"eat" → sorted → "aet"
"tea" → sorted → "aet"  ← same key!
"tan" → sorted → "ant"  ← different key
```

**Template:**
```python
from collections import defaultdict

groups = defaultdict(list)
for word in words:
    key = ''.join(sorted(word))   # sort chars → hash key
    groups[key].append(word)
return list(groups.values())
```

**Complexity:** O(N · K log K) — N words, each sorted in K log K

---

## 🎯 Pattern 2 — Sliding Window + Counter

**Insight:** Maintain a running counter — don't rebuild from scratch each slide.

```
s = "cbaebabacd", p = "abc" (len=3)

Step 0: window = "cba" → check
Step 1: add s[3]='e', remove s[0]='c' → window = "bae" → check
Step 2: add s[4]='b', remove s[1]='b' → window = "aeb" → check
```

**At step i:**
- Add: `s[i + len(p) - 1]` (new right char)
- Remove: `s[i - 1]` (old left char)

**Template:**
```python
from collections import Counter

def findAnagrams(s, p):
    result = []
    p_count = Counter(p)
    window_count = Counter(s[:len(p)])

    if window_count == p_count:
        result.append(0)

    for i in range(1, len(s) - len(p) + 1):
        window_count[s[i + len(p) - 1]] += 1      # add right
        window_count[s[i - 1]] -= 1                # remove left
        if window_count[s[i - 1]] == 0:
            del window_count[s[i - 1]]             # clean zeros
        if window_count == p_count:
            result.append(i)

    return result
```

**Complexity:** O(N) time | O(K) space (K = unique chars in p, max 26)

---

## 💻 Problems Solved

### Problem 1 — LC 49: Group Anagrams
```python
from collections import defaultdict

def groupAnagrams(strs):
    groups = defaultdict(list)
    for word in strs:
        key = ''.join(sorted(word))
        groups[key].append(word)
    return list(groups.values())

# Input:  ["eat","tea","tan","ate","nat","bat"]
# Output: [["eat","tea","ate"],["tan","nat"],["bat"]]
# Time: O(N·K log K) | Space: O(N·K)
```

---

### Problem 2 — LC 438: Find All Anagrams in a String
```python
from collections import Counter

class Solution:
    def findAnagrams(self, s, p):
        result = []
        p_count = Counter(p)
        window_count = Counter(s[:len(p)])

        if window_count == p_count:
            result.append(0)

        for i in range(1, len(s) - len(p) + 1):
            window_count[s[i + len(p) - 1]] += 1
            window_count[s[i - 1]] -= 1
            if window_count[s[i - 1]] == 0:
                del window_count[s[i - 1]]
            if window_count == p_count:
                result.append(i)

        return result

# Input: s="cbaebabacd", p="abc" → Output: [0, 6]
# Time: O(N) | Space: O(K)
```

---

### Boss Problem — Meta Log Analyzer (String + Hashmap + Heap)

**Scenario:** Parse millions of raw server logs, group by template, return Top 3 most frequent.

```python
import heapq
from collections import defaultdict

def analyze_logs(logs):
    log = defaultdict(int)
    heap = []

    # Step 1: parse + count templates
    for i in logs:
        a = i.split()
        b = a[2].split('=')[1]   # extract action value
        c = a[3].split('=')[1]   # extract msg value
        elog = a[0] + ' ' + b + ' ' + c  # template key
        log[elog] += 1

    # Step 2: Top-3 via min-heap
    for temp, count in log.items():
        heapq.heappush(heap, (count, temp))
        if len(heap) > 3:
            heapq.heappop(heap)

    # Step 3: return sorted highest → lowest
    return sorted([(t, c) for c, t in heap], key=lambda x: -x[1])

# Input:
logs = [
    "ERROR user=123 action=login msg=timeout",
    "WARN  user=456 action=checkout msg=retry",
    "ERROR user=789 action=login msg=timeout",
    "INFO  user=123 action=logout msg=success",
    "ERROR user=456 action=login msg=timeout"
]
# Output: [('ERROR login timeout', 3), ('INFO logout success', 1), ('WARN checkout retry', 1)]
# Time: O(N + M log 3) | Space: O(M)
```

**Key parsing trick:**
```python
"action=login".split('=')[1]  # → "login" ✅
# Better than hardcoded slicing s[7:] ✅
```

---

## 🔗 DE Connections

| String Pattern | Real DE Use Case |
|---|---|
| Sort as hash key | Deduplicating schema variants in data catalog |
| Sliding window + counter | Real-time log pattern detection |
| Split + parse | ETL cleaning (fname/lname, key=value logs) |
| Template grouping | Log aggregation (Datadog, CloudWatch, Splunk) |
| Counter comparison | Schema drift detection |

---

## 🐛 Common Mistakes

1. **Hardcoded slicing** — `s[7:]` breaks when key length changes. Use `split('=')[1]` instead
2. **Rebuilding Counter each slide** — O(K) per step. Maintain running counter instead
3. **Heap logic inside parsing loop** — build hashmap fully first, then heap
4. **Pushing wrong thing to heap** — push `(count, template)` not the whole dict

---

## ⚡ Complexity Cheatsheet

| Operation | Time | Notes |
|---|---|---|
| Sort word as key | O(K log K) | K = word length |
| Group N anagrams | O(N · K log K) | N words |
| Sliding window | O(N) | Single pass |
| Counter comparison | O(K) | K = unique chars |
| Log parse + Top-K | O(N + M log K) | M = unique templates |

---

## 📝 Warm-Up Recall (for tomorrow — Mock Assessment)

1. How do you detect if two strings are anagrams without sorting?
2. In sliding window, at step `i`, what index is the new right char? Old left char?
3. Why use `split('=')[1]` instead of hardcoded slicing?
4. What's the time complexity of grouping N anagrams of average length K?

---
*Week 4 Day 5 Complete ✅ | Commit: `week-04: day 5 complete - string manipulation, LC49, LC438, meta log analyzer boss problem`*
