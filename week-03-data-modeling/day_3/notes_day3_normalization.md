# Week 3 — Day 3: Normalization

## The Problem — Why Normalize?

A flat/denormalized table causes 3 anomalies:

| Anomaly | Problem | Example |
|---|---|---|
| Update | One fact in many rows | Bob renamed → update 100 rows |
| Insert | Can't add data without unrelated data | Can't add Finance dept without employee |
| Delete | Lose unrelated data | Delete last Marketing emp → lose dept info |

---

## The 3 Normal Forms

### 1NF — First Normal Form
**Rule:** One value per cell. No lists, no repeating columns.

❌ Bad:
emp_id | skills
1      | Python, SQL, Spark

✅ Good:
emp_id | skill
1      | Python
1      | SQL
1      | Spark

**Simple test:** Can you store this in a spreadsheet
with one value per cell? If yes → 1NF ✅

---

### 2NF — Second Normal Form
**Rule:** Every column must depend on the WHOLE 
composite key — not just part of it.
(Only applies when you have a composite primary key)

❌ Bad — primary key is (student_id + subject_id)
but student_name only depends on student_id:

student_id | subject_id | score | student_name
101        | Math       | 85    | Alice
101        | Science    | 90    | Alice  ← repeated!

✅ Good — split student_name into its own table:

exam_scores                    students
student_id | subject_id | score  student_id | name
101        | Math       | 85     101        | Alice
101        | Science    | 90     102        | Bob

**Simple test:** Does any column depend on only 
HALF the composite key? If yes → 2NF violation!

**The Pizza Analogy 🍕**
Alice has 2 dipping sauces (composite key) —
both together identify the order.
If one sauce alone determines something → 2NF violation!

---

### 3NF — Third Normal Form
**Rule:** No non-key column should depend on 
ANOTHER non-key column (no transitive dependencies)

❌ Bad — dept_location depends on dept_id, not emp_id:

emp_id | emp_name | dept_id | dept_location
1      | Alice    | D1      | NYC
2      | Eve      | D1      | NYC  ← repeated!

✅ Good — split department into its own table:

employees                    departments
emp_id | emp_name | dept_id  dept_id | dept_location
1      | Alice    | D1       D1      | NYC
2      | Eve      | D1       D2      | LA

**Simple test:** Draw the dependency chain:
key → column A → column B ❌ (transitive = 3NF violation)
key → column A ✅ (direct = fine)

**The Pizza Analogy 🍕**
Bob's order (primary key) → Ranch → Mayo
Mayo depends on Ranch, not directly on Bob's order
That chain = transitive dependency = 3NF violation!

---

## 2NF vs 3NF — The Key Difference

|          | 2NF                        | 3NF                          |
|----------|----------------------------|------------------------------|
| Key type | Composite key              | Single OR composite key      |
| Problem  | Partial dependency         | Transitive dependency        |
| Chain    | key → column ❌ (partial)  | key → A → B ❌ (transitive)  |
| Memory   | "Don't be PARTIAL"         | "Don't be TRANSITIVE"        |

---

## The Full Normalization Flow

Original flat table:
emp_id | emp_name | dept_name | dept_loc | mgr_id | mgr_name | salary

1NF ✅ — one value per cell

2NF ✅ — emp_id is single key → auto 2NF

3NF — transitive dependencies found:
emp_id → dept_name ❌ (via dept_id)
emp_id → mgr_name ❌ (via mgr_id)

Final normalized structure (3NF):
employees   → emp_id, emp_name, dept_id, mgr_id, salary
departments → dept_id, dept_name, dept_loc
managers    → mgr_id, mgr_name

---

## Normalization vs Snowflake Schema

| | Normalization | Snowflake Schema |
|---|---|---|
| Context | Transactional DB (OLTP) | Data Warehouse (OLAP) |
| Goal | Eliminate redundancy | Reduce storage redundancy |
| Method | Split tables, use FKs | Split dimensions into sub-dimensions |
| Result | Many tables, many joins | More joins, less redundancy |

Key insight ⭐:
Snowflake Schema = 3NF applied to dimension tables!
Star Schema = deliberate denormalization for query speed!

---

## The One Rule to Remember Forever
> "Every non-key column must depend on the key,
>  the whole key, and nothing but the key"

---

## Interview Keywords
- Transitive dependency (3NF)
- Partial dependency (2NF)
- Composite key (2NF)
- Update/Insert/Delete anomalies
- OLTP (normalized) vs OLAP (denormalized)