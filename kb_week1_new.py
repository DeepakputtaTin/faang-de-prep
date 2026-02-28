def L(n, emoji, title, body):
    return f'''<div class="level level-{n}">
<div class="level-badge">{emoji} Level {n} — {title}</div>
<div class="rich">{body}</div>
</div>'''

WEEK1 = {

# ── DAY 1: WINDOW FUNCTION BASICS ─────────────────────────────────
"window_function_basics": {
"basics": '<div class="lesson-levels">' + L(1,"🟢","The Problem Window Functions Solve","""
<h4>Start Here — Before Any Code</h4>
<p>Let's say you're a data analyst at Spotify and your manager walks over with this question:<br>
<em>"Can you show me each employee's salary alongside the average salary for their department — but keep each employee as their own row?"</em></p>

<p>Your first instinct might be <code>GROUP BY department</code>. But here's the problem: <strong>GROUP BY collapses rows</strong>. Once you group, you get one row per department, not one row per employee. You lose the individual data. You can't have both the individual detail AND the group-level aggregation in the same result — unless you use a self-join (slow and complex).</p>

<p>This is exactly the gap that <strong>Window Functions</strong> fill. They compute calculations across a set of rows <em>related to the current row</em>, but unlike GROUP BY, <strong>they never collapse the result</strong>. Every row stays in the output. The function just adds a new computed column alongside.</p>

<h4>The Mental Model: A Sliding Frame of Glass</h4>
<p>Imagine placing a sheet of glass over a spreadsheet. The glass can be positioned to cover different sets of rows. For each row in your table, the database looks through that glass at the "window" of rows it covers, performs a calculation on those rows, and writes the result into a new column — then moves to the next row and repositions the glass.</p>

<pre>Your full table (5 rows):                Window for Alice's row:
┌───────┬─────────────┬────────┐         ┌───────┬─────────────┬────────┐
│ name  │ dept        │ salary │         │ Alice │ Engineering │ 95,000 │  ←
│ Alice │ Engineering │ 95,000 │  ───→   │ Bob   │ Engineering │ 85,000 │
│ Bob   │ Engineering │ 85,000 │         │ Eve   │ Engineering │ 90,000 │
│ Eve   │ Engineering │ 90,000 │         └───────┴─────────────┴────────┘
│ Carol │ Marketing   │ 70,000 │    Average of this window = 90,000
│ Dave  │ Marketing   │ 75,000 │    This value goes into Alice's new column
└───────┴─────────────┴────────┘    Then the window MOVES to Marketing rows</pre>

<h4>GROUP BY vs Window Functions — The Critical Difference</h4>
<pre>GROUP BY result:            Window Function result:
┌─────────────┬─────────┐   ┌───────┬─────────────┬────────┬──────────┐
│ dept        │ avg_sal │   │ name  │ dept        │ salary │ dept_avg │
├─────────────┼─────────┤   ├───────┼─────────────┼────────┼──────────┤
│ Engineering │  90,000 │   │ Alice │ Engineering │ 95,000 │  90,000  │
│ Marketing   │  72,500 │   │ Bob   │ Engineering │ 85,000 │  90,000  │
└─────────────┴─────────┘   │ Eve   │ Engineering │ 90,000 │  90,000  │
                             │ Carol │ Marketing   │ 70,000 │  72,500  │
2 rows — detail lost!        │ Dave  │ Marketing   │ 75,000 │  72,500  │
                             └───────┴─────────────┴────────┴──────────┘
                             5 rows — ALL detail preserved! ✅</pre>

<p>✍️ <strong>Write this down:</strong> Window functions NEVER reduce the number of rows in your output. They only ADD new computed columns. This is the single most important thing to remember about them.</p>

<h4>The Syntax Structure</h4>
<pre>FUNCTION_NAME() OVER (
    PARTITION BY column   -- defines which rows form the "window" for each row
    ORDER BY column       -- defines sort order within that window
    ROWS BETWEEN ...      -- optional: further limits the window frame
)</pre>
<p>The <code>OVER()</code> clause is what tells the database "this is a window function, not a regular aggregate." Without <code>OVER()</code>, <code>AVG(salary)</code> is a GROUP BY aggregate. With <code>OVER()</code>, it becomes a window function that keeps all rows.</p>
""") + L(2,"🔵","Understanding ROW_NUMBER — Step by Step","""
<h4>What ROW_NUMBER() Does (In Plain English)</h4>
<p><code>ROW_NUMBER()</code> assigns a unique sequential integer to each row within a window. Think of it like physically numbering the rows after sorting them — row #1, row #2, row #3, etc. The numbering restarts for each partition (group).</p>

<p><strong>Important:</strong> ROW_NUMBER always gives unique numbers. Even if two rows are equal in every way, they get different numbers. This makes it perfect for deduplication (keeping exactly one copy per group).</p>

<h4>Step 1 — Build the table</h4>
<pre>-- We create a simple employees table.
-- dept is VARCHAR not a foreign key in this example — keep it simple.
CREATE TABLE employees (
  emp_id   INT,
  emp_name VARCHAR(50),
  dept     VARCHAR(50),
  salary   INT
);

-- 5 employees across 2 departments
INSERT INTO employees VALUES
  (1, 'Alice', 'Engineering', 95000),
  (2, 'Bob',   'Engineering', 85000),
  (3, 'Carol', 'Marketing',   70000),
  (4, 'Dave',  'Marketing',   75000),
  (5, 'Eve',   'Engineering', 90000);</pre>

<h4>Step 2 — Your First Window Function</h4>
<pre>SELECT
  emp_name,
  dept,
  salary,
  ROW_NUMBER() OVER (
    PARTITION BY dept      -- restart the counter for each department
    ORDER BY salary DESC   -- sort highest salary first within each dept
  ) AS rank_in_dept
FROM employees;</pre>

<h4>Step 3 — Read the output and understand WHY each row got its number</h4>
<pre>emp_name │ dept        │ salary │ rank_in_dept
─────────┼─────────────┼────────┼─────────────
Alice    │ Engineering │  95000 │      1       ← highest in Eng dept → rank 1
Eve      │ Engineering │  90000 │      2       ← 2nd highest → rank 2
Bob      │ Engineering │  85000 │      3       ← 3rd highest → rank 3
Dave     │ Marketing   │  75000 │      1       ← RESTARTS! Dave is #1 in Marketing
Carol    │ Marketing   │  70000 │      2       ← #2 in Marketing</pre>

<p>Notice Dave gets rank_in_dept = 1 even though he earns less than Bob. Why? Because <code>PARTITION BY dept</code> told the database: "start a fresh ranking for each department." Dave is simply the highest-paid person in the Marketing partition — he deserves rank 1 in his department.</p>

<h4>What the Database Engine Actually Does</h4>
<p>When your database processes this query, here's the internal sequence:</p>
<ol>
  <li><strong>Read all rows</strong> from the employees table (5 rows)</li>
  <li><strong>Identify PARTITION groups</strong> — split rows into Engineering (3 rows) and Marketing (2 rows)</li>
  <li><strong>Sort each partition</strong> by salary DESC</li>
  <li><strong>Assign row numbers</strong> within each sorted partition, starting from 1</li>
  <li><strong>Attach the number</strong> to each original row and return everything</li>
</ol>
<p>The original 5 rows are never removed — only augmented with a new column.</p>
""") + L(3,"🟡","RANK vs DENSE_RANK vs ROW_NUMBER — When Ties Change Everything","""
<h4>Why Ties Matter More Than You Think</h4>
<p>In the real world, many values tie. Two employees earn the exact same salary. Two products have identical ratings. Two dates have equal revenue. The three ranking functions handle these ties differently, and choosing the wrong one gives you wrong business results.</p>

<p>Let's add Frank who earns exactly the same as Eve (90,000) to see what happens:</p>
<pre>INSERT INTO employees VALUES (6, 'Frank', 'Engineering', 90000);</pre>

<pre>SELECT
  emp_name, salary,
  ROW_NUMBER() OVER (ORDER BY salary DESC) AS row_num,
  RANK()       OVER (ORDER BY salary DESC) AS rnk,
  DENSE_RANK() OVER (ORDER BY salary DESC) AS dense_rnk
FROM employees WHERE dept = 'Engineering';</pre>

<h4>Output with Explanation</h4>
<pre>emp_name │ salary │ row_num │ rnk │ dense_rnk │ Explanation
─────────┼────────┼─────────┼─────┼───────────┼──────────────────────────────────────
Alice    │  95000 │    1    │  1  │     1     │ Unambiguous #1
Eve      │  90000 │    2    │  2  │     2     │ Tied with Frank
Frank    │  90000 │    3    │  2  │     2     │ Tied with Eve
Bob      │  85000 │    4    │  4  │     3     │ After the tie</pre>

<p>Look at Bob's row carefully. In <code>RANK()</code>, Bob gets rank 4 because ranks 1, 2, 2 are taken — rank 3 is "skipped" since two people share position 2. In <code>DENSE_RANK()</code>, Bob gets rank 3 with no skip.</p>

<h4>The Real-World Rule for Choosing</h4>
<table>
<tr><th>Question to ask</th><th>Use this</th><th>Why</th></tr>
<tr><td>"Do I need exactly ONE result per group (e.g., deduplication)?"</td><td>ROW_NUMBER()</td><td>Always unique, no ties possible</td></tr>
<tr><td>"Does the gap after a tie matter? (sports: no 3rd place if two 2nd places)"</td><td>RANK()</td><td>Skip shows the position gap is real</td></tr>
<tr><td>"Do I want sequential tiers? (medals, grade bands, product tiers)"</td><td>DENSE_RANK()</td><td>No gaps — Bronze is always 3rd tier</td></tr>
</table>

<p>✍️ <strong>Interview trap:</strong> LeetCode "Department Top Three Salaries" (Problem 185) — the question asks for top 3 <em>salary values</em>, not top 3 employees. If two people tie for 2nd, both appear. Use <code>DENSE_RANK</code> here, NOT <code>ROW_NUMBER</code>. Using <code>ROW_NUMBER</code> is the most common mistake in this interview problem.</p>
""") + L(4,"🔴","FAANG-Scale: Top-N Per Group + Production Secrets","""
<h4>The Most Important Window Function Pattern at FAANG</h4>
<p>The "Top-N per group" pattern appears in virtually every FAANG data engineering and analytics interview. Meta asks it. Amazon asks it. Google asks it. The reason: it tests whether you truly understand window functions or just memorized syntax.</p>

<p>The pattern has two parts: (1) rank the rows within each group using a CTE, (2) filter to keep only the top N ranks. You <strong>cannot</strong> use WHERE with a window function directly — window functions are evaluated in SELECT, but WHERE runs before SELECT in SQL's logical execution order. The CTE makes the rank visible so WHERE can filter on it.</p>

<pre>-- Classic pattern: top 3 earners per department
WITH ranked AS (
  SELECT
    emp_name,
    dept,
    salary,
    DENSE_RANK() OVER (          -- use DENSE_RANK if "top 3 salaries" (ties both show)
      PARTITION BY dept
      ORDER BY salary DESC
    ) AS rk
  FROM employees
)
SELECT dept, emp_name, salary
FROM ranked
WHERE rk &lt;= 3
ORDER BY dept, rk;</pre>

<h4>SQL Execution Order — Why the CTE Is Mandatory</h4>
<pre>SQL runs in this order (NOT the order you write it):
1. FROM       — identify the table(s)
2. WHERE      — filter rows (window functions don't exist yet!)
3. GROUP BY   — aggregate
4. HAVING     — filter aggregates
5. SELECT     — compute expressions including window functions  ← windows run HERE
6. ORDER BY   — sort the final result
7. LIMIT      — restrict output

So: WHERE rk &lt;= 3 in the outer query is VALID because by the time
we're back in that outer WHERE, the CTE has already run step 5 and
rk is a real column we can filter on.</pre>

<h4>Why PARTITION BY Matters at Petabyte Scale</h4>
<p>At companies like Meta or Google, this pattern runs on tables with billions of daily events. Without <code>PARTITION BY</code>, one single window covers ALL rows — this means one node must hold all data in memory to compute rankings. With <code>PARTITION BY dept</code>, each department's rows can be processed independently and in parallel across different machines. Good PARTITION BY choice is literally the difference between a query finishing in 30 seconds or running out of memory.</p>

<p><strong>Cardinality rule:</strong> Choose partition keys that split data into many roughly equal groups. <code>PARTITION BY user_id</code> (millions of users) = excellent parallelism. <code>PARTITION BY is_active</code> (just TRUE/FALSE) = terrible — one partition holds 99% of your data.</p>
""") + '</div>',
"key_concepts": [
    "Window functions compute across related rows WITHOUT collapsing them — unlike GROUP BY which removes individual rows.",
    "OVER() is the keyword that transforms any aggregate into a window function. Without OVER(), AVG() collapses rows. With OVER(), it keeps all rows.",
    "PARTITION BY divides the window into independent groups — like GROUP BY but without losing individual rows. Rankings restart per partition.",
    "ORDER BY inside OVER() determines sort order within each partition window — this controls which row gets rank 1.",
    "ROW_NUMBER(): always unique sequential integers. Use for dedup, pagination, keeping exactly 1 row per group.",
    "RANK(): ties get same number, next number is SKIPPED (1,2,2,4). Use when the gap after a tie is meaningful (sports, competitions).",
    "DENSE_RANK(): ties get same number, no skipping (1,2,2,3). Use for tiered rankings, product grades, interview question 185.",
    "Top-N per group pattern: wrap in CTE to rank, then WHERE rk <= N in outer query. Cannot filter on window function in same SELECT.",
    "SQL execution order: FROM → WHERE → GROUP BY → HAVING → SELECT (windows computed here) → ORDER BY → LIMIT.",
],
"hints": [
    "Whenever a question says 'per group' or 'within each category' — that's your signal to use PARTITION BY.",
    "DENSE_RANK vs ROW_NUMBER interview trap: if the question says 'top N values' (not top N rows), use DENSE_RANK so tied values both appear.",
    "Can't use window function in WHERE? Wrap in CTE first — this is always the solution.",
    "At scale: high-cardinality PARTITION BY keys (user_id, device_id) = good parallelism. Low-cardinality (boolean, status) = hotspot.",
    "NULL salaries sort LAST by default in DESC order. Add NULLS LAST explicitly to be safe: ORDER BY salary DESC NULLS LAST.",
],
"tasks": [
    "<strong>Step 1 — Setup:</strong> Run the CREATE TABLE and INSERT statements in a SQL editor (DB Fiddle at dbfiddle.uk is free). Verify 5 rows inserted.",
    "<strong>Step 2 — Run & verify:</strong> Execute the ROW_NUMBER query. Confirm Dave gets rank 1 in Marketing. Explain in writing WHY this happens.",
    "<strong>Step 3 — Experiment with ties:</strong> Add Frank (Engineering, 90000) and rerun with all three ranking functions. Write down the difference you see for Bob's row.",
    "<strong>Step 4 — Write from scratch:</strong> Without looking at the code above, write the Top-3-per-department query using DENSE_RANK. Check it returns both Eve and Frank when they tie.",
],
"hard_problem": "Boss Problem (Meta Interview): You have a 5-billion row table: user_events(user_id BIGINT, event_type VARCHAR, revenue DECIMAL, event_ts TIMESTAMP). Write a query that: (1) Ranks each user's events by revenue descending using DENSE_RANK, (2) Returns only their top 3 revenue events per user, (3) Also computes a running total revenue column per user. Now explain: Which PARTITION BY key did you choose and why? What happens to memory usage if you accidentally used no PARTITION BY on 5 billion rows? How would you run this in Spark instead of SQL?",
},

# ── DAY 2: ROLLING WINDOWS ────────────────────────────────────────
"rolling_windows": {
"basics": '<div class="lesson-levels">' + L(1,"🟢","Understanding Rolling Windows","""
<h4>The Business Problem First</h4>
<p>You're a data analyst at Netflix. Every day you get a report of how many hours of content were streamed. The daily number jumps around a lot — a new popular show drops on Saturday and the number spikes, then drops on Monday when people go back to work. Your VP of Content doesn't want to see these spiky daily numbers; they want to see the <em>trend</em>. "Is engagement growing over the past few weeks, or shrinking?"</p>

<p>What they're asking for is a <strong>moving average</strong> — also called a rolling average or sliding window average. Instead of reporting just today's number, you average the last 7 days together. When tomorrow arrives, you drop day 1 and add day 8, keeping the window exactly 7 days wide, always moving forward. The spikes get smoothed out, and the underlying trend becomes visible.</p>

<h4>The Physical Intuition</h4>
<pre>Daily streams data:    Day 1  Day 2  Day 3  Day 4  Day 5  Day 6  Day 7
                        100    80    120    90    110    95    105

3-day rolling window:
  Day 1: only [100]                          → avg = 100.0
  Day 2: [100, 80]                           → avg = 90.0
  Day 3: [100, 80, 120]   ← window full      → avg = 100.0
  Day 4:      [80, 120, 90]  ← 100 drops off → avg = 96.7
  Day 5:           [120, 90, 110]            → avg = 106.7
  Day 6:                [90, 110, 95]        → avg = 98.3
  Day 7:                     [110, 95, 105]  → avg = 103.3</pre>

<p>Notice what happens in the first few days: the window is smaller because there aren't enough prior rows to fill it. This is called a "partial window" — SQL handles this automatically. For Day 1, there's no Day 0 or Day -1, so the average is just of the one available row.</p>

<h4>Where Rolling Windows Are Used at FAANG</h4>
<ul>
  <li><strong>Finance:</strong> Stock price smoothing, portfolio 30-day rolling returns</li>
  <li><strong>Product:</strong> 7-day and 28-day rolling DAU/MAU ratios (Facebook's core engagement metric)</li>
  <li><strong>Operations:</strong> Detecting when a metric drops more than 2 standard deviations below its rolling baseline (anomaly detection)</li>
  <li><strong>Marketing:</strong> 14-day rolling conversion rates to account for the weekend effect</li>
</ul>

<p>✍️ <strong>Key formula to memorize:</strong> For a 7-day rolling window, you use <code>ROWS BETWEEN 6 PRECEDING AND CURRENT ROW</code> — that's 6 rows before + the current row = 7 rows total.</p>
""") + L(2,"🔵","Building Your First Rolling Window — Every Line Explained","""
<h4>The ROWS BETWEEN Clause — What It Actually Means</h4>
<p>Standard window functions use the default frame: all rows from the start of the partition to the current row. To control precisely <em>which rows</em> surround the current row, you use the <code>ROWS BETWEEN</code> clause. Think of it as telling the database: "when you're sitting on row N, look at rows N-2, N-1, and N — that's your window frame."</p>

<pre>CREATE TABLE daily_revenue (
  rev_date  DATE,
  revenue   DECIMAL(10,2)
);

INSERT INTO daily_revenue VALUES
  ('2024-01-01', 100), ('2024-01-02', 150),
  ('2024-01-03', 120), ('2024-01-04', 200),
  ('2024-01-05', 180), ('2024-01-06', 250), ('2024-01-07', 300);

SELECT
  rev_date,
  revenue,
  -- Running total: from very first row all the way to current row
  SUM(revenue) OVER (
    ORDER BY rev_date
    ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
  ) AS running_total,

  -- 3-day rolling average: only the last 3 rows including today
  ROUND(AVG(revenue) OVER (
    ORDER BY rev_date
    ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
  ), 2) AS rolling_avg_3d
FROM daily_revenue;</pre>

<h4>Output — Trace Through Each Row Manually</h4>
<pre>rev_date   │ revenue │ running_total │ rolling_avg_3d
───────────┼─────────┼───────────────┼───────────────
2024-01-01 │   100   │      100      │    100.00   ← only [100], partial window
2024-01-02 │   150   │      250      │    125.00   ← [100,150], partial window
2024-01-03 │   120   │      370      │    123.33   ← [100,150,120], full window now
2024-01-04 │   200   │      570      │    156.67   ← [150,120,200], 100 dropped
2024-01-05 │   180   │      750      │    166.67   ← [120,200,180]
2024-01-06 │   250   │     1000      │    210.00   ← [200,180,250]
2024-01-07 │   300   │     1300      │    243.33   ← [180,250,300]</pre>

<p>See how the running_total keeps growing (it never resets — UNBOUNDED PRECEDING brings in all history), while rolling_avg_3d only ever looks at the last 3 rows and forgets older data.</p>
""") + L(3,"🟡","ROWS vs RANGE — The Hidden Gotcha","""
<h4>Two Types of Window Frames — and Why They Produce Different Results</h4>
<p>SQL offers two ways to define the frame boundary: <code>ROWS</code> and <code>RANGE</code>. They seem identical but behave very differently when your data has <em>duplicate values in the ORDER BY column</em>.</p>

<ul>
  <li><strong>ROWS BETWEEN:</strong> counts physical rows regardless of their values. "2 PRECEDING" means exactly the 2 rows above in the sorted result, period.</li>
  <li><strong>RANGE BETWEEN:</strong> counts by value range. All rows with the same ORDER BY value as the current row are treated as part of the frame. This can include many more rows than you expect.</li>
</ul>

<pre>-- If two rows have rev_date = '2024-01-03' (duplicates):
ROWS BETWEEN 1 PRECEDING AND CURRENT ROW
  → always exactly 2 rows (1 before + current)

RANGE BETWEEN 1 PRECEDING AND CURRENT ROW
  → includes ALL rows with dates within 1 unit of current date
  → both Jan 3 entries are in each other's frames!

Which to use?
  ROWS  → when you want a fixed count of physical rows (moving average)
  RANGE → when you want a value-based boundary (sum within ±$50 of current price)</pre>

<p><strong>Default behavior:</strong> When you write <code>OVER (ORDER BY col)</code> with no ROWS or RANGE clause, SQL uses <code>RANGE BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW</code> by default. This means if you have duplicate dates, the running total will show the SAME cumulative value for all rows with that date (it includes all same-date rows). Use <code>ROWS BETWEEN</code> explicitly when you want predictable row-by-row behavior.</p>

<h4>The Most Common Rolling Window Patterns</h4>
<table>
<tr><th>Pattern</th><th>Frame Clause</th><th>Use Case</th></tr>
<tr><td>Running total</td><td>ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW</td><td>Cumulative sales, cumulative signups</td></tr>
<tr><td>7-day rolling avg</td><td>ROWS BETWEEN 6 PRECEDING AND CURRENT ROW</td><td>Smoothed engagement metrics</td></tr>
<tr><td>Centered 3-day avg</td><td>ROWS BETWEEN 1 PRECEDING AND 1 FOLLOWING</td><td>Smoothing without lag bias</td></tr>
<tr><td>Whole partition avg</td><td>ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING</td><td>Each row shows % of total</td></tr>
</table>
""") + L(4,"🔴","FAANG Pattern: Anomaly Detection with Rolling Baseline","""
<h4>How Netflix and Uber Actually Use Rolling Windows in Production</h4>
<p>One of the most valuable production uses of rolling windows is <strong>anomaly detection</strong>: automatically flagging when a metric falls unusually far below its recent historical baseline. A one-day drop might be normal noise; a drop of 3 standard deviations below the 30-day average is a signal that something broke in production.</p>

<p>The technique is called <strong>Z-score</strong>: how many standard deviations away from the mean is this data point? Z-score beyond ±2 = unusual. Beyond ±3 = almost certainly an anomaly.</p>

<pre>WITH rolling_stats AS (
  SELECT
    rev_date,
    revenue,
    -- Rolling average of PREVIOUS 30 days (not including today)
    -- Why exclude today? To create a "baseline" from before today's event
    AVG(revenue)    OVER (ORDER BY rev_date ROWS BETWEEN 29 PRECEDING AND 1 PRECEDING) AS avg_30d,
    STDDEV(revenue) OVER (ORDER BY rev_date ROWS BETWEEN 29 PRECEDING AND 1 PRECEDING) AS std_30d
  FROM daily_revenue
),
scored AS (
  SELECT *,
    -- Z-score: how many std deviations from the baseline?
    (revenue - avg_30d) / NULLIF(std_30d, 0) AS z_score
    -- NULLIF prevents division by zero when all 30 days had identical revenue
  FROM rolling_stats
  WHERE avg_30d IS NOT NULL   -- first 30 rows have no baseline, skip them
)
SELECT
  rev_date, revenue,
  ROUND(avg_30d, 2) AS baseline_avg,
  ROUND(z_score, 2) AS z_score,
  CASE
    WHEN z_score &lt; -2 THEN '🔴 ANOMALY — Revenue crash! Page on-call.'
    WHEN z_score &lt; -1 THEN '🟡 Warning — Below baseline, watch closely'
    WHEN z_score &gt;  2 THEN '🟢 Spike — Possible viral event, verify'
    ELSE '✅ Normal range'
  END AS alert_status
FROM scored
ORDER BY rev_date;</pre>

<p>This query pattern runs in production Spark jobs at FAANG for monitoring data pipeline health, detecting revenue anomalies, and flagging broken data ingestion — all automatically, without human review of every metric.</p>
""") + '</div>',
"key_concepts": [
    "Rolling window = compute over a sliding subset of rows that moves forward with each row.",
    "ROWS BETWEEN 6 PRECEDING AND CURRENT ROW = 7 rows total (6 before + current). N-day rolling = (N-1) PRECEDING.",
    "ROWS counts physical rows. RANGE counts by value — they differ when ORDER BY column has duplicates.",
    "UNBOUNDED PRECEDING = from the very first row of the partition. Use for running totals.",
    "Partial windows: for the first N-1 rows, the window is smaller than N. SQL handles this automatically and averages fewer rows.",
    "NULLIF(stddev, 0) prevents division by zero when all values in the window are identical.",
    "Default frame when you write OVER(ORDER BY col) with no ROWS/RANGE: RANGE BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW.",
],
"hints": [
    "7-day rolling avg: ROWS BETWEEN 6 PRECEDING AND CURRENT ROW. Always (N-1) PRECEDING for N-day window.",
    "Use ROWS not RANGE for moving averages — RANGE behaves unexpectedly with duplicate ORDER BY values.",
    "For anomaly detection, use ROWS BETWEEN 29 PRECEDING AND 1 PRECEDING (exclude today) to create a prior-only baseline.",
    "NULLIF(denominator, 0) is mandatory whenever you divide — zero stddev means all values are equal, division would crash.",
],
"tasks": [
    "<strong>Step 1:</strong> Create the daily_revenue table and insert the 7 rows. Run the Level 2 query and manually verify that Jan 4's rolling_avg_3d is (150+120+200)/3 = 156.67.",
    "<strong>Step 2:</strong> Change the rolling average to 5 days (ROWS BETWEEN 4 PRECEDING). How many rows have a partial window now? What does Jan 2's average become?",
    "<strong>Step 3:</strong> Write a query that shows revenue AND the % it represents of the total (revenue / SUM(revenue) OVER () * 100). What frame clause gives you the grand total in the denominator?",
    "<strong>Step 4:</strong> Explain in writing: why do we use ROWS BETWEEN 29 PRECEDING AND 1 PRECEDING in the anomaly detection query instead of 30 PRECEDING AND CURRENT ROW?",
],
"hard_problem": "Boss Problem (Airbnb): Table booking_events(booking_date DATE, property_id INT, revenue DECIMAL). Write a single query showing for each property: daily revenue, 30-day rolling average, % change vs same day last week (use LAG), and a flag 'DECLINING' if the 7-day rolling avg dropped >20% vs the prior 7-day period. Edge case: some properties have zero bookings on certain days — how do you handle the missing dates so your rolling window doesn't accidentally skip those days?",
},

}
