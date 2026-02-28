def L(n, emoji, title, body):
    return f'''<div class="level level-{n}">
<div class="level-badge">{emoji} Level {n} — {title}</div>
<div class="rich">{body}</div>
</div>'''

WEEK2 = {

# ─── DAY 1: RECURSIVE CTEs ────────────────────────────────────────
"recursive_ctes": {
"basics": '<div class="lesson-levels">' + L(1,"🟢","What Are CTEs and Why Do Recursive CTEs Exist?","""
<h4>First — What Is a CTE?</h4>
<p>A <strong>Common Table Expression (CTE)</strong> is a named, temporary result set defined at the top of a query using <code>WITH</code>. Think of it as giving a name to a subquery so you can reference it later — like naming a variable in programming. It makes complex queries readable by breaking them into clear, named steps.</p>
<pre>-- Without CTE: nested, hard to read
SELECT dept, avg_sal FROM (SELECT dept, AVG(salary) AS avg_sal FROM employees GROUP BY dept) sub;

-- With CTE: reads like steps of a story
WITH dept_averages AS (
  SELECT dept, AVG(salary) AS avg_sal FROM employees GROUP BY dept
)
SELECT dept, avg_sal FROM dept_averages;   -- clean!</pre>
<h4>Now — Why Recursive CTEs?</h4>
<p>Some data is naturally hierarchical: an employee reports to a manager who reports to a VP who reports to a CEO. Or a product category has subcategories which have sub-subcategories. Or a network of roads connects city A → B → C → D with no fixed depth.</p>
<p>Standard SQL can't traverse this structure because it doesn't know how many levels deep to go — the depth is unknown until you actually walk the hierarchy. <strong>Recursive CTEs</strong> solve this by defining a query that calls itself, going one level deeper on each iteration, until it reaches the bottom (a row with no more children).</p>
<h4>The Mental Model: A Snowball Rolling Downhill</h4>
<p>Imagine rolling a snowball from the top of a hill. It starts small (the CEO, the root node). As it rolls down, it picks up more snow (each level of employees). Each iteration, it grows by one layer, until it reaches the bottom of the hill (leaf employees with no reports). The recursive CTE is the rule that says "keep rolling, picking up one layer at a time, until there's nothing left to pick up."</p>
<pre>Iteration 1 (Anchor): seed_rows = [CEO]
Iteration 2: rows where manager = CEO → [VP1, VP2]
Iteration 3: rows where manager = VP1 or VP2 → [Dir1, Dir2, Dir3]
Iteration 4: rows where manager = Dir1,2,3 → [Emp1, Emp2 ... Emp8]
Iteration 5: no more rows → STOP</pre>
<p>✍️ <strong>Write this down:</strong> A recursive CTE has two mandatory parts — the <strong>anchor member</strong> (the starting point, non-recursive) and the <strong>recursive member</strong> (the part that references the CTE itself, going one level deeper). They are joined with <code>UNION ALL</code>.</p>
""") + L(2,"🔵","Step-by-Step: Traversing an Employee Hierarchy","""
<h4>The Data: A Classic Manager-Employee Tree</h4>
<pre>CREATE TABLE employees (
  emp_id   INT PRIMARY KEY,
  emp_name VARCHAR(50),
  manager_id INT    -- NULL means this person is the CEO (top of tree)
);
INSERT INTO employees VALUES
  (1, 'Alice (CEO)',   NULL),   -- root
  (2, 'Bob (VP Eng)',    1),
  (3, 'Carol (VP Mkt)',  1),
  (4, 'Dave (Dir)',      2),
  (5, 'Eve (Dir)',       2),
  (6, 'Frank (Eng)',     4),
  (7, 'Grace (Eng)',     4),
  (8, 'Heidi (Mkt)',     3);</pre>
<h4>The Recursive CTE — Every Line Explained</h4>
<pre>WITH RECURSIVE org_tree AS (

  -- ① ANCHOR MEMBER: the starting point
  -- This runs ONCE. It seeds the recursion with the root row(s).
  SELECT
    emp_id, emp_name, manager_id,
    0 AS level,                      -- CEO is at depth 0
    emp_name AS path                 -- start the full path string
  FROM employees
  WHERE manager_id IS NULL           -- "give me the top of the tree"

  UNION ALL                          -- stack anchor rows + recursive rows

  -- ② RECURSIVE MEMBER: runs once per level, references org_tree
  -- Each iteration, it finds direct reports of the PREVIOUS iteration's results
  SELECT
    e.emp_id, e.emp_name, e.manager_id,
    t.level + 1,                     -- go one level deeper
    t.path || ' → ' || e.emp_name    -- extend the path string
  FROM employees e
  INNER JOIN org_tree t              -- join employees to LAST iteration's results
    ON e.manager_id = t.emp_id      -- "whose manager is one of the rows already found?"
)
SELECT * FROM org_tree ORDER BY level, emp_id;</pre>
<pre>emp_name          │ level │ path
──────────────────┼───────┼────────────────────────────────────
Alice (CEO)       │   0   │ Alice (CEO)
Bob (VP Eng)      │   1   │ Alice (CEO) → Bob (VP Eng)
Carol (VP Mkt)    │   1   │ Alice (CEO) → Carol (VP Mkt)
Dave (Dir)        │   2   │ Alice (CEO) → Bob (VP Eng) → Dave (Dir)
Eve (Dir)         │   2   │ Alice (CEO) → Bob (VP Eng) → Eve (Dir)
Frank (Eng)       │   3   │ Alice (CEO) → Bob → Dave → Frank (Eng)
Grace (Eng)       │   3   │ Alice (CEO) → Bob → Dave → Grace (Eng)
Heidi (Mkt)       │   2   │ Alice (CEO) → Carol (VP Mkt) → Heidi (Mkt)</pre>
<p>The level column gives you depth. The path column builds a breadcrumb trail. Both are built incrementally: each iteration adds 1 to level and appends → emp_name to path.</p>
""") + L(3,"🟡","Number Generation, Fibonacci, and Graph Traversal","""
<h4>Beyond Hierarchies: Three More Recursive CTE Patterns</h4>
<p><strong>Pattern 1: Generating a number sequence without a numbers table.</strong> Instead of having a static table of integers for JOIN tricks, generate them on the fly:</p>
<pre>WITH RECURSIVE nums AS (
  SELECT 1 AS n          -- anchor: start at 1
  UNION ALL
  SELECT n + 1 FROM nums -- recursive: add 1 each time
  WHERE n &lt; 100          -- termination condition: stop at 100!
)
SELECT n FROM nums;      -- gives you 1, 2, 3, ... 100</pre>
<p>⚠️ <strong>Always include a termination condition</strong> (the WHERE clause in the recursive member). Without it, the query runs forever — an infinite loop that will kill your database connection or exhaust memory.</p>
<p><strong>Pattern 2: Date sequence generation.</strong> Fill in missing dates between two endpoints:</p>
<pre>WITH RECURSIVE date_range AS (
  SELECT '2024-01-01'::DATE AS d        -- anchor: start date
  UNION ALL
  SELECT d + INTERVAL 1 DAY FROM date_range
  WHERE d &lt; '2024-01-31'               -- stop at end date
)
SELECT d AS all_dates FROM date_range;   -- all 31 dates, even if no data</pre>
<p>Use case: LEFT JOIN this date_range to your events table to fill zeros on days with no activity — essential for rolling window calculations that would otherwise skip silent days.</p>
<p><strong>Pattern 3: Graph shortest path.</strong> Given a roads table (city_from, city_to, distance), find all cities reachable from London and their total distance:</p>
<pre>WITH RECURSIVE reachable AS (
  SELECT 'London' AS city, 0 AS total_dist
  UNION ALL
  SELECT r.city_to, rch.total_dist + r.distance
  FROM roads r JOIN reachable rch ON r.city_from = rch.city
  WHERE rch.total_dist &lt; 500            -- stop searching beyond 500 miles
)
SELECT DISTINCT city, MIN(total_dist) AS shortest FROM reachable GROUP BY city;</pre>
""") + L(4,"🔴","FAANG Interview: Bill of Materials + Cycle Detection","""
<h4>The Bill of Materials Problem (Amazon Interview Staple)</h4>
<p>A bill of materials (BOM) asks: "What are ALL the components needed to build product X, including components of components?" A car needs an engine which needs a cylinder block which needs bolts... the depth is unknown. This is recursive CTE territory.</p>
<pre>WITH RECURSIVE bom AS (
  SELECT component_id, component_name, parent_id, quantity, 1 AS depth
  FROM components WHERE parent_id IS NULL  -- top-level products
  UNION ALL
  SELECT c.component_id, c.component_name, c.parent_id, c.quantity, b.depth + 1
  FROM components c JOIN bom b ON c.parent_id = b.component_id
  WHERE b.depth &lt; 10   -- safety valve: never go deeper than 10 levels
)
SELECT * FROM bom ORDER BY depth;</pre>
<h4>Cycle Detection — The Critical Safety Check</h4>
<p>In graph data (not tree data), cycles can exist: A → B → C → A. Without protection, the recursive CTE loops forever. The defense: track the path as an array and stop if the next node is already in the array.</p>
<pre>WITH RECURSIVE traverse AS (
  SELECT node_id, ARRAY[node_id] AS visited_path
  FROM graph WHERE node_id = 1
  UNION ALL
  SELECT e.to_node, t.visited_path || e.to_node
  FROM edges e JOIN traverse t ON e.from_node = t.node_id
  WHERE NOT (e.to_node = ANY(t.visited_path))  -- stop if cycle detected!
)
SELECT * FROM traverse;</pre>
<p>Interview tip: always mention cycle detection when discussing recursive CTEs on graph data. Interviewers specifically check whether you know this failure mode — it's one of the most common causes of runaway queries in production.</p>
""") + '</div>',
"key_concepts": [
    "CTE = named subquery using WITH. Makes complex queries readable. Evaluated once per reference in most DBs.",
    "Recursive CTE = two parts joined by UNION ALL: anchor (seeds the recursion) + recursive member (references itself).",
    "The recursive member runs repeatedly until it produces zero new rows — that's the automatic stop condition.",
    "Always include an explicit termination condition (WHERE depth &lt; N) as a safety valve against infinite loops.",
    "level column: add 1 per iteration to track depth. path column: append names per iteration to build breadcrumbs.",
    "Cycle detection: track visited nodes in an array; stop if next node is already in the array (graph data only).",
    "Date sequence trick: generate all dates between two endpoints using recursive CTE to fill 'silent day' gaps.",
],
"hints": [
    "Infinite loop? You forgot the WHERE termination condition in the recursive member. Always add WHERE depth &lt; N.",
    "UNION vs UNION ALL in recursive CTEs: always use UNION ALL — UNION deduplicates on every iteration which is very slow.",
    "For manager hierarchy queries, always include a 'max depth' guard: even clean data can have accidental cycles.",
    "Date generation with recursive CTE is cleaner than a calendar table for ad-hoc ranges.",
],
"tasks": [
    "<strong>Step 1:</strong> Create the employee hierarchy table. Run the recursive CTE. Verify Frank and Grace appear at level 3.",
    "<strong>Step 2:</strong> Modify the query to also show how many direct reports each employee has (add a subquery count).",
    "<strong>Step 3:</strong> Write a number generator from 1 to 50. Extend it: show only even numbers.",
    "<strong>Step 4 — Write from scratch:</strong> Generate all dates in January 2024. LEFT JOIN to a sales table to show $0 for days with no sales.",
],
"hard_problem": "Boss Problem (LinkedIn): You have a table: connections(user_id, connected_to, connection_date). Write a query that finds all users reachable from user #1 within 3 degrees of connection (like LinkedIn's '3rd connection'). Return: user_id, degree, and the path of user IDs from user 1 to them. Handle cycles (mutual connections A↔B). Explain how performance degrades as the graph grows and what index you'd add.",
},

# ─── DAY 2: QUERY OPTIMIZATION ────────────────────────────────────
"query_optimization": {
"basics": '<div class="lesson-levels">' + L(1,"🟢","How the Database Actually Executes Your Query","""
<h4>The Hidden Machinery: Query Execution Pipeline</h4>
<p>When you press Enter on a SQL query, you think the database just "runs" it. In reality, there are 4 distinct steps, and understanding them is the key to knowing WHY some queries are fast and others crawl on the same data:</p>
<ol>
  <li><strong>Parsing:</strong> The SQL text is tokenized and parsed into a syntax tree. If you have a typo, the error happens here — before touching any data.</li>
  <li><strong>Optimization:</strong> The <em>query optimizer</em> — one of the most sophisticated pieces of software in a database — rewrites your query into the most efficient physical execution plan. It considers: which index to use, which table to scan first, how to order JOINs, whether to hash or sort. It evaluates thousands of possible plans and picks the cheapest based on cost estimates.</li>
  <li><strong>Execution:</strong> The plan is carried out on actual data, reading pages from disk or buffer cache.</li>
  <li><strong>Result return:</strong> Rows flow back to the client.</li>
</ol>
<p>You only write step 1 (the SQL text). Steps 2 and 3 are entirely the database's decision. But you can influence step 2 enormously by understanding what the optimizer looks for.</p>
<h4>The Most Important Tool: EXPLAIN / EXPLAIN ANALYZE</h4>
<p><code>EXPLAIN</code> shows what plan the optimizer chose <em>without running the query</em>. <code>EXPLAIN ANALYZE</code> runs the query AND shows actual vs estimated row counts — the discrepancy between those two numbers is where you find bugs in the optimizer's cost model.</p>
<pre>EXPLAIN ANALYZE
SELECT * FROM orders WHERE customer_id = 42;
-- Output shows: Seq Scan or Index Scan, rows estimated vs actual, time
-- "Seq Scan" = reading EVERY row = slow on large tables
-- "Index Scan" = jumping directly using an index = fast</pre>
<p>✍️ <strong>Rule 1:</strong> Anytime a query is slow, your first action is always EXPLAIN ANALYZE. Everything else is guessing.</p>
<h4>What "Slow Query" Actually Means</h4>
<p>A query that processes 1 million rows where it only needed to look at 100 is slow because of <em>unnecessary I/O</em>. Every row the database reads from disk costs time. The optimizer's #1 job is to minimize the rows read. Your job is to write SQL that gives the optimizer a chance to do that — by using indexed columns, avoiding function wrappers on columns, and joining in the right order.</p>
""") + L(2,"🔵","The Rules of Sargability — What the Optimizer Can and Can't Use","""
<h4>SARGable: Search ARGument able</h4>
<p>A query condition is <strong>sargable</strong> if the database engine can use an index to satisfy it. Non-sargable conditions force a full table scan — reading every single row even if only 1 matches. Learning to spot non-sargable patterns and fix them is worth hours of optimization effort.</p>
<pre>-- ❌ NON-SARGABLE: function wrapped around the column
-- The DB cannot use an index on order_date because it must first
-- call YEAR() on EVERY row to evaluate the condition.
SELECT * FROM orders WHERE YEAR(order_date) = 2024;

-- ✅ SARGABLE: rewrite as a RANGE on the raw column
-- The DB can jump directly to the first Jan 1 entry in the index.
SELECT * FROM orders WHERE order_date &gt;= '2024-01-01' AND order_date &lt; '2025-01-01';

-- ❌ NON-SARGABLE: arithmetic on the indexed column
SELECT * FROM orders WHERE order_amount * 1.1 &gt; 1000;

-- ✅ SARGABLE: move the math to the right side
SELECT * FROM orders WHERE order_amount &gt; 1000 / 1.1;   -- 909.09

-- ❌ NON-SARGABLE: LIKE with leading wildcard
-- '%ion' means "ends with ion" — no way to use alphabetical index
SELECT * FROM products WHERE name LIKE '%ion';

-- ✅ SARGABLE: leading-fixed LIKE
-- 'ion%' means "starts with ion" — index can seek to first 'ion' entry
SELECT * FROM products WHERE name LIKE 'ion%';</pre>
<p>The fix pattern is always the same: <em>never wrap the indexed column in a function or formula</em>. Instead, rewrite the condition so the column stands alone on one side of the operator and all transformations happen on the constant (literal value) side.</p>
<h4>The Optimizer's Cost Estimate — Why It Sometimes Gets It Wrong</h4>
<p>The optimizer doesn't "see" the data — it uses statistics (histograms of column value distributions) collected by the last ANALYZE command. If statistics are stale (your table grew by 10x since last ANALYZE), the optimizer may think a column has 1,000 distinct values when it actually has 1 billion — and choose a terrible plan. The fix: run <code>ANALYZE table_name</code> to refresh statistics on large tables after bulk loads.</p>
""") + L(3,"🟡","Join Order, Predicate Pushdown, and CTE Optimization","""
<h4>Join Order Matters More Than You Think</h4>
<p>When you join 3 tables, there are 6 possible join orders (3! = 6). The optimizer tries all of them and picks the cheapest. But on 10+ tables, this becomes 3.6 million possibilities — optimizers use heuristics instead, which can be wrong. The general rule: <strong>filter early, join small tables first</strong>. Bring large tables in late after they've been pre-filtered.</p>
<pre>-- ❌ Slow: JOIN all three tables first, THEN filter by high-value
SELECT o.order_id, c.name, p.category
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
JOIN products p ON o.product_id = p.product_id
WHERE o.revenue &gt; 10000;

-- ✅ Fast: filter orders FIRST (to a small set), then join
WITH high_value_orders AS (
  SELECT * FROM orders WHERE revenue &gt; 10000  -- reduce from 1B to 50K rows
)
SELECT h.order_id, c.name, p.category
FROM high_value_orders h
JOIN customers c ON h.customer_id = c.customer_id
JOIN products p ON h.product_id = p.product_id;</pre>
<h4>Predicate Pushdown</h4>
<p>Modern optimizers automatically "push" WHERE conditions as deep into the query plan as possible — applying filters before joins rather than after. But this has limits: conditions on computed columns, window functions, and some subqueries don't get pushed down automatically. Always apply your most selective filters as early as possible in your CTE chain — don't rely on the optimizer to do it.</p>
<h4>CTE Materialization — A Critical Database Difference</h4>
<p>In <strong>PostgreSQL 12+</strong>: CTEs are lazily evaluated — the optimizer can inline them and push predicates through. In <strong>older PostgreSQL and SQL Server</strong>: CTEs are "optimization fences" — they're evaluated once, results materialized into a temp table, optimizer cannot push outer WHERE into them. This makes some CTEs on old systems unexpectedly slow. Fix: use subqueries or WITH MATERIALIZED/NOT MATERIALIZED hints.</p>
""") + L(4,"🔴","FAANG-Scale: Reading EXPLAIN Plans and Common Anti-Patterns","""
<h4>Reading an EXPLAIN ANALYZE Output</h4>
<pre>EXPLAIN ANALYZE SELECT * FROM orders WHERE customer_id = 42;

-- Sample output:
-- Index Scan using orders_customer_idx on orders (cost=0.56..8.58 rows=3 width=120)
--   (actual time=0.042..0.044 rows=3 loops=1)
--   Index Cond: (customer_id = 42)
-- Planning Time: 0.3 ms
-- Execution Time: 0.1 ms
</pre>
<p><strong>What to look for:</strong></p>
<ul>
  <li><code>Seq Scan</code> on a large table = 🔴 missing index or optimizer chose wrong plan</li>
  <li><code>rows=3</code> estimated vs <code>rows=3 million</code> actual = 🔴 stale statistics, run ANALYZE</li>
  <li><code>Hash Join</code> with large hash table = 🟡 may spill to disk if work_mem is too small</li>
  <li><code>Nested Loop</code> on large tables = 🔴 usually means wrong join order or missing index</li>
  <li><code>Sort</code> before a window function without ORDER BY index = 🟡 add index on window ORDER BY column</li>
</ul>
<h4>Top 5 Query Anti-Patterns at FAANG Scale</h4>
<table>
<tr><th>Anti-Pattern</th><th>Why It's Slow</th><th>Fix</th></tr>
<tr><td>SELECT *</td><td>Reads all columns even if you need 2. Breaks column pruning in columnar stores.</td><td>List only needed columns</td></tr>
<tr><td>Subquery in WHERE per row</td><td>Runs the subquery once per outer row = N² scans</td><td>Convert to JOIN or EXISTS</td></tr>
<tr><td>DISTINCT to fix bad JOINs</td><td>Sorts/hashes entire result to deduplicate. Hides the real problem.</td><td>Fix the JOIN cardinality instead</td></tr>
<tr><td>OR on different columns</td><td>Cannot use index on either column — full scan</td><td>UNION ALL of two indexed queries</td></tr>
<tr><td>Implicit type cast</td><td>WHERE int_col = '42' casts every row to string — loses index</td><td>Match types: WHERE int_col = 42</td></tr>
</table>
""") + '</div>',
"key_concepts": [
    "Query execution: Parse → Optimize (choose plan) → Execute (read data) → Return. You influence step 2 via SQL structure.",
    "EXPLAIN ANALYZE: always your first debugging tool. Shows actual vs estimated rows — discrepancy = stale stats or bad plan.",
    "Sargable: condition the optimizer can use an index for. Non-sargable = full table scan.",
    "Never apply functions to indexed columns in WHERE. Rewrite: move transformations to the literal side.",
    "LIKE '%word' is non-sargable (leading wildcard). LIKE 'word%' is sargable (trailing wildcard only).",
    "Join order: filter early (small result sets), join large tables last. Most selective filter first.",
    "CTE materialization: PostgreSQL 12+ inlines CTEs. Older versions materialize them — can cause slowness.",
    "Stale optimizer statistics cause bad plans. Run ANALYZE after bulk loads on large tables.",
],
"hints": [
    "Slow query? EXPLAIN ANALYZE first, always. Never guess at optimization without the execution plan.",
    "Seq Scan on a large table = missing index OR non-sargable WHERE condition. Check both.",
    "SELECT * in production = red flag. Always list specific columns especially in columnar stores (BigQuery, Redshift).",
    "OR across different columns can't use indexes. Rewrite as UNION ALL of two queries, each using its own index.",
],
"tasks": [
    "<strong>Step 1:</strong> Write a query on orders with YEAR(order_date) = 2024. Run EXPLAIN. Note 'Seq Scan'. Then rewrite as a range condition and compare EXPLAIN output.",
    "<strong>Step 2:</strong> Write a query with a correlated subquery in WHERE (SELECT MAX(x) FROM other WHERE other.id = outer.id). Rewrite as a JOIN. Compare explain plans.",
    "<strong>Step 3:</strong> Write SELECT * from a 3-table join. Then rewrite selecting only 3 necessary columns. Is there a difference in execution time?",
    "<strong>Step 4:</strong> Create a table with 100,000 rows. Run EXPLAIN on a WHERE condition. Then run ANALYZE. Run EXPLAIN again. Did the estimated row count change?",
],
"hard_problem": "Boss Problem (Google): A table user_events(user_id, event_type, event_ts, session_id) has 10 billion rows. Query: count distinct users per event_type for last 24 hours, ordered by count DESC. The current query takes 45 minutes. Walk through: (1) What does EXPLAIN ANALYZE show? (2) What indexes would you add? (3) How would you rewrite the query? (4) Would you partition the table? On what column? (5) In BigQuery, why does SELECT * hurt this query more than in PostgreSQL?",
},

# ─── DAY 3: INDEXING ──────────────────────────────────────────────
"indexing": {
"basics": '<div class="lesson-levels">' + L(1,"🟢","Why Indexes Exist — The Library Analogy","""
<h4>The Problem: Finding a Needle in a 10-Billion-Row Haystack</h4>
<p>Imagine a library with 10 million books, organized in no particular order. You want "The Great Gatsby." Without a catalog, you'd have to walk through every single shelf, checking each book one by one. That's a <strong>sequential scan</strong> — exactly what the database does on an un-indexed column.</p>
<p>Now the librarian hands you a catalog — an alphabetical index of every book title mapped to its shelf location. You flip to G, find "Great Gatsby," see "Shelf 4B, position 22," walk directly there. Done. That's an <strong>index scan</strong> — the database equivalent.</p>
<p>On a 10-billion-row table, a sequential scan might read every row off disk over 10 minutes. An index scan jumps directly to the matching rows in 0.1 seconds. <strong>The index is often the difference between a query that works and one that doesn't.</strong></p>
<h4>What an Index Actually Is (Under the Hood)</h4>
<p>Most database indexes are <strong>B-Trees</strong> (Balanced Trees) — a sorted, tree-structured file stored separately from the main table data. The tree has a root node at the top, internal nodes that guide navigation, and leaf nodes at the bottom that contain the indexed column values plus pointers (physical addresses) to the actual table rows.</p>
<pre>B-Tree Index on salary column:
                    [50000]
                   /       \
           [30000]           [80000]
           /     \           /     \
       [10k,20k] [40k]  [60k,70k] [90k,95k]
         ↓         ↓       ↓          ↓
     (row pointers to actual table pages)</pre>
<p>To find salary = 90000: start at root, go right (90000 > 50000), go right again (90000 > 80000), read the leaf — find the row pointer — jump to that exact table page. 3 operations instead of 10 billion.</p>
<p>✍️ <strong>Key trade-off:</strong> Every index speeds up reads but slows down writes (INSERT/UPDATE/DELETE must update the index too). You never add indexes blindly — only on columns that appear in WHERE, JOIN ON, or ORDER BY of frequent, slow queries.</p>
""") + L(2,"🔵","B-Tree, Hash, and Composite Indexes — When to Use Each","""
<h4>The 4 Main Index Types</h4>
<p><strong>1. B-Tree Index (default)</strong> — works for equality, ranges, BETWEEN, LIKE 'prefix%', and ORDER BY. This is the index you use 90% of the time.</p>
<pre>CREATE INDEX idx_orders_date ON orders(order_date);
-- Now fast: WHERE order_date = '2024-01-15'
-- Also fast: WHERE order_date BETWEEN '2024-01-01' AND '2024-01-31'
-- Also fast: ORDER BY order_date (sorted already!)</pre>
<p><strong>2. Hash Index</strong> — works ONLY for equality checks (=). Faster than B-Tree for pure equality, but useless for ranges, sorting, or LIKE. Rare in practice.</p>
<pre>CREATE INDEX idx_users_email_hash ON users USING HASH (email);
-- Fast: WHERE email = 'alice@example.com'
-- ❌ Cannot use for: WHERE email LIKE 'alice%' or ORDER BY email</pre>
<p><strong>3. Composite Index (multi-column)</strong> — indexes multiple columns together. Column order matters critically.</p>
<pre>-- Composite index on (customer_id, order_date)
CREATE INDEX idx_orders_customer_date ON orders(customer_id, order_date);

-- ✅ Uses the index (matches leftmost prefix: customer_id)
SELECT * FROM orders WHERE customer_id = 42;

-- ✅ Uses the index (both columns in order)
SELECT * FROM orders WHERE customer_id = 42 AND order_date > '2024-01-01';

-- ❌ Does NOT use the index (skipped the first column!)
SELECT * FROM orders WHERE order_date > '2024-01-01';</pre>
<p><strong>The Leftmost Prefix Rule:</strong> A composite index (A, B, C) can be used for queries on: A alone, A+B together, or A+B+C together. It CANNOT be used for B alone or C alone or B+C without A. The index is like a phone book sorted by last name, then first name — you can look up by last name, or last+first, but not by first name alone.</p>
<p><strong>4. Covering Index (Partial Index)</strong> — if the index contains ALL columns the query needs, the DB never touches the main table at all (index-only scan).</p>
<pre>-- Query only needs customer_id and total_amount
CREATE INDEX idx_orders_covering ON orders(customer_id, total_amount);
-- Now this query reads the index only — never visits the table!
SELECT customer_id, SUM(total_amount) FROM orders WHERE customer_id = 42;</pre>
""") + L(3,"🟡","Index Selectivity, Bloat, and the Cases to AVOID Indexes","""
<h4>Selectivity — The Most Important Index Concept You're Never Taught</h4>
<p><strong>Selectivity</strong> is the ratio of distinct values to total rows. High selectivity = many distinct values relative to total rows = the index is useful. Low selectivity = few distinct values = the index is nearly worthless.</p>
<pre>Table: 10 million orders

Column: order_id (10M distinct values)
  Selectivity: 10M/10M = 100% → perfect index
  Finding one order: 3 B-Tree hops → 1 row returned

Column: status ('pending', 'shipped', 'delivered', 'cancelled')
  Selectivity: 4/10M = 0.00004% → terrible index!
  "WHERE status = 'shipped'" returns 3 million rows
  The DB will IGNORE the index and do a full table scan anyway —
  it's faster to scan sequentially than do 3M random I/O jumps</pre>
<p>Rule of thumb: if a WHERE condition returns more than ~5-10% of the table, the DB will ignore the index. Focus indexes on high-cardinality columns.</p>
<h4>Index Bloat — When Indexes Hurt Performance</h4>
<p>Every UPDATE and DELETE on indexed columns leaves "dead" entries in the B-Tree that aren't immediately removed. Over time, this bloat grows. A table with 1 million live rows might have an index 3x the size it should be — all dead entries. This wastes memory (buffer cache fills with dead pages) and slows scans. Fix: run <code>VACUUM ANALYZE</code> in PostgreSQL or <code>REBUILD INDEX</code> in SQL Server periodically.</p>
<h4>When NOT to Add an Index</h4>
<table>
<tr><th>Scenario</th><th>Reason to skip the index</th></tr>
<tr><td>Column with few distinct values (gender, boolean)</td><td>Low selectivity — DB will ignore it</td></tr>
<tr><td>Small tables (&lt; ~10,000 rows)</td><td>Full scan is faster than B-Tree overhead</td></tr>
<tr><td>Write-heavy tables (logs, events)</td><td>Every INSERT must update all indexes — can be 5x slower writes</td></tr>
<tr><td>Columns never in WHERE/JOIN/ORDER BY</td><td>Index never used — pure overhead</td></tr>
</table>
""") + L(4,"🔴","FAANG Patterns: Partial Indexes, Function Indexes, Index-Only Scans","""
<h4>3 Advanced Index Patterns Used in Production at FAANG</h4>
<p><strong>1. Partial Index</strong> — index only a subset of rows matching a condition. Dramatically smaller and faster than a full index when queries almost always filter on a fixed condition.</p>
<pre>-- 99% of queries only look at active users
-- Full index on user_id: 100M entries
-- Partial index: only 2M active user entries — 50x smaller!
CREATE INDEX idx_active_users ON users(user_id) WHERE status = 'active';
-- This index is only used for: WHERE user_id = X AND status = 'active'</pre>
<p><strong>2. Function-Based Index</strong> — index the result of a function on a column. Solves the non-sargable LOWER() problem.</p>
<pre>-- Queries always do case-insensitive email search
WHERE LOWER(email) = LOWER('Alice@Example.com')

-- Solution: index the lowercased value
CREATE INDEX idx_users_email_lower ON users(LOWER(email));
-- Now LOWER(email) = '...' uses the index!</pre>
<p><strong>3. Index-Only Scan (Covering Index)</strong> — the most powerful optimization: structure the index so all needed columns are IN the index, eliminating table heap access entirely.</p>
<pre>-- Query: monthly revenue per customer
SELECT customer_id, DATE_TRUNC('month', order_date), SUM(revenue)
FROM orders
GROUP BY 1, 2;

-- Create covering index with ALL 3 needed columns
CREATE INDEX idx_orders_cust_date_rev ON orders(customer_id, order_date, revenue);
-- Result: Seq scan on index only — never touches the table at all</pre>
<p>At petabyte scale (BigQuery, Redshift), covering indexes are replaced by <strong>column clustering</strong>: physically sorting the table by frequently used filter columns so range scans read contiguous pages. The concept is identical — reduce pages read for common access patterns.</p>
""") + '</div>',
"key_concepts": [
    "Sequential scan = read every row. Index scan = jump directly using B-Tree navigation.",
    "B-Tree: default index. Works for =, ranges, BETWEEN, ORDER BY, LIKE 'prefix%'. Not LIKE '%suffix'.",
    "Hash index: only for equality (=). Never for ranges or ordering.",
    "Composite index leftmost prefix rule: index(A,B,C) can be used on A, A+B, A+B+C — NOT B alone.",
    "Selectivity: high cardinality = useful index. Low cardinality (boolean, status) = index often ignored.",
    "Covering index: all queried columns in the index → index-only scan, never touches table heap.",
    "Index trade-off: speeds reads, slows writes. Every INSERT/UPDATE/DELETE must maintain all indexes.",
    "Partial index: index only rows matching a condition. Smaller, faster for queries that always filter on that condition.",
],
"hints": [
    "Add indexes on: WHERE columns, JOIN ON columns, ORDER BY columns of frequent slow queries.",
    "Low-cardinality columns (gender, boolean) get bad indexes. Check selectivity before indexing.",
    "Composite index: put the most-selective column first (highest cardinality) to prune the tree fastest.",
    "Missing covering index? Add the remaining SELECT columns as the trailing part of the index.",
],
"tasks": [
    "<strong>Step 1:</strong> Create an orders table with 50,000 rows and no index. Run EXPLAIN on a WHERE order_date query. Note 'Seq Scan'.",
    "<strong>Step 2:</strong> Add a B-Tree index on order_date. Re-run the same EXPLAIN. Note the plan change to 'Index Scan'.",
    "<strong>Step 3:</strong> Create a composite index on (customer_id, order_date). Test which of these 3 queries use it: (1) WHERE customer_id=42, (2) WHERE order_date>'2024-01-01', (3) WHERE customer_id=42 AND order_date>'2024-01-01'.",
    "<strong>Step 4:</strong> Design a covering index for: SELECT customer_id, SUM(revenue) FROM orders WHERE customer_id=42 GROUP BY customer_id.",
],
"hard_problem": "Boss Problem (Uber): You have a rides table: rides(ride_id, driver_id, rider_id, start_ts, end_ts, ride_status, city, fare). The following 3 queries are all slow on 5 billion rows: (Q1) WHERE city='NYC' AND ride_status='completed' AND start_ts > NOW()-30d; (Q2) WHERE driver_id=X ORDER BY start_ts DESC LIMIT 10; (Q3) SELECT city, AVG(fare) GROUP BY city WHERE ride_status='completed'. Design the optimal index for each query. Can one composite index serve all three? What are the trade-offs?",
},



# ─── DAY 4: COMPLEX JOINS & NULLs ────────────────────────────────
"complex_joins_nulls": {
"basics": '<div class="lesson-levels">' + L(1,"🟢","How Joins Actually Work — Not Just Syntax","""
<h4>What a JOIN Really Does</h4>
<p>Most engineers think of a JOIN as "connecting two tables." That's accurate but incomplete. Precisely: a JOIN produces every combination of rows from two tables that satisfies a matching condition. The database doesn't "link" rows — it tests each row from the left table against each row from the right table and keeps the pairs that match. Understanding this process explains why joins on large tables are expensive and how different join types produce different results.</p>
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
<h4>NULL is Not Zero, Not Empty String, Not False — It's Unknown</h4>
<p>NULL represents "the value is unknown or does not exist." This creates a <strong>three-valued logic system</strong> in SQL: TRUE, FALSE, and UNKNOWN. Any comparison with NULL returns UNKNOWN — not TRUE or FALSE. UNKNOWN in a WHERE clause means the row is silently dropped. This is the #1 source of subtle bugs in SQL.</p>
<pre>-- All of these return UNKNOWN (not TRUE, not FALSE!):
NULL = NULL     → UNKNOWN   -- two unknowns are not equal
NULL &lt;&gt; NULL    → UNKNOWN
NULL + 5        → NULL      -- any arithmetic with NULL = NULL
'text' || NULL  → NULL      -- any concatenation with NULL = NULL
NULL = 0        → UNKNOWN
NULL = ''       → UNKNOWN

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
SELECT COALESCE(phone, mobile, 'No contact') AS best_contact FROM users;

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
""") + '</div>',
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
    "'Find users who never did X': LEFT JOIN + WHERE right.key IS NULL. Don't use NOT IN if NULLs possible.",
    "COUNT(*) counts all rows including NULLs. COUNT(col) counts only non-NULL values. Know the difference.",
    "Join producing too many rows? Check if the join key is unique in both tables. Aggregate smaller side first.",
    "COALESCE(a, b, c): returns the first non-NULL. Perfect for fallback chains and report formatting.",
],
"tasks": [
    "<strong>Step 1:</strong> Create customers (5 rows) and orders (3 rows, 2 customers unordered). Write LEFT JOIN + WHERE IS NULL to find unordered customers. Verify 2 results.",
    "<strong>Step 2:</strong> Test NULL logic: SELECT NULL = NULL, NULL &lt;&gt; 5, COALESCE(NULL, NULL, 42). Verify the outputs.",
    "<strong>Step 3:</strong> Create a many-to-many join scenario (orders × order_items). Write the broken SUM query, verify it double-counts. Fix it with a pre-aggregated CTE.",
    "<strong>Step 4:</strong> Write a self-join to show each employee and their manager's name from a single employees table.",
],
"hard_problem": "Boss Problem (Stripe): Table: transactions(txn_id, user_id, amount, status, created_at). Another table: refunds(refund_id, txn_id, refund_amount, created_at). (1) Find all transactions that were partially refunded (refund_amount < transaction amount). (2) Find transactions with NO refund. (3) Find users who had more than 3 refunds in the last 30 days — flag them as fraud risk. Handle: a transaction can have multiple refunds. A refund can reference a NULL txn_id (orphaned refund). Does NULL in txn_id affect your NOT IN query?",
},

# ─── DAY 5: PERFORMANCE REVIEW ────────────────────────────────────
"performance_review": {
"basics": '<div class="lesson-levels">' + L(1,"🟢","The Performance Mindset — Measuring Before Optimizing","""
<h4>The Cardinal Rule: Measure First, Optimize Second</h4>
<p>The biggest mistake engineers make in performance optimization is guessing. They add an index, rewrite a join, or change a parameter — without measuring the before and after. Then they're surprised when the "optimization" made things slower, or didn't help at all.</p>
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
  Filter: (order_date &gt; '2024-01-01'::date)
  Rows Removed by Filter: 16759</pre>
<p>Breaking this down:</p>
<ul>
  <li><code>cost=0.00..42391.00</code>: Estimated cost in arbitrary units. First number = startup cost (before first row). Second = total cost.</li>
  <li><code>rows=1000000</code>: Optimizer's estimate of rows this node returns. Compare to actual!</li>
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
<h4>When Indexing Isn't Enough — Partition Pruning</h4>
<p>For truly enormous tables (100B+ rows), even a perfect B-Tree index may not be enough because the index itself becomes huge and lives on disk. The solution: <strong>table partitioning</strong> — physically splitting the table into smaller files (partitions) based on a partition key (usually a date).</p>
<p>When you query <code>WHERE order_date = '2024-01-15'</code>, the database reads ONLY the January 2024 partition file — ignoring all other 11 monthly files completely. This is called <strong>partition pruning</strong>. For a table with 10 years of data, you read 1/120th of the data automatically.</p>
<pre>-- PostgreSQL range partitioning by month
CREATE TABLE orders (
  order_id   BIGINT,
  order_date DATE,
  revenue    DECIMAL
) PARTITION BY RANGE (order_date);

CREATE TABLE orders_2024_01 PARTITION OF orders
  FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');
CREATE TABLE orders_2024_02 PARTITION OF orders
  FOR VALUES FROM ('2024-02-01') TO ('2024-03-01');
-- etc.

-- Now: WHERE order_date = '2024-01-15' reads ONLY orders_2024_01
EXPLAIN SELECT * FROM orders WHERE order_date = '2024-01-15';
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
<p>This is one of the most common FAANG data engineering interview questions. The expected answer is a structured, systematic diagnosis — not a list of guesses. Here's the exact framework:</p>
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
""") + '</div>',
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
    "'Our query is slow' interview question: always start with EXPLAIN ANALYZE, never guess first.",
    "Estimated rows=1, actual=1M: run ANALYZE to refresh statistics. This one command can fix a slow query instantly.",
    "Hash Join with high batch count → spilling to disk → increase work_mem in session: SET work_mem = '256MB'.",
    "Partition tables almost always by date for analytics workloads — time-range queries are the most common.",
],
"tasks": [
    "<strong>Step 1:</strong> On a large table, run EXPLAIN ANALYZE on a slow query. Find the node with the highest actual time.",
    "<strong>Step 2:</strong> Run ANALYZE on the table. Re-run EXPLAIN ANALYZE. Did the estimated row count improve?",
    "<strong>Step 3:</strong> Create a partitioned orders table with 2 monthly partitions. Run EXPLAIN on a date-filtered query. Verify partition pruning occurs.",
    "<strong>Step 4:</strong> Walk through the 5-step performance diagnosis framework for this scenario: 'SELECT * FROM events WHERE user_id=42 takes 60 seconds on a 5B-row table.'",
],
"hard_problem": "Boss Problem (Netflix): Your Spark job that computes daily user engagement metrics grew from 2h to 14h over 6 months as data volume tripled. Walk through your diagnosis and fix: (1) What metrics do you look at first? (2) You find 3 stages with massive shuffle — what causes that and how do you reduce it? (3) One executor is running 10x longer than others (data skew) — what's the fix? (4) The job reads 50TB but only uses 2TB after filtering — how do you fix this at the storage layer?",
},

# ─── DAY 6-7: REST ────────────────────────────────────────────────
"week2_rest": {
"basics": '<div class="lesson-levels">' + L(1,"🟢","Consolidation Day — How Expert Knowledge Forms","""
<h4>The Difference Between Knowing and Understanding</h4>
<p>At this point you've been exposed to CTE recursion, query optimization, indexing internals, join algorithms, NULL logic, and performance layers. These are the topics. But "knowing about them" and "understanding them" are different cognitive states.</p>
<p><strong>Knowing:</strong> You can recognize these concepts when someone mentions them. You remember the syntax. You could pick the right answer in a multiple-choice test.</p>
<p><strong>Understanding:</strong> You can look at a slow query you've never seen before and immediately know WHY it's slow. You can explain join fanout to someone else without notes. You reach for COALESCE automatically when you see a NULL risk. You notice a non-sargable WHERE condition while code-reviewing someone else's PR.</p>
<p>Understanding is built by retrieving knowledge under different conditions — not by re-reading it. Today's goal: <strong>retrieve</strong> what you learned this week in three different formats: writing, coding, and verbal explanation.</p>
""") + L(2,"🔵","Active Recall — No Notes","""
<h4>Answer These From Pure Memory (Write Answers Before Checking)</h4>
<pre>Recursive CTEs:
□ What are the two mandatory parts of a recursive CTE?
□ What keyword joins them? UNION or UNION ALL — which and why?
□ Write the termination condition syntax from memory
□ Name 3 use cases for recursive CTEs

Query Optimization:
□ What does EXPLAIN ANALYZE show that EXPLAIN alone doesn't?
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
<p>✍️ <strong>The most retained knowledge comes from teaching.</strong> Schedule 20 minutes this weekend to explain one of this week's topics to a colleague, friend, or the AI chatbot. Even if they know nothing about databases — the act of simplifying a concept to explain it to a non-expert cements it in your own memory far more than reading or re-reading.</p>
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
""") + '</div>',
"key_concepts": [
    "Understanding ≠ knowing. Understanding = applying concepts automatically in new, unseen situations.",
    "Active recall under time pressure is the closest simulation to a real interview — do it regularly.",
    "Three formats for retrieval: writing (explain in prose), coding (blank editor), verbal (explain to someone).",
    "The Feynman Technique for databases: explain EXPLAIN ANALYZE to a non-technical person. If you struggle, that's the gap.",
],
"hints": [
    "Use the AI chatbot as a practice interviewer: 'Give me a SQL optimization question about indexing.'",
    "Write SQL on paper — no autocomplete. If you can't write it on paper, you can't write it in an interview.",
    "Any score below 10/16 on the recall quiz: revisit that specific day's Level 1 + Level 2 content tomorrow.",
],
"tasks": [
    "<strong>Active recall:</strong> Write the recursive CTE pattern from memory. Include the anchor, UNION ALL, recursive member, and termination clause.",
    "<strong>EXPLAIN practice:</strong> Run EXPLAIN ANALYZE on a real query. Identify the slowest node. Propose one fix.",
    "<strong>Teach it:</strong> Explain the leftmost prefix rule for composite indexes to the chatbot using a concrete example.",
    "<strong>Mock interview:</strong> Set a 45-minute timer. Solve the 3 problems above without notes.",
],
"hard_problem": "Connect the dots: Explain how recursive CTEs, indexing strategy, query optimization, and join ordering would ALL work together in one production scenario: 'Find the top 5 highest-revenue customers for each account manager, where account managers are defined in a 4-level hierarchy, for orders placed in 2024, on a 10-billion-row orders table.' Walk through every decision.",
},

}
