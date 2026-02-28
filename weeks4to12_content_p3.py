"""
Weeks 9-12 Content: kafka_pub_sub, dag_architecture, data_quality, system_design_batch_etl
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
# TOPIC: kafka_pub_sub  (Week 11 — Streaming)
# ═══════════════════════════════════════════════════════════════════
kafka_l1 = (
    H('h4', 'Why Kafka Exists — The Message Bus Problem') +
    P('In 2010, LinkedIn had a problem: dozens of services needed to share data in real time. '
      'Payment service needed transaction events. Recommendation engine needed click events. '
      'Analytics needed all of it. Point-to-point connections between all services would require '
      'N² connections and N² custom APIs. Every new consumer meant updating every producer.') +
    P('LinkedIn built <strong>Apache Kafka</strong> as a distributed, append-only commit log '
      'that acts as a central data bus. Producers write events to Kafka topics. '
      'Any number of consumers read those events independently, at their own pace, '
      'without affecting other consumers or the producers.') +
    H('h4', 'Core Concepts') +
    TABLE([
        ['Concept', 'What it is', 'Analogy'],
        ['Topic', 'Named channel of events', 'A TV channel — broadcast to all who tune in'],
        ['Partition', 'Ordered, immutable log within a topic', 'A video tape — you can only append, reads have an offset'],
        ['Offset', 'Position of a message within a partition', 'Page number in a book — resume from where you left off'],
        ['Producer', 'Writes messages to a topic', 'A journalist who publishes articles'],
        ['Consumer', 'Reads messages from a topic', 'A reader who subscribes to the newspaper'],
        ['Consumer Group', 'Set of consumers sharing work', 'A team reading different sections of the newspaper'],
        ['Broker', 'A Kafka server storing partitions', 'A post office branch'],
    ]) +
    P('✍️ <strong>Key insight:</strong> Messages in Kafka are NOT deleted when consumed. '
      'They are retained for a configurable period (typically 7 days). '
      'Multiple consumers read the same message independently — each gets their own offset pointer.')
)

kafka_l2 = (
    H('h4', 'Partitions — The Key to Kafka\'s Scalability') +
    P('A topic is split into partitions. Each partition is an ordered, immutable log stored on one broker. '
      'Producers can write to any partition (using a key for deterministic routing). '
      'Each consumer in a group is assigned one or more partitions exclusively.') +
    P('<strong>The fundamental rule:</strong> one partition is consumed by exactly one consumer in a group at any time. '
      'This is how Kafka provides ordering guarantees and prevents duplicate processing within a group.') +
    PRE(
        'Topic "user_events" with 4 partitions, Consumer Group A with 3 consumers:\n\n'
        'Partition 0 → Consumer 1 (assigned exclusively)\n'
        'Partition 1 → Consumer 1 (one consumer can have multiple partitions)\n'
        'Partition 2 → Consumer 2\n'
        'Partition 3 → Consumer 3\n\n'
        'If Consumer 1 crashes:\n'
        '  Kafka rebalances → Consumer 2 picks up Partition 0 and 1\n\n'
        '# Scaling rule: max parallelism = number of partitions\n'
        '# 4 partitions → max 4 consumers in a group can work in parallel\n'
        '# Adding a 5th consumer → it sits idle (no partition to consume)\n\n'
        '# Partition key routing:\n'
        '# producer.send("user_events", key="user_42", value=event)\n'
        '# → All events for user_42 always go to the SAME partition\n'
        '# → All events for user_42 are processed in ORDER by the same consumer'
    ) +
    H('h4', 'Consumer Group — Independent Consumers Read the Same Stream') +
    PRE(
        'Topic "orders":\n'
        '  Group A (analytics): reads orders → writes to DW → at offset 50,000\n'
        '  Group B (fraud):     reads orders → checks for fraud → at offset 49,500\n'
        '  Group C (email):     reads orders → sends shipping emails → at offset 51,000\n\n'
        '# Each group has its own independent offset tracking\n'
        '# Producer\'s throughput is unaffected by how fast consumers read\n'
        '# If Group B (fraud) is slow, it does not slow down Group A or C'
    )
)

kafka_l3 = (
    H('h4', 'Delivery Semantics — At-Most-Once, At-Least-Once, Exactly-Once') +
    P('The most common Kafka interview question: what delivery guarantee does Kafka provide?') +
    TABLE([
        ['Semantic', 'Messages delivered', 'Duplicates?', 'Data loss?', 'When to use'],
        ['At-most-once', 'Maybe delivered', 'Never', 'Possible', 'Metrics sampling, non-critical logs'],
        ['At-least-once', 'Guaranteed delivered', 'Possible', 'Never', 'Most common: process with idempotent consumer'],
        ['Exactly-once', 'Exactly once end-to-end', 'Never', 'Never', 'Financial transactions, audit logs'],
    ]) +
    P('<strong>How at-least-once works:</strong> Consumer reads message → processes it → commits offset. '
      'If the consumer crashes AFTER processing but BEFORE committing, '
      'the next consumer starts from the last committed offset and re-processes the same message. '
      'This is why consuming applications must be idempotent — processing the same message twice produces the correct result.') +
    PRE(
        '# Idempotent consumer pattern: INSERT ... ON CONFLICT DO NOTHING\n'
        'INSERT INTO processed_orders (order_id, status, updated_at)\n'
        'VALUES (%(order_id)s, %(status)s, %(ts)s)\n'
        'ON CONFLICT (order_id) DO UPDATE\n'
        '  SET status = EXCLUDED.status,\n'
        '      updated_at = EXCLUDED.updated_at\n'
        '  WHERE orders.updated_at < EXCLUDED.updated_at;\n'
        '-- Running this query twice with the same data = same result (idempotent)'
    ) +
    H('h4', 'Kafka vs Message Queue — A Critical Distinction') +
    TABLE([
        ['Feature', 'Kafka (Log)', 'RabbitMQ/SQS (Queue)'],
        ['Message retention', 'Retained for days (configurable)', 'Deleted after consumption'],
        ['Multiple consumers', 'Yes — each group reads independently', 'No — one consumer gets each message'],
        ['Replay', 'Yes — seek to any offset', 'No — once consumed, gone'],
        ['Ordering', 'Guaranteed within partition', 'Generally no guarantee'],
        ['Throughput', 'Millions/sec (sequential disk)', 'Thousands/sec'],
        ['Best for', 'Event streaming, audit log, multiple consumers', 'Task queues, job distribution'],
    ])
)

kafka_l4 = (
    H('h4', 'Windowing — Aggregating Over Time in a Stream') +
    P('Streams are infinite, but analytics need finite windows: '
      '"revenue per hour," "error rate per 5-minute window," "top 10 pages per day."') +
    PRE(
        '# Three types of windows in stream processing (Flink/Kafka Streams/Spark Structured Streaming):\n\n'
        '# 1. Tumbling Window: fixed, non-overlapping\n'
        '#    |---1min---|---1min---|---1min---|\n'
        '#    Each event belongs to exactly one window.\n\n'
        '# 2. Sliding Window: fixed size, overlapping (stride < window size)\n'
        '#    |---10min---|\n'
        '#        |---10min---|\n'
        '#            |---10min---|\n'
        '#    Each event appears in multiple windows.\n\n'
        '# 3. Session Window: dynamic, gap-based\n'
        '#    A session starts on first event, ends after N seconds of inactivity.\n'
        '#    Common for: user session analytics, page view sessions.\n\n'
        '# Late data problem:\n'
        '#   Event timestamp: 14:02 (when it happened on the device)\n'
        '#   Processing timestamp: 14:09 (when Kafka received it — 7min late)\n'
        '#   The 14:00-14:05 window is already closed! What do you do?\n\n'
        '# Solutions:\n'
        '#   Watermark: allow data up to N minutes late, then close the window\n'
        '#   Reprocess: store events in a buffer period, re-aggregate after watermark\n'
        '#   Lambda architecture: batch layer handles late data correctness,\n'
        '#   speed layer handles real-time approximate results'
    ) +
    H('h4', 'FAANG Interview: Design a Real-Time Analytics Pipeline') +
    P('Question: "Design a system to display real-time metrics for a ride-sharing app: '
      'active riders, active drivers, rides per minute by city, surge pricing signal."') +
    PRE(
        'Sources: mobile apps emit GPS pings, ride state changes → Kafka topics\n\n'
        'Kafka topics:\n'
        '  - driver_pings (partitioned by driver_id) → 100K msgs/sec\n'
        '  - ride_events  (partitioned by city)      →  10K msgs/sec\n\n'
        'Stream processing (Flink):\n'
        '  - 1-minute tumbling window on ride_events → count rides per city\n'
        '  - 5-minute window on driver_pings → count active drivers per city\n'
        '  - Session window on driver_pings → detect driver going offline\n\n'
        'Output sinks:\n'
        '  - Redis (for dashboard): SET city:rides:nyc 125   (1-min rolling count)\n'
        '  - Kafka topic "metrics" → dashboard WebSocket feed\n'
        '  - S3 Parquet → hourly batch for BI reporting\n\n'
        'Surge pricing signal:\n'
        '  - rides_requested / active_drivers > 1.5 in last 5 minutes → surge!'
    )
)

KAFKA_CONTENT = '<div class="lesson-levels">' + L(1, '🟢', 'Why Kafka Exists — Core Concepts', kafka_l1) + L(2, '🔵', 'Partitions + Consumer Groups', kafka_l2) + L(3, '🟡', 'Delivery Semantics + Kafka vs Queue', kafka_l3) + L(4, '🔴', 'Windowing + Real-Time Analytics Design', kafka_l4) + '</div>'


# ═══════════════════════════════════════════════════════════════════
# TOPIC: dag_architecture  (Week 10 — Orchestration)
# ═══════════════════════════════════════════════════════════════════
dag_l1 = (
    H('h4', 'What is a DAG and Why Orchestration Matters') +
    P('A data pipeline consists of multiple steps: extract from source, validate, transform, load, test, notify. '
      'These steps have dependencies — step 3 cannot start until steps 1 and 2 complete. '
      'Some steps can run in parallel (downloading from multiple sources simultaneously). '
      'Some steps must run in sequence (load only after validation passes).') +
    P('A <strong>Directed Acyclic Graph (DAG)</strong> is the formal way to represent these dependencies: '
      'nodes are tasks, directed edges represent "must complete before." '
      'Acyclic means there are no circular dependencies (which would cause deadlock). '
      'Apache Airflow is the dominant DAG orchestration platform at FAANG companies.') +
    PRE(
        '# Example DAG: daily customer revenue pipeline\n\n'
        '     [extract_orders]   [extract_customers]   ← parallel execution\n'
        '            \\                 /\n'
        '          [validate_data]            ← waits for both\n'
        '                  |\n'
        '     [compute_revenue]              ← runs after validation\n'
        '         /          \\\\\n'
        '[load_to_dw]  [send_slack_report]   ← parallel execution\n'
        '         \\\\\n'
        '       [run_dbt_tests]              ← runs after load'
    ) +
    H('h4', 'Airflow Core Concepts') +
    TABLE([
        ['Concept', 'What It Does'],
        ['DAG', 'A Python file defining the workflow graph'],
        ['Task', 'A single unit of work (one node in the graph)'],
        ['Operator', 'Type of task: PythonOperator, BashOperator, SparkSubmitOperator, etc.'],
        ['Sensor', 'Special operator that waits for a condition (file arrives, API responds)'],
        ['Schedule', 'Cron expression or timedelta defining when DAG runs'],
        ['DAG Run', 'One execution instance of a DAG for a specific logical date'],
        ['Task Instance', 'One execution of one task within a DAG Run'],
        ['XCom', 'Mechanism for tasks to pass small values to downstream tasks'],
    ])
)

dag_l2 = (
    H('h4', 'Operators and Sensors — The Building Blocks') +
    P('An <strong>Operator</strong> defines what a task does. '
      'Airflow provides built-in operators for common actions, '
      'and you can write custom operators for anything else.') +
    PRE(
        'from airflow import DAG\n'
        'from airflow.operators.python import PythonOperator\n'
        'from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator\n'
        'from airflow.sensors.filesystem import FileSensor\n'
        'from datetime import datetime, timedelta\n\n'
        'default_args = {\n'
        '    "owner": "data-team",\n'
        '    "retries": 3,\n'
        '    "retry_delay": timedelta(minutes=5),\n'
        '    "email_on_failure": True,\n'
        '}\n\n'
        'with DAG(\n'
        '    dag_id="daily_revenue_pipeline",\n'
        '    schedule_interval="0 3 * * *",    # 3am UTC daily\n'
        '    start_date=datetime(2024, 1, 1),\n'
        '    catchup=False,                    # don\'t backfill old runs\n'
        '    default_args=default_args,\n'
        ') as dag:\n\n'
        '    wait_for_source = FileSensor(\n'
        '        task_id="wait_for_source_file",\n'
        '        filepath="/data/source/orders_{{ ds }}.csv",\n'
        '        poke_interval=60,   # check every 60 seconds\n'
        '        timeout=3600,       # fail if not found within 1 hour\n'
        '    )\n\n'
        '    run_spark = SparkSubmitOperator(\n'
        '        task_id="compute_revenue",\n'
        '        application="s3://jobs/revenue_job.py",\n'
        '        conf={"spark.executor.memory": "8g"},\n'
        '    )\n\n'
        '    def validate(**context):\n'
        '        # access the execution date via context\n'
        '        ds = context["ds"]  # "2024-01-15"\n'
        '        count = check_row_count(ds)\n'
        '        if count < 1000:\n'
        '            raise ValueError(f"Only {count} rows — expected > 1000")\n\n'
        '    validate_task = PythonOperator(\n'
        '        task_id="validate_output",\n'
        '        python_callable=validate,\n'
        '    )\n\n'
        '    # Dependency chain\n'
        '    wait_for_source >> run_spark >> validate_task'
    )
)

dag_l3 = (
    H('h4', 'XComs — Passing Data Between Tasks') +
    P('XCom (cross-communication) allows tasks to pass small values to downstream tasks. '
      '<strong>Critical rule:</strong> XComs are stored in the Airflow metadata database. '
      'They are for small values only: row counts, file paths, status strings, timestamps. '
      'Never XCom a DataFrame or large file — use S3/GCS paths instead.') +
    PRE(
        '# Task 1: pushes a value via XCom (auto-push with return)\n'
        'def extract(**context):\n'
        '    rows = run_extraction()\n'
        '    return len(rows)  # auto-pushed to XCom key "return_value"\n\n'
        '# Task 2: pulls the value from upstream task\n'
        'def validate(**context):\n'
        '    row_count = context["ti"].xcom_pull(\n'
        '        task_ids="extract_task",  # which task\n'
        '        key="return_value"        # which XCom key\n'
        '    )\n'
        '    if row_count < 1000:\n'
        '        raise ValueError(f"Too few rows: {row_count}")\n\n'
        '# Better pattern for large data: pass S3 path, not the data itself\n'
        'def extract(**context):\n'
        '    ds = context["ds"]\n'
        '    path = f"s3://staging/orders/{ds}/data.parquet"\n'
        '    write_data_to_s3(path)\n'
        '    return path  # XCom the path, not the data'
    ) +
    H('h4', 'Backfilling — Running Historical Dates') +
    P('<strong>Backfilling</strong> means running a DAG for historical dates — for example, '
      'you added a new column to your pipeline and need to reprocess the last 90 days of data. '
      'Airflow can trigger DAG runs for any historical date via the CLI or UI.') +
    PRE(
        '# Backfill via CLI: run every day from Jan 1 to Jan 31\n'
        'airflow dags backfill \\\n'
        '  --dag-id daily_revenue_pipeline \\\n'
        '  --start-date 2024-01-01 \\\n'
        '  --end-date 2024-01-31\n\n'
        '# ⚠️  Backfill pitfalls:\n'
        '# 1. catchup=True (default) auto-backfills missed runs on restart\n'
        '#    → set catchup=False to prevent surprise backfills\n'
        '# 2. Backfills run concurrently (all 31 days at once by default)\n'
        '#    → set max_active_runs=1 to run one day at a time\n'
        '# 3. Tasks may not be idempotent → backfill causes duplicate data\n'
        '#    → always make your pipeline idempotent!'
    )
)

dag_l4 = (
    H('h4', 'Dynamic DAGs — Generating at Scale') +
    P('When you need dozens or hundreds of similar pipelines (one DAG per client, per table, per region), '
      'manually writing each DAG is impractical. '
      '<strong>Dynamic DAGs</strong> generate the DAG structure programmatically from a config or database.') +
    PRE(
        '# Pattern: generate one DAG per client from a config file\n'
        '# clients.yaml: [{name: "acme", tables: ["orders","users"]}, ...]\n\n'
        'import yaml\n'
        'from airflow import DAG\n'
        'from airflow.operators.python import PythonOperator\n\n'
        'with open("/dags/config/clients.yaml") as f:\n'
        '    clients = yaml.safe_load(f)["clients"]\n\n'
        'for client in clients:\n'
        '    dag_id = f"etl_{client[\'name\']}"\n\n'
        '    with DAG(\n'
        '        dag_id=dag_id,\n'
        '        schedule_interval="0 4 * * *",\n'
        '        ...\n'
        '    ) as dag:\n'
        '        for table in client["tables"]:\n'
        '            task = PythonOperator(\n'
        '                task_id=f"process_{table}",\n'
        '                python_callable=process_table,\n'
        '                op_args=[client["name"], table],\n'
        '            )\n'
        '        globals()[dag_id] = dag  # register DAG globally for Airflow scanner\n\n'
        '# Result: one DAG per client, all generated from config\n'
        '# Adding a new client = add one line to clients.yaml'
    ) +
    H('h4', 'FAANG Interview: DAG Design Best Practices') +
    UL(
        '<strong>Idempotent tasks:</strong> running the same task twice for the same date should produce the same result. No duplicate inserts. Use INSERT ... ON CONFLICT or DELETE then INSERT.',
        '<strong>Atomic writes:</strong> write to a staging location, atomically move to final location. Never overwrite production data partially.',
        '<strong>Alerting:</strong> every production DAG should have email_on_failure=True and PagerDuty/Slack integration for SLA misses.',
        '<strong>SLA monitoring:</strong> if a DAG that normally finishes at 4am does not complete by 6am, trigger an alert — the downstream team needs to know.',
        '<strong>Prefer sensors over long-running tasks:</strong> a FileSensor that checks every 60 seconds uses minimal resources. A sleep loop in a Python task holds an executor slot.'
    )
)

DAG_CONTENT = '<div class="lesson-levels">' + L(1, '🟢', 'What DAGs Are + Airflow Core Concepts', dag_l1) + L(2, '🔵', 'Operators, Sensors, Real DAG Code', dag_l2) + L(3, '🟡', 'XComs + Backfilling Pitfalls', dag_l3) + L(4, '🔴', 'Dynamic DAGs + Design Best Practices', dag_l4) + '</div>'


# ═══════════════════════════════════════════════════════════════════
# TOPIC: data_quality  (Week 9 — Quality + dbt)
# ═══════════════════════════════════════════════════════════════════
dq_l1 = (
    H('h4', 'Data Quality — The Silent Business Risk') +
    P('Data quality failures are responsible for an estimated $3.1 trillion in losses annually in the US alone '
      '(IBM, 2016). At FAANG scale, bad data can cause: incorrect recommendations (Netflix), '
      'miscounted ad impressions (Google billing error), wrong product availability (Amazon), '
      'or payments to the wrong accounts (banking). Data quality is not a nice-to-have — it is a business-critical function.') +
    H('h4', 'The Five Dimensions of Data Quality') +
    TABLE([
        ['Dimension', 'Definition', 'Example check'],
        ['Completeness', 'Are required values present?', 'WHERE user_id IS NULL → count should be 0'],
        ['Uniqueness', 'No duplicate records?', 'COUNT(*) vs COUNT(DISTINCT pk) → must be equal'],
        ['Validity', 'Values within expected range/format?', 'age BETWEEN 0 AND 120, email LIKE \'%@%\''],
        ['Consistency', 'Same fact represented the same way?', 'revenue = SUM(line_items) for every order'],
        ['Timeliness', 'Data arrives when expected?', 'MAX(event_time) > NOW() - INTERVAL 1 HOUR'],
    ]) +
    H('h4', 'Data Quality Checks — Where to Put Them') +
    PRE(
        'Three places to add quality checks:\n\n'
        '1. INGESTION: validate data as it arrives from source\n'
        '   → Reject/quarantine rows that fail schema/range checks\n'
        '   → Stop bad data from entering the warehouse\n\n'
        '2. TRANSFORMATION: check intermediate results after each step\n'
        '   → Assert: if I join A to B, I should get X rows (± 5%)\n'
        '   → Check: did revenue change by >50% overnight? (anomaly)\n\n'
        '3. OUTPUT: check the final data before publishing to consumers\n'
        '   → Ensure tables are not empty\n'
        '   → Verify foreign key integrity\n'
        '   → Check business rules (all orders have a payment)'
    )
)

dq_l2 = (
    H('h4', 'dbt — Data Build Tool') +
    P('dbt (data build tool) is the standard tool for SQL-based transformations in modern data warehouses. '
      'It lets you write SQL SELECT queries (models), run them as CREATE TABLE / CREATE VIEW, '
      'test them automatically, document them, and track lineage.') +
    PRE(
        '# dbt model: models/revenue/daily_revenue.sql\n'
        '-- This SQL becomes a table in your data warehouse\n'
        '{{ config(materialized=\'table\') }}\n\n'
        'SELECT\n'
        '    order_date,\n'
        '    SUM(revenue)     AS total_revenue,\n'
        '    COUNT(order_id)  AS order_count\n'
        'FROM {{ ref(\'stg_orders\') }}   -- reference another dbt model\n'
        'WHERE order_status = \'COMPLETED\'\n'
        'GROUP BY order_date\n\n'
        '# dbt test: models/revenue/schema.yml\n'
        '# Tests run automatically after each model build\n'
        'models:\n'
        '  - name: daily_revenue\n'
        '    columns:\n'
        '      - name: order_date\n'
        '        tests:\n'
        '          - not_null\n'
        '          - unique\n'
        '      - name: total_revenue\n'
        '        tests:\n'
        '          - not_null\n'
        '          - dbt_utils.expression_is_true:\n'
        '              expression: "> 0"  # revenue must be positive'
    ) +
    H('h4', 'Schema Evolution — Handling Schema Changes Safely') +
    PRE(
        '# Adding a column: backwards compatible — safe\n'
        'ALTER TABLE orders ADD COLUMN promo_code VARCHAR(50);\n'
        '-- Existing readers ignore the new column (Parquet, Avro do this automatically)\n\n'
        '# Removing a column: BREAKING CHANGE\n'
        '-- Readers that expect the column will fail!\n'
        '-- Strategy: deprecate first (document), migrate readers, then drop\n\n'
        '# Changing a column type: almost always BREAKING\n'
        '-- VARCHAR(50) → VARCHAR(200): safe (wider)\n'
        '-- INT → BIGINT: safe in Parquet (widening)\n'
        '-- INT → VARCHAR: breaking (downstream code fails)\n\n'
        '# Schema enforcement in Parquet (PySpark):\n'
        'df.write.option("mergeSchema", "true").parquet("s3://data/orders/")\n'
        '# mergeSchema=True: allows new columns to be added to existing Parquet files\n'
        '# Missing columns in old files appear as NULL in combined reads'
    )
)

dq_l3 = (
    H('h4', 'Idempotency — The Most Important Pipeline Property') +
    P('<strong>Idempotency:</strong> running a pipeline multiple times for the same date produces the same result. '
      'This is essential for: safe retries after failures, safe backfills, and debugging in production.') +
    PRE(
        '# ❌ NON-IDEMPOTENT: running twice creates duplicate rows\n'
        'INSERT INTO daily_revenue\n'
        'SELECT order_date, SUM(revenue) FROM orders GROUP BY order_date;\n'
        '-- Run twice for 2024-01-15 → two rows for 2024-01-15!\n\n'
        '# ✅ IDEMPOTENT pattern 1: DELETE THEN INSERT (delete-and-replace)\n'
        'DELETE FROM daily_revenue WHERE order_date = \'2024-01-15\';\n'
        'INSERT INTO daily_revenue\n'
        'SELECT order_date, SUM(revenue) FROM orders WHERE order_date=\'2024-01-15\' GROUP BY 1;\n\n'
        '# ✅ IDEMPOTENT pattern 2: INSERT ... ON CONFLICT UPDATE\n'
        'INSERT INTO daily_revenue(order_date, total_revenue)\n'
        'SELECT order_date, SUM(revenue) FROM orders GROUP BY order_date\n'
        'ON CONFLICT (order_date) DO UPDATE SET total_revenue=EXCLUDED.total_revenue;\n\n'
        '# ✅ IDEMPOTENT pattern 3: overwrite the partition\n'
        'df.write\\\n'
        '  .partitionBy("order_date")\\\n'
        '  .mode("overwrite")\\\n'
        '  .parquet("s3://revenue/")\n'
        '# Rewrites only the affected partition — other partitions untouched'
    ) +
    H('h4', 'Unit Testing Data Pipelines') +
    PRE(
        'import pytest\n'
        'from pyspark.sql import SparkSession\n\n'
        'def test_revenue_computation():\n'
        '    spark = SparkSession.builder.master("local[2]").getOrCreate()\n\n'
        '    # Create small test dataframe\n'
        '    input_data = [\n'
        '        ("2024-01-15", "COMPLETED", 100.0),\n'
        '        ("2024-01-15", "COMPLETED", 50.0),\n'
        '        ("2024-01-15", "CANCELLED", 200.0),   # should be excluded\n'
        '    ]\n'
        '    orders_df = spark.createDataFrame(input_data, ["order_date","status","revenue"])\n\n'
        '    # Run the transformation\n'
        '    result = compute_daily_revenue(orders_df)\n\n'
        '    # Assert expected output\n'
        '    rows = result.collect()\n'
        '    assert len(rows) == 1, "Expected one result row"\n'
        '    assert rows[0].total_revenue == 150.0, "Cancelled orders should be excluded"\n'
        '    assert rows[0].order_date == "2024-01-15"'
    )
)

dq_l4 = (
    H('h4', 'Data Governance — Lineage, Catalog, Access Control') +
    P('Data governance answers: what data do we have, what is it for, who should access it, where did it come from? '
      'At FAANG scale, this is essential because hundreds of engineers use the same data warehouse, '
      'and a new engineer must be able to find trustworthy data without asking.') +
    UL(
        '<strong>Data Catalog</strong>: searchable index of all tables with descriptions, owners, update frequency. Tools: AWS Glue, Amundsen, DataHub.',
        '<strong>Data Lineage</strong>: visualizes the transformation chain: "This dashboard metric comes from table X, which is built from source table Y, which ingests from API Z." Enables impact analysis: "If API Z changes, what breaks?"',
        '<strong>Column-level lineage</strong>: even more granular — traces which source columns contributed to each output column.',
        '<strong>PII governance</strong>: tables containing personal data (name, email, SSN) require special access controls, encryption, and retention policies.',
        '<strong>Row-level security</strong>: different rows visible to different users (e.g., each sales rep sees only their region\'s data).'
    ) +
    H('h4', 'FAANG Interview: "How do you handle bad data in production?"') +
    PRE(
        'Framework answer:\n\n'
        '1. DETECT: automated quality checks at every pipeline stage\n'
        '   - dbt tests on output models\n'
        '   - Great Expectations or custom SQL assertions\n'
        '   - Anomaly detection (revenue dropped 80%? → alert)\n\n'
        '2. ALERT: PagerDuty or Slack notification immediately\n'
        '   - Include: which table, which check failed, expected vs actual\n\n'
        '3. QUARANTINE: do not propagate bad data downstream\n'
        '   - Move failing records to quarantine table\n'
        '   - Good records continue to production\n\n'
        '4. INVESTIGATE: what is the root cause?\n'
        '   - Source system change? (schema evolution)\n'
        '   - Missing upstream data? (late arrival)\n'
        '   - Pipeline bug? (code change)\n\n'
        '5. FIX + BACKFILL: fix the pipeline, reprocess affected dates'
    )
)

DQ_CONTENT = '<div class="lesson-levels">' + L(1, '🟢', 'Data Quality Dimensions + Where to Check', dq_l1) + L(2, '🔵', 'dbt + Schema Evolution', dq_l2) + L(3, '🟡', 'Idempotency + Unit Testing', dq_l3) + L(4, '🔴', 'Governance + Handling Bad Data in Production', dq_l4) + '</div>'


# ═══════════════════════════════════════════════════════════════════
# TOPIC: system_design_batch_etl  (Week 12 — System Design)
# ═══════════════════════════════════════════════════════════════════
sd_l1 = (
    H('h4', 'Data Engineering System Design — What\'s Different from Software Engineering') +
    P('Software engineering system design interviews focus on: web services, APIs, databases, caching, load balancers. '
      'Data engineering system design adds: data volume math, pipeline latency, storage formats, '
      'streaming vs batch trade-offs, failure modes at scale, and cost optimization.') +
    H('h4', 'Back-of-Envelope Math — Essential for DE Interviews') +
    P('FAANG interviewers expect you to quickly estimate: how much storage do we need? '
      'How long will it take to process? What network bandwidth is required? '
      'This is called "back-of-envelope" calculation. Here are the key numbers to memorize:') +
    PRE(
        'Useful numbers:\n'
        '  1 byte       = 1 character\n'
        '  1 KB         = 1,000 bytes\n'
        '  1 MB         = 1,000 KB\n'
        '  1 GB         = 1,000 MB\n'
        '  1 TB         = 1,000 GB\n'
        '  1 PB         = 1,000 TB\n\n'
        '  SSD read     = 500 MB/sec\n'
        '  HDD read     = 100 MB/sec\n'
        '  Network LAN  = 1 GB/sec\n'
        '  S3/cloud     = 100-500 MB/sec (per file, in parallel: much more)\n\n'
        '  1 million events/day × 100 bytes/event = 100 MB/day\n'
        '  1 billion events/day × 100 bytes/event = 100 GB/day\n'
        '  = 3 TB/month ≈ 36 TB/year (uncompressed)\n'
        '  Parquet at 5x compression = 7 TB/year — easily fits in S3\n\n'
        '  100 million users × 1 KB profile = 100 GB — fits in memory on a large machine!'
    ) +
    H('h4', 'Batch ETL vs Streaming — The Core Trade-Off') +
    TABLE([
        ['Dimension', 'Batch ETL', 'Streaming'],
        ['Data freshness', 'Hours to daily', 'Seconds to minutes'],
        ['Complexity', 'Lower (simpler tooling)', 'Higher (state, ordering, fault tolerance)'],
        ['Cost', 'Lower (bursty compute)', 'Higher (always-running compute)'],
        ['Failure recovery', 'Simple: re-run the batch', 'Complex: replay from Kafka offset'],
        ['Best for', 'Daily reports, historical analysis', 'Fraud detection, live dashboards, alerting'],
        ['Tooling', 'Spark, dbt, Airflow', 'Kafka, Flink, Spark Structured Streaming'],
    ])
)

sd_l2 = (
    H('h4', 'Pattern: Designing a Batch ETL System') +
    P('Interview: "Design a system to compute daily sales metrics for a 50M-user e-commerce platform."') +
    PRE(
        '=== Requirements ===\n'
        'Functional:\n'
        '  - Daily revenue by product category and region\n'
        '  - Top 100 products by revenue per day\n'
        '  - Customer lifetime value (CLV) updated daily\n\n'
        'Non-functional:\n'
        '  - Pipeline must complete by 6am (SLA: 3 hours after midnight)\n'
        '  - Data must be queryable by the BI team by 7am\n'
        '  - Failures must auto-retry, team alerted if SLA missed\n\n'
        '=== Volume math ===\n'
        '  50M users × avg 1 order/day = 50M orders/day\n'
        '  50M orders × 3 items avg   = 150M order items/day\n'
        '  150M rows × 200 bytes      = 30GB/day uncompressed\n'
        '  Parquet compression (5x)   = 6GB/day to write\n'
        '  Running 1 year             = 2.2TB stored — very manageable\n\n'
        '=== Architecture ===\n'
        '  Source: OLTP PostgreSQL → CDC (Debezium) → Kafka topics\n'
        '  Landing zone: Kafka → raw Parquet on S3 (append every 5 min)\n'
        '  Daily batch: Airflow DAG at 00:30 UTC\n'
        '    Task 1: Spark reads raw S3 Parquet, computes dim + fact tables\n'
        '    Task 2: dbt runs transformation models + tests\n'
        '    Task 3: Snowflake/BigQuery tables updated for BI queries\n'
        '    Task 4: SLA check — alert if not done by 03:00 UTC'
    ) +
    H('h4', 'CDC — Change Data Capture') +
    P('<strong>CDC (Change Data Capture)</strong> captures database changes (INSERT/UPDATE/DELETE) '
      'in real time from the database\'s transaction log, without polling. '
      'Debezium is the open-source tool that reads PostgreSQL/MySQL WAL logs and '
      'publishes changes as Kafka messages.') +
    PRE(
        '# Why CDC instead of "SELECT * WHERE updated_at > last_run_time"?\n\n'
        '# Problem with polling:\n'
        '  1. Misses DELETEs (deleted rows cannot be queried)\n'
        '  2. Missing updated_at on some tables\n'
        '  3. High load on source DB (full table scans)\n'
        '  4. Possible race condition: row updated between runs\n\n'
        '# CDC reads from the WAL (Write-Ahead Log) directly:\n'
        '  - Captures every INSERT/UPDATE/DELETE as it happens\n'
        '  - Zero load on source tables\n'
        '  - No missed changes\n'
        '  - Before/after images of every row change\n\n'
        '# Debezium Kafka message format:\n'
        '{\n'
        '  "op": "u",         # u=update, c=create, d=delete\n'
        '  "before": {"user_id": 42, "tier": "silver"},\n'
        '  "after":  {"user_id": 42, "tier": "gold"},\n'
        '  "ts_ms": 1704067200000\n'
        '}'
    )
)

sd_l3 = (
    H('h4', 'Pattern: Lambda Architecture + Lambda vs Kappa') +
    P('<strong>Lambda Architecture:</strong> run two parallel systems — a batch layer for accuracy '
      '(recomputes everything correctly, but slowly) and a speed layer for freshness '
      '(approximate real-time results using streaming). Serving layer merges both.') +
    PRE(
        'Lambda Architecture:\n\n'
        'Raw data ──┬── Batch Layer (Spark, daily job) ──────► Batch views (exact)\n'
        '           │                                                  │\n'
        '           └── Speed Layer (Kafka+Flink, real-time) ──► Real-time views ──► Serving Layer ──► App\n\n'
        'Pros: batch layer corrects errors in real-time layer\n'
        'Cons: two codebases to maintain, possible inconsistencies between layers\n\n'
        'Kappa Architecture:\n'
        '  Only a speed layer. Use streaming for EVERYTHING, including historical reprocessing.\n'
        '  If you need to reprocess, replay from Kafka (if retention long enough) or S3.\n'
        '  Pros: one codebase. Cons: streaming code is harder, Kafka storage costs.\n\n'
        'Trend at FAANG: Kappa is winning for new systems.\n'
        'Lambda still common in legacy systems built 2015-2020.'
    ) +
    H('h4', 'Trade-Offs Matrix — For System Design Interviews') +
    TABLE([
        ['Requirement', 'Batch', 'Micro-batch (Spark SS)', 'Streaming (Flink/Kafka)'],
        ['Data freshness needed', 'Hours/daily', '5-30 min', '<1 min'],
        ['Historical reprocessing', 'Easy: re-run job', 'Moderate', 'Complex: replay from log'],
        ['Exactly-once guarantee', 'Easy: idempotent writes', 'Possible with checkpointing', 'Hard: requires distributed transactions'],
        ['Dev complexity', 'Low', 'Medium', 'High'],
        ['Infrastructure cost', 'Low (bursty)', 'Medium (semi-continuous)', 'High (always-on)'],
    ])
)

sd_l4 = (
    H('h4', 'Complete System Design: Real-Time Fraud Detection') +
    PRE(
        'Interview: "Design a real-time fraud detection system for a payments company."\n\n'
        '=== Functional Requirements ===\n'
        '  - Flag suspicious transactions within 500ms of payment attempt\n'
        '  - 10,000 transactions/second peak\n'
        '  - Fraud signal based on: velocity (too many txns), location change,\n'
        '    unusual amount, high-risk merchant category\n\n'
        '=== Architecture ===\n'
        '  Step 1: Ingestion\n'
        '    Payment service → Kafka topic "transactions" (partitioned by user_id)\n'
        '    Partitioning by user_id ensures all events for one user → same consumer\n\n'
        '  Step 2: Feature computation (Flink, <100ms)\n'
        '    - 5-min tumbling window: count txns per user_id → velocity feature\n'
        '    - 1-hour rolling window: SUM(amount) per user → amount feature\n'
        '    - Point lookup: last known location from Redis → location change\n\n'
        '  Step 3: Fraud scoring\n'
        '    - ML model (loaded in Flink job): score transaction given features\n'
        '    - Or: rule engine: IF velocity > 10 AND amount > $1000 → high risk\n\n'
        '  Step 4: Decision output\n'
        '    - Low risk: allow → write event to "fraud_scores" Kafka topic\n'
        '    - High risk: block → write to "blocked_txns" + alert fraud team\n\n'
        '  Step 5: Storage\n'
        '    - All scored transactions → Kafka → S3 Parquet (audit log)\n'
        '    - Daily batch: Spark recomputes features with full history → retrain ML model\n\n'
        '=== Key design decisions to state ===\n'
        '  1. Why Kafka? → decouples payment service from fraud service\n'
        '  2. Why Flink? → stateful streaming, low latency, exactly-once\n'
        '  3. Why Redis? → O(1) user state lookups (cannot query DW in 500ms)\n'
        '  4. Why batch layer too? → retrain ML model with corrected labels weekly'
    )
)

SD_CONTENT = '<div class="lesson-levels">' + L(1, '🟢', 'DE System Design + Back-of-Envelope Math', sd_l1) + L(2, '🔵', 'Batch ETL Architecture + CDC', sd_l2) + L(3, '🟡', 'Lambda vs Kappa Architecture', sd_l3) + L(4, '🔴', 'Real-Time Fraud Detection Design', sd_l4) + '</div>'


WEEKS4_PARTIAL3 = {
    "kafka_pub_sub": {
        "basics": KAFKA_CONTENT,
        "key_concepts": [
            "Kafka = distributed append-only commit log. Producers write, consumers read independently.",
            "Topic: named channel. Partition: ordered immutable log within a topic. Offset: position in partition.",
            "Consumer group: each partition served by exactly one consumer in the group. Max parallelism = partition count.",
            "Partition key routing: all events with the same key always go to the same partition (and same consumer).",
            "Messages NOT deleted after consumption — retained for configurable period. Multiple groups read independently.",
            "At-most-once: may lose. At-least-once: may duplicate (most common). Exactly-once: hardest, needed for finance.",
            "Consumer must be idempotent for at-least-once: INSERT ON CONFLICT DO NOTHING, or overwrite partition.",
            "Kafka vs queue: Kafka retains messages for replay. Queue deletes after consumption. Kafka supports many consumers.",
            "Windowing: tumbling (non-overlapping), sliding (overlapping), session (gap-based). Late data needs watermarks.",
        ],
        "hints": [
            "Interview: 'guarantee each message processed exactly once?' → explain at-least-once + idempotent consumer.",
            "Partition count limits parallelism: 4 partitions → max 4 consumers per group. Adding a 5th consumer idles.",
            "Use partition key = user_id when ordering per-user matters (e.g., user's event stream must be ordered).",
            "Kafka is NOT a database. Don't use it as a primary store. Consumers should always write to a real store.",
        ],
        "tasks": [
            "<strong>Step 1:</strong> Design a Kafka topic layout for an e-commerce order pipeline: what topics? How many partitions each? What partition key?",
            "<strong>Step 2:</strong> Write an idempotent consumer for an orders topic: receive order events, INSERT into PostgreSQL with ON CONFLICT DO NOTHING.",
            "<strong>Step 3:</strong> Design: multiple consumers reading the same 'orders' topic independently — analytics, fraud detection, inventory update. How many consumer groups?",
            "<strong>Step 4:</strong> Model a late-arriving event problem: events arrive 5 minutes late. You have a 1-minute tumbling window for revenue. How do you handle late data?",
        ],
        "hard_problem": "Boss Problem (LinkedIn): Design Kafka's original use case — the activity feed pipeline. Every LinkedIn user action (post, like, comment, view) is an event streamed to Kafka. (1) What topics and partitions? (2) 3 consumers need the same data: feed renderer, analytics, notifications — how many consumer groups? (3) A user with 50M followers posts — fan-out-on-write creates 50M messages. How does Kafka handle this? (4) You need to replay the last 7 days of events to rebuild the recommendation model. Are 7-day retention and 50M events/day feasible on Kafka?",
    },

    "dag_architecture": {
        "basics": DAG_CONTENT,
        "key_concepts": [
            "DAG = Directed Acyclic Graph. Nodes are tasks, edges are dependencies. Acyclic = no circular dependencies.",
            "Airflow: Python-defined DAGs. schedule_interval (cron), start_date, catchup, max_active_runs.",
            "Operator types: PythonOperator, BashOperator, SparkSubmitOperator, SqlOperator, S3ToRedshiftOperator.",
            "Sensor: waits for a condition. FileSensor, HttpSensor, S3KeySensor. Uses poke_interval to check periodically.",
            "XCom: small values passed between tasks (paths, counts, flags). Never XCom large data — use S3 path instead.",
            "catchup=False: prevents Airflow from backfilling all missed runs on restart. Almost always set this.",
            "Idempotent tasks: running twice for the same date = same result. Essential for safe retries and backfills.",
            "Dynamic DAGs: generate multiple DAGs from a config (loop in Python file). Use globals() to register.",
        ],
        "hints": [
            "catchup=True (default) can auto-run hundreds of missed historical DAG runs — almost always set catchup=False.",
            "XCom best practice: pass S3 paths, not data. The data lives in S3, the path lives in XCom.",
            "Sensor vs sleep in task: sensor releases executor slot while waiting. Sleep holds the slot — avoid it.",
            "max_active_runs=1: prevents concurrent DAG runs. Important for pipelines that write to the same partition.",
        ],
        "tasks": [
            "<strong>Step 1:</strong> Write an Airflow DAG with 3 tasks: extract (PythonOperator), transform (SparkSubmitOperator), load (PythonOperator). Set up correct dependencies.",
            "<strong>Step 2:</strong> Add a FileSensor before extract that waits for a source file to appear in S3. Set poke_interval=60 and timeout=3600.",
            "<strong>Step 3:</strong> Make the extract task push a row count to XCom. Have the validate task pull it and raise ValueError if count < 1000.",
            "<strong>Step 4:</strong> Write a dynamic DAG generator that creates one DAG per client from a JSON config file with 5 client entries. Verify all 5 DAGs appear in Airflow UI.",
        ],
        "hard_problem": "Boss Problem (Spotify): You manage a daily pipeline: 200 Airflow DAGs, each processing data for one country. DAGs run at different times (by time zone) and share downstream dependencies (a global aggregation DAG that waits for ALL 200 country DAGs to finish). (1) Design the dependency structure. (2) One country DAG fails — should the global aggregation wait or proceed with 199/200 countries? (3) A new country is added — how do you add it without rewriting code? (4) The global aggregation consistently misses its 6am SLA by 15 minutes — diagnose and fix.",
    },

    "data_quality": {
        "basics": DQ_CONTENT,
        "key_concepts": [
            "5 quality dimensions: Completeness, Uniqueness, Validity, Consistency, Timeliness.",
            "Add quality checks at: ingestion (reject bad data), transformation (assert intermediate results), output (verify before publish).",
            "dbt: write SQL SELECT → runs as table/view. Built-in tests: not_null, unique, accepted_values, relationships.",
            "Schema evolution: adding columns = safe. Removing/renaming columns = breaking. Changing types = usually breaking.",
            "Idempotency: pipeline can run multiple times for same date → same result. Critical for safe retries + backfills.",
            "Idempotent patterns: DELETE+INSERT, INSERT ON CONFLICT UPDATE, write.mode('overwrite').partitionBy().",
            "Unit testing: create small input DataFrame, run transformation, assert expected output. Use pytest + local Spark.",
            "Data governance: catalog (what exists), lineage (where it comes from), access control (who sees what).",
        ],
        "hints": [
            "dbt test types: not_null, unique (built-in), accepted_values, relationships (built-in), custom SQL assertions.",
            "Non-idempotent pipelines are the #1 cause of duplicate data bugs at scale. Always design for idempotency.",
            "Great Expectations: Python library for defining and running data validation rules (similar to dbt tests but in Python).",
            "Anomaly detection alert: if today's row count < 80% or > 120% of last 7-day average → alert. Simple and powerful.",
        ],
        "tasks": [
            "<strong>Step 1:</strong> Write 5 SQL quality checks for an orders table: NULL check, uniqueness, range validation (amount > 0), foreign key integrity, and timeliness (max order_date within last 2 hours).",
            "<strong>Step 2:</strong> Write a dbt model and schema.yml with at least 3 tests (not_null, unique, expression_is_true). Run dbt test.",
            "<strong>Step 3:</strong> Make a non-idempotent INSERT idempotent using all 3 patterns: DELETE+INSERT, ON CONFLICT, and Spark overwrite partition. Verify by running twice.",
            "<strong>Step 4:</strong> Write a pytest unit test for a Spark transformation that computes daily revenue. Include edge cases: empty input, all-NULL revenue, negative amounts.",
        ],
        "hard_problem": "Boss Problem (Airbnb): You are the data quality lead. Your nightly ETL ingests from 20 source databases across 5 countries. (1) Design a quality check framework: what checks run at each stage, who is alerted when they fail, and how do you prevent bad data from reaching BI reports? (2) A source system in Germany changes the 'price' column from EUR decimal to STRING '€X.XX' without warning. How does your system detect this? What happens to the pipeline? How do you fix it? (3) A data engineer accidentally writes non-idempotent code that ran 3 times — you now have 3x the rows for 2024-01-15 only. How do you fix production data?",
    },

    "system_design_batch_etl": {
        "basics": SD_CONTENT,
        "key_concepts": [
            "DE system design adds: volume math, latency requirements, storage formats, streaming vs batch trade-offs.",
            "Back-of-envelope: 1B events/day × 100 bytes = 100GB/day. With 5x Parquet compression = 20GB/day.",
            "Batch: simple, cheaper, hours of latency. Streaming: complex, expensive, seconds of latency.",
            "CDC: reads database transaction log (WAL). Captures INSERT/UPDATE/DELETE including hard DELETES. No source load.",
            "Lambda: batch (accurate) + streaming (fast) layers. Complex: two codebases. Used in legacy systems.",
            "Kappa: streaming only. Simpler codebase. Historical reprocessing via log replay. Winning in new systems.",
            "Fraud detection: Kafka → Flink (stateful windows) → ML scoring → Redis (block/allow) → result topic.",
            "Always justify architecture choices: 'I chose Kafka because...', 'I chose Flink over Spark SS because...'",
        ],
        "hints": [
            "Interview: always start with volume math before architecture. Shows structured engineering thinking.",
            "CDC vs polling: CDC catches DELETEs (polling cannot). CDC has zero source DB load. CDC is always preferred.",
            "Lambda vs Kappa: Lambda = two codebases (batch + streaming). Kappa = one codebase (streaming only). New systems = Kappa.",
            "Fraud detection latency budget: 500ms total = 50ms Kafka → 200ms Flink → 100ms Redis lookup → 150ms ML scoring.",
        ],
        "tasks": [
            "<strong>Step 1:</strong> Back-of-envelope: 100M daily active users, each viewing 20 pages/day, each page view is 500 bytes. Calculate: daily data volume (uncompressed + Parquet compressed), monthly storage cost at $0.023/GB-month on S3.",
            "<strong>Step 2:</strong> Design a batch ETL system for a SaaS company: daily computation of MRR (monthly recurring revenue) by plan tier and country. Draw the pipeline from OLTP to BI-ready table.",
            "<strong>Step 3:</strong> Explain CDC to a non-technical stakeholder in 3 sentences. Then explain to a technical interviewer why it is better than polling.",
            "<strong>Step 4:</strong> Mock interview: 'Design a real-time recommendation system for Netflix (movies to show on homepage, updated every 5 minutes based on viewing history).' Use the structured framework: requirements → volume math → architecture → trade-offs.",
        ],
        "hard_problem": "Boss Problem (Stripe): Design a complete data platform for Stripe's analytics needs. Requirements: (1) 100M transactions/day, real-time fraud detection within 200ms; (2) Daily financial reports (revenue by country, product, merchant type) available by 6am UTC; (3) Ad-hoc SQL queries by 200 data analysts on 5 years of historical data; (4) GDPR: delete all data for a user within 30 days of request; (5) Data catalog: any analyst can discover what tables exist and their meaning. Design: the complete architecture (streaming + batch + storage + catalog + governance), justify every component choice, and explain the failure modes.",
    },
}

print("WEEKS4_PARTIAL3 keys:", list(WEEKS4_PARTIAL3.keys()))
print("Kafka basics len:", len(WEEKS4_PARTIAL3['kafka_pub_sub']['basics']))
print("DAG basics len:", len(WEEKS4_PARTIAL3['dag_architecture']['basics']))
print("DQ basics len:", len(WEEKS4_PARTIAL3['data_quality']['basics']))
print("SD basics len:", len(WEEKS4_PARTIAL3['system_design_batch_etl']['basics']))
