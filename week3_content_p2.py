"""Build Week 3 Part 2: nosql_patterns, schema_design_interview, week3_rest."""

def L(n, emoji, title, body):
    return f'<div class="level level-{n}"><div class="level-badge">{emoji} Level {n} — {title}</div><div class="rich">{body}</div></div>'

def P(text): return f'<p>{text}</p>'
def H(tag, text): return f'<{tag}>{text}</{tag}>'
def PRE(text): return f'<pre>{text}</pre>'
def UL(*items): return '<ul>' + ''.join(f'<li>{i}</li>' for i in items) + '</ul>'
def OL(*items): return '<ol>' + ''.join(f'<li>{i}</li>' for i in items) + '</ol>'
def TABLE(rows): return '<table>' + ''.join('<tr>' + ''.join(f'<th>{c}</th>' if i==0 else f'<td>{c}</td>' for i, c in enumerate(r)) + '</tr>' for r in rows) + '</table>'


# ── DAY 4: NOSQL PATTERNS ─────────────────────────────────────────
nosql_l1 = (
    H('h4', 'Why NoSQL Was Invented — The 2000s Scaling Crisis') +
    P('In the early 2000s, companies like Google, Amazon, and Facebook hit a fundamental wall with relational databases:') +
    UL(
        '<strong>Scale:</strong> PostgreSQL on one server handles maybe 10TB. Google had petabytes.',
        '<strong>Speed:</strong> JOIN operations on billions of rows are slow regardless of optimization.',
        '<strong>Flexibility:</strong> Rigid schemas could not keep up with fast-changing product requirements.'
    ) +
    P('NoSQL was born to solve these. But it comes with trade-offs. '
      'The most important: you lose the ability to freely JOIN tables and get ACID guarantees simultaneously.') +
    H('h4', 'The Fundamental Mental Model Shift') +
    P('<strong>Relational (SQL):</strong> "Design around entities and relationships. Queries figure themselves out. '
      'Normalize first, add indexes later."') +
    P('<strong>NoSQL:</strong> "Design around ACCESS PATTERNS. Know your most common queries first, '
      'then design your data model to serve them in O(1). If you do not know your access patterns, you cannot design a NoSQL model."') +
    P('✍️ <strong>Write this down:</strong> This is the most important conceptual shift in NoSQL. '
      'SQL is query-flexible but schema-rigid. NoSQL is query-specific but schema-flexible.') +
    H('h4', 'The 4 Families of NoSQL Databases') +
    TABLE([
        ['Type', 'Examples', 'Best For'],
        ['Key-Value', 'Redis, DynamoDB', 'Session storage, caching, simple lookups by ID'],
        ['Wide-Column', 'Cassandra, HBase', 'Time-series, event logs, high write throughput'],
        ['Document', 'MongoDB, Firestore', 'JSON objects, variable structure, nested documents'],
        ['Graph', 'Neo4j, Amazon Neptune', 'Social networks, fraud detection, relationship traversal'],
    ]) +
    P('The family choice is determined by your access patterns. '
      'Use the wrong family and even perfect schema design cannot save query performance.')
)

nosql_l2 = (
    H('h4', 'Cassandra: Wide-Column Store — Three Absolute Rules') +
    P('Apache Cassandra is the choice when you need: massive write throughput (millions of writes/second), '
      'linear horizontal scalability, and no-single-point-of-failure availability. '
      'Used by Apple (Siri storage), Netflix (viewing history), Instagram (feed). '
      'But Cassandra has hard rules — violating them destroys performance.') +
    P('The three rules:') +
    OL(
        '<strong>Rule 1: Queries drive tables.</strong> In SQL you design one table and write any query. '
        'In Cassandra, design one table PER query pattern. The table exists to serve exactly one access pattern efficiently.',
        '<strong>Rule 2: No JOINs, no subqueries.</strong> Data must be pre-joined at write time. '
        'If you need user data alongside their posts, denormalize: store user data inside the posts table.',
        '<strong>Rule 3: No unbounded queries.</strong> Every query MUST include the partition key in WHERE. '
        'You cannot do full table scans or range queries without a partition key — Cassandra will reject or time out.'
    ) +
    H('h4', 'Partition Key vs Clustering Key') +
    P('In Cassandra, the PRIMARY KEY has two parts: <code>(partition_key, clustering_key)</code>. '
      'The partition key determines which node stores the data. '
      'The clustering key determines the sort order of rows WITHIN a partition.') +
    PRE(
        '-- Netflix watch history: one partition per user\n'
        '-- All of one user\'s history on the same node for fast retrieval\n'
        'CREATE TABLE watch_history (\n'
        '  user_id    UUID,              -- PARTITION KEY: routes to one node\n'
        '  watched_at TIMESTAMP,         -- CLUSTERING KEY: sorted within partition\n'
        '  show_id    UUID,\n'
        '  show_title TEXT,\n'
        '  duration_mins INT,\n'
        '  PRIMARY KEY (user_id, watched_at)\n'
        ') WITH CLUSTERING ORDER BY (watched_at DESC);\n\n'
        '-- ✅ Fast: give me user 42\'s last 20 shows\n'
        'SELECT * FROM watch_history WHERE user_id=42 LIMIT 20;\n\n'
        '-- ❌ Rejected: no partition key given — would scan entire cluster\n'
        'SELECT * FROM watch_history WHERE show_title=\'Stranger Things\';'
    ) +
    P('The LIMIT 20 is served from a single node in milliseconds — O(1) lookup. '
      'The rejected query would require scanning every partition on every node — Cassandra refuses it.')
)

nosql_l3 = (
    H('h4', 'DynamoDB: Single-Table Design') +
    P('Amazon DynamoDB is a managed key-value and document store. '
      'The "single-table design" pattern — storing multiple entity types in ONE table using a '
      'generic partition key (PK) and sort key (SK) — is the most important and most misunderstood DynamoDB pattern.') +
    P('The motivation: DynamoDB charges for reads/writes per request. '
      'If you need Customer + Orders + OrderItems in one API call, '
      'querying 3 separate tables costs 3 requests. Single-table design allows all related entities '
      'to be co-located under one partition — fetched in a single request.') +
    PRE(
        '-- Single table: "ecommerce_table"\n'
        '-- pk=partition key, sk=sort key — generic names, specific values\n'
        '--\n'
        '-- Row type  │ pk            │ sk              │ attributes\n'
        '-- ──────────┼───────────────┼─────────────────┼──────────────────\n'
        '-- Customer  │ CUST#42       │ METADATA        │ name, email, city\n'
        '-- Order     │ CUST#42       │ ORDER#1001      │ total, status, date\n'
        '-- OrderItem │ CUST#42       │ ORDER#1001#P01  │ qty, price, name\n'
        '-- Product   │ PRODUCT#P01   │ METADATA        │ name, category, price\n'
        '--\n'
        '-- Query: get customer 42 + all their orders in ONE request:\n'
        'GET pk=CUST#42            → customer metadata + all orders + all items\n\n'
        '-- Query: get just orders for customer 42:\n'
        'QUERY pk=CUST#42, sk BEGINS_WITH "ORDER#"'
    ) +
    H('h4', 'The SQL→NoSQL Decision Framework') +
    TABLE([
        ['Requirement', 'Choose'],
        ['Complex ad-hoc reporting with JOINs', 'PostgreSQL / BigQuery (SQL)'],
        ['High write throughput (>100K writes/sec), time-series', 'Cassandra'],
        ['Single-millisecond reads by ID at massive scale', 'DynamoDB / Redis'],
        ['Flexible/variable document structure', 'MongoDB'],
        ['Graph traversal (friends-of-friends, fraud rings)', 'Neo4j / Neptune'],
        ['Caching, session storage (data expires)', 'Redis'],
    ])
)

nosql_l4 = (
    H('h4', 'CAP Theorem — The Fundamental Distributed Systems Constraint') +
    P('CAP theorem (Brewer, 2000): in a distributed system, you can guarantee at most TWO of three properties simultaneously:') +
    UL(
        '<strong>Consistency (C):</strong> Every read receives the most recent write, or an error. No stale data.',
        '<strong>Availability (A):</strong> Every request receives a response (not guaranteed to be latest).',
        '<strong>Partition Tolerance (P):</strong> The system operates even when network messages are lost between nodes.'
    ) +
    P('Network partitions are unavoidable in real distributed systems — you ALWAYS need P. '
      'So the real choice is: sacrifice C (choose AP) or sacrifice A (choose CP).') +
    TABLE([
        ['Database', 'CAP Choice', 'Trade-off'],
        ['Cassandra', 'AP (tunable)', 'May return stale reads. Uses eventual consistency by default.'],
        ['HBase', 'CP', 'May refuse requests during partition. Strongly consistent.'],
        ['DynamoDB', 'AP (default) / CP (opt-in)', 'Eventually consistent by default, strongly consistent reads available.'],
        ['Redis', 'AP (single-node) / CP (cluster)', 'Depends on replication config and cluster mode.'],
        ['PostgreSQL (single)', 'CP', 'No partition tolerance — it is a single node.'],
    ]) +
    H('h4', 'FAANG Interview: Modeling Instagram Feed in Cassandra') +
    P('Interview question: "Design the data model for Instagram user feeds in Cassandra."') +
    PRE(
        '-- Access pattern: "Get my feed — posts from people I follow, newest first"\n'
        '-- Option A: Fan-out on Write\n'
        '--   When Alice posts → immediately write to every follower\'s feed partition\n'
        '--   Pro: feed reads are O(1)\n'
        '--   Con: if Alice has 10M followers, one post = 10M writes\n\n'
        '-- Option B: Fan-out on Read\n'
        '--   When user requests feed → read from all 300 followees\' timelines, merge\n'
        '--   Pro: writes are cheap (one write per post)\n'
        '--   Con: feed reads are O(followees) — slow for users who follow 1,000 accounts\n\n'
        '-- Real Instagram hybrid: fan-out on write for normal users,\n'
        '--   fan-out on read for celebrity accounts (10M+ followers)'
    )
)

NOSQL_CONTENT = '<div class="lesson-levels">' + L(1,'🟢','Why NoSQL Exists — The Mental Model Shift',nosql_l1) + L(2,'🔵','Cassandra: Wide-Column + Three Rules',nosql_l2) + L(3,'🟡','DynamoDB: Single-Table Design',nosql_l3) + L(4,'🔴','CAP Theorem + Instagram Feed Design',nosql_l4) + '</div>'


# ── DAY 5: SCHEMA DESIGN INTERVIEW ───────────────────────────────
schema_l1 = (
    H('h4', 'What Schema Design Interviews Actually Test') +
    P('Schema design interviews are not about knowing the "right answer." '
      'They test: (1) how you ask clarifying questions before designing, '
      '(2) how you identify access patterns before picking a database, '
      '(3) how you handle evolving requirements, '
      '(4) how you discuss trade-offs openly instead of presenting one solution as absolute truth.') +
    P('The most common failure: jumping into CREATE TABLE statements in the first 30 seconds. '
      'Interviewers specifically watch to see whether you ask questions first. '
      'An engineer who designs first and asks questions later is dangerous in production.') +
    H('h4', 'The Framework: 5 Questions Before Any Design') +
    OL(
        '<strong>"What are the most frequent read queries?"</strong> — Access patterns drive everything.',
        '<strong>"What are the most frequent write patterns?"</strong> — High write → Cassandra. Mostly reads → PostgreSQL/DynamoDB.',
        '<strong>"What is the expected data volume?"</strong> — 10K rows/day → any DB. 10M rows/day → need partitioning strategy.',
        '<strong>"How fresh must the data be?"</strong> — Real-time → strong consistency. Dashboard → eventual OK.',
        '<strong>"What is the read-to-write ratio?"</strong> — 1000:1 → optimize reads. 1:1 → optimize both.'
    ) +
    P('✍️ After asking these 5 questions, you have enough information to make an informed schema decision. '
      'Before asking them, you are guessing.')
)

schema_l2 = (
    H('h4', 'Designing Twitter\'s Schema — A Worked Example') +
    P('<strong>Requirements:</strong> Users post tweets. Users follow other users. Users see a timeline of tweets from accounts they follow. '
      'System has 500M users, 500M tweets/day, average user follows 300 accounts.') +
    H('h4', 'Step 1: Access Patterns') +
    PRE(
        'Read patterns (must be fast):\n'
        '  R1: Get a user\'s home timeline (latest tweets from followees), newest first\n'
        '  R2: Get a user\'s own tweets (profile page)\n'
        '  R3: Get a single tweet by ID\n'
        '  R4: Get a user\'s follower/following counts\n\n'
        'Write patterns:\n'
        '  W1: Post a new tweet\n'
        '  W2: Follow / unfollow a user\n'
        '  W3: Like / retweet a tweet\n\n'
        'Volume: 500M tweets/day = ~5,800 tweets/second. 100B timeline reads/day.'
    ) +
    H('h4', 'Step 2: Data Entities and SQL Schema') +
    PRE(
        '-- Core entities\n'
        'CREATE TABLE users (\n'
        '  user_id BIGINT PRIMARY KEY,\n'
        '  username VARCHAR(50) UNIQUE,\n'
        '  display_name VARCHAR(100),\n'
        '  bio TEXT,\n'
        '  follower_count INT,    -- denormalized counter (avoid COUNT(*) on every read)\n'
        '  following_count INT\n'
        ');\n\n'
        'CREATE TABLE tweets (\n'
        '  tweet_id BIGINT PRIMARY KEY,  -- Snowflake ID: encodes timestamp+machine+seq\n'
        '  user_id  BIGINT REFERENCES users(user_id),\n'
        '  content  VARCHAR(280),\n'
        '  created_at TIMESTAMP,\n'
        '  like_count INT,         -- denormalized: avoid COUNT per query\n'
        '  retweet_count INT\n'
        ');\n\n'
        'CREATE TABLE follows (\n'
        '  follower_id BIGINT REFERENCES users(user_id),\n'
        '  followee_id BIGINT REFERENCES users(user_id),\n'
        '  followed_at TIMESTAMP,\n'
        '  PRIMARY KEY (follower_id, followee_id)\n'
        ');\n'
        'CREATE INDEX ON follows(followee_id);  -- reverse: who follows this user?'
    ) +
    H('h4', 'Step 3: The Timeline Problem') +
    P('Naive timeline query: <code>SELECT t.* FROM tweets t JOIN follows f ON t.user_id = f.followee_id WHERE f.follower_id=42 ORDER BY created_at DESC LIMIT 20</code>. '
      'This joins 500M tweets × 300 followees = runs the follower check on millions of rows. Too slow.') +
    P('<strong>Solution: Precomputed timeline fan-out.</strong> When Alice posts a tweet, immediately write it to every follower\'s timeline cache (Redis sorted set by timestamp). '
      'Timeline reads become O(1). Trade-off: writes are amplified (300 follower writes per tweet from an average user).')
)

schema_l3 = (
    H('h4', 'Handling Edge Cases — The Interview Differentiator') +
    P('Strong schema design candidates address edge cases before the interviewer asks. '
      'Here are the 5 most common schema edge cases and how to handle each:') +
    TABLE([
        ['Edge Case', 'Problem', 'Solution'],
        ['Soft deletes', 'DELETE removes audit trail', 'Add is_deleted BOOLEAN + deleted_at TIMESTAMP. Filter WHERE NOT is_deleted.'],
        ['Large blobs (images/video)', 'Storing files in DB is slow and expensive', 'Store in object storage (S3). DB stores only the URL/path.'],
        ['Counters (likes, followers)', 'COUNT(*) on every request is expensive', 'Denormalize: maintain a counter column. Increment on write.'],
        ['User-generated content moderation', 'Need to hide content without deleting', 'Add status enum: ACTIVE / HIDDEN / REMOVED. Filter on status.'],
        ['Time zones', 'ambiguous timestamps in analytics', 'Always store timestamps in UTC. Convert to user local time in the application layer.'],
    ]) +
    H('h4', 'Indexing as Part of Schema Design') +
    P('An incomplete schema interview answer presents only the CREATE TABLE DDL. '
      'A complete answer also states: which columns need indexes and why. '
      'For every frequent query\'s WHERE and ORDER BY clause, explicitly name the index.') +
    PRE(
        '-- Twitter schema indexes:\n'
        'CREATE INDEX tweets_user_created ON tweets(user_id, created_at DESC);\n'
        '-- Supports: WHERE user_id=X ORDER BY created_at DESC LIMIT 20 (profile page)\n\n'
        'CREATE INDEX follows_followee ON follows(followee_id);\n'
        '-- Supports: WHERE followee_id=X (find all followers of a user)\n\n'
        'CREATE INDEX tweets_created ON tweets(created_at DESC);\n'
        '-- Supports: global trending (recent tweets across all users)'
    )
)

schema_l4 = (
    H('h4', 'Uber/Lyft Schema: The Ride + Driver Matching Problem') +
    P('A more complex FAANG schema problem: design the data model for Uber trips.') +
    PRE(
        '-- Entities: users (riders), drivers, vehicles, trips, payments\n\n'
        'CREATE TABLE drivers (\n'
        '  driver_id   BIGINT PRIMARY KEY,\n'
        '  user_id     BIGINT UNIQUE REFERENCES users(user_id),\n'
        '  license_no  VARCHAR(50),\n'
        '  rating      DECIMAL(3,2),\n'
        '  status      ENUM(\'ACTIVE\',\'INACTIVE\',\'SUSPENDED\')\n'
        ');\n\n'
        'CREATE TABLE trips (\n'
        '  trip_id         BIGINT PRIMARY KEY,\n'
        '  rider_id        BIGINT REFERENCES users(user_id),\n'
        '  driver_id       BIGINT REFERENCES drivers(driver_id),\n'
        '  vehicle_id      BIGINT REFERENCES vehicles(vehicle_id),\n'
        '  status          ENUM(\'REQUESTED\',\'ACCEPTED\',\'IN_PROGRESS\',\'COMPLETED\',\'CANCELLED\'),\n'
        '  requested_at    TIMESTAMP,\n'
        '  pickup_lat      DECIMAL(9,6),\n'
        '  pickup_lng      DECIMAL(9,6),\n'
        '  dropoff_lat     DECIMAL(9,6),\n'
        '  dropoff_lng     DECIMAL(9,6),\n'
        '  fare_amount     DECIMAL(10,2),\n'
        '  distance_miles  DECIMAL(8,2),\n'
        '  duration_mins   INT\n'
        ');\n\n'
        '-- For matching: drivers need to be queried by location\n'
        '-- Use geospatial index (PostGIS) on current lat/lng\n'
        'CREATE INDEX idx_driver_location ON driver_locations\n'
        'USING GIST (location);  -- enables radius queries: WHERE ST_Distance(location, point) < 2km'
    ) +
    P('<strong>Key design decisions to state in an interview:</strong>') +
    UL(
        'Driver real-time location goes in a SEPARATE table (high write frequency, different retention)',
        'Geospatial queries require GIST index (not B-Tree)',
        'Trip status uses ENUM — adding a new state requires ALTER TABLE (discuss migration strategy)',
        'Fare calculation stored as result (denormalized) — never recompute from distance/time on every read',
        'Soft deletes on trips (audit trail, disputes) — never hard DELETE trip records'
    )
)

SCHEMA_CONTENT = '<div class="lesson-levels">' + L(1,'🟢','What Schema Design Interviews Test',schema_l1) + L(2,'🔵','Twitter Schema — Full Worked Example',schema_l2) + L(3,'🟡','Edge Cases — The Interview Differentiator',schema_l3) + L(4,'🔴','Uber Schema + Geospatial Design',schema_l4) + '</div>'


# ── DAY 6-7: REST ─────────────────────────────────────────────────
rest_l1 = (
    H('h4', 'Week 3 Was Dense — Here\'s How to Consolidate It') +
    P('This week covered: dimensional modeling (star schemas, grain, surrogate keys), '
      'slowly changing dimensions (Types 1/2/3, bi-temporal, late-arriving facts), '
      'normalization (1NF/2NF/3NF, denormalization trade-offs), '
      'NoSQL modeling (Cassandra rules, DynamoDB single-table, CAP theorem), '
      'and schema design interviews (5-question framework, edge cases).') +
    P('That is 5 major bodies of knowledge in 5 days. '
      'Today\'s goal: surface the knowledge you\'ve acquired so it becomes retrievable under pressure — not just familiar when re-read.') +
    H('h4', 'The Most Commonly Confused Concepts This Week') +
    UL(
        '<strong>Star vs Snowflake:</strong> star = flat dims = simpler queries. Most people say "snowflake is better because it\'s more normalized" — wrong for analytics.',
        '<strong>SCD Type 1 vs 2:</strong> Type 1 loses history. Type 2 preserves history. You almost always want Type 2.',
        '<strong>2NF vs 3NF:</strong> 2NF is about partial dependencies on composite keys. 3NF is about column-to-column (transitive) dependencies.',
        '<strong>Cassandra partition key vs clustering key:</strong> partition key routes to a node, clustering key sorts within that partition.',
        '<strong>CAP theorem choices:</strong> Cassandra = AP (eventually consistent). HBase = CP (strongly consistent). Not interchangeable.'
    )
)

rest_l2 = (
    H('h4', 'Active Recall — No Notes Allowed') +
    PRE(
        'Dimensional Modeling:\n'
        '□ What is a fact table? What is a dimension table? Name 3 examples of each.\n'
        '□ What is grain? Give an example of a mixed-grain table and why it breaks analytics.\n'
        '□ Why are surrogate keys used instead of natural keys?\n'
        '□ What columns does a date dimension always have?\n\n'
        'SCDs:\n'
        '□ Draw SCD Type 2 — what columns are required? What happens when an attribute changes?\n'
        '□ Write the UPDATE + INSERT pattern from memory for closing/opening a Type 2 row.\n'
        '□ What is the point-in-time query pattern? Write the WHERE clause.\n\n'
        'Normalization:\n'
        '□ Explain 2NF in one sentence without jargon.\n'
        '□ Give an example of a 3NF violation and how to fix it.\n'
        '□ When is denormalization correct? When is it wrong?\n\n'
        'NoSQL:\n'
        '□ What are Cassandra\'s 3 rules? Why can\'t you query without a partition key?\n'
        '□ Explain DynamoDB single-table design in 2 sentences.\n'
        '□ CAP theorem: what does Cassandra sacrifice? What does HBase sacrifice?\n\n'
        'Score: 14+/16 = interview ready | <10 = revisit weakest day'
    )
)

rest_l3 = (
    H('h4', 'Spaced Repetition Schedule') +
    TABLE([
        ['Topic','Review in 3 days','Review in 7 days','Review in 30 days'],
        ['Dimensional Modeling','Redesign a star schema from scratch','Add SCD handling to your design','Design a complete DW: Amazon or Netflix'],
        ['SCDs','Write the SCD Type 2 ETL MERGE','Point-in-time query on real data','Explain bi-temporal to a colleague'],
        ['Normalization','Normalize a 10-column flat table','Identify violations in real schemas','Explain 3NF violation to a non-engineer'],
        ['NoSQL','Design a Cassandra table for an access pattern','When Cassandra vs DynamoDB','CAP theorem applied to 3 real systems'],
        ['Schema Design','Mock interview: design Twitter schema','Add indexes to your design','Review a real production schema at work'],
    ]) +
    P('✍️ <strong>The most effective review:</strong> schedule a 45-minute mock interview with yourself or the chatbot. '
      'Pick one of this week\'s Boss Problems and work through it completely from scratch, out loud, under time pressure.')
)

rest_l4 = (
    H('h4', '45-Minute Mock Interview — Data Modeling Exam') +
    PRE(
        'Timer: 45 minutes. No notes. Speak out loud as you design.\n\n'
        'Problem: Design the data model for Airbnb.\n\n'
        'Requirements:\n'
        '  - Hosts list properties (each has multiple rooms/beds, photos, amenities, price rules)\n'
        '  - Guests search for properties (by location, dates, price, amenities)\n'
        '  - Guests book properties (one booking per property per date range)\n'
        '  - Both hosts and guests can leave reviews\n'
        '  - Analytics team needs: revenue by city and month, occupancy rates, top-rated hosts\n\n'
        'You will be scored on:\n'
        '  □ Did you ask clarifying questions before designing?\n'
        '  □ Did you identify the grain of each table before writing DDL?\n'
        '  □ Did you choose SQL vs NoSQL and justify it?\n'
        '  □ Did you handle: property price changes over time (SCD!), soft deletes, review integrity\n'
        '  □ Did you design for the analytics queries (star schema for DW layer)?\n'
        '  □ Did you state which indexes are needed and why?\n'
        '  □ Did you mention at least one edge case unprompted?'
    ) +
    H('h4', 'Self-Evaluation Rubric') +
    PRE(
        '5/7 checklist items = Strong Pass ✅\n'
        '3-4/7 = Pass with coaching\n'
        '<3/7 = Revisit weakest area before interviewing\n\n'
        'Most common gaps:\n'
        '  - Forgetting to state the grain before writing DDL\n'
        '  - Not mentioning indexes (always mention them)\n'
        '  - Not asking clarifying questions at the start\n'
        '  - Picking SQL without considering access pattern volume'
    )
)

REST_CONTENT = '<div class="lesson-levels">' + L(1,'🟢','Consolidation — What to Focus On',rest_l1) + L(2,'🔵','Active Recall Quiz',rest_l2) + L(3,'🟡','Spaced Repetition Schedule',rest_l3) + L(4,'🔴','45-Minute Mock Interview',rest_l4) + '</div>'


WEEK3_PARTIAL2 = {
    "nosql_patterns": {
        "basics": NOSQL_CONTENT,
        "key_concepts": [
            "NoSQL was built to address SQL's scale (storage), speed (join cost), and flexibility (schema rigidity) limits.",
            "Fundamental shift: SQL = design around entities, queries are flexible. NoSQL = design around access patterns first.",
            "Key-Value (Redis/DynamoDB): O(1) by ID. Wide-Column (Cassandra): time-series, high write throughput.",
            "Document (MongoDB): variable/nested structures. Graph (Neo4j): relationship traversal.",
            "Cassandra Rule 1: one table per query. Rule 2: no JOINs — pre-join at write time. Rule 3: always provide partition key.",
            "Partition key = which node stores the data. Clustering key = sort order within that partition.",
            "DynamoDB single-table: all entity types in one table with generic PK/SK. Co-located for single-request fetches.",
            "CAP theorem: choose 2 of Consistency/Availability/Partition-tolerance. Partitions are unavoidable → choose C or A.",
            "Cassandra = AP (eventual). HBase = CP (strong). DynamoDB = AP by default, CP opt-in.",
        ],
        "hints": [
            "Interview: 'When would you use Cassandra?' → high write throughput, time-series, queries always by partition key.",
            "Cassandra: missing partition key in WHERE = full cluster scan = query rejected. Always include partition key.",
            "DynamoDB single-table: use BEGINS_WITH on SK to query subsets (all orders for a customer).",
            "CAP: Cassandra AP = may return stale reads. HBase CP = may refuse under partition. Trade-off, not bug.",
        ],
        "tasks": [
            "<strong>Step 1:</strong> Design a Cassandra table for: 'Get all messages in a chat room, newest first, limit 50.' State partition key, clustering key, and why.",
            "<strong>Step 2:</strong> Design a DynamoDB single-table for an e-commerce app with customers, orders, and order items. Show 3 rows of sample data.",
            "<strong>Step 3:</strong> Given the fan-out Instagram feed problem: write the data model for fan-out-on-write. What happens when a celebrity with 10M followers posts?",
            "<strong>Step 4:</strong> For each of 3 systems (Twitter, Netflix, Uber), state which NoSQL family you'd use and why.",
        ],
        "hard_problem": "Boss Problem (Facebook Messenger): Design the data model for a chat app. Access patterns: (1) get the last 50 messages in a conversation, newest first; (2) get all conversations for a user, sorted by most recent message; (3) get unread message count per conversation. 10B messages/day. Design: SQL, Cassandra, or DynamoDB? Why? What is the partition key for each table? Handle: group chats (1 conversation, many users), message deletion, read receipts.",
    },

    "schema_design_interview": {
        "basics": SCHEMA_CONTENT,
        "key_concepts": [
            "Schema design interviews test process (ask first, design second) more than encyclopedic knowledge.",
            "5 questions before any design: access patterns, write patterns, volume, freshness requirement, read/write ratio.",
            "Twitter timeline problem: naive JOIN on followees is O(followees) — precomputed feed fan-out is O(1).",
            "Denormalized counters (like_count, follower_count): maintain on write to avoid COUNT(*) on every read.",
            "Always include index design in your schema answer — incomplete without it.",
            "Snowflake IDs (tweet_id): encode timestamp + machine ID + sequence. Sortable by time, no central coordinator.",
            "Geospatial queries require GIST index (not B-Tree). Always mention this for location-based schemas.",
            "Soft deletes: is_deleted + deleted_at. Never hard DELETE records that may be needed for disputes/audits.",
        ],
        "hints": [
            "Never jump to CREATE TABLE before asking clarifying questions — it is a red flag in schema interviews.",
            "Counter columns (follower_count): faster than COUNT(*) per request. Trade-off: counts can drift if not careful.",
            "Status as ENUM vs VARCHAR: ENUM is validated at DB level (safer). VARCHAR is more flexible for new states.",
            "Always state your indexes — 'I would add an index on user_id + created_at DESC for the profile page query.'",
        ],
        "tasks": [
            "<strong>Step 1:</strong> Design the schema for a URL shortener (bit.ly). What are the access patterns? What is the primary table? What index makes redirect O(1)?",
            "<strong>Step 2:</strong> Design the schema for a parking app (SpotHero). Users book parking spots by location and time. Handle: spots have complex pricing rules, bookings can be cancelled.",
            "<strong>Step 3:</strong> Take your Twitter schema from Level 2. Add: (1) soft deletes on tweets, (2) a hashtags table with many-to-many to tweets, (3) a media_attachments table for images.",
            "<strong>Step 4:</strong> Mock: design YouTube's schema in 20 minutes. Ask yourself the 5 questions first. Then design. Then check: did you state all indexes? Did you mention edge cases?",
        ],
        "hard_problem": "Boss Problem (Airbnb): Design Airbnb's complete data model: properties (photos, amenities, room types), hosts, guests, bookings (no double-booking), reviews (bidirectional: host reviews guest AND guest reviews property), pricing (variable by date, seasonality). The analytics team needs a star schema for: revenue by city/month, occupancy rate by property type, host performance. Design: (1) operational schema (OLTP), (2) DW schema (star schema), (3) which data flows from OLTP to DW via ETL.",
    },

    "week3_rest": {
        "basics": REST_CONTENT,
        "key_concepts": [
            "Week 3 topics: dimensional modeling, SCDs, normalization, NoSQL, schema design interviews.",
            "Most confused: star vs snowflake, SCD Type 1 vs 2, 2NF vs 3NF, Cassandra partition vs clustering key.",
            "Active recall is 3x more effective than re-reading — test yourself before reviewing notes.",
        ],
        "hints": [
            "Mock interview with chatbot: 'Design Airbnb's schema. Ask me clarifying questions then build it step by step.'",
            "Write CREATE TABLE DDL on paper without autocomplete — builds syntax recall for actual interviews.",
            "Any recall gap: go directly back to that specific day's Level 1 content and re-read the mental model section.",
        ],
        "tasks": [
            "<strong>Active Recall:</strong> From memory, draw a star schema for a ride-sharing app. Name all facts, all dimensions, and state the grain.",
            "<strong>SCD Practice:</strong> Write the SCD Type 2 UPDATE + INSERT pattern from memory. Include all 6 required columns.",
            "<strong>Normalization:</strong> Given a 10-column flat table, identify violations and normalize to 3NF. Time yourself: 15 minutes.",
            "<strong>Mock Interview:</strong> 45-minute Airbnb schema design. Record yourself speaking through the design.",
        ],
        "hard_problem": "Connect-the-dots: A senior data engineer says: 'We have a 5TB PostgreSQL OLTP database (fully normalized, 3NF). Analysts are complaining that their revenue-by-region-by-month queries take 40 minutes. The database is also getting slower for application writes because of too many indexes.' Walk through the complete architectural solution: (1) what data warehouse design would you build? (2) what ETL would populate it? (3) how would you handle slowly changing dimensions in the pipeline? (4) which NoSQL component (if any) would you add and for what purpose?",
    },
}

print("WEEK3_PARTIAL2 keys:", list(WEEK3_PARTIAL2.keys()))
print("NoSQL basics len:", len(WEEK3_PARTIAL2['nosql_patterns']['basics']))
print("Schema basics len:", len(WEEK3_PARTIAL2['schema_design_interview']['basics']))
