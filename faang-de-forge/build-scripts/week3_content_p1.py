def L(n, emoji, title, body):
    return f'<div class="level level-{n}"><div class="level-badge">{emoji} Level {n} — {title}</div><div class="rich">{body}</div></div>'


def H(tag, text): return f'<{tag}>{text}</{tag}>'
def P(text): return f'<p>{text}</p>'
def PRE(text): return f'<pre>{text}</pre>'
def UL(*items): return '<ul>' + ''.join(f'<li>{i}</li>' for i in items) + '</ul>'
def OL(*items): return '<ol>' + ''.join(f'<li>{i}</li>' for i in items) + '</ol>'
def TABLE(rows): return '<table>' + ''.join('<tr>' + ''.join(f'<th>{c}</th>' if i==0 else f'<td>{c}</td>' for i,c in enumerate(r)) + '</tr>' for r in rows) + '</table>'


# ── DAY 1: DIMENSIONAL MODELING ───────────────────────────────────
dim_l1 = (
    H('h4','Why Dimensional Modeling Exists — The History') +
    P('In the 1960s databases were built for transactions: record an order, update inventory, log a payment. '
      'Every table was tightly normalized. Queries were simple lookups. IBM\'s relational model was perfect for this.') +
    P('Then businesses wanted <em>analytics</em>. Not "what is this customer\'s balance?" but '
      '"how did western-region revenue compare to last year, by product category and month?" '
      'These questions required joining 8-12 tables, aggregating millions of rows, slicing across multiple dimensions simultaneously. '
      'Normalized OLTP schemas were terrible at this — joins were slow, SQL was unreadable, answers took hours.') +
    P('<strong>Ralph Kimball\'s insight (1990s):</strong> every business question has the same structure — '
      '"How much [measure] by [dimension] by [dimension]?" '
      'He designed the <strong>Star Schema</strong>: one central fact table of numbers, '
      'surrounded by dimension tables of context. The shape is a star. It mirrors how humans think about data.') +
    PRE(
        '           DIM_PRODUCT             DIM_DATE\n'
        '           (category, brand)       (year, month, quarter)\n'
        '                    \\\\              /\n'
        '       DIM_STORE ── FACT_SALES ── DIM_CUSTOMER\n'
        '       (city,region)  (revenue,   (segment, age)\n'
        '                       units,\n'
        '                       discount)\n'
    ) +
    P('✍️ <strong>Core rule:</strong> Fact tables contain MEASUREMENTS (numbers you aggregate: revenue, clicks, quantity). '
      'Dimension tables contain CONTEXT (who, what, where, when). '
      'Quick test: "Can I SUM this column?" — yes → fact/measure, no → dimension/attribute.')
)

dim_l2 = (
    H('h4','Building a Star Schema — Step by Step') +
    P('The fact table contains one row per business event — one sale, one click, one payment. '
      'It has foreign keys to every dimension (who/what/where/when) and numeric measures.') +
    PRE(
        'CREATE TABLE fact_sales (\n'
        '  sale_id      BIGINT PRIMARY KEY,\n'
        '  date_key     INT REFERENCES dim_date(date_key),       -- WHEN\n'
        '  product_key  INT REFERENCES dim_product(product_key), -- WHAT\n'
        '  store_key    INT REFERENCES dim_store(store_key),      -- WHERE\n'
        '  customer_key INT REFERENCES dim_customer(customer_key),-- WHO\n'
        '  quantity_sold INT,\n'
        '  unit_price    DECIMAL(10,2),\n'
        '  total_revenue DECIMAL(10,2)   -- additive: SUM across all dims\n'
        ');'
    ) +
    H('h4','The Date Dimension — Why It\'s Special') +
    P('The date dimension is pre-populated for 10 years (3,650 rows). '
      'It stores year, quarter, month, week, day, holiday/weekend flags so analysts can '
      '<code>GROUP BY d.quarter</code> without ever calling EXTRACT(). '
      'It is the most important and most universally present dimension in any data warehouse.') +
    PRE(
        'CREATE TABLE dim_date (\n'
        '  date_key    INT PRIMARY KEY,   -- e.g. 20240115\n'
        '  full_date   DATE,\n'
        '  year INT, quarter INT, month INT, month_name VARCHAR(20),\n'
        '  is_holiday BOOLEAN, is_weekend BOOLEAN\n'
        ');'
    ) +
    P('<strong>Surrogate keys:</strong> We use simple integer PKs in dimension tables, not natural business keys. '
      'If an upstream product ID format changes, only the ETL mapping changes — not the entire fact table.')
)

dim_l3 = (
    H('h4','Star vs Snowflake Schema — When to Normalize Dimensions') +
    P('<strong>Star schema:</strong> dimension tables are denormalized — category, subcategory, and brand all live '
      'in one flat product dimension. Some string repetition, but JOIN queries are simple (one join per dimension).') +
    P('<strong>Snowflake schema:</strong> dimension tables are normalized — '
      'dim_product → dim_subcategory → dim_category, each linked by FK. '
      'Less redundancy, but every analytical query needs 3 joins to get from a sale to its category.') +
    TABLE([
        ['Aspect','Star Schema','Snowflake Schema'],
        ['Storage','More (repeated strings)','Less (normalized)'],
        ['Query complexity','1 join per dimension','3–4 joins per dimension chain'],
        ['Query speed','Faster (fewer joins)','Slower on large data sets'],
        ['FAANG preference','✅ Almost universal','❌ Rare — only for very large dims'],
    ]) +
    H('h4','Grain — The Most Critical Design Decision') +
    P('A fact table\'s <strong>grain</strong> is the precise definition of what one row represents. '
      'Getting grain wrong is the most expensive modeling mistake — nearly impossible to fix without rebuilding.') +
    PRE(
        'Grains for sales data:\n'
        '  ✅ "One row per line item in a sales transaction" (finest grain)\n'
        '  ✅ "One row per sales receipt"\n'
        '  ✅ "One row per day per store total"\n'
        '  ❌ "One row per transaction... sometimes per day" — MIXED grain!\n\n'
        'Mixed grain: SUM(revenue) double-counts. Every analyst gets different numbers.\n'
        'Trust in the data warehouse collapses.'
    )
)

dim_l4 = (
    H('h4','The Interview Framework: Designing a Data Warehouse From Scratch') +
    P('FAANG interview: "Design a data warehouse for an e-commerce company." '
      'The interviewer scores: (1) grain identified first, (2) facts vs dimensions correct, '
      '(3) SCD strategy named, (4) query pattern driven design.') +
    PRE(
        'Step 1 — Ask clarifying questions:\n'
        '  "What questions will analysts need to answer?"\n'
        '  "What is the finest level of detail needed? Line item or order?"\n'
        '  "How often does product/customer data change?"\n'
        '  "Expected data volume — rows per day?"\n\n'
        'Step 2 — State the grain explicitly:\n'
        '  "One row per order line item"\n\n'
        'Step 3 — Identify measures:\n'
        '  quantity, unit_price, discount, line_total, margin\n\n'
        'Step 4 — Identify dimensions:\n'
        '  dim_date (when), dim_customer (who), dim_product (what),\n'
        '  dim_store (where), dim_promotion (why discounted)\n\n'
        'Step 5 — Handle attribute changes:\n'
        '  "Products change prices, customers move — SCD Type 2 on both"\n\n'
        'Step 6 — Plan aggregations:\n'
        '  "Daily dashboard sums pre-aggregated in agg_daily_sales\n'
        '   so we don\'t scan the 10B-row fact table on every request"'
    )
)

DIM_CONTENT = '<div class="lesson-levels">' + L(1,'🟢','The History — Why This Exists',dim_l1) + L(2,'🔵','Building a Star Schema',dim_l2) + L(3,'🟡','Star vs Snowflake + Grain',dim_l3) + L(4,'🔴','FAANG Interview Framework',dim_l4) + '</div>'


# ── DAY 2: SLOWLY CHANGING DIMENSIONS ────────────────────────────
scd_l1 = (
    H('h4','The Business Problem That Makes SCDs Hard') +
    P('You\'ve built a star schema. dim_customer has customer_id, name, city, loyalty_tier. '
      'Your boss asks: "Show revenue from gold-tier customers last year — but I want the tier they had '
      '<em>AT THE TIME OF PURCHASE</em>, not what tier they have today."') +
    P('This reveals the fundamental problem: <strong>the real world changes over time</strong>. '
      'Customers move cities. Products change categories. If you simply UPDATE a dimension row, '
      'you permanently lose the history. Yesterday\'s record no longer exists. '
      'Historical questions become unanswerable.') +
    P('This is the <strong>Slowly Changing Dimension (SCD)</strong> problem. Three strategies dominate:') +
    UL(
        '<strong>SCD Type 1:</strong> Overwrite. No history kept. Simple but lossy.',
        '<strong>SCD Type 2:</strong> Add a new row per change. Full history. The gold standard.',
        '<strong>SCD Type 3:</strong> Add a "previous value" column. One level of history.'
    ) +
    P('✍️ <strong>In 95% of FAANG interviews and DW jobs, SCD means Type 2. Know this one deeply.</strong>')
)

scd_l2 = (
    H('h4','SCD Type 1: Overwrite — Simple but History-Destroying') +
    PRE(
        '-- Alice moves from Boston to Dallas:\n'
        'UPDATE dim_customer SET city = \'Dallas\' WHERE customer_id = 42;\n'
        '-- ⚠️  Boston is GONE. All historical orders now falsely show Dallas.\n'
        '-- Use Type 1 ONLY for data corrections (typos) — never for real changes.'
    ) +
    H('h4','SCD Type 2: New Row Per Change — Full History Preserved') +
    PRE(
        'CREATE TABLE dim_customer (\n'
        '  customer_key   INT PRIMARY KEY,  -- surrogate: changes with each version\n'
        '  customer_id    INT,              -- natural key: stays the same always\n'
        '  name           VARCHAR(100),\n'
        '  city           VARCHAR(100),\n'
        '  loyalty_tier   VARCHAR(20),\n'
        '  effective_start DATE NOT NULL,\n'
        '  effective_end   DATE,            -- NULL = currently active\n'
        '  is_current      BOOLEAN DEFAULT TRUE\n'
        ');\n\n'
        '-- Alice starts in Boston, Silver tier:\n'
        'INSERT INTO dim_customer VALUES (1001,42,\'Alice\',\'Boston\',\'Silver\',\'2023-01-01\',NULL,TRUE);\n\n'
        '-- Alice moves to Dallas on March 15, 2024:\n'
        '-- Step 1: Close old row\n'
        'UPDATE dim_customer SET effective_end=\'2024-03-15\', is_current=FALSE\n'
        'WHERE customer_id=42 AND is_current=TRUE;\n\n'
        '-- Step 2: Insert new row (NEW surrogate key!)\n'
        'INSERT INTO dim_customer VALUES (1087,42,\'Alice\',\'Dallas\',\'Silver\',\'2024-03-15\',NULL,TRUE);\n\n'
        '-- Alice now has TWO rows:\n'
        '-- key=1001: Boston, Silver, 2023-01-01 → 2024-03-15 (historical)\n'
        '-- key=1087: Dallas, Silver, 2024-03-15 → NULL (current)\n\n'
        '-- fact_sales rows from 2023 → customer_key=1001 (Boston)\n'
        '-- fact_sales rows from Apr 2024 → customer_key=1087 (Dallas)\n'
        '-- Revenue by city is now historically accurate ✅'
    ) +
    H('h4','SCD Type 3: Previous Value Column — One Level Only') +
    PRE(
        'ALTER TABLE dim_customer ADD COLUMN prev_city VARCHAR(100);\n'
        'UPDATE dim_customer SET prev_city=city, city=\'Dallas\' WHERE customer_id=42;\n'
        '-- city=Dallas, prev_city=Boston\n'
        '-- ⚠️  If Alice moves again to Austin: prev_city=Dallas, Boston is gone.\n'
        '-- Use for: planned reorgs where you need both old+new for 6 months only.'
    )
)

scd_l3 = (
    H('h4','Three Essential SCD Type 2 Query Patterns') +
    P('<strong>Pattern 1: Current state</strong>') +
    PRE(
        'SELECT customer_id, name, city, loyalty_tier\n'
        'FROM dim_customer WHERE is_current = TRUE;'
    ) +
    P('<strong>Pattern 2: Historical accuracy — tier at time of purchase</strong>') +
    PRE(
        '-- Revenue by tier AT time of sale (not current tier)\n'
        'SELECT c.loyalty_tier, SUM(f.total_revenue)\n'
        'FROM fact_sales f\n'
        'JOIN dim_customer c ON f.customer_key = c.customer_key  -- direct FK!\n'
        'JOIN dim_date d ON f.date_key = d.date_key\n'
        'WHERE d.year = 2023\n'
        'GROUP BY c.loyalty_tier;\n'
        '-- Works automatically: fact FK already points to the right version'
    ) +
    P('<strong>Pattern 3: Point-in-time</strong> — what tier was customer 42 on Feb 1, 2024?') +
    PRE(
        'SELECT customer_id, name, city, loyalty_tier\n'
        'FROM dim_customer\n'
        'WHERE customer_id = 42\n'
        '  AND effective_start <= \'2024-02-01\'\n'
        "  AND (effective_end > '2024-02-01' OR effective_end IS NULL);"
    ) +
    H('h4','The SCD ETL Pipeline — How Nightly Loads Work') +
    OL(
        'Extract: pull changed records from OLTP (via CDC — Change Data Capture)',
        'Compare: for each changed record, compare to current dim row. Any tracked attribute changed?',
        'Expire: UPDATE old row — set effective_end = today, is_current = FALSE',
        'Insert: INSERT new row with new surrogate key and new attribute values',
        'No-change: skip records with unchanged tracked attributes entirely'
    )
)

scd_l4 = (
    H('h4','Bi-temporal Modeling — Two Timelines') +
    P('SCD Type 2 tracks ONE timeline: when did the attribute change in our database? '
      'Bi-temporal modeling tracks TWO: '
      '<strong>valid time</strong> (when true in reality) vs '
      '<strong>transaction time</strong> (when our system recorded it). '
      'A customer might move cities Jan 1 but we don\'t record it until Jan 15 — these differ.') +
    PRE(
        'CREATE TABLE dim_customer_bitemporal (\n'
        '  customer_key    INT PRIMARY KEY,\n'
        '  customer_id     INT,\n'
        '  city            VARCHAR(100),\n'
        '  -- Axis 1: when true in the real world\n'
        '  valid_start     DATE,\n'
        '  valid_end       DATE,\n'
        '  -- Axis 2: when our system recorded this\n'
        '  recorded_start  TIMESTAMP,\n'
        '  recorded_end    TIMESTAMP\n'
        ');\n'
        '-- Enables: "What did our SYSTEM BELIEVE on Jan 10 about Jan 1\'s state?"\n'
        '-- Critical for: auditing, compliance, retroactive corrections'
    ) +
    H('h4','Late-Arriving Facts — The Night Shift Problem') +
    P('A mobile app logs an event offline, connects to WiFi 3 days later. '
      'The event arrives Day+3 but the dimension may have changed in those 3 days. '
      'Load the fact by joining to the dimension version active on the ORIGINAL event date.') +
    PRE(
        'INSERT INTO fact_sales (customer_key, ...)\n'
        'SELECT c.customer_key, ...\n'
        'FROM source_events e\n'
        'JOIN dim_customer c\n'
        '  ON c.customer_id = e.customer_id\n'
        "  AND e.event_date BETWEEN c.effective_start AND COALESCE(c.effective_end, '9999-12-31');"
    )
)

SCD_CONTENT = '<div class="lesson-levels">' + L(1,'🟢','The Problem and Three Strategies',scd_l1) + L(2,'🔵','Type 1, Type 2, Type 3 — Full Examples',scd_l2) + L(3,'🟡','Query Patterns and ETL Pipeline',scd_l3) + L(4,'🔴','Bi-temporal + Late-Arriving Facts',scd_l4) + '</div>'


# ── DAY 3: NORMALIZATION ──────────────────────────────────────────
norm_l1 = (
    H('h4','The Anomaly Problem — What Happens Without Normalization') +
    P('Imagine storing everything in one flat table:') +
    PRE(
        'orders_flat:\n'
        'order_id │ customer_id │ customer_email    │ product_id │ product_name │ price\n'
        '─────────┼─────────────┼───────────────────┼────────────┼──────────────┼──────\n'
        '1001     │  42         │ alice@example.com  │  P01       │ iPhone 15    │  999\n'
        '1002     │  42         │ alice@example.com  │  P02       │ AirPods      │  199\n'
        '1003     │  55         │ bob@example.com    │  P01       │ iPhone 15    │  999\n'
        '1004     │  42         │ alice_new@ex.com   │  P03       │ MacBook      │ 1999'
    ) +
    P('This structure has three types of anomalies:') +
    UL(
        '<strong>Update anomaly:</strong> Alice changes email → must UPDATE every row for customer 42. '
        'Miss one row → customer 42 now has two different emails → data is inconsistent.',
        '<strong>Insert anomaly:</strong> Cannot add a new product to the database until someone orders it — '
        'product data lives inside the orders row, not in its own table.',
        '<strong>Delete anomaly:</strong> Cancel order 1003 → lose all information about Bob\'s existence entirely.'
    ) +
    P('<strong>Normalization</strong> eliminates these anomalies by ensuring each fact lives in exactly one place. '
      'Formalized by E.F. Codd (inventor of the relational model) in 1972.') +
    P('The three main normal forms:') +
    UL(
        '<strong>1NF</strong> — Atomic values. No lists or multi-values in one cell.',
        '<strong>2NF</strong> — Every non-key column depends on the ENTIRE primary key.',
        '<strong>3NF</strong> — Non-key columns depend ONLY on the primary key, not on each other.'
    ) +
    P('✍️ <strong>Memory trick:</strong> "The key (1NF), the whole key (2NF), and nothing but the key (3NF)."')
)

norm_l2 = (
    H('h4','1NF: Atomic Values — No Multi-Values in a Cell') +
    PRE(
        '-- ❌ VIOLATES 1NF: multiple phone numbers in one cell\n'
        'customer_id │ name  │ phone_numbers\n'
        '────────────┼───────┼─────────────────────\n'
        '42          │ Alice │ 555-1234, 555-9876   ← TWO values in one cell!\n\n'
        '-- ✅ 1NF: separate table, one value per row\n'
        'customer_phones: (customer_id, phone_number)\n'
        '42, 555-1234\n'
        '42, 555-9876'
    ) +
    H('h4','2NF: No Partial Dependencies (Only for Composite PKs)') +
    P('2NF only matters when the primary key uses multiple columns. '
      'Every non-key column must depend on the FULL composite key, not just part of it.') +
    PRE(
        '-- ❌ VIOLATES 2NF — PK = (order_id, product_id)\n'
        'order_items: order_id│product_id│quantity│product_name│category\n'
        '-- product_name and category depend ONLY on product_id, not the full PK!\n\n'
        '-- ✅ 2NF: split out partial-dependent columns\n'
        'order_items: (order_id, product_id, quantity)   ← full-key only\n'
        'products:    (product_id, product_name, category) ← product-specific'
    ) +
    H('h4','3NF: No Transitive Dependencies') +
    P('3NF: a non-key column must not determine another non-key column. '
      'zip_code → city is a transitive dependency (zip determines city, not customer_id).') +
    PRE(
        '-- ❌ VIOLATES 3NF: zip_code determines city (non-key → non-key)\n'
        'customers: customer_id│name│zip_code│city\n'
        '42, Alice, 10001, New York   ← city determined by zip, not by customer_id!\n'
        '55, Bob,   10001, New York   ← same zip, same city always\n\n'
        '-- ✅ 3NF: separate the zip-to-city mapping\n'
        'zip_codes: (zip_code, city, state)   ← zip determines city here\n'
        'customers: (customer_id, name, zip_code FK)  ← customer holds the zip'
    )
)

norm_l3 = (
    H('h4','Denormalization — When NOT to Normalize') +
    P('A fully normalized (3NF) schema is ideal for OLTP where updates are frequent. '
      'For analytical queries on large data sets, full normalization is a performance disaster — '
      'every business question requires 5–8 JOINs, and JOINs on 100M+ rows are expensive.') +
    P('<strong>Denormalization</strong> is the deliberate re-introduction of redundancy for query speed. '
      'This is intentional engineering, not bad design.') +
    PRE(
        '-- Normalized 3NF: 6 joins to get revenue by category by region\n'
        'SELECT r.region, p.category, SUM(f.revenue)\n'
        'FROM fact_sales f\n'
        'JOIN dim_order o       ON f.order_id = o.order_id\n'
        'JOIN dim_product p     ON o.product_id = p.product_id\n'
        'JOIN dim_category c    ON p.category_id = c.category_id\n'
        'JOIN dim_customer cu   ON o.customer_id = cu.customer_id\n'
        'JOIN dim_region r      ON cu.region_id = r.region_id\n'
        'GROUP BY r.region, p.category;\n\n'
        '-- Star schema (denormalized): 2 joins only\n'
        'SELECT ds.region, dp.category, SUM(f.revenue)\n'
        'FROM fact_sales f\n'
        'JOIN dim_product dp ON f.product_key = dp.product_key\n'
        'JOIN dim_store   ds ON f.store_key   = ds.store_key\n'
        'GROUP BY ds.region, dp.category;'
    ) +
    TABLE([
        ['Scenario','Normalize?','Denormalize?'],
        ['OLTP (transactions, user accounts)','✅ Yes — updates frequent','❌ Causes anomalies'],
        ['Analytics / BI dashboards','❌ Too many joins, too slow','✅ Wide pre-joined tables'],
        ['Data warehouse (star schema)','❌ Snowflake = complex queries','✅ Flat dimension tables'],
    ])
)

norm_l4 = (
    H('h4','BCNF, 4NF, and the Limits of Normalization') +
    P('<strong>BCNF (Boyce-Codd Normal Form)</strong> is a slightly stronger version of 3NF: '
      'every determinant must be a candidate key. '
      'Most 3NF tables are automatically in BCNF — violations only occur with multiple overlapping candidate keys. '
      'In practice: achieve 3NF and BCNF is usually also satisfied.') +
    P('<strong>4NF</strong> handles multi-valued dependencies: when columns are independently multi-valued '
      'but stored together, creating false combinations.') +
    PRE(
        '-- ❌ 4NF violation: Alice has 2 hobbies AND 2 languages\n'
        '-- stored together → 4 rows, but only 2+2 independent facts\n'
        'person │ hobby    │ language\n'
        'Alice  │ painting │ English\n'
        'Alice  │ painting │ French   ← painting accidentally paired with French\n'
        'Alice  │ cooking  │ English\n'
        'Alice  │ cooking  │ French\n\n'
        '-- ✅ 4NF: separate independent multi-valued facts\n'
        'person_hobbies:   (Alice,painting), (Alice,cooking)\n'
        'person_languages: (Alice,English), (Alice,French)'
    ) +
    H('h4','The Practical Decision Framework') +
    P('At FAANG, "is this normalized correctly?" is always followed by "for what purpose?" '
      'The answer changes the entire design:') +
    UL(
        '<strong>OLTP:</strong> aim for 3NF/BCNF — consistency, update integrity paramount',
        '<strong>Analytics/DW:</strong> deliberately denormalize — query speed paramount',
        '<strong>Streaming/NoSQL:</strong> schema may not be relational — access pattern drives design',
        'Know which context you are in before choosing normalization strategy'
    )
)

NORM_CONTENT = '<div class="lesson-levels">' + L(1,'🟢','The Anomaly Problem',norm_l1) + L(2,'🔵','1NF, 2NF, 3NF Step by Step',norm_l2) + L(3,'🟡','Denormalization — When to Break Rules',norm_l3) + L(4,'🔴','BCNF, 4NF, Decision Framework',norm_l4) + '</div>'


WEEK3_PARTIAL = {
    "dimensional_modeling": {
        "basics": DIM_CONTENT,
        "key_concepts": [
            "Star schema = fact table (measures) surrounded by dimension tables (context). Optimized for analytical queries.",
            "Fact table: events (sales, clicks). Contains FKs to dimensions + numeric measures to aggregate.",
            "Additive measures: SUM across all dims (revenue). Semi-additive: only across some. Non-additive: never SUM (ratios).",
            "Surrogate keys: simple integer PKs. Insulate DW from upstream ID format changes.",
            "Grain: precise definition of one fact row. Must be declared, consistent, never mixed.",
            "Star vs Snowflake: star = denormalized = simpler queries. Snowflake = normalized = more joins.",
            "Date dimension: pre-built, one row per day, 10 years. Year/quarter/month/holiday flags for fast GROUP BY.",
            "Design sequence: grain → measures → dimensions → SCD strategy → aggregation plan.",
        ],
        "hints": [
            "'Can I SUM this column?' → fact/measure. 'Is this descriptive context?' → dimension attribute.",
            "Always declare grain explicitly before DDL. Mixed-grain fact tables are the #1 data warehouse bug.",
            "Surrogate keys protect against upstream ID changes. Never use natural source keys as fact table FKs.",
            "Date dimension: analysts GROUP BY d.quarter without EXTRACT() — huge usability win.",
        ],
        "tasks": [
            "<strong>Step 1:</strong> Draw on paper: a star schema for a food delivery app. Define the grain. Name all fact measures and all dimensions.",
            "<strong>Step 2:</strong> Write DDL for fact_orders and dim_restaurant. Include surrogate keys and all measures.",
            "<strong>Step 3:</strong> Write a query joining fact_sales → dim_date → dim_product to get monthly revenue by category.",
            "<strong>Step 4:</strong> Redesign as a snowflake — add dim_subcategory and dim_category as separate tables. How many more JOINs does the same query require?",
        ],
        "hard_problem": "Boss Problem (Amazon): Design a DW for marketplace analytics. Sellers list products, customers place orders with multiple line items, items can be returned. Design fact + dimension tables for: (1) revenue by seller, product category, date, (2) return rate analysis, (3) seller performance ranking. State grain of each fact table. Handle: products changing categories over time, international orders with currency conversion.",
    },
    "slowly_changing_dimensions": {
        "basics": SCD_CONTENT,
        "key_concepts": [
            "SCD = Slowly Changing Dimension. Strategy for handling dimension attribute changes over time.",
            "SCD Type 1: overwrite. Simple, destroys history. Use only for data corrections (typos).",
            "SCD Type 2: new row per change. Full history preserved. The industry standard.",
            "SCD Type 2 columns: surrogate key (changes), natural key (constant), effective_start, effective_end, is_current.",
            "Fact table FK to surrogate key automatically delivers historical accuracy in all joins.",
            "SCD Type 3: previous_value column. One level of history. Use for planned reorgs, not permanent tracking.",
            "Point-in-time query: WHERE natural_key=X AND start<=date AND (end>date OR end IS NULL).",
            "Bi-temporal: valid time (real world) + transaction time (recorded). For auditing and late corrections.",
            "Late-arriving facts: join to dimension version active on the original event date, not current.",
        ],
        "hints": [
            "Interview: 'Which SCD type?' — almost always Type 2. Explain why Type 1 loses history.",
            "Surrogate key changes with each new version row. Natural/business key stays the same across all versions.",
            "Current records: WHERE is_current=TRUE or WHERE effective_end IS NULL. Both work.",
            "MERGE statement (UPSERT) handles the SCD Type 2 ETL expire+insert in a single SQL command.",
        ],
        "tasks": [
            "<strong>Step 1:</strong> Create dim_customer with SCD Type 2 columns. Insert one customer (Boston, Silver tier).",
            "<strong>Step 2:</strong> Simulate a tier upgrade (Silver → Gold). Write the UPDATE + INSERT correctly.",
            "<strong>Step 3:</strong> Write a point-in-time query: 'What tier was customer 42 on March 1, 2024?' — dates span before and after the change.",
            "<strong>Step 4:</strong> A late-arriving fact arrives with event_date=2023-11-15. Write the INSERT that joins to the correct historical dimension version.",
        ],
        "hard_problem": "Boss Problem (Spotify): 50M users, average 4 tier changes over 3 years. (1) Design dim_user with SCD Type 2. (2) A user can change country too — when both tier AND country change on the same day, do you create 1 or 2 new rows? Why? (3) Write a MERGE statement that handles insert/update(expire+insert)/no-change in one SQL command. (4) If 200K users change tier every day, how does this affect fact table FK updates?",
    },
    "normalization": {
        "basics": NORM_CONTENT,
        "key_concepts": [
            "Normalization eliminates insert/update/delete anomalies. Each fact lives in exactly one place.",
            "1NF: atomic values. No lists, no arrays, no comma-separated multiple values in one cell.",
            "2NF: every non-key column depends on the FULL composite PK. Only relevant for composite-PK tables.",
            "3NF: every non-key column depends ONLY on the PK. No column-to-column (transitive) dependencies.",
            "Memory trick: 'the key (1NF), the whole key (2NF), and nothing but the key (3NF)'.",
            "Denormalization: deliberate redundancy for query speed. Appropriate for analytics. Not a mistake.",
            "OLTP → normalize (updates frequent). Analytics → denormalize (queries frequent).",
            "BCNF: stronger than 3NF — every determinant is a candidate key. Usually automatic with 3NF.",
        ],
        "hints": [
            "Updating one value → must change multiple rows → find which normalization form is violated.",
            "2NF violations always involve composite PKs. Single-column PK = automatically 2NF.",
            "Transitive dependency: A→B→C where A is PK. Violates 3NF. Fix: move B→C to its own table.",
            "Denormalization is correct when the trade-off is intentional and documented.",
        ],
        "tasks": [
            "<strong>Step 1:</strong> Given: orders(order_id, customer_id, customer_email, product_id, product_name, quantity, price). Identify which normal form it violates and which specific columns cause violations.",
            "<strong>Step 2:</strong> Normalize to 3NF. Draw the schema with 3 tables, their PKs and FKs.",
            "<strong>Step 3:</strong> Write DDL for all 3 normalized tables with PK and FK constraints.",
            "<strong>Step 4:</strong> Write the query on the normalized schema that gets total revenue by product category for customer 42. How many JOINs vs the flat table version?",
        ],
        "hard_problem": "Boss Problem (Stripe): Flat table: payments(payment_id, merchant_id, merchant_name, merchant_country, buyer_id, buyer_email, buyer_country, payment_method_id, method_type, method_last4, amount, currency, timestamp). (1) Identify every normalization violation — state which NF rule is broken and why. (2) Normalize to 3NF — draw the full schema. (3) A business analyst says 'your normalized schema is too slow — queries take 2 minutes.' How do you respond and what do you build?",
    },
}

print("WEEK3_PARTIAL keys:", list(WEEK3_PARTIAL.keys()))
print("SCD basics length:", len(WEEK3_PARTIAL['slowly_changing_dimensions']['basics']))
