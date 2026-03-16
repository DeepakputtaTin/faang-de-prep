# Week 4 Day 6 — Mock Assessment
**FAANG DE Prep | 13-Week Plan**

---

## 📊 Assessment Results

| Problem | Approach | Score |
|---|---|---|
| LC 560 — Subarray Sum Equals K | Brute Force + Prefix Sum | 9.5/10 |
| LC 3 — Longest Substring Without Repeating | Variable Sliding Window + Set | 10/10 |
| LC 242 — Valid Anagram | Counter + Sorted | 10/10 |
| **Overall** | | **9.8/10** ✅ |

---

## 💻 Problems Solved

### LC 560 — Subarray Sum Equals K

**Brute Force — O(N²):**
```python
def subsum_bf(nums, k):
    res = 0
    for i in range(len(nums)):
        cs = 0
        for j in range(i, len(nums)):
            cs += nums[j]
            if cs == k:
                res += 1
    return res
```

**Optimal — Prefix Sum + HashMap — O(N):**
```python
def subsum_prefix(nums, k):
    res = cursum = 0
    prefixSums = {0: 1}  # handles subarrays starting from index 0
    for num in nums:
        cursum += num
        diff = cursum - k
        res += prefixSums.get(diff, 0)
        prefixSums[cursum] = 1 + prefixSums.get(cursum, 0)
    return res
```

**Key insight:**
- `prefix[j] - prefix[i] = k` → `prefix[i] = prefix[j] - k`
- At each step ask: "how many previous prefix sums equal `cursum - k`?"
- Initialize `{0: 1}` — handles subarrays starting from index 0
- Works for **negative numbers** — sliding window does NOT ⚠️

**Why sliding window fails here:**
- Sliding window assumes shrinking window reduces sum
- With negatives, removing left element might increase sum
- Always ask: "can this array have negatives?" before choosing sliding window

---

### LC 3 — Longest Substring Without Repeating Characters

```python
def lengthOfLongestSubstring(s):
    char_set = set()
    left = 0
    max_len = 0

    for right in range(len(s)):
        while s[right] in char_set:
            char_set.remove(s[left])
            left += 1
        char_set.add(s[right])
        max_len = max(max_len, right - left + 1)
    return max_len

# "abcabcbb" → 3
# "bbbbb"    → 1
# "pwwkew"   → 3
# Time: O(N) | Space: O(K) K = unique chars
```

**Pattern:** Variable sliding window + Set for O(1) duplicate check
- Expand right until duplicate found
- Shrink left until duplicate removed
- Track max window size throughout

---

### LC 242 — Valid Anagram

```python
from collections import Counter

# Approach 1 — Counter O(N) time, O(K) space
def isAnagram(s, t):
    return Counter(s) == Counter(t)

# Approach 2 — Sorted O(N log N) time, O(N) space
def isAnagram_sorted(s, t):
    return sorted(s) == sorted(t)

# Counter wins at scale ✅
```

---

## 🧠 Week 4 Pattern Summary

| Topic | Key Pattern | Gotcha |
|---|---|---|
| Hash Maps | Two Sum, frequency count | O(1) lookup vs O(N) list |
| Sets | Dedup, membership check | No duplicates, unordered |
| Sliding Window | Fixed/variable window | Fails with negative numbers |
| Heaps | Top-K, min/max tracking | Min-heap for K largest |
| Strings | Sort as key, sliding window | split('=')[1] over hardcoding |

---

## ⚠️ Key Warnings

1. **Sliding window + negatives = wrong** — use prefix sum instead
2. **Always give brute force first** — shows trade-off thinking
3. **Initialize prefixSums = {0: 1}** — never forget this for subarray problems
4. **Counter vs sorted** — Counter O(N) beats sorted O(N log N) at scale

---

## 📝 Warm-Up Recall (for Week 5)

1. Why does sliding window fail for arrays with negative numbers?
2. What does `{0: 1}` initialization mean in the prefix sum approach?
3. What's the time complexity difference between Counter and sorted for anagram check?
4. In variable sliding window, when do you shrink from the left?

---
*Week 4 Day 6 Complete ✅ | Mock Assessment: 9.8/10*
*Commit: `week-04: day 6 complete - mock assessment, LC560, LC3, LC242`*
