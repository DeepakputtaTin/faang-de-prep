"""Build kb_week3.py Part 1 — dimensional_modeling, slowly_changing_dimensions, normalization."""

p1 = '''def L(n, emoji, title, body):
    return f\'\'\'<div class="level level-{n}">
<div class="level-badge">{emoji} Level {n} — {title}</div>
<div class="rich">{body}</div>
</div>\'\'\'

WEEK3 = {

# ─── DAY 1: DIMENSIONAL MODELING ─────────────────────────────────
"dimensional_modeling": {
"basics": \'<div class="lesson-levels">\' + L(1,"🟢","Why Dimensional Modeling Exists — The History","""
<h4>The Problem with Transactional Databases for Analytics</h4>
<p>In the 1960s and 70s, databases were designed for one purpose: recording business transactions. When a customer places an order, record it. When inventory changes, update it. When money moves, log it. Every table was tightly normalized to avoid data duplication, updates were frequent, and queries were simple lookups. IBM\'s relational model — rows, columns, foreign keys — was perfect for this.</p>
<p>Then in the 1980s, businesses wanted something different: <em>analytics</em>. Not "what is this customer\'s current balance?" but "how did our revenue in the western region compare to last year, broken down by product category and month?" These questions were fundamentally different — they required joining many tables, aggregating millions of rows, and slicing data across multiple dimensions simultaneously. </p>
<p>The problem: normalized OLTP schemas were terrible at this. Answering a complex business question required joining 8-12 tables, made the SQL nearly unreadable, and took hours on large datasets. Business users needed something they could understand and analysts could query quickly.</p>
<h4>Ralph Kimball\'s Insight: Design for How Humans Think</h4>
<p>In the 1990s, Ralph Kimball studied how businesses naturally think about data. He noticed that every business question has the same structure: <em>"How much [measure] by [dimension] for [dimension]?"</em> Examples:</p>
<ul>
  <li>"How much <strong>revenue</strong> (measure) by <strong>product category</strong> (dimension) by <strong>quarter</strong> (dimension)?"</li>
  <li>"How many <strong>units sold</strong> (measure) by <strong>store location</strong> (dimension) by <strong>customer segment</strong> (dimension)?"</li>
</ul>
<p>This led him to the <strong>Star Schema</strong>: one central <em>fact table</em> containing the numbers, surrounded by <em>dimension tables</em> containing the context. The shape looks like a star — fact in the center, dimensions radiating outward. It mirrors exactly how humans think about business data.</p>
<pre>           DIM_PRODUCT             DIM_DATE
           (category, brand)       (year, month, quarter)
                    \\              /
       DIM_STORE ── FACT_SALES ── DIM_CUSTOMER
       (city,region)  (revenue,   (segment, age)
                       units_sold,
                       discount)
                    /
           DIM_PROMOTION
           (type, discount_pct)</pre>
<p>✍️ <strong>The core principle:</strong> Fact tables contain MEASUREMENTS (numbers you aggregate: revenue, quantity, clicks, duration). Dimension tables contain CONTEXT (who, what, where, when, why the measurement happened). If you\'re unsure which is which, ask: "Can I SUM this column?" — if yes, it\'s likely a fact/measure. If no, it\'s likely a dimension/attribute.</p>
""") + L(2,"🔵","Building a Star Schema — Step by Step","""
<h4>Designing the Fact Table</h4>
<p>The fact table is the heart of the star schema. Each row represents one <em>business event</em> — one sale, one click, one payment, one delivery. Think of it as the transaction log, but stripped of all descriptive detail (that goes in dimensions). The fact table has:</p>
<ul>
  <li><strong>Foreign keys</strong> to every dimension table (who, what, where, when)</li>
  <li><strong>Additive measures</strong> — numbers you can SUM, AVG, COUNT across any dimension</li>
  <li>Optionally: <strong>semi-additive</strong> measures (e.g., inventory balance: can SUM across products but NOT across time) or <strong>non-additive</strong> (e.g., ratio, percentage — never SUM these)</li>
</ul>
<pre>-- Fact table: one row per sales transaction
CREATE TABLE fact_sales (
  sale_id      BIGINT PRIMARY KEY,
  date_key     INT REFERENCES dim_date(date_key),    -- WHEN
  product_key  INT REFERENCES dim_product(product_key), -- WHAT
  store_key    INT REFERENCES dim_store(store_key),   -- WHERE
  customer_key INT REFERENCES dim_customer(customer_key), -- WHO
  -- Measures (the numbers analysts aggregate)
  quantity_sold     INT,
  unit_price        DECIMAL(10,2),
  discount_amount   DECIMAL(10,2),
  total_revenue     DECIMAL(10,2),   -- additive: SUM across all dimensions
  gross_margin      DECIMAL(10,2)    -- additive
);</pre>
<h4>Designing the Dimension Tables</h4>
<pre>-- Date dimension: the most important dimension in any DW
-- Pre-populated for 10 years: 3,650 rows
CREATE TABLE dim_date (
  date_key    INT PRIMARY KEY,   -- surrogate key: 20240115
  full_date   DATE,
  year        INT,
  quarter     INT,              -- enables GROUP BY quarter without EXTRACT()
  month       INT,
  month_name  VARCHAR(20),      -- \'January\' — human-readable
  week_number INT,
  day_of_week VARCHAR(20),
  is_holiday  BOOLEAN,          -- enables filtering by holiday/non-holiday
  is_weekend  BOOLEAN
);

-- Product dimension: descriptive attributes about products
CREATE TABLE dim_product (
  product_key   INT PRIMARY KEY,   -- surrogate key
  product_id    VARCHAR(20),       -- natural/business key
  product_name  VARCHAR(200),
  category      VARCHAR(100),
  subcategory   VARCHAR(100),
  brand         VARCHAR(100),
  unit_cost     DECIMAL(10,2),
  is_active     BOOLEAN           -- current status
);</pre>
<p>Notice: we use <strong>surrogate keys</strong> (simple integers) in dimension tables, not natural business keys. This protects the data warehouse from changes in source systems — if the upstream product ID format changes, only the ETL mapping changes, not the entire fact table.</p>
""") + L(3,"🟡","Snowflake Schema vs Star Schema — When to Normalize Dimensions","""
<h4>The Star vs Snowflake Trade-Off</h4>
<p><strong>Star schema:</strong> dimension tables are denormalized. The product dimension has category, subcategory, and brand all in one flat table — even though category-subcategory has a parent-child relationship. This means some data repetition (the string "Electronics" appears in thousands of rows), but JOIN queries are simpler (just one join to get any product attribute).</p>
<p><strong>Snowflake schema:</strong> dimension tables ARE normalized. Product splits into dim_product → dim_subcategory → dim_category, each linked by foreign keys. Less storage redundancy, but every analytical query now needs to JOIN 3 tables to get from a sale to its category — more complexity, often slower on large analytical queries.</p>
<pre>Star Schema:                        Snowflake Schema:
dim_product                         dim_product → dim_subcategory → dim_category
┌──────────────────────────┐         ┌────────────┐   ┌────────────┐   ┌────────┐
│ product_key              │         │ product_key│──>│ subcat_key │──>│cat_key │
│ product_name             │         │ product_name│  │ subcat_name│   │cat_name│
│ category    (repeated!)  │         │ subcat_key │   │ cat_key    │   └────────┘
│ subcategory (repeated!)  │         └────────────┘   └────────────┘
│ brand       (repeated!)  │
└──────────────────────────┘

Star: 1 join to get category      Snowflake: 3 joins to get category
Star: more storage                Snowflake: less storage
Star: better query performance    Snowflake: harder to query</pre>
<p><strong>FAANG preference:</strong> Almost universally, star schemas for analytical workloads. Storage is cheap. Query performance and simplicity are precious. The Kimball Method is explicitly pro-star and anti-snowflake for most use cases. The exception: very large dimension tables where the redundancy becomes genuinely problematic (e.g., a customer dimension with 500MB of repeated country-name strings).</p>
<h4>Grain — The Most Critical Design Decision</h4>
<p>A fact table\'s <strong>grain</strong> is the precise definition of what one row represents. Getting the grain wrong is the most expensive data modeling mistake — it\'s nearly impossible to fix without rebuilding the entire fact table.</p>
<pre>Examples of different grains for sales data:
  ✅ "One row per individual item in a sales transaction" (finest grain)
  ✅ "One row per sales transaction (receipt)"
  ✅ "One row per daily total sales per store"
  ❌ "One row per transaction... sometimes per day" (MIXED grain = disaster)

Why mixed grain destroys analytics:
  SUM(revenue) on a mixed grain table double-counts or under-counts.
  Every analyst gets different numbers. Trust in the data warehouse collapses.</pre>
""") + L(4,"🔴","FAANG Interview: Designing a Data Warehouse From Scratch","""
<h4>The Classic Interview Question: "Design the Data Model for X"</h4>
<p>At FAANG, you\'ll be asked: "Design a data warehouse for an e-commerce company\'s analytics needs." The interviewer wants to see: (1) that you identify the grain first, (2) that you know the difference between facts and dimensions, (3) that you can handle slowly changing dimensions, (4) that you think about query patterns first.</p>
<pre>Step 1 — Ask clarifying questions:
  "What questions will analysts need to answer?"
  "What is the finest level of detail we need? Per transaction? Per day?"
  "How often does product/customer data change?"
  "What\'s the expected data volume (rows/day)?"

Step 2 — Identify the grain:
  "One row per line item in an order" → grain is order_item level

Step 3 — Identify measures (facts):
  → quantity, unit_price, discount, line_total, margin, shipping_cost

Step 4 — Identify dimensions:
  → dim_date (when), dim_customer (who), dim_product (what),
     dim_store/channel (where), dim_promotion (why discounted)

Step 5 — Handle slowly changing dimensions:
  "Product prices change, customers move cities — how do we track history?"
  → SCD Type 2 (new row for each change — see tomorrow\'s topic)

Step 6 — Plan aggregations:
  "For daily dashboards summing all orders, we pre-aggregate into
   agg_daily_sales to avoid scanning the 10B-row fact table every time"</pre>
<p>The interviewer scores you on: clarity of thought, structured approach, awareness of trade-offs, and handling of real-world messiness (NULLs, late-arriving facts, dimension changes).</p>
""") + \'</div>\',
"key_concepts": [
    "Star schema = fact table (measures) surrounded by dimension tables (context). Optimized for analytical queries.",
    "Fact table: events (sales, clicks, deliveries). Contains foreign keys to dimensions + numeric measures.",
    "Additive measures: SUM across all dimensions (revenue). Semi-additive: SUM across some (inventory). Non-additive: never SUM (ratios).",
    "Surrogate keys: simple integer PKs in dimensions. Insulate data warehouse from upstream system ID changes.",
    "Grain: the precise definition of one fact row. Must be declared, consistent, and never mixed.",
    "Star vs Snowflake: star = denormalized dimensions = simpler queries. Snowflake = normalized = less storage but more joins.",
    "Date dimension: pre-built, one row per day for 10 years. Contains year/month/quarter/holiday flags for fast GROUP BY.",
    "Design sequence: grain → measures → dimensions → SCD strategy → aggregation plan.",
],
"hints": [
    "\'Can I SUM this column?\' → fact/measure. \'Is this descriptive context?\' → dimension attribute.",
    "Always declare grain explicitly before writing DDL. Mixed-grain fact tables are the #1 data warehouse modeling bug.",
    "Surrogate keys protect against upstream ID changes. Never use natural keys from source systems as FK in fact tables.",
    "Date dimension enables GROUP BY quarter without EXTRACT() — analysts can just GROUP BY d.quarter directly.",
],
"tasks": [
    "<strong>Step 1:</strong> Draw a star schema on paper for a food delivery app (DoorDash). What are the facts? What are the dimensions? What is the grain?",
    "<strong>Step 2:</strong> Write the DDL for fact_orders and dim_restaurant. Include all measures and surrogate keys.",
    "<strong>Step 3:</strong> Write a query joining fact_sales to dim_date and dim_product to get monthly revenue by category. Use the star schema tables from Level 2.",
    "<strong>Step 4:</strong> Redesign the same schema as a snowflake. Add dim_subcategory and dim_category as separate tables. Write the same query — how many more JOINs does it require?",
],
"hard_problem": "Boss Problem (Amazon): Design a data warehouse for Amazon\'s marketplace analytics. Sellers list products, customers place orders containing multiple items, each item can be returned. Design the fact and dimension tables for: (1) revenue analysis by seller, product category, and date, (2) return rate analysis, (3) seller performance ranking. State the grain of each fact table. Handle: products that change categories over time, sellers who deactivate then reactivate, international orders with currency conversion.",
},

# ─── DAY 2: SLOWLY CHANGING DIMENSIONS ───────────────────────────
"slowly_changing_dimensions": {
"basics": \'<div class="lesson-levels">\' + L(1,"🟢","The Fundamental Problem — Dimension Data Changes","""
<h4>The Business Problem That Makes This a Hard Problem</h4>
<p>You\'ve built a beautiful star schema. Your dim_customer table has customer_id, name, city, and loyalty_tier. Life is good. Then your boss asks: "Show me the revenue we earned from gold-tier customers last year — but I want to see what tier they were in AT THE TIME OF PURCHASE, not what tier they are now."</p>
<p>This question reveals the fundamental problem of dimensional modeling: <strong>the real world changes over time</strong>. Customers move cities. Products change categories. Prices change. Salespeople change regions. If you just UPDATE the dimension table when something changes, you permanently lose the history. Yesterday\'s record of what tier a customer was in no longer exists. You can\'t answer historical questions accurately.</p>
<p>This is the <strong>Slowly Changing Dimension (SCD)</strong> problem — dimensions that "slowly" change over time and require careful handling to preserve historical accuracy in your analytics.</p>
<h4>Three Strategies, Three Trade-Offs</h4>
<p>Ralph Kimball defined six SCD types. In practice, three dominate:</p>
<ul>
  <li><strong>SCD Type 1:</strong> Just overwrite. No history kept. Simple but lossy.</li>
  <li><strong>SCD Type 2:</strong> Add a new row for each change. Full history preserved. The gold standard.</li>
  <li><strong>SCD Type 3:</strong> Add a "previous value" column. Only 1 level of history. Useful for migrations.</li>
</ul>
<p>✍️ <strong>Write this down:</strong> In 95% of FAANG interviews and real data warehouse jobs, when someone says "SCD," they mean <strong>SCD Type 2</strong>. Know this one deeply. Know the others exist.</p>
""") + L(2,"🔵","SCD Type 1 vs Type 2 vs Type 3 — With Real Examples","""
<h4>SCD Type 1: Overwrite (Simple, No History)</h4>
<p>When a customer changes their city, simply UPDATE the row. The old city is gone forever. Use this ONLY when history genuinely doesn\'t matter — for example, correcting a data entry typo. If someone\'s name was misspelled "Jon" and it should be "John," Type 1 is correct — the misspelling never mattered.</p>
<pre>-- Type 1: just update. History is lost.
UPDATE dim_customer
SET city = \'Dallas\'
WHERE customer_id = 42;
-- ⚠️ Boston (the old city) is permanently gone. Revenue analysis will
-- incorrectly show all of customer 42\'s historical orders as Dallas orders.</pre>

<h4>SCD Type 2: New Row (Full History — The Standard)</h4>
<p>When an attribute changes, close the current row (set effective_end_date and is_current=FALSE) and insert a new row with the new value and a new surrogate key. The fact table\'s FK points to the dimension row that was current AT THE TIME OF THE EVENT — so historical queries are always accurate.</p>
<pre>-- dim_customer with Type 2 columns
CREATE TABLE dim_customer (
  customer_key   INT PRIMARY KEY,   -- surrogate key (changes with each version!)
  customer_id    INT,               -- natural/business key (stays the same)
  customer_name  VARCHAR(100),
  city           VARCHAR(100),
  loyalty_tier   VARCHAR(20),
  effective_start DATE NOT NULL,    -- when this version became active
  effective_end   DATE,             -- NULL means "currently active"
  is_current      BOOLEAN DEFAULT TRUE
);

-- Customer 42 starts in Boston as Silver tier:
INSERT INTO dim_customer VALUES (1001, 42, \'Alice\', \'Boston\', \'Silver\', \'2023-01-01\', NULL, TRUE);

-- Alice moves to Dallas on March 15, 2024:
-- Step 1: Close the old row
UPDATE dim_customer
SET effective_end=\'2024-03-15\', is_current=FALSE
WHERE customer_id=42 AND is_current=TRUE;

-- Step 2: Insert the new row (NEW surrogate key!)
INSERT INTO dim_customer VALUES (1087, 42, \'Alice\', \'Dallas\', \'Silver\', \'2024-03-15\', NULL, TRUE);

-- Now Alice appears TWICE in dim_customer:
-- customer_key=1001: Boston, Silver, 2023-01-01 to 2024-03-15 (historical)
-- customer_key=1087: Dallas, Silver, 2024-03-15 to NULL (current)</pre>

<p>Now fact_sales rows from 2023 point to customer_key=1001 (Boston). Rows from April 2024 point to customer_key=1087 (Dallas). "Revenue by city" gives historically accurate results — exactly what your boss asked for!</p>

<h4>SCD Type 3: Previous Value Column (One Step of History)</h4>
<pre>-- Add a \'previous_city\' column — only tracks the immediate last value
ALTER TABLE dim_customer ADD COLUMN prev_city VARCHAR(100);

-- When Alice moves to Dallas:
UPDATE dim_customer
SET prev_city = city, city = \'Dallas\'  -- save old value, update to new
WHERE customer_id = 42;

-- Result: city=\'Dallas\', prev_city=\'Boston\'
-- ⚠️ If Alice later moves to Austin: city=\'Austin\', prev_city=\'Dallas\'
-- Boston history is GONE. Only one level of history survives.</pre>
<p>Type 3\'s use case: a company reorganizes its sales territories. For 6 months, reports need to show BOTH "new territory" and "old territory" side by side. After 6 months, the old territory column is meaningless. Type 3 handles this gracefully — it was never designed for permanent historical tracking.</p>
""") + L(3,"🟡","SCD Type 2 Query Patterns — Getting History Right","""
<h4>The Three Most Common SCD Type 2 Query Patterns</h4>
<p><strong>Pattern 1: Get the current dimension attributes (most common).</strong></p>
<pre>-- Current state of all customers
SELECT customer_id, name, city, loyalty_tier
FROM dim_customer
WHERE is_current = TRUE;   -- or: WHERE effective_end IS NULL</pre>

<p><strong>Pattern 2: Historical query — what was the customer\'s tier AT THE TIME of each sale?</strong></p>
<pre>-- Revenue by loyalty tier AT TIME OF PURCHASE (historically accurate)
SELECT
  c.loyalty_tier,           -- tier customer had WHEN they bought, not now
  SUM(f.total_revenue) AS revenue
FROM fact_sales f
JOIN dim_customer c ON f.customer_key = c.customer_key  -- DIRECT FK join
JOIN dim_date d ON f.date_key = d.date_key
WHERE d.year = 2023
GROUP BY c.loyalty_tier;
-- ✅ Works because fact_sales.customer_key already points to the
-- dimension row that was current at purchase time</pre>

<p><strong>Pattern 3: Point-in-time query — what was Alice\'s tier on a specific date?</strong></p>
<pre>-- What tier was customer 42 on February 1, 2024?
SELECT customer_id, name, city, loyalty_tier
FROM dim_customer
WHERE customer_id = 42
  AND effective_start &lt;= \'2024-02-01\'
  AND (effective_end &gt; \'2024-02-01\' OR effective_end IS NULL);
-- This returns the row that was active on that specific date</pre>

<h4>The SCD ETL Pipeline</h4>
<p>In practice, loading SCD Type 2 dimensions is done nightly through an ETL (Extract-Transform-Load) process:</p>
<ol>
  <li>Extract: pull changed customer records from the OLTP database (CDC — Change Data Capture)</li>
  <li>Compare: for each changed record, compare to the current dim row. Did any tracked attribute change?</li>
  <li>Expire: UPDATE old row: set effective_end = today, is_current = FALSE</li>
  <li>Insert: INSERT new row with new surrogate key, new attribute values, effective_start = today</li>
  <li>No-change: records with unchanged attributes are skipped entirely</li>
</ol>
<p>MERGE statement (also called UPSERT) handles steps 3+4+5 in one SQL command in most modern databases.</p>
""") + L(4,"🔴","FAANG Patterns: Bi-temporal Modeling and Late-Arriving Facts","""
<h4>When One Timeline Isn\'t Enough: Bi-temporal Modeling</h4>
<p>SCD Type 2 tracks ONE timeline: when did the attribute change in our database? But businesses sometimes need TWO timelines: when did the change happen in reality (valid time) vs when did we record it in our system (transaction time). These are different — a customer might move cities on January 1 but we don\'t update our records until January 15.</p>
<pre>CREATE TABLE dim_customer_bitemporal (
  customer_key    INT PRIMARY KEY,
  customer_id     INT,
  city            VARCHAR(100),
  -- Axis 1: Valid time — when this was TRUE in the real world
  valid_start     DATE,
  valid_end       DATE,
  -- Axis 2: Transaction time — when our system recorded this fact
  recorded_start  TIMESTAMP,
  recorded_end    TIMESTAMP
);
-- This lets you query: "What did our SYSTEM BELIEVE on Jan 10
-- about what was TRUE on Jan 1?" — crucial for auditing, compliance,
-- and fixing retroactive corrections without corrupting history.</pre>
<h4>Late-Arriving Facts — The Night Shift Problem</h4>
<p>In a data pipeline, events sometimes arrive late — a mobile app logs an event offline, the phone connects to wifi 3 days later, the event arrives in the pipeline on Day+3. The dimension may have changed in those 3 days. To load the fact correctly, you must JOIN to the dimension version active ON THE ORIGINAL EVENT DATE, not today\'s current version.</p>
<pre>-- Loading a late-arriving fact correctly
INSERT INTO fact_sales (customer_key, ...)
SELECT
  c.customer_key,   -- get the version that was active on the event date!
  ...
FROM source_events e
JOIN dim_customer c
  ON c.customer_id = e.customer_id
  AND e.event_date BETWEEN c.effective_start AND COALESCE(c.effective_end, \'9999-12-31\');</pre>
""") + \'</div>\',
"key_concepts": [
    "SCD = Slowly Changing Dimension. How to handle dimension attribute changes over time.",
    "SCD Type 1: overwrite. Simple, no history. Use only for data corrections (typos, irrelevant changes).",
    "SCD Type 2: add a new row per change. Full history preserved. The industry standard for analytical accuracy.",
    "SCD Type 2 columns: surrogate key (changes), natural key (stays), effective_start, effective_end, is_current.",
    "Fact table FK points to the surrogate key active at event time — enables automatic historical accuracy in joins.",
    "SCD Type 3: previous_value column. Only one level of history. Use for planned reorganizations, not permanent tracking.",
    "Point-in-time query: WHERE natural_key=X AND start <= date AND (end > date OR end IS NULL).",
    "Bi-temporal: two timelines (valid time + transaction time). For auditing, compliance, late corrections.",
    "Late-arriving facts: join to dimension version active on original event date, not today\'s current version.",
],
"hints": [
    "Interview question: \'Which SCD type would you use?\' — almost always Type 2. Explain why Type 1 loses history.",
    "SCD Type 2 surrogate key changes with each new row. The natural/business key stays the same across all versions.",
    "Current dimension records: WHERE is_current=TRUE or WHERE effective_end IS NULL. Both work; IS NULL is simpler.",
    "MERGE statement (UPSERT) handles SCD Type 2 ETL in one SQL command — learn merge syntax for your target DB.",
],
"tasks": [
    "<strong>Step 1:</strong> Create dim_customer with SCD Type 2 columns. Insert one customer (Boston, Silver tier).",
    "<strong>Step 2:</strong> Simulate a tier upgrade (Silver → Gold). Write the UPDATE + INSERT to close the old row and create the new version.",
    "<strong>Step 3:</strong> Write a point-in-time query: \'What tier was customer 42 on March 1, 2024?\' — dates span before and after the change.",
    "<strong>Step 4:</strong> A late-arriving fact comes in with event_date=2023-11-15. Write the INSERT that joins to the dimension version active on that specific date.",
],
"hard_problem": "Boss Problem (Spotify): User subscription tiers change frequently: Free → Premium → Family → Free → Premium. You have 50M users, each with an average of 4 tier changes over 3 years. (1) Design the SCD Type 2 dim_user table. (2) A user can also change their country — that\'s a second tracked attribute. How does your design handle when BOTH city AND tier change on the same day — do you create 1 or 2 new rows? (3) Write the ETL MERGE statement that handles inserts, updates (expire old + insert new), and no-changes in a single SQL command.",
},

# ─── DAY 3: NORMALIZATION ─────────────────────────────────────────
"normalization": {
"basics": \'<div class="lesson-levels">\' + L(1,"🟢","What Normalization Solves — The Anomaly Problem","""
<h4>The Problem: What Happens Without Normalization</h4>
<p>Imagine storing all order information in one flat table:</p>
<pre>orders_flat:
order_id │ customer_id │ customer_email     │ product_id │ product_name │ category    │ price
──────────┼─────────────┼────────────────────┼────────────┼──────────────┼─────────────┼──────
1001     │  42         │ alice@example.com   │  P01       │ iPhone 15    │ Electronics │ 999
1002     │  42         │ alice@example.com   │  P02       │ AirPods      │ Electronics │ 199
1003     │  55         │ bob@example.com     │  P01       │ iPhone 15    │ Electronics │ 999
1004     │  42         │ alice_new@ex.com    │  P03       │ MacBook      │ Computers   │ 1999</pre>
<p>This structure has three types of "anomalies" — problems that occur when you insert, update, or delete data:</p>
<ul>
  <li><strong>Update anomaly:</strong> If alice changes her email, you must UPDATE every row where customer_id=42. Miss one row, and customer 42 now has two different emails in the database — your data is inconsistent.</li>
  <li><strong>Insert anomaly:</strong> You can\'t add a new product to the database until someone actually orders it — because the product data lives inside the orders table, not in its own table.</li>
  <li><strong>Delete anomaly:</strong> If order 1003 is cancelled and deleted, you lose all information about Bob\'s existence in the database entirely.</li>
</ul>
<p><strong>Normalization</strong> is the process of structuring tables to eliminate these anomalies by ensuring each piece of information exists in exactly one place. It was formalized by E.F. Codd (the inventor of the relational model) in 1972.</p>
<h4>The Three Normal Forms — What Each One Fixes</h4>
<ul>
  <li><strong>1NF</strong> — Eliminate repeating groups. Each cell must have atomic (single) values.</li>
  <li><strong>2NF</strong> — Eliminate partial dependencies. Every non-key column must depend on the ENTIRE primary key.</li>
  <li><strong>3NF</strong> — Eliminate transitive dependencies. Non-key columns must depend ONLY on the primary key, not on other non-key columns.</li>
</ul>
<p>✍️ <strong>Memory trick:</strong> "The key (1NF), the whole key (2NF), and nothing but the key (3NF)." Each form builds on the previous one.</p>
""") + L(2,"🔵","1NF, 2NF, 3NF — Step by Step Transformation","""
<h4>First Normal Form (1NF): Atomic Values, No Repeating Groups</h4>
<p>A table is in 1NF if every cell contains a single, indivisible value — no lists, no arrays, no comma-separated values. The table from Level 1 violates 1NF if a cell contains multiple values.</p>
<pre>-- ❌ VIOLATES 1NF: multiple phone numbers in one cell
customer_id │ name  │ phone_numbers
────────────┼───────┼─────────────────────
42          │ Alice │ 555-1234, 555-9876   ← TWO values in one cell!

-- ✅ 1NF compliant: separate table for phone numbers
customer_phones:
customer_id │ phone_number
────────────┼─────────────
42          │ 555-1234
42          │ 555-9876</pre>

<h4>Second Normal Form (2NF): No Partial Dependencies</h4>
<p>2NF only applies when the primary key is composite (multiple columns). Every non-key column must depend on the ENTIRE key, not just part of it. Example: an order_items table with PK = (order_id, product_id).</p>
<pre>-- ❌ VIOLATES 2NF (composite PK = order_id + product_id)
order_items:
order_id │ product_id │ quantity │ product_name │ product_category
─────────┼────────────┼──────────┼──────────────┼─────────────────
1001     │ P01        │    2     │ iPhone 15    │ Electronics
-- product_name and product_category depend ONLY on product_id,
-- not on the full (order_id, product_id) key!
-- This means iPhone 15\'s name is repeated in every order row.

-- ✅ 2NF compliant: move partial-dependent columns to their own table
order_items:     (order_id, product_id, quantity)   ← only full-key columns
products:        (product_id, product_name, category) ← product-specific data</pre>

<h4>Third Normal Form (3NF): No Transitive Dependencies</h4>
<p>Even after removing partial dependencies, a table can still have transitive dependencies — where a non-key column determines another non-key column. 3NF removes these.</p>
<pre>-- ❌ VIOLATES 3NF: zip_code → city (non-key determines non-key)
customers:
customer_id │ name  │ zip_code │ city
────────────┼───────┼──────────┼──────
42          │ Alice │  10001   │ New York    ← city is determined by zip, not by customer_id!
55          │ Bob   │  10001   │ New York    ← same zip = same city (always)
99          │ Carol │  90210   │ Beverly Hills

-- Update anomaly: renaming a zip\'s city requires updating every customer row
-- ✅ 3NF compliant: separate the zip-to-city mapping
zip_codes:   (zip_code, city, state)  ← zip determines city
customers:   (customer_id, name, zip_code)  ← customer has a zip FK</pre>
""") + L(3,"🟡","When NOT to Normalize — Denormalization for Performance","""
<h4>Normalization Has a Cost: More JOINs</h4>
<p>A fully normalized database (3NF) is ideal for OLTP (transaction processing) — updates happen in one place, integrity is guaranteed. But for <strong>analytical queries</strong> on large datasets, full normalization can be a performance disaster. Every analytical question now requires joining 5-8 tables, and joins on 100M+ row tables are expensive.</p>
<p><strong>Denormalization</strong> is the deliberate decision to re-introduce redundancy in exchange for query performance. This is NOT bad design — it is intentional engineering for a specific use case.</p>
<pre>-- Normalized (3NF): 6 joins to get revenue by product category by region
SELECT r.region, p.category, SUM(f.revenue)
FROM fact_sales f
JOIN dim_order o       ON f.order_id = o.order_id
JOIN dim_product p     ON o.product_id = p.product_id
JOIN dim_category c    ON p.category_id = c.category_id
JOIN dim_customer cu   ON o.customer_id = cu.customer_id
JOIN dim_region r      ON cu.region_id = r.region_id
GROUP BY r.region, p.category;

-- Denormalized (star schema): 2 joins only
SELECT dp.category, ds.region, SUM(f.revenue)
FROM fact_sales f
JOIN dim_product dp ON f.product_key = dp.product_key
JOIN dim_store ds   ON f.store_key = ds.store_key
GROUP BY dp.category, ds.region;</pre>
<h4>When to Normalize vs Denormalize</h4>
<table>
<tr><th>Scenario</th><th>Normalize (3NF)?</th><th>Denormalize?</th></tr>
<tr><td>OLTP (transactions, user accounts)</td><td>✅ Yes — updates happen frequently</td><td>❌ Causes update anomalies</td></tr>
<tr><td>Analytics / BI dashboards</td><td>❌ Too many joins, too slow</td><td>✅ Pre-join into wide tables</td></tr>
<tr><td>Data warehouse dimensions</td><td>❌ Snowflake = complex queries</td><td>✅ Star schema — flat dims</td></tr>
<tr><td>Real-time streaming data</td><td>❌ Schema rigidity slows ingestion</td><td>✅ Denormalize for write speed</td></tr>
</table>
""") + L(4,"🔴","FAANG Interview: BCNF, 4NF, and the Limits of Normalization","""
<h4>Beyond 3NF: Boyce-Codd Normal Form and 4NF</h4>
<p><strong>BCNF (Boyce-Codd Normal Form)</strong> is a slightly stronger version of 3NF. A table is in BCNF if every determinant is a candidate key. Most tables in 3NF are also in BCNF — violations only occur in specific cases with multiple overlapping candidate keys. In practice, if you\'ve achieved 3NF, BCNF is usually satisfied automatically.</p>
<p><strong>4NF</strong> deals with multi-valued dependencies — when one column can independently determine multiple values of two other columns. Example: a person can have multiple hobbies AND multiple languages. If stored in one table (person, hobby, language), every hobby is paired with every language unnecessarily. 4NF would split this into (person, hobby) and (person, language) tables.</p>
<pre>-- ❌ 4NF violation: multi-valued dependencies
person_skills:
person │ hobby    │ language
───────┼──────────┼─────────
Alice  │ painting │ English    ← 2 hobbies × 2 languages = 4 rows but only 2+2 facts
Alice  │ painting │ French
Alice  │ cooking  │ English
Alice  │ cooking  │ French

-- ✅ 4NF: separate tables with independent facts
person_hobbies:   (Alice, painting), (Alice, cooking)
person_languages: (Alice, English),  (Alice, French)</pre>
<h4>The Practical Normalization Decision Framework</h4>
<p>At FAANG, the question "is this normalized correctly?" is almost always followed by "for what purpose?" The answer changes the entire design. OLTP: aim for 3NF/BCNF — consistency is paramount. Analytics/DW: deliberately denormalize — query speed is paramount. Streaming/NoSQL: schema may not be relational at all — access pattern drives design. Know which context you\'re in before choosing your normalization strategy.</p>
""") + \'</div>\',
"key_concepts": [
    "Normalization eliminates insert/update/delete anomalies by ensuring each fact lives in exactly one place.",
    "1NF: atomic values in each cell. No lists, no arrays, no comma-separated multi-values.",
    "2NF: every non-key column depends on the FULL composite primary key. Applies only to composite-PK tables.",
    "3NF: every non-key column depends ONLY on the primary key. No column-to-column dependencies (transitive deps).",
    "Memory trick: \'the key (1NF), the whole key (2NF), and nothing but the key (3NF)\'.",
    "Denormalization: deliberate redundancy for query speed. Appropriate for analytics/DW — not a design mistake.",
    "OLTP → normalize (updates are frequent). Analytics → denormalize (queries are frequent, updates are rare).",
    "BCNF: stronger than 3NF — every determinant is a candidate key. Usually satisfied automatically by 3NF.",
],
"hints": [
    "Interview test: if updating one value requires changing multiple rows → normalization violation, find which form.",
    "2NF violations always involve composite primary keys. If PK is a single column, the table is automatically 2NF.",
    "Transitive dependency: A→B→C where A is PK, B and C are non-keys. Violates 3NF. Fix: move B→C to its own table.",
    "Is it wrong to denormalize? No — if the trade-off is intentional and documented. Wrong when done accidentally.",
],
"tasks": [
    "<strong>Step 1:</strong> Take this table: orders(order_id, customer_id, customer_email, product_id, product_name, quantity, price). Identify which normal form it violates and specifically which column(s) cause the violation.",
    "<strong>Step 2:</strong> Normalize the table to 3NF. Draw the resulting schema with 3 tables and their PKs/FKs.",
    "<strong>Step 3:</strong> Write the DDL for all 3 normalized tables. Include correct primary keys and foreign key constraints.",
    "<strong>Step 4:</strong> Write the query on the normalized schema that gets total revenue by product category for customer 42. How many JOINs does it need vs the denormalized version?",
],
"hard_problem": "Boss Problem (Stripe): You have a single flat table: payments(payment_id, merchant_id, merchant_name, merchant_country, buyer_id, buyer_email, buyer_country, payment_method_id, method_type, method_last4, amount, currency, timestamp). (1) Identify every normalization violation (state which NF rule is violated and why). (2) Normalize to 3NF — draw the full schema. (3) A business analyst says \'your normalized schema is too slow for our dashboard — queries take 2 minutes.\' How do you respond and what do you build?",
},

}
\'\'\'

with open("kb_week3_part1.py", "w", encoding="utf-8") as f:
    f.write(p1)
print("Part 1 written.")
