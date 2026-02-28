"""
Week 6-7 Content: row_vs_columnar (Storage), spark_logical_plan (Spark)
"""

def L(n, emoji, title, body):
    return f'<div class="level level-{n}"><div class="level-badge">{emoji} Level {n} — {title}</div><div class="rich">{body}</div></div>'

def P(t): return f'<p>{t}</p>'
def H(tag, t): return f'<{tag}>{t}</{tag}>'
def PRE(t): return f'<pre>{t}</pre>'
def UL(*items): return '<ul>' + ''.join(f'<li>{i}</li>' for i in items) + '</ul>'
def OL(*items): return '<ol>' + ''.join(f'<li>{i}</li>' for i in items) + '</ol>'
def TABLE(rows): return '<table>' + ''.join('<tr>' + ''.join(f'<th>{c}</th>' if i == 0 else f'<td>{c}</td>' for i, c in enumerate(r)) + '</tr>' for r in rows) + '</table>'


# ═══════════════════════════════════════════════════════════════════
# TOPIC: row_vs_columnar  (Week 6 — Storage Formats)
# ═══════════════════════════════════════════════════════════════════
col_l1 = (
    H('h4', 'The Fundamental Trade-Off in Storage Layout') +
    P('When you store data on disk, you have a fundamental choice: '
      'store all columns of one row together (row-oriented) '
      'or store all values of one column together (column-oriented). '
      'This decision affects compression ratios, query speed, write speed, '
      'and how much data you scan for any given query.') +
    H('h4', 'Row-Oriented Storage — How It Works') +
    P('In a row-oriented format (CSV, MySQL, PostgreSQL by default), '
      'all columns of Row 1 are stored together on disk, then all columns of Row 2, etc.') +
    PRE(
        'Disk layout for a 3-row, 4-column table:\n\n'
        'Row 1: [user_id=1][name=Alice][age=30][country=US]\n'
        'Row 2: [user_id=2][name=Bob][age=25][country=UK]\n'
        'Row 3: [user_id=3][name=Carol][age=28][country=US]\n\n'
        'Query: SELECT country, SUM(age) GROUP BY country\n'
        'What disk must read: ALL of [user_id, name, age, country] for every row\n'
        'Even though user_id and name are not needed at all!\n\n'
        'For 100 columns, analytical queries typically need 3-5.\n'
        'Row storage reads 100 columns to use 5 = 95% wasted I/O.'
    ) +
    H('h4', 'Column-Oriented Storage — How It Works') +
    P('In a column-oriented format (Parquet, ORC), '
      'all values of column 1 are stored together, then all of column 2, etc.') +
    PRE(
        'Disk layout (same data, columnar):\n\n'
        'Column user_id: [1][2][3]\n'
        'Column name:    [Alice][Bob][Carol]\n'
        'Column age:     [30][25][28]\n'
        'Column country: [US][UK][US]\n\n'
        'Query: SELECT country, SUM(age) GROUP BY country\n'
        'What disk must read: ONLY [age] and [country] column blocks\n'
        'user_id and name are not read at all — they live in different disk blocks!\n\n'
        'For a 100-column table querying 5 columns: reads 5% of the data.'
    ) +
    P('✍️ <strong>Rule:</strong> Row storage is optimal for OLTP (write one complete row, read one complete row). '
      'Column storage is optimal for OLAP (read few columns across all rows, aggregate).')
)

col_l2 = (
    H('h4', 'Why Columnar Format Compresses So Well') +
    P('Compression works by finding patterns and encoding them more efficiently. '
      'Column storage makes compression dramatically more effective because '
      '<strong>values in the same column have the same type and similar values</strong>.') +
    UL(
        '<strong>country column:</strong> ["US","UK","US","US","CA","US","UK"] — only a few unique values repeat. '
        'Dictionary encoding: US=1, UK=2, CA=3 → stores [1,2,1,1,3,1,2] as integers. 90%+ compression.',
        '<strong>age column:</strong> [30,25,28,31,22,25,28] — small integers, all similar range. '
        'Delta encoding: store [30, -5, +3, +3, -9, +3, +3]. Small deltas compress extremely well.',
        '<strong>timestamp column:</strong> [1704067200, 1704067800, 1704068400] — '
        'always increasing, constant difference. RLE encodes as: start=1704067200, step=600, count=3.'
    ) +
    TABLE([
        ['Format', 'Compression', 'Read speed', 'Write speed', 'Best for'],
        ['CSV', 'None (text)', 'Slow (parse text)', 'Fast', 'Data exchange, debugging'],
        ['JSON', 'None', 'Very slow (parse tree)', 'Medium', 'APIs, nested data'],
        ['Avro', 'Medium', 'Medium (row-oriented)', 'Very fast', 'Kafka messages, write-heavy'],
        ['Parquet', 'High (columnar)', 'Very fast for queries', 'Slower', 'Analytics, data warehouses'],
        ['ORC', 'High (columnar)', 'Very fast (Hive/Spark)', 'Slower', 'Hive workloads, transactional'],
        ['Delta Lake', 'High + ACID', 'Very fast + time-travel', 'Medium', 'Lakehouse: ACID + analytics'],
    ]) +
    H('h4', 'Parquet File Structure — What\'s Inside') +
    PRE(
        'Parquet file internals:\n\n'
        '┌─────────────────────────────────────────────┐\n'
        '│  MAGIC BYTES: "PAR1"                        │\n'
        '│──────────────────────────────────────────── │\n'
        '│  Row Group 1 (e.g., 128MB of rows)          │\n'
        '│    Column chunk: user_id   [encoded values] │\n'
        '│    Column chunk: age       [encoded values] │\n'
        '│    Column chunk: country   [encoded values] │\n'
        '│──────────────────────────────────────────── │\n'
        '│  Row Group 2 (next 128MB of rows)           │\n'
        '│    Column chunks...                         │\n'
        '│──────────────────────────────────────────── │\n'
        '│  Footer: schema + row group offsets         │\n'
        '│    min/max statistics per column per chunk  │\n'
        '└─────────────────────────────────────────────┘\n\n'
        '# Statistics in footer enable predicate pushdown:\n'
        '# WHERE country = "US" → check if "US" is within [min,max] of each row group\n'
        '# Skip entire row groups that cannot contain the value → zero bytes read!'
    )
)

col_l3 = (
    H('h4', 'S3 Partitioning — Hive-Style Directory Layout') +
    P('When storing large datasets on S3 (or HDFS), the directory structure acts as a physical partition. '
      'Spark/Hive reads ONLY partition directories that match the query filter, '
      'completely skipping all other directories.') +
    PRE(
        '# Good partition structure (by year/month/day)\n'
        's3://my-bucket/events/\n'
        '    year=2024/\n'
        '        month=01/\n'
        '            day=01/\n'
        '                part-00000.parquet\n'
        '                part-00001.parquet\n'
        '            day=02/\n'
        '                ...\n'
        '        month=02/...\n\n'
        '# Query: WHERE year=2024 AND month=01 AND day=01\n'
        '# Reads: ONLY s3://my-bucket/events/year=2024/month=01/day=01/\n'
        '# Skips: all other months and days entirely\n\n'
        '# Spark reads partition from path automatically:\n'
        'df = spark.read.parquet("s3://my-bucket/events/")\n'
        'df.filter((df.year==2024) & (df.month==1)).show()\n'
        '# Spark sees partition filter → reads only matching directories'
    ) +
    H('h4', 'The Small File Problem — The Silent Performance Killer') +
    P('Data lakes accumulate thousands of tiny files (1-10MB each) over time, typically from: '
      'streaming jobs writing every minute, or daily partitions with many sub-partitions.') +
    P('The problem: Parquet/HDFS has per-file overhead. '
      '10,000 files of 5MB each reads SLOWER than 50 files of 1GB each — '
      'even though it\'s the same total data. Every file requires one filesystem API call, '
      'one file open, reading the footer, and metadata validation.') +
    PRE(
        '# Detect small file problem in Spark:\n'
        'df.rdd.getNumPartitions()  # if this is > 10,000, you have too many small files\n\n'
        '# Fix: coalesce (narrow transform) or repartition (full shuffle)\n'
        'df.coalesce(200).write.parquet("output/")  # merge to 200 files — no shuffle\n'
        'df.repartition(200).write.parquet("output/")  # redistribute evenly — full shuffle\n\n'
        '# Rule: target file size 128MB–1GB. coalesce < 200 files is usually fine.'
    )
)

col_l4 = (
    H('h4', 'Delta Lake — ACID Transactions on a Data Lake') +
    P('Traditional data lakes (S3 + Parquet) have no transaction support: '
      'if you DELETE or UPDATE records, you have to rewrite entire Parquet files. '
      'If your job fails halfway through, you have partial data written — corrupted state. '
      '<strong>Delta Lake</strong> adds ACID transactions and time travel to any Parquet-based data lake.') +
    PRE(
        '# Delta Lake stores data as Parquet + a transaction log (_delta_log/)\n'
        's3://my-bucket/orders/\n'
        '    _delta_log/\n'
        '        00000000000000000000.json  # commit 0: initial data\n'
        '        00000000000000000001.json  # commit 1: added rows\n'
        '        00000000000000000002.json  # commit 2: deleted rows\n'
        '    part-00000.parquet\n'
        '    part-00001.parquet\n\n'
        '# ACID operations:\n'
        'from delta.tables import DeltaTable\n'
        'dt = DeltaTable.forPath(spark, "s3://my-bucket/orders/")\n\n'
        '# DELETE with conditions (records are marked deleted in log, not physically removed)\n'
        'dt.delete("order_status = \'CANCELLED\'")\n\n'
        '# UPSERT (MERGE INTO): insert new rows, update existing ones\n'
        'dt.alias("target").merge(\n'
        '    updates_df.alias("source"),\n'
        '    "target.order_id = source.order_id"\n'
        ').whenMatchedUpdateAll().whenNotMatchedInsertAll().execute()\n\n'
        '# Time travel: query data as it was at a previous point\n'
        'df_yesterday = spark.read.format("delta").option("timestampAsOf", "2024-01-01").load(...)'
    ) +
    P('<strong>FAANG interview:</strong> "When would you choose Delta Lake over plain Parquet?"') +
    UL(
        'You need to DELETE or UPDATE individual records (GDPR right-to-be-forgotten)',
        'You need ACID guarantees: multiple writers, no partial writes',
        'You need time travel: audit trail, debugging, rollbacks',
        'You process late-arriving data that needs to be merged into historical partitions',
        'Plain Parquet is better: write-once append-only workloads where simplicity is valued'
    )
)

COL_CONTENT = '<div class="lesson-levels">' + L(1, '🟢', 'Row vs Columnar — The Layout Trade-Off', col_l1) + L(2, '🔵', 'Compression, Formats, Parquet Internals', col_l2) + L(3, '🟡', 'S3 Partitioning + Small File Problem', col_l3) + L(4, '🔴', 'Delta Lake — ACID on Data Lakes', col_l4) + '</div>'


# ═══════════════════════════════════════════════════════════════════
# TOPIC: spark_logical_plan  (Week 7 — Spark)
# ═══════════════════════════════════════════════════════════════════
spark_l1 = (
    H('h4', 'What Spark Actually Is — And Why It Exists') +
    P('Apache Spark was created in 2009 at UC Berkeley\'s AMPLab as a faster replacement for Hadoop MapReduce. '
      'Hadoop MapReduce wrote intermediate results to disk after every step. '
      'A 10-step pipeline wrote and read disk 10 times — massive I/O overhead. '
      'Spark keeps intermediate results <strong>in memory</strong>, passing data between stages without disk. '
      'For iterative algorithms (machine learning) and multi-step pipelines, this is 10–100x faster.') +
    H('h4', 'How Spark Executes Code — The Driver/Executor Model') +
    PRE(
        'Spark Cluster Architecture:\n\n'
        '┌─────────────────────────────────────────────────┐\n'
        '│              DRIVER (your Python code)          │\n'
        '│  - Runs on the master node                      │\n'
        '│  - Builds the execution plan                    │\n'
        '│  - Sends tasks to executors                     │\n'
        '│  - Collects results                             │\n'
        '└───────────────────┬─────────────────────────────┘\n'
        '                    │ (sends serialized tasks)\n'
        '     ┌──────────────┼──────────────┐\n'
        '     ▼              ▼              ▼\n'
        '┌─────────┐  ┌─────────┐  ┌─────────┐\n'
        '│Executor │  │Executor │  │Executor │\n'
        '│ - Node 1│  │ - Node 2│  │ - Node 3│\n'
        '│ - tasks │  │ - tasks │  │ - tasks │\n'
        '│ - cache │  │ - cache │  │ - cache │\n'
        '└─────────┘  └─────────┘  └─────────┘\n\n'
        '# DataFrame operations run on executors in parallel\n'
        '# Driver only sees final results (unless you call .collect() — dangerous!)'
    ) +
    H('h4', 'Lazy Evaluation — Nothing Runs Until You Ask') +
    P('Spark is lazy: DataFrame transformations (filter, select, join, groupBy) do NOT execute immediately. '
      'They build a <strong>query plan</strong>. Only <strong>actions</strong> '
      '(collect(), count(), write(), show()) trigger actual execution.') +
    PRE(
        'df = spark.read.parquet("s3://events/")   # no I/O yet\n'
        'df2 = df.filter(df.year == 2024)           # no I/O yet — builds plan\n'
        'df3 = df2.groupBy("country").count()       # no I/O yet — extends plan\n\n'
        'df3.show()  # ← ACTION: NOW Spark executes the entire plan\n\n'
        '# Why lazy? Spark\'s optimizer (Catalyst) can rearrange operations:\n'
        '# - Pushes filters before joins (read less data)\n'
        '# - Eliminates unused columns early\n'
        '# - Merges multiple transformations into single scan\n'
        '# This often makes your unoptimized code run faster automatically.'
    )
)

spark_l2 = (
    H('h4', 'The Shuffle — The Most Expensive Spark Operation') +
    P('A <strong>shuffle</strong> occurs when data needs to be redistributed across executors '
      'based on a key — for example, during a <code>groupBy</code>, <code>join</code>, or <code>repartition</code>. '
      'Shuffle is expensive because: (1) executors must write their partition to disk, '
      '(2) data is sent over the network, (3) receiving executors read from disk and memory. '
      'In a job with 100 executors processing 1TB, a shuffle can move terabytes over the network.') +
    PRE(
        '# Operations that trigger a shuffle:\n'
        'df.groupBy("country").count()            # ← SHUFFLE: all rows for same country\n'
        '                                         #   must land on same executor\n'
        'df.join(other, "user_id")               # ← SHUFFLE: matching user_ids must\n'
        '                                         #   be co-located\n'
        'df.repartition(200, "country")          # ← SHUFFLE: explicit redistribution\n'
        'df.distinct()                            # ← SHUFFLE: deduplicate requires global view\n\n'
        '# Operations that do NOT shuffle (cheap "narrow" transformations):\n'
        'df.filter(df.year == 2024)              # stays on same partition\n'
        'df.select("user_id", "amount")          # stays on same partition\n'
        'df.withColumn("total", df.a + df.b)    # stays on same partition\n'
        'df.coalesce(10)                         # merge partitions, no redistribution\n\n'
        '# Reduce shuffles by:\n'
        '# 1. Partition data by join key BEFORE the join (pre-partition)\n'
        '# 2. Broadcast small tables (eliminates join shuffle entirely)\n'
        '# 3. Aggregate before joining (reduce data volume before shuffle)'
    ) +
    H('h4', 'Broadcast Join — Eliminating the Join Shuffle') +
    PRE(
        '# Problem: joining a 100TB fact table with a 50MB dimension\n'
        '# Default join → shuffle 100TB over network (catastrophically slow)\n\n'
        '# Solution: broadcast the small table to ALL executors\n'
        '# Each executor gets a full copy — no network movement for the large table\n\n'
        'from pyspark.sql.functions import broadcast\n\n'
        'result = large_df.join(\n'
        '    broadcast(small_dim_df),  # ← small table copied to all executors\n'
        '    on="product_id"\n'
        ')  # No shuffle of large_df! Each executor joins locally.\n\n'
        '# Spark auto-broadcasts tables < spark.sql.autoBroadcastJoinThreshold (default 10MB)\n'
        '# Increase for larger dimensions if they fit in executor memory:\n'
        'spark.conf.set("spark.sql.autoBroadcastJoinThreshold", "100m")'
    )
)

spark_l3 = (
    H('h4', 'Data Skew — When One Executor Does 90% of the Work') +
    P('<strong>Data skew</strong> is the #1 production Spark performance problem. '
      'It occurs when one partition key value has far more rows than others. '
      'Example: a NULL user_id for all guest orders means the "NULL" partition '
      'gets 80% of all rows. One executor processing 8TB while others process 100GB — '
      'the job is only as fast as the slowest executor.') +
    PRE(
        '# Detect skew: check partition sizes\n'
        'df.groupBy(spark_partition_id()).count().show()  # see partition row counts\n'
        '# If one partition has 100M rows and others have 1M → skew\n\n'
        '# Fix 1: Salt the key (add random suffix to distribute skewed keys)\n'
        'from pyspark.sql import functions as F\n\n'
        '# Add salt to the large table\n'
        'num_salt_buckets = 10\n'
        'salted_large = large_df.withColumn(\n'
        '    "salted_key",\n'
        '    F.concat(F.col("user_id"), F.lit("_"), (F.rand() * num_salt_buckets).cast("int"))\n'
        ')\n\n'
        '# Explode the small table to match all salted keys\n'
        'salt_values = spark.range(num_salt_buckets).withColumnRenamed("id", "salt")\n'
        'salted_small = small_df.crossJoin(salt_values).withColumn(\n'
        '    "salted_key",\n'
        '    F.concat(F.col("user_id"), F.lit("_"), F.col("salt"))\n'
        ')\n\n'
        '# Now join on salted_key — skew is evenly distributed!\n'
        'result = salted_large.join(salted_small, "salted_key")\n\n'
        '# Fix 2: Filter skewed keys and process separately\n'
        'normal = df.filter(F.col("user_id").isNotNull())\n'
        'nulls  = df.filter(F.col("user_id").isNull())\n'
        '# Process each differently, then union'
    ) +
    H('h4', 'Partitions vs Tasks — Understanding Parallelism') +
    P('In Spark, a <strong>partition</strong> is a chunk of data. A <strong>task</strong> processes one partition. '
      'The number of parallel tasks = number of executor cores. '
      'If you have 100 cores and 1,000 partitions → 100 tasks run simultaneously, '
      '10 rounds of 100 tasks = 10 rounds total.') +
    PRE(
        '# Rule of thumb: 2-4 partitions per CPU core\n'
        '# 100 cores → 200-400 partitions\n\n'
        '# Too few partitions: executors are idle (not enough work to distribute)\n'
        '# Too many partitions: per-partition overhead dominates (too many small tasks)\n\n'
        'df.rdd.getNumPartitions()  # check current partition count\n'
        'df.repartition(400)  # redistribute to 400 partitions (shuffle)\n'
        'df.coalesce(10)      # reduce to 10 partitions (no shuffle, but may be uneven)\n\n'
        'spark.conf.set("spark.sql.shuffle.partitions", "400")  # for groupBy/join output'
    )
)

spark_l4 = (
    H('h4', 'FAANG Interview: Diagnosing a Slow Spark Job') +
    P('Interview question: "Your Spark job processes 10TB of data but takes 6 hours. Walk me through diagnosing it."') +
    PRE(
        'Step 1 — Open the Spark UI (port 4040)\n'
        '  → DAG tab: which stage takes the most time?\n'
        '  → Stage details: which task is the slowest? (skew indicator)\n'
        '  → Storage tab: how much data is cached? Is spill occurring?\n\n'
        'Step 2 — Identify the type of slowdown:\n'
        '\n'
        '  A. One stage takes 90% of job time:\n'
        '     → Check if it contains a shuffle (groupBy, join)\n'
        '     → If so: can you reduce data before the shuffle? Broadcast the smaller side?\n'
        '\n'
        '  B. One task in a stage takes 10x longer than others:\n'
        '     → Data skew. Check: what is the key distribution?\n'
        '     → Fix: salt the key, or handle skewed keys separately\n'
        '\n'
        '  C. Spill to disk (red in Spark UI):\n'
        '     → Executor ran out of memory, wrote shuffle data to disk\n'
        '     → Fix: increase executor memory, or increase spark.sql.shuffle.partitions\n'
        '       (more partitions = smaller per-partition size = less memory per partition)\n'
        '\n'
        '  D. Many stages, each fast individually but slow overall:\n'
        '     → Wide dependency chain — hard to parallelize\n'
        '     → Fix: checkpoint intermediate results, cache frequently reused DataFrames\n\n'
        'df.cache()  # cache in memory — avoid recomputing in subsequent actions\n'
        'df.persist(StorageLevel.DISK_ONLY)  # persist to disk if too large for memory'
    ) +
    P('✍️ <strong>The Spark UI is your most important debugging tool.</strong> '
      'FAANG interviewers expect you to know how to read it and what each metric means.')
)

SPARK_CONTENT = '<div class="lesson-levels">' + L(1, '🟢', 'What Spark Is — Driver/Executor + Lazy Eval', spark_l1) + L(2, '🔵', 'The Shuffle + Broadcast Joins', spark_l2) + L(3, '🟡', 'Data Skew + Partitions vs Tasks', spark_l3) + L(4, '🔴', 'Diagnosing a Slow Spark Job', spark_l4) + '</div>'


WEEKS4_PARTIAL2 = {
    "row_vs_columnar": {
        "basics": COL_CONTENT,
        "key_concepts": [
            "Row storage: all columns of one row together. Fast for full-row reads/writes (OLTP).",
            "Columnar storage: all values of one column together. Fast for analytical queries (scan few columns of many rows).",
            "Columnar compression: same-type values in a block compress 5–10x better than mixed row data.",
            "Parquet internals: row groups (128MB), column chunks within groups, statistics in footer.",
            "Footer statistics enable predicate pushdown: skip entire row groups that can't match WHERE condition.",
            "S3 partitioning: Hive-style year=/month=/day= directories. Spark reads only matching partitions.",
            "Small file problem: 10K 5MB files read slower than 50 1GB files. Target 128MB–1GB per file.",
            "Delta Lake: adds ACID + time travel to Parquet. Use when you need DELETE/UPDATE/upsert on a data lake.",
        ],
        "hints": [
            "Interview: 'Why Parquet over CSV?' → columnar compression, predicate pushdown, schema enforcement.",
            "Footer statistics in Parquet: min/max per column chunk enable row group skipping — huge for filtered reads.",
            "Small file fix: df.coalesce(200) (no shuffle, reduce only) or df.repartition(200) (shuffle, redistribute evenly).",
            "Delta Lake vs Parquet: Parquet = simple, immutable. Delta = ACID + time travel + schema enforcement.",
        ],
        "tasks": [
            "<strong>Step 1:</strong> Create a 1M-row DataFrame. Write it as CSV and as Parquet. Compare file sizes on disk. Then query only 2 of 10 columns — compare read times.",
            "<strong>Step 2:</strong> Write the same DataFrame partitioned by year and month. Confirm Spark uses partition pruning by checking the query plan with .explain().",
            "<strong>Step 3:</strong> Simulate small file problem: write 1,000 small Parquet files. Then coalesce to 10 files. Compare read performance.",
            "<strong>Step 4:</strong> Try a Delta Lake MERGE (upsert): start with 1M orders, receive 10K updates and 5K new rows. Use .merge() to apply changes. Read back and verify.",
        ],
        "hard_problem": "Boss Problem (Databricks): You manage a data lake with 3TB of daily event data, stored as Parquet, partitioned by date. Problems: (1) 18 months of data — 540 date partitions × 2,000 small files each = 1.08M files. Query times degraded from 2min to 45min. (2) GDPR requires deleting all data for specific user_ids within 30 days. (3) Late-arriving data lands 3-5 days after the event date, breaking partition assumptions. Design the migration plan to Delta Lake that fixes all three problems.",
    },

    "spark_logical_plan": {
        "basics": SPARK_CONTENT,
        "key_concepts": [
            "Spark = distributed in-memory computing. Driver builds plan, executors execute tasks on partitions.",
            "Lazy evaluation: transformations build a plan. Actions (count/show/write) trigger execution.",
            "Catalyst optimizer: rearranges your query plan for efficiency — predicate pushdown, column pruning.",
            "Shuffle: data redistribution across network. Most expensive operation. Triggered by groupBy, join, distinct.",
            "Narrow transformation: each partition maps to exactly one output partition. No shuffle. Fast.",
            "Broadcast join: copies small table to all executors. Eliminates join shuffle for large+small joins.",
            "Data skew: one partition key has disproportionate rows. Fix: salting (randomize key) or separate processing.",
            "Partitions = data chunks. Tasks = work units (1 per partition). Target 2-4 partitions per core.",
            "spark.sql.shuffle.partitions default = 200. Tune to 2-4x your number of cores.",
        ],
        "hints": [
            "Seeing one stage taking 90% of job time? Check for shuffle. Can you broadcast the smaller side?",
            "One task running 10x longer than others? Data skew. Check key value distribution with groupBy + count.",
            "Spill to disk in Spark UI? Executor out of memory. Increase executor memory or spark.sql.shuffle.partitions.",
            "Cache DataFrames reused multiple times: df.cache(). Unpersist when done: df.unpersist().",
        ],
        "tasks": [
            "<strong>Step 1:</strong> Read 10M rows. Chain: filter → groupBy → count. Use .explain(True) to show the physical plan. Identify which operations cause shuffles.",
            "<strong>Step 2:</strong> Join a 1B-row fact table with a 5MB lookup table. Compare: regular join vs broadcast join. Measure time difference with spark.time().",
            "<strong>Step 3:</strong> Simulate data skew: create a dataset where 80% of rows have user_id=NULL. Run a groupBy. Observe one task taking 10x longer. Apply the salt fix.",
            "<strong>Step 4:</strong> Set spark.sql.shuffle.partitions to 10, 200, 1000 on the same groupBy query. Observe partition count and execution time changes.",
        ],
        "hard_problem": "Boss Problem (Uber): Your daily Spark job aggregates 500B GPS ping events (5TB) to compute driver earnings per city. It runs in 14 hours but needs to run in 2 hours. Steps: (1) You find 3 shuffle stages dominate. How do you investigate each one? (2) One join between pings (5TB) and a driver_metadata table (2GB) causes a 3TB shuffle. How do you fix it without salting? (3) City='NULL' has 60% of all pings (GPS loss). How do you handle this skew? (4) The job reads the same 5TB raw data for 4 different aggregations. How do you avoid reading it 4 times?",
    },
}

print("WEEKS4_PARTIAL2 keys:", list(WEEKS4_PARTIAL2.keys()))
print("COL basics len:", len(WEEKS4_PARTIAL2['row_vs_columnar']['basics']))
print("SPARK basics len:", len(WEEKS4_PARTIAL2['spark_logical_plan']['basics']))
