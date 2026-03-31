# Week 5 Day 3 — File I/O & Linked Lists
**FAANG DE Prep | 13-Week Plan**

---

## 🧠 Core Theory

### JSON Lines Format (.jsonl)
- One JSON object per line — no wrapping array
- **Splittable** — parallel processing across Spark workers
- **Appendable** — just add a new line
- **Streamable** — Kafka, Kinesis prefer JSONL
- Regular JSON → needs full file loaded to parse
- JSONL → one line = one record = process and move on

### CSV → JSONL Key Modules
- `csv.DictReader` — maps headers to values automatically → `{"name": "Deepak", "age": "25"}`
- `csv.reader` — raw rows as lists → `["Deepak", "25"]` (loses headers)
- `json.dumps(row)` → converts dict to JSON string
- Always `+ '\n'` when writing JSONL

### Linked List vs Python List
| | Python List | Linked List |
|---|---|---|
| Memory | Contiguous | Anywhere (pointers) |
| Index access | O(1) | O(N) |
| Insert/Delete | O(N) | O(1) at head |
| Structure | Array | Nodes with next pointer |

### ListNode Structure
```python
class ListNode(object):
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next
```

---

## 💻 Problems Solved

### Problem 1 — CSV to JSON Lines (without Pandas)

```python
import csv
import json

with open('input.csv', newline='') as csvfile:
    reader = csv.DictReader(csvfile)          # headers → keys automatically
    with open('output.jsonl', 'w', encoding='utf-8') as jsonfile:
        for row in reader:                    # O(1) memory — one row at a time
            jsonfile.write(json.dumps(row) + '\n')

# Time: O(N) | Memory: O(1)
```

---

### Boss Problem — Airbnb Booking Pipeline

**Scenario:** Nightly CSV dump → filter confirmed bookings → convert currency → JSONL

```python
import csv
import json

with open('airbnb.csv', newline='') as csvfile:
    csvreader = csv.DictReader(csvfile, delimiter=',')
    with open('airbnbdata.jsonl', 'w', encoding='utf-8') as jsonfile:
        for row in csvreader:
            if row['status'] == 'confirmed':
                # Currency conversion
                amount_usd = 0.00
                if row['currency'] == 'USD':
                    amount_usd = float(row['amount']) * 1.00
                elif row['currency'] == 'EUR':
                    amount_usd = float(row['amount']) * 1.08
                elif row['currency'] == 'GBP':
                    amount_usd = float(row['amount']) * 1.27

                # Build clean output dict
                output = {
                    'booking_id': row['booking_id'],
                    'user_id': row['user_id'],
                    'property_id': row['property_id'],
                    'amount_usd': amount_usd
                }
                jsonfile.write(json.dumps(output) + '\n')

# Real pattern: Read → Filter → Transform → Load
# Memory: O(1) — one row at a time ✅
```

**Key lessons:**
- `float(row['amount'])` — CSV values are always strings, cast before math
- Build new output dict — don't modify original row for clean output
- Filter at read time, not after load — push-down computation

---

### LC 206 — Reverse Linked List

**4-step pointer pattern — burn into memory:**
```python
class Solution(object):
    def reverseList(self, head):
        prev = None
        curr = head
        while curr:
            next = curr.next    # 1. save next (before losing reference)
            curr.next = prev    # 2. flip pointer
            prev = curr         # 3. advance prev
            curr = next         # 4. advance curr
        return prev             # new head

# Time: O(N) | Space: O(1)
```

**Trace through `1 → 2 → 3`:**
```
Start:  prev=None, curr=1
Step 1: next=2, 1→None, prev=1, curr=2
Step 2: next=3, 2→1,    prev=2, curr=3
Step 3: next=None, 3→2, prev=3, curr=None
Return: 3 → 2 → 1 → None ✅
```

---

## ⚠️ Common Mistakes

1. **Using `csv.reader` instead of `csv.DictReader`** — loses column headers
2. **Forgetting `+ '\n'`** — all records on same line
3. **Not casting amount to float** — `"180.00" * 1.08` = TypeError
4. **Double encoding** — `json.dump(json.dumps(row))` encodes twice
5. **Forgetting to save `next`** before flipping pointer in linked list reversal

---

## 🔗 DE Connections

| Concept | Real DE Use Case |
|---|---|
| CSV → JSONL | S3 raw zone ingestion, BigQuery native format |
| Filter at read time | Push-down computation, Spark predicate pushdown |
| Currency conversion | Financial data pipelines, FX rate ETL |
| Linked List reversal | Stream processing, queue reversal |
| JSONL format | Kafka message format, ML training data |

---

## 📝 Warm-Up Recall (for tomorrow)

1. What's the difference between `csv.reader` and `csv.DictReader`?
2. Why must you cast `float(row['amount'])` before multiplying?
3. What are the 4 steps in linked list reversal?
4. Why is JSONL preferred over regular JSON for large files?

---
*Week 5 Day 3 Complete ✅*
*Commit: `week-05: day 3 complete - file I/O, CSV to JSONL, airbnb pipeline, LC206 reverse linked list`*
