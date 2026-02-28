"""
Generator for kb_week1.py with deep narrative content.
Run: python build_kb_week1.py
"""

content = '''def L(n, emoji, title, body):
    return f\'\'\'<div class="level level-{n}">
<div class="level-badge">{emoji} Level {n} — {title}</div>
<div class="rich">{body}</div>
</div>\'\'\'

WEEK1 = {

# ─── DAY 1: WINDOW FUNCTION BASICS ────────────────────────────────
"window_function_basics": {
"basics": \'<div class="lesson-levels">\' + L(1,"🟢","The Problem Window Functions Solve","""
<h4>Start Here — Before Any Code</h4>
<p>You're a data analyst at Spotify. Your manager asks: <em>"Show me each employee\'s salary AND the average salary for their department — on the same row."</em></p>
<p>Your first instinct: <code>GROUP BY department</code>. Problem: <strong>GROUP BY collapses rows</strong>. You get one row per department, losing individual employee detail. You can\'t have both on the same row — unless you use a slow self-join. This is exactly the gap <strong>Window Functions</strong> fill: they compute aggregates across related rows while <strong>keeping every row in the output</strong>.</p>
<h4>The Mental Model: A Sliding Frame of Glass</h4>
<p>Imagine placing a sheet of glass over a spreadsheet. For each row, the database looks through that glass at a "window" of rows, performs a calculation, and writes the result back into a new column — without removing the original row.</p>
<pre>GROUP BY result:              Window Function result:
┌─────────────┬─────────┐    ┌───────┬─────────────┬────────┬──────────┐
│ dept        │ avg_sal │    │ name  │ dept        │ salary │ dept_avg │
├─────────────┼─────────┤    ├───────┼─────────────┼────────┼──────────┤
│ Engineering │  90,000 │    │ Alice │ Engineering │ 95,000 │  90,000  │
│ Marketing   │  72,500 │    │ Bob   │ Engineering │ 85,000 │  90,000  │
└─────────────┴─────────┘    │ Eve   │ Engineering │ 90,000 │  90,000  │
2 rows — detail lost!         │ Carol │ Marketing   │ 70,000 │  72,500  │
                              │ Dave  │ Marketing   │ 75,000 │  72,500  │
                              └───────┴─────────────┴────────┴──────────┘
                              5 rows — ALL detail preserved ✅</pre>
<p>✍️ <strong>Write this down:</strong> Window functions NEVER reduce row count. They only ADD new computed columns. The <code>OVER()</code> keyword is the signal that tells the database "this is a window function." Without OVER(), AVG() collapses rows. With OVER(), it keeps all rows.</p>
<h4>The Syntax Structure</h4>
<pre>FUNCTION_NAME() OVER (
    PARTITION BY column   -- which rows form the window for each row
    ORDER BY column       -- sort order within the window
    ROWS BETWEEN ...      -- optional: how many surrounding rows to include
)</pre>
""") + L(2,"🔵","ROW_NUMBER — Step by Step with Full Explanation","""
<h4>What ROW_NUMBER() Does</h4>
<p><code>ROW_NUMBER()</code> assigns a unique sequential integer to each row within a window, sorted as you specify. It ALWAYS gives unique numbers — even if two rows are completely identical. This makes it perfect for deduplication: you can always pick row #1 per group and discard the rest.</p>
<h4>Step 1 — Create and populate the table</h4>
<pre>CREATE TABLE employees (
  emp_id   INT,
  emp_name VARCHAR(50),
  dept     VARCHAR(50),
  salary   INT
);
INSERT INTO employees VALUES
  (1, \'Alice\', \'Engineering\', 95000),
  (2, \'Bob\',   \'Engineering\', 85000),
  (3, \'Carol\', \'Marketing\',   70000),
  (4, \'Dave\',  \'Marketing\',   75000),
  (5, \'Eve\',   \'Engineering\', 90000);</pre>
<h4>Step 2 — Run your first window function</h4>
<pre>SELECT
  emp_name, dept, salary,
  ROW_NUMBER() OVER (
    PARTITION BY dept      -- restart numbering for each department
    ORDER BY salary DESC   -- highest salary = rank 1
  ) AS rank_in_dept
FROM employees;</pre>
<h4>Step 3 — Trace the output and understand WHY</h4>
<pre>emp_name │ dept        │ salary │ rank_in_dept
─────────┼─────────────┼────────┼─────────────
Alice    │ Engineering │  95000 │      1    ← highest in Eng → rank 1
Eve      │ Engineering │  90000 │      2    ← 2nd in Eng
Bob      │ Engineering │  85000 │      3    ← 3rd in Eng
Dave     │ Marketing   │  75000 │      1    ← RESTARTS! Highest in Marketing
Carol    │ Marketing   │  70000 │      2    ← 2nd in Marketing</pre>
<p>Dave gets rank 1 even though he earns less than Bob — because PARTITION BY dept created a completely separate window for Marketing. Dave is simply the top earner within his own department\'s window.</p>
<h4>What the Engine Does Internally</h4>
<ol>
  <li>Read all 5 rows from the table</li>
  <li>Split into partitions: Engineering (3 rows), Marketing (2 rows)</li>
  <li>Sort each partition by salary DESC</li>
  <li>Assign row numbers 1,2,3... within each sorted partition</li>
  <li>Attach numbers back to original rows and return all 5 rows</li>
</ol>
""") + L(3,"🟡","RANK vs DENSE_RANK — Why Ties Change Everything","""
<h4>The Problem with Ties in Real Data</h4>
<p>In practice, duplicate values are common: two products with the same rating, two employees with the same salary, two cities with equal population. The three ranking functions handle ties differently, and choosing the wrong one produces wrong business results.</p>
<pre>-- Add Frank — same salary as Eve
INSERT INTO employees VALUES (6, \'Frank\', \'Engineering\', 90000);

SELECT emp_name, salary,
  ROW_NUMBER() OVER (ORDER BY salary DESC) AS row_num,
  RANK()       OVER (ORDER BY salary DESC) AS rnk,
  DENSE_RANK() OVER (ORDER BY salary DESC) AS dense_rnk
FROM employees WHERE dept = \'Engineering\';</pre>
<pre>emp_name │ salary │ row_num │ rnk │ dense_rnk
─────────┼────────┼─────────┼─────┼──────────
Alice    │  95000 │    1    │  1  │     1
Eve      │  90000 │    2    │  2  │     2    ← tied with Frank
Frank    │  90000 │    3    │  2  │     2    ← tied with Eve
Bob      │  85000 │    4    │  4  │     3    ← RANK skips 3, DENSE_RANK doesn\'t</pre>
<p>Bob gets RANK 4 because ranks 1, 2, 2 are taken — the number 3 is "skipped" to reflect that two people occupy the 2nd position. DENSE_RANK gives Bob a 3 with no gap.</p>
<h4>Choosing the Right Function</h4>
<table>
<tr><th>Need exactly one result per group (dedup)?</th><td>ROW_NUMBER()</td></tr>
<tr><th>Gap after tie is meaningful (sports: no 3rd if two share 2nd)?</th><td>RANK()</td></tr>
<tr><th>Sequential tiers without gaps (medals, grade bands)?</th><td>DENSE_RANK()</td></tr>
</table>
<p>✍️ <strong>Interview trap (LeetCode 185):</strong> "Top 3 salary values per department" — ties must BOTH appear. Use DENSE_RANK not ROW_NUMBER. ROW_NUMBER eliminates tied rows arbitrarily — wrong answer.</p>
""") + L(4,"🔴","FAANG Pattern: Top-N Per Group + Scale Secrets","""
<h4>The Most Common FAANG Window Function Pattern</h4>
<p>Top-N per group appears in virtually every FAANG interview. The key constraint: you CANNOT filter on a window function in the same SELECT — window functions run in step 5 of SQL\'s execution order, but WHERE runs in step 2. The solution is always a CTE.</p>
<pre>-- Top 3 earners per department
WITH ranked AS (
  SELECT emp_name, dept, salary,
    DENSE_RANK() OVER (PARTITION BY dept ORDER BY salary DESC) AS rk
    -- DENSE_RANK: if 2 people tie for 2nd, both appear in top 3
  FROM employees
)
SELECT dept, emp_name, salary
FROM ranked
WHERE rk &lt;= 3          -- NOW we can filter because rk is a real column
ORDER BY dept, rk;</pre>
<h4>SQL Execution Order — Memorize This</h4>
<pre>1. FROM       ← identify tables
2. WHERE      ← filter rows (window functions do NOT exist here yet!)
3. GROUP BY   ← aggregate
4. HAVING     ← filter aggregates
5. SELECT     ← compute expressions — window functions are evaluated HERE
6. ORDER BY   ← sort final result
7. LIMIT      ← restrict rows

This is why you need a CTE: the outer WHERE sees the CTE\'s rk column
because by then, the CTE\'s step 5 has already been executed.</pre>
<h4>Scale: Why PARTITION BY Key Choice Matters</h4>
<p>On billions of rows: good PARTITION BY keys (user_id, device_id) spread data across thousands of nodes — parallel and fast. Bad keys (is_active: TRUE/FALSE) dump 99% of data on one node — memory crash. Always ask: "does my partition key distribute data evenly?"</p>
""") + \'</div>\',
"key_concepts": [
    "Window functions compute over related rows WITHOUT collapsing output — unlike GROUP BY.",
    "OVER() transforms any aggregate into a window function. Without OVER: GROUP BY. With OVER: window.",
    "PARTITION BY = independent windows per group. Rankings restart per partition.",
    "ORDER BY inside OVER = sort order within partition. Determines which row gets rank 1.",
    "ROW_NUMBER(): always unique. Use for dedup, pagination, keeping exactly 1 row per group.",
    "RANK(): ties share same number, next is SKIPPED (1,2,2,4). Use for sports/competitions.",
    "DENSE_RANK(): ties share same number, no skip (1,2,2,3). Use for tiered rankings. Use for LeetCode 185.",
    "SQL execution order: FROM→WHERE→GROUP BY→HAVING→SELECT(windows here)→ORDER BY→LIMIT.",
    "Cannot use window function result in WHERE. Always wrap in CTE first.",
],
"hints": [
    "\'Per group\' or \'within each category\' → your signal to use PARTITION BY.",
    "LeetCode 185 trap: \'top 3 salaries\' not \'top 3 employees\' → DENSE_RANK so ties both show.",
    "Can\'t use window function in WHERE? Wrap in CTE — this is always the fix.",
    "High-cardinality PARTITION BY (user_id) = good parallelism. Low-cardinality (boolean) = hotspot.",
],
"tasks": [
    "<strong>Step 1:</strong> Create employees table and insert 5 rows. Run the ROW_NUMBER query. Explain in writing why Dave gets rank 1.",
    "<strong>Step 2:</strong> Add Frank (Engineering, 90000) and run all 3 ranking functions. Write the difference you see in Bob\'s row.",
    "<strong>Step 3:</strong> Write the DENSE_RANK top-3-per-department query from scratch without looking. Test it shows both Eve and Frank when tied.",
    "<strong>Step 4:</strong> Try adding WHERE rank_in_dept &lt;= 3 directly in the window query (no CTE). Note the error. Then fix it with a CTE.",
],
"hard_problem": "Boss Problem (Meta): 5-billion row table: user_events(user_id, event_type, revenue, event_ts). (1) Rank each user\'s events by revenue using DENSE_RANK. (2) Return only top 3 per user. (3) Add running total revenue per user. Explain: Which PARTITION BY key? What happens memory-wise with no PARTITION BY on 5B rows? How would you run this in Spark?",
},

# ─── DAY 2: ROLLING WINDOWS ───────────────────────────────────────
"rolling_windows": {
"basics": \'<div class="lesson-levels">\' + L(1,"🟢","What Rolling Windows Solve and Why","""
<h4>The Business Problem</h4>
<p>You\'re a data analyst at Netflix. Daily streaming hours spike on Saturdays and drop on Mondays. Your VP doesn\'t want spiky daily numbers — they want to see the <em>trend</em>. "Is engagement growing or shrinking?" The answer is a <strong>7-day rolling average</strong>: instead of just today\'s number, average the last 7 days. As each new day arrives, the oldest day drops off — the window "rolls" forward smoothly.</p>
<pre>Day data:   100   80   120   90   110   95   105
3-day rolling averages:
  Day 1: [100]             → avg = 100.0   (partial window — only 1 row)
  Day 2: [100, 80]         → avg = 90.0    (partial — only 2 rows)
  Day 3: [100, 80, 120]    → avg = 100.0   (full 3-day window)
  Day 4: [     80, 120, 90]→ avg = 96.7    (100 dropped off!)
  Day 5: [         120, 90, 110] → avg = 106.7</pre>
<p>The first N-1 rows have "partial windows" — there aren\'t enough prior rows yet. SQL handles this automatically, averaging whatever rows ARE available. This is normal and expected behavior.</p>
<h4>Where Rolling Windows Appear at FAANG</h4>
<ul>
  <li><strong>Facebook:</strong> 28-day rolling DAU/MAU ratio — their core engagement metric</li>
  <li><strong>Netflix:</strong> 7-day rolling content hours to smooth weekend effects</li>
  <li><strong>Uber:</strong> 30-day rolling driver earnings to assess compensation fairness</li>
  <li><strong>Finance:</strong> 200-day moving average used in stock trading algorithms</li>
</ul>
<p>✍️ <strong>Formula to memorize:</strong> For N-day rolling window → ROWS BETWEEN (N-1) PRECEDING AND CURRENT ROW. 7-day = 6 PRECEDING. 30-day = 29 PRECEDING.</p>
""") + L(2,"🔵","Building Rolling Windows — Every Clause Explained","""
<h4>The ROWS BETWEEN Clause</h4>
<p>By default, a window function without ROWS BETWEEN includes all rows from partition start to current row. ROWS BETWEEN lets you control exactly which surrounding rows to include. Think of it as telling the DB: "I\'m on row N, look at rows N-6 through N — those are my 7 rows."</p>
<pre>CREATE TABLE daily_revenue (
  rev_date DATE,
  revenue  DECIMAL(10,2)
);
INSERT INTO daily_revenue VALUES
  (\'2024-01-01\', 100), (\'2024-01-02\', 150),
  (\'2024-01-03\', 120), (\'2024-01-04\', 200),
  (\'2024-01-05\', 180), (\'2024-01-06\', 250), (\'2024-01-07\', 300);

SELECT
  rev_date,
  revenue,
  -- Running total: from the very first row to today — never resets
  SUM(revenue) OVER (
    ORDER BY rev_date
    ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
  ) AS running_total,
  -- 3-day rolling avg: only the 3 most recent rows
  ROUND(AVG(revenue) OVER (
    ORDER BY rev_date
    ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
  ), 2) AS rolling_3d_avg
FROM daily_revenue;</pre>
<pre>rev_date   │ revenue │ running_total │ rolling_3d_avg
───────────┼─────────┼───────────────┼───────────────
2024-01-01 │   100   │      100      │  100.00  ← partial: [100]
2024-01-02 │   150   │      250      │  125.00  ← partial: [100,150]
2024-01-03 │   120   │      370      │  123.33  ← full: [100,150,120]
2024-01-04 │   200   │      570      │  156.67  ← [150,120,200] — 100 dropped!
2024-01-05 │   180   │      750      │  166.67  ← [120,200,180]</pre>
<p>The running_total grows forever (never resets — UNBOUNDED PRECEDING brings all history). The rolling_3d_avg only ever sees 3 rows and forgets older data.</p>
""") + L(3,"🟡","ROWS vs RANGE — The Hidden Trap","""
<h4>Two Frame Types That Look Identical But Aren\'t</h4>
<p><strong>ROWS BETWEEN:</strong> counts physical rows. "2 PRECEDING" = exactly 2 rows above in sorted order, regardless of their values. Always predictable.</p>
<p><strong>RANGE BETWEEN:</strong> counts by value. All rows with the SAME ORDER BY value as the current row are treated as peers and included in the frame. This can include far more rows than you expect.</p>
<pre>-- If you have two rows both with rev_date=\'2024-01-03\':
ROWS BETWEEN 1 PRECEDING AND CURRENT ROW
  → exactly 2 rows always (1 before + current row)

RANGE BETWEEN 1 PRECEDING AND CURRENT ROW
  → includes BOTH Jan-3 rows in each Jan-3 row\'s frame
  → result: BOTH rows show the same running total value
  → can be very confusing!</pre>
<p><strong>Default:</strong> Writing just <code>OVER (ORDER BY col)</code> uses RANGE BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW. This means duplicate ORDER BY values all show the same cumulative total — sometimes desired, often surprising. Use ROWS BETWEEN explicitly for predictable behavior.</p>
<h4>Frame Clause Reference</h4>
<table>
<tr><th>What you want</th><th>Frame clause</th></tr>
<tr><td>Running total</td><td>ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW</td></tr>
<tr><td>7-day rolling avg</td><td>ROWS BETWEEN 6 PRECEDING AND CURRENT ROW</td></tr>
<tr><td>Centered avg (before+after)</td><td>ROWS BETWEEN 1 PRECEDING AND 1 FOLLOWING</td></tr>
<tr><td>% of grand total</td><td>ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING</td></tr>
</table>
""") + L(4,"🔴","FAANG: Anomaly Detection with Z-Score Rolling Baseline","""
<h4>How Netflix Detects Pipeline Failures Automatically</h4>
<p>In production, rolling windows power anomaly detection: when a daily metric drops more than 2 standard deviations below its prior 30-day average, alert the on-call engineer. This runs automatically via scheduled SQL or Spark jobs — no human manually reviews every metric.</p>
<p>The Z-score formula: <code>(today - rolling_avg) / rolling_stddev</code>. Values outside ±2 are flagged. We use ROWS BETWEEN 29 PRECEDING AND <strong>1 PRECEDING</strong> (not CURRENT ROW) to create a baseline from <em>before today</em> — otherwise today\'s anomaly would bias its own baseline.</p>
<pre>WITH rolling_stats AS (
  SELECT rev_date, revenue,
    AVG(revenue)    OVER (ORDER BY rev_date ROWS BETWEEN 29 PRECEDING AND 1 PRECEDING) AS avg_30d,
    STDDEV(revenue) OVER (ORDER BY rev_date ROWS BETWEEN 29 PRECEDING AND 1 PRECEDING) AS std_30d
  FROM daily_revenue
)
SELECT rev_date, revenue,
  ROUND((revenue - avg_30d) / NULLIF(std_30d, 0), 2) AS z_score,
  CASE
    WHEN (revenue - avg_30d) / NULLIF(std_30d, 0) &lt; -2 THEN \'🔴 ANOMALY\'
    WHEN (revenue - avg_30d) / NULLIF(std_30d, 0) &gt;  2 THEN \'🟡 SPIKE\'
    ELSE \'✅ Normal\'
  END AS status
FROM rolling_stats
WHERE avg_30d IS NOT NULL  -- skip first 30 rows: no baseline yet
ORDER BY rev_date;</pre>
<p><code>NULLIF(std_30d, 0)</code> prevents division by zero when all 30 days had identical revenue — returns NULL instead of crashing. Always include this when dividing by a window aggregate.</p>
""") + \'</div>\',
"key_concepts": [
    "Rolling window = sliding subset of rows that moves with each row. Window slides forward, oldest row drops off.",
    "N-day rolling window → ROWS BETWEEN (N-1) PRECEDING AND CURRENT ROW.",
    "ROWS counts physical rows (predictable). RANGE counts by value (can include many more rows with duplicate values).",
    "UNBOUNDED PRECEDING = from partition start. Use for running totals that never reset.",
    "Partial windows: first N-1 rows have fewer than N rows available. SQL averages what exists — this is correct behavior.",
    "NULLIF(denominator, 0): prevents division by zero in Z-score and percentage calculations.",
    "Anomaly baseline: use 1 PRECEDING not CURRENT ROW to exclude today from its own baseline.",
],
"hints": [
    "7-day rolling: ROWS BETWEEN 6 PRECEDING AND CURRENT ROW. Always N-1 PRECEDING for N-day.",
    "Use ROWS not RANGE for moving averages — RANGE surprises you with duplicate ORDER BY values.",
    "Rolling % of total: OVER(ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) gives grand total.",
    "In anomaly detection, always exclude today from the baseline window (1 PRECEDING not CURRENT ROW).",
],
"tasks": [
    "<strong>Step 1:</strong> Create daily_revenue table with 7 rows. Run Level 2 query. Manually verify Jan 4 rolling_3d_avg = (150+120+200)/3 = 156.67.",
    "<strong>Step 2:</strong> Change to 5-day rolling. How many rows still have partial windows? What does Jan 2 become?",
    "<strong>Step 3:</strong> Write a query showing each day\'s revenue as % of the grand total. What frame gives you the grand total in the denominator?",
    "<strong>Step 4 (write from memory):</strong> Without looking, write the Z-score anomaly detection query. Test: insert an extreme value (revenue=10000 on Jan 8) and verify it gets flagged.",
],
"hard_problem": "Boss Problem (Airbnb): Table booking_events(booking_date, property_id, revenue). For each property show: daily revenue, 30-day rolling avg, % change vs same day last week (LAG), flag \'DECLINING\' if 7-day rolling avg dropped >20% vs prior 7-day period. Edge case: some properties have zero bookings on certain dates — how do you fill the missing dates so your 7-day window doesn\'t skip them?",
},

# ─── DAY 3: LAG/LEAD ─────────────────────────────────────────────
"lead_lag": {
"basics": \'<div class="lesson-levels">\' + L(1,"🟢","Comparing Adjacent Rows — The Problem","""
<h4>The Problem: Row-to-Row Comparison</h4>
<p>You have a table of daily stock prices. Your manager asks: <em>"How much did Apple\'s stock move from yesterday to today?"</em> Each row only knows its own date and price — it doesn\'t automatically "see" the previous row.</p>
<p>The naive solution is a self-join: join the table to itself where today\'s date equals yesterday\'s date plus one day. But self-joins on large tables are slow, complex to write, and break when dates have gaps (weekends, holidays). <code>LAG</code> and <code>LEAD</code> solve this cleanly in one pass.</p>
<ul>
  <li><strong>LAG(col, n, default)</strong> — looks BACKWARDS n rows from the current row. Returns the value of col from n rows ago, or the default if no such row exists.</li>
  <li><strong>LEAD(col, n, default)</strong> — looks FORWARDS n rows. Returns the value from n rows ahead.</li>
</ul>
<pre>Sorted by date:
  Row 1 (Jan 1): price=185  → LAG returns NULL (no prior row), LEAD returns 188.50
  Row 2 (Jan 2): price=188.50 → LAG returns 185, LEAD returns 182
  Row 3 (Jan 3): price=182  → LAG returns 188.50, LEAD returns 191
  Row 4 (Jan 4): price=191  → LAG returns 182, LEAD returns NULL (no next row)</pre>
<p>✍️ LAG requires ORDER BY in the OVER clause — without it, "previous" has no meaning. Always include PARTITION BY when you want the lookback to reset at group boundaries (e.g., per stock symbol).</p>
""") + L(2,"🔵","LAG in Action — Day-over-Day Price Change","""
<pre>CREATE TABLE stock_prices (
  trade_date  DATE,
  symbol      VARCHAR(10),
  close_price DECIMAL(10,2)
);
INSERT INTO stock_prices VALUES
  (\'2024-01-01\', \'AAPL\', 185.00),
  (\'2024-01-02\', \'AAPL\', 188.50),
  (\'2024-01-03\', \'AAPL\', 182.00),
  (\'2024-01-04\', \'AAPL\', 191.00),
  (\'2024-01-05\', \'AAPL\', 189.00);

SELECT
  trade_date, close_price,
  -- LAG(column, offset, default_if_null)
  LAG(close_price, 1, 0) OVER (
    PARTITION BY symbol   -- reset for each stock symbol
    ORDER BY trade_date   -- "previous" means previous trading day
  ) AS prev_close,
  -- Dollar change: today minus yesterday
  close_price - LAG(close_price) OVER (PARTITION BY symbol ORDER BY trade_date) AS dollar_change,
  -- % change: (today-yesterday)/yesterday * 100
  ROUND(100.0 * (close_price - LAG(close_price) OVER (PARTITION BY symbol ORDER BY trade_date))
    / NULLIF(LAG(close_price) OVER (PARTITION BY symbol ORDER BY trade_date), 0), 2) AS pct_change
FROM stock_prices;</pre>
<pre>trade_date │ close │ prev_close │ dollar_change │ pct_change
───────────┼───────┼────────────┼───────────────┼───────────
2024-01-01 │ 185.0 │      0.00  │     NULL      │   NULL    ← no prior row
2024-01-02 │ 188.5 │    185.00  │     3.50      │   1.89
2024-01-03 │ 182.0 │    188.50  │    -6.50      │  -3.44   ← price dropped
2024-01-04 │ 191.0 │    182.00  │     9.00      │   4.95
2024-01-05 │ 189.0 │    191.00  │    -2.00      │  -1.05</pre>
<p>The third argument to LAG (the 0 in <code>LAG(close_price, 1, 0)</code>) is the default value returned when there is no prior row (the first row). Without it, you get NULL, which can crash downstream percentage calculations.</p>
""") + L(3,"🟡","Session Detection with LAG — Uber Pattern","""
<h4>Finding Time Gaps Between Events</h4>
<p>A "session" in product analytics is a group of consecutive events with no long gap between them. If a user makes 5 clicks within 10 minutes, that\'s one session. If they then come back 2 hours later, that\'s a new session. LAG lets you detect the boundary: wherever the time gap between two consecutive events exceeds the threshold, a new session starts.</p>
<pre>-- Step 1: compute the gap between each event and the one before it
WITH event_gaps AS (
  SELECT
    user_id, event_type, event_ts,
    LAG(event_ts) OVER (PARTITION BY user_id ORDER BY event_ts) AS prev_ts,
    TIMESTAMPDIFF(MINUTE,
      LAG(event_ts) OVER (PARTITION BY user_id ORDER BY event_ts),
      event_ts
    ) AS gap_minutes
  FROM user_events
),
-- Step 2: mark each row as a new-session-start if gap > 30 min or it\'s the first event
session_markers AS (
  SELECT *,
    SUM(CASE WHEN gap_minutes > 30 OR gap_minutes IS NULL THEN 1 ELSE 0 END)
      OVER (PARTITION BY user_id ORDER BY event_ts) AS session_id
    -- SUM of 1s: every time a new session starts, the running count increments
    -- This gives a unique session_id per session per user
  FROM event_gaps
)
-- Step 3: aggregate each session
SELECT
  user_id, session_id,
  MIN(event_ts) AS session_start,
  MAX(event_ts) AS session_end,
  COUNT(*)      AS events_in_session,
  TIMESTAMPDIFF(MINUTE, MIN(event_ts), MAX(event_ts)) AS session_duration_mins
FROM session_markers
GROUP BY user_id, session_id
ORDER BY user_id, session_start;</pre>
<p>The key insight: <code>SUM(CASE WHEN new_session THEN 1 ELSE 0 END) OVER (ORDER BY ts)</code> creates a running count of how many sessions have started so far — which becomes a unique session number per user.</p>
""") + L(4,"🔴","Month-over-Month and Year-over-Year with LAG","""
<h4>The Most Common Reporting Pattern in Business Intelligence</h4>
<p>Every business dashboard needs month-over-month and year-over-year comparisons. LAG with offset=1 gives you last month; LAG with offset=12 gives you the same month last year. The key trick: pre-aggregate to monthly first (GROUP BY), then apply LAG in a CTE or subquery on the monthly totals.</p>
<pre>WITH monthly_revenue AS (
  SELECT
    DATE_TRUNC(\'month\', order_date) AS month,
    SUM(revenue) AS monthly_rev
  FROM orders
  GROUP BY 1
),
comparisons AS (
  SELECT
    month, monthly_rev,
    LAG(monthly_rev, 1) OVER (ORDER BY month) AS prev_month,
    LAG(monthly_rev, 12) OVER (ORDER BY month) AS same_month_last_year
  FROM monthly_revenue
)
SELECT
  month, monthly_rev,
  -- MoM change: (this month - last month) / last month * 100
  ROUND(100.0 * (monthly_rev - prev_month) / NULLIF(prev_month, 0), 1) AS mom_pct,
  -- YoY change: (this month - same month last year) / same month last year * 100
  ROUND(100.0 * (monthly_rev - same_month_last_year) / NULLIF(same_month_last_year, 0), 1) AS yoy_pct
FROM comparisons
ORDER BY month;</pre>
<p>Always wrap the LAG value in NULLIF(value, 0) before dividing — if last month\'s revenue was zero (new product, seasonal lull), division by zero crashes the query or produces infinity.</p>
""") + \'</div>\',
"key_concepts": [
    "LAG(col, n, default): look back n rows. Returns default (not NULL) when no prior row exists.",
    "LEAD(col, n, default): look forward n rows. Returns default when no next row exists.",
    "Both require ORDER BY inside OVER — without it, \'previous\' and \'next\' are undefined.",
    "PARTITION BY resets LAG/LEAD boundaries per group (e.g., per stock symbol, per user).",
    "LAG(col, 12) = same value 12 rows back = same month last year (when data is monthly).",
    "Session detection: SUM of new-session flags OVER (ORDER BY time) creates unique session IDs.",
    "NULLIF(denominator, 0): always use when dividing by a LAG value to prevent division-by-zero.",
],
"hints": [
    "First row returns NULL from LAG with no default — this crashes % change calculations. Always add default 0.",
    "% change formula: (new - old) / NULLIF(old, 0) * 100. Always NULLIF the denominator.",
    "Session detection: gap > threshold OR gap IS NULL (IS NULL = the first event per user, always a new session).",
    "LeetCode 180 \'Consecutive Numbers\': uses LAG twice to look at previous two rows. Practice this.",
],
"tasks": [
    "<strong>Step 1:</strong> Create stock_prices and run the Level 2 query. Verify Jan 3 shows dollar_change = -6.50.",
    "<strong>Step 2:</strong> Add the pct_change column. What happens to Jan 1 pct_change without NULLIF? Add NULLIF and confirm it becomes NULL instead of an error.",
    "<strong>Step 3:</strong> Use LEAD to add a \'tomorrow_price\' column. For the last row (Jan 5), what does LEAD return?",
    "<strong>Step 4:</strong> Identify all consecutive 2-day price increases using LAG twice: WHERE today > yesterday AND yesterday > day-before-yesterday.",
],
"hard_problem": "Boss Problem (LinkedIn): Table post_views(post_id, view_date, view_count). Write a query: (1) daily view count, (2) 7-day % change using LAG(7), (3) classify each row as \'VIRAL\' (>20% gain), \'DECLINING\' (>20% loss), or \'STABLE\'. Optimize for 1 billion rows: what index would you add? What partition strategy in Spark?",
},

# ─── DAY 4: GAPS & ISLANDS ────────────────────────────────────────
"gaps_islands_logic": {
"basics": \'<div class="lesson-levels">\' + L(1,"🟢","Finding Breaks in Sequences — The Intuition","""
<h4>The Problem: SQL Doesn\'t Understand \'Consecutive\'</h4>
<p>You\'re a data engineer at Duolingo. You have a table of dates when users studied. The product team wants to know: "What are each user\'s study streaks — continuous blocks of consecutive study days?" A streak is a run of consecutive days with no gap.</p>
<pre>User 42\'s study dates:
Jan 1, Jan 2, Jan 3, [gap: Jan 4 missing], Jan 5, Jan 6, [gap], Jan 10
                                                                      ↑
Islands (continuous streaks):    Gaps (missing days):
  Island 1: Jan 1 → Jan 3         Gap 1: Jan 4
  Island 2: Jan 5 → Jan 6         Gap 2: Jan 7, 8, 9
  Island 3: Jan 10</pre>
<p>SQL can sort rows and count them, but it has no built-in concept of "these rows are consecutive." We need a trick to group consecutive dates together. This is the <strong>Gaps & Islands</strong> problem — one of the most elegant SQL puzzles and heavily tested at FAANG.</p>
<h4>The Core Insight — date minus row_number ✍️</h4>
<p>For consecutive dates, if you subtract the row\'s sequential number from the date itself, you get the SAME constant value for every date in the same island. When a gap occurs, the constant changes. This is the key: use that constant as a GROUP BY key to aggregate each island.</p>
<pre>date    rn    date - rn
Jan 1    1    Dec 31    ←┐ same value = same island
Jan 2    2    Dec 31    ←┘
Jan 3    3    Dec 31    ←┘ all three in Island 1
Jan 5    4    Jan 1     ← DIFFERENT value = new island!
Jan 6    5    Jan 1     ←─ Island 2
Jan 10   6    Jan 4     ← another new island</pre>
""") + L(2,"🔵","Step-by-Step Implementation","""
<pre>CREATE TABLE user_logins (user_id INT, login_date DATE);
INSERT INTO user_logins VALUES
  (1,\'2024-01-01\'),(1,\'2024-01-02\'),(1,\'2024-01-03\'),
  -- gap: Jan 4 missing --
  (1,\'2024-01-05\'),(1,\'2024-01-06\'),
  -- gap: Jan 7,8,9 --
  (1,\'2024-01-10\');</pre>

<h4>Step 1 — Assign row numbers and compute the group key</h4>
<pre>SELECT
  user_id, login_date,
  ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY login_date) AS rn,
  login_date - INTERVAL (
    ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY login_date)
  ) DAY AS group_key   -- this is constant for consecutive dates!
FROM user_logins;</pre>
<pre>Output:
user_id │ login_date  │ rn │ group_key
────────┼─────────────┼────┼───────────
   1    │ 2024-01-01  │  1 │ 2023-12-31  ← Island 1
   1    │ 2024-01-02  │  2 │ 2023-12-31  ← same!
   1    │ 2024-01-03  │  3 │ 2023-12-31  ← same!
   1    │ 2024-01-05  │  4 │ 2024-01-01  ← Island 2
   1    │ 2024-01-06  │  5 │ 2024-01-01  ← same!
   1    │ 2024-01-10  │  6 │ 2024-01-04  ← Island 3</pre>

<h4>Step 2 — GROUP BY the group key to get each island\'s bounds</h4>
<pre>WITH numbered AS (
  SELECT user_id, login_date,
    login_date - INTERVAL (ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY login_date)) DAY AS grp
  FROM user_logins
)
SELECT
  user_id,
  MIN(login_date) AS streak_start,
  MAX(login_date) AS streak_end,
  COUNT(*)        AS streak_days
FROM numbered
GROUP BY user_id, grp
ORDER BY user_id, streak_start;</pre>
<pre>user_id │ streak_start │ streak_end  │ streak_days
────────┼──────────────┼─────────────┼────────────
   1    │ 2024-01-01   │ 2024-01-03  │      3
   1    │ 2024-01-05   │ 2024-01-06  │      2
   1    │ 2024-01-10   │ 2024-01-10  │      1</pre>
""") + L(3,"🟡","Finding the Gaps (Missing Dates)","""
<h4>From Islands to Gaps — What\'s Missing?</h4>
<p>Once you have island boundaries (start and end of each streak), finding the gaps is straightforward: a gap starts the day AFTER an island ends and finishes the day BEFORE the next island starts. Use LEAD to look at the next island\'s start.</p>
<pre>WITH numbered AS (
  SELECT user_id, login_date,
    login_date - INTERVAL (ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY login_date)) DAY AS grp
  FROM user_logins
),
islands AS (
  SELECT user_id,
    MIN(login_date) AS island_start,
    MAX(login_date) AS island_end
  FROM numbered
  GROUP BY user_id, grp
),
gaps AS (
  SELECT
    user_id,
    island_end + INTERVAL 1 DAY AS gap_start,
    LEAD(island_start) OVER (PARTITION BY user_id ORDER BY island_start)
      - INTERVAL 1 DAY AS gap_end,
    DATEDIFF(
      LEAD(island_start) OVER (PARTITION BY user_id ORDER BY island_start),
      island_end
    ) - 1 AS gap_days
  FROM islands
)
SELECT * FROM gaps WHERE gap_days > 0;</pre>
<pre>user_id │ gap_start   │ gap_end     │ gap_days
────────┼─────────────┼─────────────┼─────────
   1    │ 2024-01-04  │ 2024-01-04  │    1     ← Jan 4 missing
   1    │ 2024-01-07  │ 2024-01-09  │    3     ← Jan 7,8,9 missing</pre>
<p>FAANG uses this exact pattern for: billing gaps (subscription payment missing), SLA violations (service down for N hours), outage windows (server status logs), and content recommendation dead zones (user didn\'t watch for N days).</p>
""") + L(4,"🔴","Session Detection and Advanced Variants","""
<h4>Gaps & Islands with Timestamps (Meta Interview Question)</h4>
<p>The same pattern works for timestamps. Define a "session" as: consecutive events where no gap exceeds 30 minutes. Instead of subtracting a row number from a date, you use a different grouping technique: a running SUM of "did this event start a new session?" flags.</p>
<pre>WITH diffs AS (
  SELECT *,
    TIMESTAMPDIFF(MINUTE,
      LAG(event_ts) OVER (PARTITION BY user_id ORDER BY event_ts),
      event_ts
    ) AS gap_minutes
  FROM user_events
),
sessions AS (
  SELECT *,
    -- Every time gap > 30 OR no prior event (NULL), increment session counter
    SUM(CASE WHEN gap_minutes > 30 OR gap_minutes IS NULL THEN 1 ELSE 0 END)
      OVER (PARTITION BY user_id ORDER BY event_ts) AS session_id
  FROM diffs
)
SELECT user_id, session_id,
  MIN(event_ts) AS session_start,
  MAX(event_ts) AS session_end,
  COUNT(*)      AS event_count
FROM sessions
GROUP BY user_id, session_id
ORDER BY user_id, session_start;</pre>
<p>Why does the SUM trick work? Every time a new session starts, we add 1 to the running sum. The running sum at any point = the total number of sessions started so far = a unique session ID. On average, this pattern appears in every 3rd FAANG product analytics interview.</p>
""") + \'</div>\',
"key_concepts": [
    "Gaps & Islands: group consecutive sequences (dates, IDs, timestamps) into islands (runs without gaps).",
    "Core trick: for consecutive dates, (date - ROW_NUMBER()) produces the SAME constant value per island.",
    "The constant changes at each gap — use it as a GROUP BY key to aggregate each island separately.",
    "Finding gaps: use LEAD to get next island\'s start, compute: gap_start = island_end+1, gap_end = next_start-1.",
    "Session detection: SUM(CASE WHEN new_session_start THEN 1 ELSE 0 END) OVER (ORDER BY ts) = session ID.",
    "The date arithmetic: in MySQL use DATE_ADD(date, INTERVAL -rn DAY). In Postgres use date - rn::integer.",
    "Always deduplicate (DISTINCT) before applying gaps & islands — duplicate dates break the row number math.",
],
"hints": [
    "Always print the intermediate table (with date - rn) to verify consecutive dates share the same group_key.",
    "For integers instead of dates: id - ROW_NUMBER() — same trick, even simpler math.",
    "New session flag: gap IS NULL (first event per user) should ALSO trigger a new session.",
    "Longest streak: after finding all islands, SELECT MAX(streak_days) per user.",
],
"tasks": [
    "<strong>Step 1:</strong> Create the user_logins table with 3 islands (Jan 1-3, Jan 5-6, Jan 10). Print the intermediate table showing date - rn. Verify same-island rows share the same group_key.",
    "<strong>Step 2:</strong> Run the complete Gaps & Islands query. Verify output: 3 islands with streak_days = 3, 2, 1.",
    "<strong>Step 3:</strong> Run the gap-finding query. Verify it finds Jan 4 (1 day) and Jan 7-9 (3 days).",
    "<strong>Step 4 — from scratch:</strong> Write the session detection (timestamp version) for a user_events table with 30-minute threshold. Test with events that have a 45-minute gap.",
],
"hard_problem": "Boss Problem (Duolingo): Table user_sessions(user_id, session_date, minutes_studied). A valid streak day = at least 10 minutes studied. Find: (1) each user\'s current streak length, (2) their all-time longest streak and its exact start/end dates, (3) users whose streak broke within the last 7 days (to trigger a \'restart your streak\' notification). Handle: a user who studied 5 minutes today (breaks streak) but had 30 minutes yesterday.",
},

# ─── DAYS 5-7: REST & REVIEW ──────────────────────────────────────
"rest_review": {
"basics": \'<div class="lesson-levels">\' + L(1,"🟢","Active Rest — How Memory Consolidates","""
<h4>The Neuroscience of Spaced Repetition</h4>
<p>Rest days are not wasted days. During rest, your brain replays what it learned — a process called <strong>memory consolidation</strong>. Research consistently shows that <em>attempting to recall from memory</em> is 3× more effective at building durable knowledge than re-reading notes. The act of struggling to remember — even failing — strengthens the neural pathway more than passive review.</p>
<p>Think of it like muscle recovery: a weightlifter who trains 7 days straight without rest gets weaker, not stronger. The growth happens during recovery. Your brain is the same.</p>
<h4>Today\'s Protocol (4 hours, structured)</h4>
<ol>
  <li><strong>Active Recall (60 min):</strong> Close everything. On a blank page, write every concept, formula, and pattern from this week from memory. Then check.</li>
  <li><strong>Error Review (60 min):</strong> Find the hardest problem you struggled with. Attempt it again completely from scratch — no notes.</li>
  <li><strong>Teach It (45 min):</strong> Open the AI chatbot and explain Gaps & Islands to it as if it\'s a junior engineer. If you stumble, that\'s your gap.</li>
  <li><strong>Next Week Preview (15 min):</strong> Skim next Monday\'s topic at headline level only — priming improves retention when you study it deeply.</li>
</ol>
""") + L(2,"🔵","Active Recall Quiz — No Notes Allowed","""
<h4>Answer These From Memory. Then Check.</h4>
<pre>Window Functions:
□ What is the difference between ROW_NUMBER, RANK, and DENSE_RANK?
  (Write the output for a table with two tied rows)
□ Write the syntax for a 7-day rolling average from memory
□ What does PARTITION BY do differently from GROUP BY?
□ Write the complete Gaps & Islands CTE from memory
□ What is the difference between ROWS BETWEEN and RANGE BETWEEN?
□ LAG(col, 1, 0) vs LAG(col, 1) — what is different?
□ In what SQL execution order step do window functions run?
□ Why can\'t you write WHERE rank &lt;= 3 in the same query as ROW_NUMBER?

Score yourself:
8/8 = 🏆 Mastery level — you\'re ready for interviews on this
5-7/8 = 🟡 Good — review the 1-2 concepts you missed
&lt; 5/8 = 🔴 Go back to the specific day\'s content, re-read Level 1-2</pre>
""") + L(3,"🟡","Spaced Repetition Schedule","""
<h4>When to Review This Week\'s Material</h4>
<table>
<tr><th>Review this content</th><th>When</th><th>How</th></tr>
<tr><td>This week</td><td>Today</td><td>Active recall quiz above</td></tr>
<tr><td>This week</td><td>In 3 days</td><td>Re-solve the hard problem from Day 4</td></tr>
<tr><td>This week</td><td>In 7 days</td><td>LeetCode: solve problems 185, 180, 196</td></tr>
<tr><td>This week</td><td>In 30 days</td><td>Explain all 4 concepts to someone else</td></tr>
</table>
<h4>The Feynman Technique</h4>
<p>After studying any concept, close your notes and explain it as if you\'re teaching a newcomer. Use only simple words. Avoid jargon. If you stumble, that\'s exactly where your understanding breaks down — return to just that part. This technique built Richard Feynman\'s legendary ability to explain complex physics simply.</p>
""") + L(4,"🔴","Interview Readiness Self-Assessment","""
<pre>Rate yourself 1–5 on each topic (honest self-assessment):
  1 = "I need to re-read from scratch"
  3 = "I understand but need to look at notes"
  5 = "I can code this under pressure from memory"

ROW_NUMBER / RANK / DENSE_RANK:        ___/5
Rolling windows (ROWS BETWEEN):        ___/5
LAG/LEAD (adjacent row comparison):    ___/5
Gaps & Islands (date streaks):         ___/5
Session detection (timestamp version): ___/5

Action:
  Score &lt;3: revisit that day\'s Level 1 and Level 2 content tomorrow
  Score 3:  do one LeetCode problem on that specific topic
  Score 5:  you\'re interview-ready ✅ on this topic</pre>
<h4>FAANG Interview Reality Check</h4>
<p>At meta, Amazon, and Google data engineering interviews, you\'ll be asked to write SQL live on a shared screen without autocomplete or documentation. The most common reason candidates fail: they know the concept but freeze on the syntax under pressure. The fix: write every pattern from memory at least 5 times this week. Muscle memory is more reliable than conscious recall under stress.</p>
""") + \'</div>\',
"key_concepts": [
    "Memory consolidation happens during rest — the brain replays and stabilizes learned patterns during downtime.",
    "Active recall (testing yourself) builds 3x stronger memory than re-reading notes.",
    "Spaced repetition: review at day 1, day 3, day 7, day 30 for maximum retention.",
    "The Feynman Technique: if you can\'t explain it simply, you don\'t fully understand it yet.",
    "Error analysis: the problems you got WRONG are your highest-value review items — spend the most time there.",
],
"hints": [
    "Use the AI chatbot to quiz yourself — ask it \'Give me a SQL window function interview question.\'",
    "Write SQL from memory in a plain text editor — no autocomplete. This builds true recall.",
    "The hardest concept this week: spend 30 minutes writing a full explanation in your own words.",
],
"tasks": [
    "<strong>Active Recall:</strong> Write the Gaps & Islands CTE from memory on paper. Check it against Day 4.",
    "<strong>Re-attempt:</strong> Pick the hardest problem from this week and solve it in 20 minutes from scratch.",
    "<strong>Teach it:</strong> Explain RANK vs DENSE_RANK to the AI chatbot as if it\'s a junior. Get it right without notes.",
    "<strong>Preview:</strong> Skim next week\'s Monday topic for 10 minutes — just headline concepts.",
],
"hard_problem": "Connect-the-dots: Write 2-3 paragraphs explaining how ROW_NUMBER, rolling averages, LAG, and Gaps & Islands could ALL be used in a single production pipeline for a ride-sharing company. What problem does each solve? How do they complement each other? What would break if you removed any one of them?",
},

}
'''

with open("kb_week1.py", "w", encoding="utf-8") as f:
    f.write(content)

print("✅ kb_week1.py written successfully")
