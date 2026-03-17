# Week 5 Day 1 — Generators & Recursive Parsing
**FAANG DE Prep | 13-Week Plan**

---

## 🧠 Core Theory

### What is a Generator?
- A function that uses `yield` instead of `return`
- **Pauses** execution after each `yield`, resumes from same spot next call
- Never materializes all data in memory — produces one value at a time
- Memory: **O(1)** vs list's O(N)

### yield vs return
| | return | yield |
|---|---|---|
| Memory | All at once | One at a time |
| Execution | Runs to end | Pauses, resumes |
| Use case | Small data | Large/infinite data |
| Memory complexity | O(N) | O(1) |

### Why Generators Matter for DE
- 10 billion row log file → can't load into memory
- Filter at **read time**, not after load
- Foundation of lazy evaluation in Spark, Apache Beam
- Push-down computation — process where data lives

---

## 💻 Problems Solved

### Problem 1 — read_massive_file() Generator

```python
def read_massive_file(filename):
    with open(filename, 'r') as file:
        for line in file:
            cleaned = line.strip()
            if cleaned:          # skip empty lines
                yield cleaned    # one line at a time

# Consuming — O(1) memory ✅
for row in read_massive_file('abc.csv'):
    print(row)  # validate, transform, load

# Never do this for large files ❌
rows = list(read_massive_file('abc.csv'))  # defeats the purpose
```

**Real pipeline pattern:**
```
read_massive_file() → validate() → transform() → load()
```
Each step a generator — data flows one row at a time. Never fully materialized.

---

### Bonus — flatten_json() Recursive Parser

**Scenario:** Patient records arrive as deeply nested JSON. Analytics team needs flat table.

```python
def flatten_json(nested, parent_key="", result=None):
    if result is None:
        result = {}  # ⚠️ never use mutable default arg result={}

    for key, value in nested.items():
        new_key = parent_key + "_" + key if parent_key else key

        if isinstance(value, dict):
            flatten_json(value, new_key, result)  # recurse deeper
        else:
            result[new_key] = value               # store leaf value

    return result

# Input:
nested = {
    "patient_id": "P123",
    "name": "John",
    "conditions": {
        "primary": {
            "disease": "diabetes",
            "severity": {
                "level": "high",
                "score": 8
            }
        }
    }
}

# Output:
# {
#   "patient_id": "P123",
#   "name": "John",
#   "conditions_primary_disease": "diabetes",
#   "conditions_primary_severity_level": "high",
#   "conditions_primary_severity_score": 8
# }
```

**Complexity:** O(N) time | O(D) space — D = max nesting depth

**Key recursive pattern:**
- Base case: value is not a dict → store it
- Recursive case: value is dict → go deeper with new key prefix

---

## ⚠️ Critical Python Gotcha — Mutable Default Arguments

```python
# WRONG ❌ — same dict reused across all calls
def flatten_json(nested, parent_key="", result={}):
    ...

# CORRECT ✅ — fresh dict created each call
def flatten_json(nested, parent_key="", result=None):
    if result is None:
        result = {}
```

**Rule:** Never use mutable objects (dict, list) as default arguments in Python.

---

## 🔗 DE Connections

| Concept | Real DE Use Case |
|---|---|
| Generator | Reading massive CSV/log files in ETL |
| yield | Spark's lazy evaluation, Apache Beam |
| Recursive JSON flatten | Kafka event normalization before Snowflake load |
| Flatten patient records | Healthcare data lake pipelines |
| Push-down computation | Filter at source, not after load |

---

## 📝 Warm-Up Recall (for tomorrow)

1. What keyword makes a function a generator?
2. Why is `result=None` safer than `result={}` as a default argument?
3. In `flatten_json`, what is the base case and recursive case?
4. Why should you never call `list()` on a generator for a 10B row file?

---
*Week 5 Day 1 Complete ✅*
*Commit: `week-05: day 1 complete - generators, read_massive_file, recursive json flatten`*
