"""Build kb_week2.py Part 2 — joins, performance, rest."""

p2 = '''
# ─── DAY 4: COMPLEX JOINS & NULLs ────────────────────────────────
"complex_joins_nulls": {
"basics": \'<div class="lesson-levels">\' + L(1,"🟢","How Joins Actually Work — Not Just Syntax","""
<h4>What a JOIN Really Does</h4>
<p>Most engineers think of a JOIN as "connecting two tables." That\'s accurate but incomplete. Precisely: a JOIN produces every combination of rows from two tables that satisfies a matching condition. The database doesn\'t "link" rows — it tests each row from the left table against each row from the right table and keeps the pairs that match. Understanding this process explains why joins on large tables are expensive and how different join types produce different results.</p>
<h4>The 3 Physical Join Algorithms (What the Engine Does)</h4>
<p><strong>1. Nested Loop Join:</strong> For each row in the outer table, scan the inner table for matches. O(N×M) complexity. Fast when outer table is tiny and inner table is indexed. Terrible on two large un-indexed tables — 1M × 1M = 1 trillion comparisons.</p>
<p><strong>2. Hash Join:</strong> Build a hash table from the smaller table (using the join key). Then scan the larger table, looking up each row in the hash table. O(N+M) complexity. The go-to algorithm for large tables. Requires enough memory to hold the hash table — can spill to disk if too large.</p>
<p><strong>3. Sort-Merge Join:</strong> Sort both tables by the join key, then merge-scan them in parallel (like merging two sorted arrays). O(N log N + M log M). Excellent when both tables are already sorted (e.g., both clustered by the join key). Very common in data warehouse query engines.</p>
<pre>Optimizer choice rule of thumb:
  Small + Large table with index on join key → Nested Loop
  Two large tables (unsorted) → Hash Join
  Two large tables (already sorted / clustered) → Sort-Merge</pre>
<h4>INNER vs LEFT vs FULL OUTER — When Each Row Appears</h4>
<pre>Table A:                   Table B:
id │ name               id │ score
───┼──────              ───┼──────
 1 │ Alice               1 │  90
 2 │ Bob                 3 │  75     ← note: no id=2 in B, no id=4 in A
 4 │ Dave                5 │  80     ← note: no id=5 in A

INNER JOIN (id match required in BOTH):
  Alice(1) + 90    ← match
  [Bob(2) dropped — no score]
  [Dave(4) dropped — no score]
  [score(5) dropped — no name]

LEFT JOIN (ALL left rows kept, NULLs if no match):
  Alice(1) + 90
  Bob(2)   + NULL   ← kept! Bob has no score yet
  Dave(4)  + NULL

FULL OUTER JOIN (ALL rows from BOTH sides):
  Alice(1) + 90
  Bob(2)   + NULL
  Dave(4)  + NULL
  NULL     + 80     ← score for id=5, no matching person!</pre>
<p>✍️ <strong>Interview insight:</strong> LEFT JOIN is the most misunderstood join. Interviewers frequently ask "find all users who have NOT made a purchase" — the correct pattern is LEFT JOIN + WHERE right_table.id IS NULL, not a subquery.</p>
""") + L(2,"🔵","NULL — The Three-Valued Logic Problem","""
<h4>NULL is Not Zero, Not Empty String, Not False — It\'s Unknown</h4>
<p>NULL represents "the value is unknown or does not exist." This creates a <strong>three-valued logic system</strong> in SQL: TRUE, FALSE, and UNKNOWN. Any comparison with NULL returns UNKNOWN — not TRUE or FALSE. UNKNOWN in a WHERE clause means the row is silently dropped. This is the #1 source of subtle bugs in SQL.</p>
<pre>-- All of these return UNKNOWN (not TRUE, not FALSE!):
NULL = NULL     → UNKNOWN   -- two unknowns are not equal
NULL &lt;&gt; NULL    → UNKNOWN
NULL + 5        → NULL      -- any arithmetic with NULL = NULL
\'text\' || NULL  → NULL      -- any concatenation with NULL = NULL
NULL = 0        → UNKNOWN
NULL = \'\'       → UNKNOWN

-- Only these work correctly for NULL:
NULL IS NULL    → TRUE
NULL IS NOT NULL → FALSE
COALESCE(NULL, 42) → 42     -- return first non-NULL value</pre>
<h4>The Anti-Pattern That Loses Data Silently</h4>
<pre>-- ❌ WRONG: this query returns 0 rows if ANY salary is NULL
SELECT emp_name FROM employees WHERE salary &lt;&gt; 90000;
-- reason: WHERE salary &lt;&gt; 90000 is UNKNOWN for NULL rows → row dropped

-- ✅ CORRECT: explicitly handle NULLs
SELECT emp_name FROM employees
WHERE salary &lt;&gt; 90000 OR salary IS NULL;

-- ❌ WRONG: COUNT(*) vs COUNT(col) confusion
SELECT COUNT(*),       -- counts every row including NULLs
       COUNT(salary)   -- counts only non-NULL salary rows
FROM employees;        -- these two numbers will differ if salary has NULLs!</pre>
<h4>COALESCE and NULLIF — Your NULL Safety Tools</h4>
<pre>-- COALESCE: return first non-NULL value (chain of fallbacks)
SELECT COALESCE(phone, mobile, \'No contact\') AS best_contact FROM users;

-- NULLIF: return NULL if two values are equal
-- Use to prevent division by zero:
SELECT revenue / NULLIF(sessions, 0) AS revenue_per_session FROM daily_stats;
-- If sessions=0, NULLIF returns NULL → division by NULL → NULL (not error)</pre>
""") + L(3,"🟡","Advanced: ANTI JOIN, CROSS JOIN, SELF JOIN","""
<h4>Three Underused but Important Join Patterns</h4>
<p><strong>ANTI JOIN</strong> — find rows in A with NO match in B. The go-to pattern for "unmatched" questions:</p>
<pre>-- Find customers who have never placed an order
-- Pattern 1: LEFT JOIN + NULL check (most common)
SELECT c.customer_id, c.name
FROM customers c
LEFT JOIN orders o ON c.customer_id = o.customer_id
WHERE o.customer_id IS NULL;   -- ← NULL means no matching order existed

-- Pattern 2: NOT EXISTS (sometimes faster — stops at first match found)
SELECT c.customer_id, c.name FROM customers c
WHERE NOT EXISTS (SELECT 1 FROM orders o WHERE o.customer_id = c.customer_id);

-- Pattern 3: NOT IN (⚠️ dangerous with NULLs!)
-- If ANY order has customer_id = NULL, NOT IN returns ZERO rows!
SELECT customer_id FROM customers
WHERE customer_id NOT IN (SELECT customer_id FROM orders);  -- risky!</pre>
<p><strong>SELF JOIN</strong> — join a table to itself. Classic use: find employee-manager pairs from a single employees table:</p>
<pre>SELECT e.emp_name AS employee, m.emp_name AS manager
FROM employees e
LEFT JOIN employees m ON e.manager_id = m.emp_id;
-- Same table used twice with different aliases</pre>
<p><strong>CROSS JOIN</strong> — every combination of rows (Cartesian product). Useful for generating test data or all pair combinations. Use with extreme caution — 1,000 × 1,000 = 1,000,000 rows:</p>
<pre>-- Generate all size × color combinations for a product catalog
SELECT s.size, c.color FROM sizes s CROSS JOIN colors c;
-- 5 sizes × 8 colors = 40 combinations</pre>
""") + L(4,"🔴","FAANG Interview: The Duplicate Join & Fanout Problem","""
<h4>The Silent Data Explosion — Many-to-Many Joins</h4>
<p>One of the most common FAANG interview mistakes: joining two tables where the join key is NOT unique in both, producing unexpected row multiplication. This is called <strong>join fanout</strong>.</p>
<pre>-- orders: one row per order (order_id is unique)
-- order_items: multiple rows per order (each item is a row)
-- Mistake: SUM on the wrong side causes double-counting!

SELECT o.order_id, SUM(o.order_total) AS wrong_total
FROM orders o
JOIN order_items oi ON o.order_id = oi.order_id
GROUP BY o.order_id;
-- ❌ If an order has 3 items, order_total is summed 3 times!

-- Fix 1: aggregate items first, then join
WITH item_counts AS (
  SELECT order_id, COUNT(*) AS item_count, SUM(item_price) AS items_total
  FROM order_items GROUP BY order_id
)
SELECT o.order_id, o.order_total, ic.item_count
FROM orders o JOIN item_counts ic ON o.order_id = ic.order_id;

-- Fix 2: detect unexpected fanout with COUNT check
SELECT order_id, COUNT(*) AS row_count
FROM (SELECT o.*, oi.item_id FROM orders o JOIN order_items oi USING (order_id)) t
GROUP BY order_id HAVING COUNT(*) &gt; 1;
-- Any order_id with count &gt; 1 means join is multiplying rows</pre>
<p><strong>Interview rule:</strong> Before writing any JOIN query in an interview, state out loud: "Let me verify the cardinality of both sides of the join key. Is order_id unique in the orders table? Could there be multiple rows in order_items per order_id?" Mentioning this thought process alone impresses interviewers.</p>
""") + \'</div>\',
"key_concepts": [
    "Nested Loop: O(N×M), fast when outer is small + inner is indexed. Hash Join: O(N+M), best for large tables.",
    "INNER JOIN: only rows with matches in BOTH tables. LEFT JOIN: ALL left rows, NULLs for unmatched right.",
    "FULL OUTER JOIN: ALL rows from both sides, NULLs where no match on either side.",
    "NULL = three-valued logic: TRUE / FALSE / UNKNOWN. Any comparison with NULL = UNKNOWN = row dropped.",
    "Use IS NULL / IS NOT NULL, never = NULL or &lt;&gt; NULL. COALESCE for defaults. NULLIF for zero-division safety.",
    "ANTI JOIN pattern: LEFT JOIN + WHERE right.id IS NULL. Use NOT EXISTS for performance on large tables.",
    "NOT IN with NULLs: dangerous. If subquery returns ANY NULL, NOT IN returns zero rows — silent bug.",
    "Join fanout: if join key is not unique on both sides, rows multiply. Always verify cardinality before joining.",
],
"hints": [
    "\'Find users who never did X\': LEFT JOIN + WHERE right.key IS NULL. Don\'t use NOT IN if NULLs possible.",
    "COUNT(*) counts all rows including NULLs. COUNT(col) counts only non-NULL values. Know the difference.",
    "Join producing too many rows? Check if the join key is unique in both tables. Aggregate smaller side first.",
    "COALESCE(a, b, c): returns the first non-NULL. Perfect for fallback chains and report formatting.",
],
"tasks": [
    "<strong>Step 1:</strong> Create customers (5 rows) and orders (3 rows, 2 customers unordered). Write LEFT JOIN + WHERE IS NULL to find unordered customers. Verify 2 results.",
    "<strong>Step 2:</strong> Test NULL logic: SELECT NULL = NULL, NULL &lt;&gt; 5, COALESCE(NULL, NULL, 42). Verify the outputs.",
    "<strong>Step 3:</strong> Create a many-to-many join scenario (orders × order_items). Write the broken SUM query, verify it double-counts. Fix it with a pre-aggregated CTE.",
    "<strong>Step 4:</strong> Write a self-join to show each employee and their manager\'s name from a single employees table.",
],
"hard_problem": "Boss Problem (Stripe): Table: transactions(txn_id, user_id, amount, status, created_at). Another table: refunds(refund_id, txn_id, refund_amount, created_at). (1) Find all transactions that were partially refunded (refund_amount < transaction amount). (2) Find transactions with NO refund. (3) Find users who had more than 3 refunds in the last 30 days — flag them as fraud risk. Handle: a transaction can have multiple refunds. A refund can reference a NULL txn_id (orphaned refund). Does NULL in txn_id affect your NOT IN query?",
},

# ─── DAY 5: PERFORMANCE REVIEW ────────────────────────────────────
"performance_review": {
"basics": \'<div class="lesson-levels">\' + L(1,"🟢","The Performance Mindset — Measuring Before Optimizing","""
<h4>The Cardinal Rule: Measure First, Optimize Second</h4>
<p>The biggest mistake engineers make in performance optimization is guessing. They add an index, rewrite a join, or change a parameter — without measuring the before and after. Then they\'re surprised when the "optimization" made things slower, or didn\'t help at all.</p>
<p>The correct approach is always: <strong>Measure → Identify bottleneck → Fix the specific bottleneck → Measure again.</strong> This is called the scientific method, and it applies perfectly to database performance. Every optimization decision should be backed by numbers, not intuition.</p>
<h4>The Three Layers of Database Performance</h4>
<p><strong>Layer 1 — Query execution time:</strong> How long does the query itself take? Measured with EXPLAIN ANALYZE. This is where you find: missing indexes, bad join orders, non-sargable conditions, excessive row scans.</p>
<p><strong>Layer 2 — I/O (disk reads):</strong> How many disk pages does the query read? A query can use an index perfectly but still be slow if it needs to read 10 million pages. Measured via buffer hit rates and block reads in EXPLAIN output. Fix: partition tables, clustering, covering indexes.</p>
<p><strong>Layer 3 — Concurrency (locking):</strong> How long does the query wait because other queries hold locks? A 0.01-second query that waits 30 seconds for a lock shows up as a 30-second query. Measured via pg_locks, wait event monitoring. Fix: shorter transactions, read replicas, MVCC settings.</p>
<p>✍️ Most tutorials only teach Layer 1. FAANG interviews often ask about Layer 2 and 3, and production slowdowns are frequently Layer 3. Know all three.</p>
""") + L(2,"🔵","EXPLAIN ANALYZE Deep Dive — Reading the Full Output","""
<h4>Understanding Every Part of an EXPLAIN ANALYZE Node</h4>
<pre>Seq Scan on orders (cost=0.00..42391.00 rows=1000000 width=72)
            (actual time=0.009..312.4 rows=983241 loops=1)
  Filter: (order_date &gt; \'2024-01-01\'::date)
  Rows Removed by Filter: 16759</pre>
<p>Breaking this down:</p>
<ul>
  <li><code>cost=0.00..42391.00</code>: Estimated cost in arbitrary units. First number = startup cost (before first row). Second = total cost.</li>
  <li><code>rows=1000000</code>: Optimizer\'s estimate of rows this node returns. Compare to actual!</li>
  <li><code>actual time=0.009..312.4</code>: Real elapsed time in milliseconds. Startup .. total.</li>
  <li><code>rows=983241</code>: Actual rows returned. If far from estimate (1M estimated, 10 actual) → stale statistics.</li>
  <li><code>loops=1</code>: How many times this node ran. In nested loop joins, inner node loops = outer row count → expensive!</li>
  <li><code>Rows Removed by Filter: 16759</code>: The filter eliminated only 16K rows from 1M — low selectivity, index would help little.</li>
</ul>
<h4>The 5 Red Flags in EXPLAIN Output</h4>
<pre>🔴 Seq Scan on a table with millions of rows (no index used)
🔴 estimated rows=1, actual rows=1,000,000 (catastrophically wrong estimate)
🔴 Nested Loop with loops=50000 (inner table scanned 50K times)
🔴 Sort (disk) → spilling to disk, increase work_mem setting
🔴 Hash Batches: 8 → hash join spilled to disk (8 batches = too little memory)</pre>
""") + L(3,"🟡","Partitioning as a Performance Tool","""
<h4>When Indexing Isn\'t Enough — Partition Pruning</h4>
<p>For truly enormous tables (100B+ rows), even a perfect B-Tree index may not be enough because the index itself becomes huge and lives on disk. The solution: <strong>table partitioning</strong> — physically splitting the table into smaller files (partitions) based on a partition key (usually a date).</p>
<p>When you query <code>WHERE order_date = \'2024-01-15\'</code>, the database reads ONLY the January 2024 partition file — ignoring all other 11 monthly files completely. This is called <strong>partition pruning</strong>. For a table with 10 years of data, you read 1/120th of the data automatically.</p>
<pre>-- PostgreSQL range partitioning by month
CREATE TABLE orders (
  order_id   BIGINT,
  order_date DATE,
  revenue    DECIMAL
) PARTITION BY RANGE (order_date);

CREATE TABLE orders_2024_01 PARTITION OF orders
  FOR VALUES FROM (\'2024-01-01\') TO (\'2024-02-01\');
CREATE TABLE orders_2024_02 PARTITION OF orders
  FOR VALUES FROM (\'2024-02-01\') TO (\'2024-03-01\');
-- etc.

-- Now: WHERE order_date = \'2024-01-15\' reads ONLY orders_2024_01
EXPLAIN SELECT * FROM orders WHERE order_date = \'2024-01-15\';
-- Shows: Seq Scan on orders_2024_01 → ignores all other partitions ✅</pre>
<h4>Partition Key Choice Rules</h4>
<ul>
  <li><strong>Date/time columns:</strong> Most common. Queries almost always filter by recency (last 30 days).</li>
  <li><strong>High-cardinality IDs</strong> (hash partitioning): Distribute writes evenly across nodes. Best for write-heavy workloads.</li>
  <li><strong>Region/country</strong> (list partitioning): Natural organizational boundary when different regions are queried independently.</li>
  <li><strong>Never partition on low-cardinality columns</strong> (boolean, status) — you get 2-4 partitions instead of 100+ — no benefit.</li>
</ul>
""") + L(4,"🔴","FAANG Interview: Performance Incident Walkthrough","""
<h4>How to Answer "Our Query is Slow — What Do You Do?"</h4>
<p>This is one of the most common FAANG data engineering interview questions. The expected answer is a structured, systematic diagnosis — not a list of guesses. Here\'s the exact framework:</p>
<pre>Step 1 — MEASURE: Run EXPLAIN ANALYZE. Get actual numbers.
  → What is the actual execution time?
  → What plan did the optimizer choose?
  → Are estimated vs actual rows wildly different?

Step 2 — IDENTIFY LAYER: Which layer is the bottleneck?
  → Query (EXPLAIN shows Seq Scan, bad join) → Layer 1
  → I/O (high page reads, low buffer hit rate) → Layer 2
  → Locking (query waits, not slow itself) → Layer 3

Step 3 — LAYER 1 FIXES (query-level):
  □ Add missing index on WHERE/JOIN column
  □ Rewrite non-sargable condition (remove function from column)
  □ Restructure CTEs to filter early
  □ Replace NOT IN with NOT EXISTS
  □ Fix join fanout (pre-aggregate one side)

Step 4 — LAYER 2 FIXES (I/O-level):
  □ Add table partitioning (date-range)
  □ Add covering index (eliminate heap access)
  □ Cluster table on frequently accessed column
  □ Increase shared_buffers to keep hot data in memory

Step 5 — LAYER 3 FIXES (concurrency):
  □ Shorten transaction duration
  □ Route read queries to replica
  □ Use optimistic locking or SKIP LOCKED
  □ Batch large UPDATE/DELETE operations</pre>
""") + \'</div>\',
"key_concepts": [
    "Measure first. Always EXPLAIN ANALYZE before guessing. Optimization without measurement is superstition.",
    "Three performance layers: Query execution (EXPLAIN), I/O (pages read, buffer hit rate), Concurrency (locking).",
    "EXPLAIN cost units are arbitrary. Compare estimated vs actual rows — big gap = stale statistics.",
    "loops=N in EXPLAIN: inner node of a nested loop ran N times. High N on large tables = performance killer.",
    "Partition pruning: the DB reads only matching partition files. WHERE order_date in Jan → reads only Jan partition.",
    "Partition key choice: date for time-series, hash for write distribution. Never boolean or low-cardinality.",
    "Performance diagnosis framework: EXPLAIN → identify layer → apply layer-specific fix → measure again.",
],
"hints": [
    "\'Our query is slow\' interview question: always start with EXPLAIN ANALYZE, never guess first.",
    "Estimated rows=1, actual=1M: run ANALYZE to refresh statistics. This one command can fix a slow query instantly.",
    "Hash Join with high batch count → spilling to disk → increase work_mem in session: SET work_mem = \'256MB\'.",
    "Partition tables almost always by date for analytics workloads — time-range queries are the most common.",
],
"tasks": [
    "<strong>Step 1:</strong> On a large table, run EXPLAIN ANALYZE on a slow query. Find the node with the highest actual time.",
    "<strong>Step 2:</strong> Run ANALYZE on the table. Re-run EXPLAIN ANALYZE. Did the estimated row count improve?",
    "<strong>Step 3:</strong> Create a partitioned orders table with 2 monthly partitions. Run EXPLAIN on a date-filtered query. Verify partition pruning occurs.",
    "<strong>Step 4:</strong> Walk through the 5-step performance diagnosis framework for this scenario: \'SELECT * FROM events WHERE user_id=42 takes 60 seconds on a 5B-row table.\'",
],
"hard_problem": "Boss Problem (Netflix): Your Spark job that computes daily user engagement metrics grew from 2h to 14h over 6 months as data volume tripled. Walk through your diagnosis and fix: (1) What metrics do you look at first? (2) You find 3 stages with massive shuffle — what causes that and how do you reduce it? (3) One executor is running 10x longer than others (data skew) — what\'s the fix? (4) The job reads 50TB but only uses 2TB after filtering — how do you fix this at the storage layer?",
},

# ─── DAY 6-7: REST ────────────────────────────────────────────────
"week2_rest": {
"basics": \'<div class="lesson-levels">\' + L(1,"🟢","Consolidation Day — How Expert Knowledge Forms","""
<h4>The Difference Between Knowing and Understanding</h4>
<p>At this point you\'ve been exposed to CTE recursion, query optimization, indexing internals, join algorithms, NULL logic, and performance layers. These are the topics. But "knowing about them" and "understanding them" are different cognitive states.</p>
<p><strong>Knowing:</strong> You can recognize these concepts when someone mentions them. You remember the syntax. You could pick the right answer in a multiple-choice test.</p>
<p><strong>Understanding:</strong> You can look at a slow query you\'ve never seen before and immediately know WHY it\'s slow. You can explain join fanout to someone else without notes. You reach for COALESCE automatically when you see a NULL risk. You notice a non-sargable WHERE condition while code-reviewing someone else\'s PR.</p>
<p>Understanding is built by retrieving knowledge under different conditions — not by re-reading it. Today\'s goal: <strong>retrieve</strong> what you learned this week in three different formats: writing, coding, and verbal explanation.</p>
""") + L(2,"🔵","Active Recall — No Notes","""
<h4>Answer These From Pure Memory (Write Answers Before Checking)</h4>
<pre>Recursive CTEs:
□ What are the two mandatory parts of a recursive CTE?
□ What keyword joins them? UNION or UNION ALL — which and why?
□ Write the termination condition syntax from memory
□ Name 3 use cases for recursive CTEs

Query Optimization:
□ What does EXPLAIN ANALYZE show that EXPLAIN alone doesn\'t?
□ Rewrite this non-sargable condition: WHERE YEAR(created_at) = 2024
□ What is a sargable condition?
□ Name 3 query anti-patterns and their fixes

Indexing:
□ Explain the leftmost prefix rule for composite indexes in 2 sentences
□ When does a low-cardinality index hurt rather than help?
□ What is a covering index and when does it eliminate heap access?

Joins & NULLs:
□ Find customers with NO orders — write the LEFT JOIN pattern
□ Why is NOT IN dangerous when the subquery can return NULLs?
□ What does COALESCE(NULL, NULL, 42) return?
□ What is join fanout and how do you detect it?

Score: 14-16/16 = interview ready | &lt;10 = revisit weakest topic</pre>
""") + L(3,"🟡","Spaced Repetition Plan for This Week","""
<h4>Schedule These Reviews Now</h4>
<table>
<tr><th>Topic</th><th>Review in 3 days</th><th>Review in 7 days</th><th>Review in 30 days</th></tr>
<tr><td>Recursive CTEs</td><td>Re-write hierarchy query from memory</td><td>LeetCode: Consecutive Numbers</td><td>Bill of Materials exercise</td></tr>
<tr><td>Query optimization</td><td>EXPLAIN on a real table you own</td><td>Fix a non-sargable query in your work</td><td>Profile a production slow query</td></tr>
<tr><td>Indexing</td><td>Design indexes for 3 queries</td><td>Verify with EXPLAIN</td><td>Analyze index usage in production DB</td></tr>
<tr><td>Joins & NULLs</td><td>Write all 3 join fanout patterns</td><td>LeetCode: Employees Earning More</td><td>Review a PR with complex joins</td></tr>
</table>
<p>✍️ <strong>The most retained knowledge comes from teaching.</strong> Schedule 20 minutes this weekend to explain one of this week\'s topics to a colleague, friend, or the AI chatbot. Even if they know nothing about databases — the act of simplifying a concept to explain it to a non-expert cements it in your own memory far more than reading or re-reading.</p>
""") + L(4,"🔴","End-of-Week Interview Readiness Check","""
<h4>Simulate the Interview Environment</h4>
<pre>Set a 45-minute timer. No notes. No SQL editor. Just paper and pen.

Problem 1 (15 min): You have employees(emp_id, emp_name, manager_id).
  Write a recursive CTE that:
  (a) Lists every employee with their full management chain as a path
  (b) Shows the depth/level from CEO
  (c) Stops at depth 5 (safety valve)
  (d) Handles the case where manager_id = emp_id (self-referential data)

Problem 2 (15 min): Table: orders(order_id, customer_id, order_date, revenue).
  This query takes 45 seconds on 500M rows:
    SELECT customer_id, SUM(revenue) FROM orders
    WHERE YEAR(order_date) = 2024 GROUP BY customer_id;
  (a) Identify what is wrong
  (b) Rewrite it to be sargable
  (c) Design the optimal index
  (d) What else would you check with EXPLAIN ANALYZE?

Problem 3 (15 min): Explain join fanout in plain English.
  Show a concrete example with sample data.
  Demonstrate the broken query and the correct fix.

Evaluate yourself:
  - Did you write complete, correct SQL? (syntax matters under pressure)
  - Did you explain your reasoning before writing code?
  - Did you mention edge cases (NULLs, cycles, empty tables)?</pre>
""") + \'</div>\',
"key_concepts": [
    "Understanding ≠ knowing. Understanding = applying concepts automatically in new, unseen situations.",
    "Active recall under time pressure is the closest simulation to a real interview — do it regularly.",
    "Three formats for retrieval: writing (explain in prose), coding (blank editor), verbal (explain to someone).",
    "The Feynman Technique for databases: explain EXPLAIN ANALYZE to a non-technical person. If you struggle, that\'s the gap.",
],
"hints": [
    "Use the AI chatbot as a practice interviewer: \'Give me a SQL optimization question about indexing.\'",
    "Write SQL on paper — no autocomplete. If you can\'t write it on paper, you can\'t write it in an interview.",
    "Any score below 10/16 on the recall quiz: revisit that specific day\'s Level 1 + Level 2 content tomorrow.",
],
"tasks": [
    "<strong>Active recall:</strong> Write the recursive CTE pattern from memory. Include the anchor, UNION ALL, recursive member, and termination clause.",
    "<strong>EXPLAIN practice:</strong> Run EXPLAIN ANALYZE on a real query. Identify the slowest node. Propose one fix.",
    "<strong>Teach it:</strong> Explain the leftmost prefix rule for composite indexes to the chatbot using a concrete example.",
    "<strong>Mock interview:</strong> Set a 45-minute timer. Solve the 3 problems above without notes.",
],
"hard_problem": "Connect the dots: Explain how recursive CTEs, indexing strategy, query optimization, and join ordering would ALL work together in one production scenario: \'Find the top 5 highest-revenue customers for each account manager, where account managers are defined in a 4-level hierarchy, for orders placed in 2024, on a 10-billion-row orders table.\' Walk through every decision.",
},

}
'''

# Read Part 1
with open("kb_week2_part1.py", encoding="utf-8") as f:
    raw = f.read()

# Part 1 ends with WEEK2 = { ... the 3 topics ... }
# Strip the closing } from p1 and the opening WEEK2 = { from p2
p1_content = raw.strip()
# Remove the trailing closing brace from p1
assert p1_content.endswith("}"), "Part 1 should end with }"
p1_body = p1_content[:-1]  # remove last }

# Combine: p1 body (no closing brace) + p2 topics + closing brace
combined = p1_body + "\n" + p2 + "\n}"

# Write the final kb_week2.py
with open("kb_week2.py", "w", encoding="utf-8") as f:
    f.write(combined)

print("✅ kb_week2.py written")
