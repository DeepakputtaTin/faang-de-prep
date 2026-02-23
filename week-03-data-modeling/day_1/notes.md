# Week 3 — Data Modeling

## Day 1 — Star Schema vs Snowflake Schema

---

## 1. Normal Forms (1NF → 3NF)

### 1NF — First Normal Form
- Every column must have atomic (single) values
- No repeating groups
- Example fix: Split "Shoes, Shirt, Bag" into separate rows

### 2NF — Second Normal Form
- Must be in 1NF
- Every non-key column must depend on the WHOLE primary key
- Example fix: Move customer_city out of orders table into customers table

### 3NF — Third Normal Form
- Must be in 2NF
- No column should depend on another non-key column (no transitive dependencies)
- Example fix: Move supplier_phone out of products table into suppliers table

### The One Rule to Remember
> "Every non-key column must depend on the key, the whole key, and nothing but the key"

---

## 2. Star Schema

### What it is
One central fact table directly connected to denormalized dimension tables.
Optimized for READ performance — fewer joins, faster aggregations.

### Structure
```
                dim_customer
                     |
dim_date ——— fact_orders ——— dim_product
                     |
                dim_store
```

### Fact Table
- Contains measurable events (orders, clicks, transactions)
- Stores ONLY foreign keys + numeric metrics
- NEVER put descriptive text in a fact table ❌
- Example columns: order_id, customer_id, product_id, date_id, quantity, revenue

### Dimension Table
- Contains descriptive context (who, what, where, when)
- Example: dim_customer → customer_id, name, city, country

### Grain
- The level of detail in the fact table
- ALWAYS define grain first in interviews
- Example: "One row per order per product"

---

## 3. Snowflake Schema

### What it is
Star Schema but dimension tables are normalized further into sub-dimensions.

### Structure
```
dim_supplier
     |
dim_category
     |
dim_product ——— fact_orders ——— dim_customer
```

### When to use
- Storage-constrained environments
- Write-heavy workloads
- Complex hierarchies (e.g. product → category → department)

---

## 4. Star vs Snowflake Comparison

| | Star | Snowflake |
|---|---|---|
| Query Speed | Faster | Slower (more joins) |
| Storage | More redundancy | Less redundancy |
| Maintenance | Easier | Harder |
| FAANG Usage | Redshift, BigQuery | Less common |
| Best For | Analytics, BI dashboards | Write-heavy, storage-constrained |

---

## 5. Why 3NF Causes Slow Analytical Queries

- 3NF splits everything into many tables to eliminate redundancy
- Every analytical query needs to JOIN everything back together
- On 500M+ row datasets, each join multiplies computational cost massively
- Solution: Denormalize into Star Schema for the analytical layer
- Key insight: Keep 3NF for transactional systems + Star Schema for analytics — they coexist

---

## 6. Boss Problem — Amazon Dashboard Fix

### Problem
Analytics dashboard query joining 6 fully normalized (3NF) tables taking 45 seconds on 500M rows.

### Root Cause
- 6 joins on 500M rows = massive data shuffle at each join
- Each join multiplies intermediate row count
- No shortcut — every piece of context requires a join in 3NF

### Fix
Redesign into Star Schema:
- 1 central fact table
- 3-4 dimension tables
- Most queries need only 2-3 joins instead of 6

### Trade-off
- More redundancy in storage
- But storage is cheap — reads are far more frequent than writes
- Acceptable trade-off for a data warehouse

### Key Interview Point ⭐
> "I'd implement Star Schema in a separate analytical layer while keeping the 
> 3NF schema intact for the transactional system. Both coexist — 3NF for writes, 
> Star Schema for reads."

---

## 7. Lab — PostgreSQL Star Schema

**File:** `lab/star_schema.py`

**Tables created:**
- `dim_customer` — customer_id, name, city, country
- `dim_product` — product_id, name, category, supplier
- `dim_date` — date_id, date, month, quarter, year
- `fact_orders` — order_id, customer_id, product_id, date_id, quantity, revenue

**Queries practiced:**
- Revenue by product category per quarter
- Top customers by total revenue

**Key output:**
```
=== Revenue by Category per Quarter ===
('Accessories', 3, Decimal('320.0'))
('Footwear', 3, Decimal('180.0'))
('Clothing', 2, Decimal('180.0'))
('Footwear', 1, Decimal('150.0'))

=== Top Customers by Revenue ===
('Carol', 'Germany', Decimal('320.0'), 1)
('Alice', 'USA', Decimal('285.0'), 2)
('Bob', 'UK', Decimal('225.0'), 2)
```

---

## Tomorrow — Day 2: SCD Types (1, 2, 3)
- What are Slowly Changing Dimensions?
- SCD Type 1 — Overwrite
- SCD Type 2 — History Tracking (most important)
- SCD Type 3 — Previous Value Column
- Lab: Implement SCD Type 2 MERGE logic in PostgreSQL


## Bridge Tables
- Solves Many-to-Many relationships in dimensional modeling
- Sits between fact and dimension tables
- 3 signs you need one:
  1. One fact row → multiple dimension values
  2. FK constraint won't allow multiple values in one column
  3. You're tempted to use comma-separated values in a column 🚩