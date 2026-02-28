"""
Week 4-12 Content Part 1: hash_maps (Python Logic), generators (Python Systems)
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
# TOPIC: hash_maps  (Week 4 — Python for Data Engineering)
# ═══════════════════════════════════════════════════════════════════
hm_l1 = (
    H('h4', 'Why Python Data Engineers Need These Structures') +
    P('SQL handles sets of rows. Python handles the transformations, pipelines, and logic that SQL cannot: '
      'parsing nested JSON, building lookups between datasets, deduplicating records, implementing custom aggregations, '
      'streaming transformations, and interview-style algorithmic challenges.') +
    P('Week 4 is about the Python data structures and patterns that show up constantly in data engineering '
      'interviews at FAANG — hash maps, sets, generators, sliding windows, and heaps. '
      'These are NOT just LeetCode prep. They solve real data problems every day.') +
    H('h4', 'Hash Maps (Dictionaries) — The Single Most Important Python Structure') +
    P('A hash map (Python: <code>dict</code>) stores key-value pairs and provides O(1) average case lookup. '
      'Internally, Python\'s dict uses a hash table: it hashes the key, computes an array index, '
      'and stores the value there. This means finding any key requires computing one hash function — '
      'NOT scanning 10M items. This is the fundamental property that makes hash maps so powerful.') +
    PRE(
        '# Hash map lookup time does not grow with size\n'
        'd = {}  # empty dict — takes up ~200 bytes\n'
        'for i in range(10_000_000):\n'
        '    d[i] = i * 2  # 10 million entries\n\n'
        '# This lookup is STILL O(1) — same speed as the empty dict\n'
        'print(d[9_999_999])  # instant\n\n'
        '# Compare to a list:\n'
        'lst = list(range(10_000_000))\n'
        '9_999_999 in lst  # O(n) — has to scan all 10M items\n'
        'lst.index(9_999_999)  # O(n) — same\n\n'
        '# Rule: if you find yourself doing "x in my_list" in a loop, use a set or dict instead.'
    ) +
    H('h4', 'The Three Core Hash Map Patterns in Data Engineering') +
    UL(
        '<strong>Frequency counting</strong>: count occurrences of any key in O(n)',
        '<strong>Grouping / bucketing</strong>: group rows by a key without sorting',
        '<strong>Two-pass lookup</strong>: build a lookup table in pass 1, answer queries in pass 2'
    )
)

hm_l2 = (
    H('h4', 'Pattern 1: Frequency Counting — The Counter Pattern') +
    P('<code>collections.Counter</code> is a specialized dict for counting. '
      'It is the right tool for any "how many times does X appear?" question.') +
    PRE(
        'from collections import Counter\n\n'
        '# Raw data: a stream of user events\n'
        'events = ["click","scroll","click","purchase","click","scroll","purchase"]\n\n'
        '# Count frequencies in O(n)\n'
        'freq = Counter(events)\n'
        '# Counter({"click": 3, "scroll": 2, "purchase": 2})\n\n'
        '# Most common events\n'
        'top_3 = freq.most_common(3)  # [("click",3), ("scroll",2), ("purchase",2)]\n\n'
        '# In data engineering: count most frequent API error codes\n'
        'error_logs = ["404","500","404","503","404","500","404"]\n'
        'error_counts = Counter(error_logs)\n'
        'print(error_counts.most_common(2))  # [(\'404\', 4), (\'500\', 2)]\n\n'
        '# Interview pattern: does any value appear more than N/2 times?\n'
        'def majority_element(nums):\n'
        '    c = Counter(nums)\n'
        '    return max(c, key=c.get)  # element with highest count'
    ) +
    H('h4', 'Pattern 2: Grouping — defaultdict') +
    PRE(
        'from collections import defaultdict\n\n'
        '# Group transactions by customer_id\n'
        'transactions = [\n'
        '    {"cust": 42, "amount": 100},\n'
        '    {"cust": 55, "amount": 200},\n'
        '    {"cust": 42, "amount": 50},\n'
        ']\n\n'
        'by_customer = defaultdict(list)  # default value is an empty list\n'
        'for txn in transactions:\n'
        '    by_customer[txn["cust"]].append(txn["amount"])\n\n'
        '# Result: {42: [100, 50], 55: [200]}\n\n'
        '# Now compute per-customer totals in O(n) total:\n'
        'totals = {cust: sum(amounts) for cust, amounts in by_customer.items()}'
    ) +
    H('h4', 'Pattern 3: Two-Pass Lookup — Find Complement') +
    PRE(
        '# Classic interview: Two Sum — find pair that sums to target\n'
        '# Brute force: O(n^2) — check every pair\n'
        '# Hash map approach: O(n) — one pass\n\n'
        'def two_sum(nums, target):\n'
        '    seen = {}  # value → index\n'
        '    for i, num in enumerate(nums):\n'
        '        complement = target - num\n'
        '        if complement in seen:   # O(1) lookup!\n'
        '            return [seen[complement], i]\n'
        '        seen[num] = i\n'
        '    return []\n\n'
        '# Data engineering version: join two datasets in memory\n'
        '# (when SQL JOIN is not available, e.g. in a Python streaming pipeline)\n'
        'def hash_join(left_rows, right_rows):\n'
        '    # Pass 1: build lookup from right table\n'
        '    lookup = {row["id"]: row for row in right_rows}  # O(n)\n\n'
        '    # Pass 2: look up each left row in O(1)\n'
        '    for left in left_rows:  # O(m)\n'
        '        right = lookup.get(left["right_id"])\n'
        '        if right:\n'
        '            yield {**left, **right}  # merged row\n'
        '    # Total: O(n + m) instead of O(n * m)'
    )
)

hm_l3 = (
    H('h4', 'Sets — O(1) Membership and Deduplication') +
    P('A Python <code>set</code> is essentially a dict with only keys (no values). '
      'It provides O(1) membership testing and deduplication. '
      'In data engineering: dedup large record streams, compute intersection/difference of ID lists.') +
    PRE(
        '# Deduplication — preserve only unique records\n'
        'user_ids = [1, 2, 3, 2, 4, 1, 5, 3]\n'
        'unique_ids = list(set(user_ids))  # [1, 2, 3, 4, 5] — order not preserved!\n\n'
        '# If order matters: use dict.fromkeys()\n'
        'unique_ordered = list(dict.fromkeys(user_ids))  # [1, 2, 3, 4, 5] — order preserved\n\n'
        '# Set operations for data reconciliation:\n'
        'db_users = {1, 2, 3, 4, 5}\n'
        'app_users = {3, 4, 5, 6, 7}\n\n'
        'only_in_db  = db_users - app_users   # {1, 2}    — in DB but not app\n'
        'only_in_app = app_users - db_users   # {6, 7}    — in app but not DB\n'
        'in_both     = db_users & app_users   # {3, 4, 5} — intersection\n'
        'in_either   = db_users | app_users   # {1,2,3,4,5,6,7} — union\n\n'
        '# DE use case: find orders with no matching customer (data quality check)\n'
        'order_customer_ids = {o["cust_id"] for o in orders}\n'
        'customer_ids       = {c["id"] for c in customers}\n'
        'orphan_orders = order_customer_ids - customer_ids  # cust IDs with no record'
    ) +
    H('h4', 'Sliding Window — Fixed and Variable Width') +
    P('Sliding window is NOT a data structure — it\'s an algorithmic technique. '
      'Instead of computing an aggregate for every possible window from scratch (O(n×k)), '
      'you maintain a running state as the window slides, re-using previous computation: O(n).') +
    PRE(
        '# Fixed window: 3-day rolling sum\n'
        'def rolling_sum(values, k):\n'
        '    window_sum = sum(values[:k])  # compute first window\n'
        '    results = [window_sum]\n'
        '    for i in range(k, len(values)):\n'
        '        window_sum += values[i]       # add new element\n'
        '        window_sum -= values[i - k]   # remove oldest element\n'
        '        results.append(window_sum)\n'
        '    return results\n\n'
        '# Variable window: longest subarray with sum <= budget\n'
        'def longest_under_budget(costs, budget):\n'
        '    left = 0\n'
        '    current_sum = 0\n'
        '    max_len = 0\n'
        '    for right in range(len(costs)):\n'
        '        current_sum += costs[right]\n'
        '        while current_sum > budget:   # shrink window from left\n'
        '            current_sum -= costs[left]\n'
        '            left += 1\n'
        '        max_len = max(max_len, right - left + 1)\n'
        '    return max_len'
    )
)

hm_l4 = (
    H('h4', 'Heaps — Priority Queues for Streaming Top-K') +
    P('A <strong>heap</strong> (Python: <code>heapq</code>) is a binary tree that always keeps '
      'the smallest element at the root. It provides O(log n) insert and O(log n) extract-min. '
      'This makes it ideal for "top K" problems in streaming data — '
      'maintain a heap of exactly K items, each incoming item either replaces the smallest or is discarded.') +
    PRE(
        'import heapq\n\n'
        '# Find top-3 highest-revenue customers from a stream of millions\n'
        '# No need to sort 10M records — O(n log k) with k=3\n'
        'def top_k_customers(stream, k):\n'
        '    heap = []  # min-heap of (revenue, cust_id)\n'
        '    for cust_id, revenue in stream:\n'
        '        heapq.heappush(heap, (revenue, cust_id))  # add to heap\n'
        '        if len(heap) > k:\n'
        '            heapq.heappop(heap)  # remove smallest — keeps top K\n'
        '    return sorted(heap, reverse=True)  # highest first\n\n'
        '# heapq.nlargest is the Pythonic version:\n'
        'top_3 = heapq.nlargest(3, stream, key=lambda x: x[1])\n\n'
        '# Merge K sorted streams (very common in data engineering)\n'
        '# e.g., merge sorted log files from 10 servers\n'
        'def merge_k_sorted(sorted_streams):\n'
        '    heap = []\n'
        '    iterators = [iter(s) for s in sorted_streams]\n'
        '    for i, it in enumerate(iterators):\n'
        '        val = next(it, None)\n'
        '        if val is not None:\n'
        '            heapq.heappush(heap, (val, i))  # (value, stream_index)\n'
        '    while heap:\n'
        '        val, i = heapq.heappop(heap)\n'
        '        yield val\n'
        '        nxt = next(iterators[i], None)\n'
        '        if nxt is not None:\n'
        '            heapq.heappush(heap, (nxt, i))'
    ) +
    P('<strong>Complexity cheat sheet for FAANG interviews:</strong>') +
    TABLE([
        ['Structure', 'Insert', 'Lookup', 'Delete', 'Best for'],
        ['dict', 'O(1)', 'O(1)', 'O(1)', 'Counting, grouping, two-pointer complement'],
        ['set', 'O(1)', 'O(1)', 'O(1)', 'Dedup, membership, set math'],
        ['list', 'O(1) append', 'O(n)', 'O(n)', 'Ordered sequence, indexed access'],
        ['heapq', 'O(log n)', 'O(1) min', 'O(log n)', 'Top-K, streaming priority'],
        ['deque', 'O(1) both ends', 'O(n)', 'O(1) ends', 'Sliding window, BFS queue'],
    ])
)

HM_CONTENT = '<div class="lesson-levels">' + L(1, '🟢', 'Why These Structures Matter in DE', hm_l1) + L(2, '🔵', 'Hash Map Patterns — Counter, Group, Join', hm_l2) + L(3, '🟡', 'Sets + Sliding Window Technique', hm_l3) + L(4, '🔴', 'Heaps + Complexity Cheat Sheet', hm_l4) + '</div>'


# ═══════════════════════════════════════════════════════════════════
# TOPIC: generators  (Week 5 — Python Systems)
# ═══════════════════════════════════════════════════════════════════
gen_l1 = (
    H('h4', 'The Memory Problem — Why Generators Exist') +
    P('Imagine you need to process a 100GB log file. The naive approach: '
      '<code>lines = open("log.txt").readlines()</code>. This reads all 100GB into RAM at once. '
      'If you only have 8GB of RAM, your process crashes. Even if it doesn\'t crash, '
      'you\'ve consumed 100GB of memory for a computation that might only need 100MB at any one time.') +
    P('This is the fundamental problem generators solve: <strong>lazy evaluation</strong>. '
      'Instead of computing all values upfront and storing them in memory, '
      'a generator computes the NEXT value only when asked. '
      'It uses O(1) memory regardless of the total sequence size.') +
    H('h4', 'Generator Functions — The yield Keyword') +
    PRE(
        '# Regular function: returns a list (loads everything into memory)\n'
        'def read_all_lines(filename):\n'
        '    return open(filename).readlines()  # 100GB in RAM if large file!\n\n'
        '# Generator function: yields one line at a time (O(1) memory)\n'
        'def stream_lines(filename):\n'
        '    with open(filename) as f:\n'
        '        for line in f:          # f iterates line by line — OS handles this\n'
        '            yield line.strip()  # pause here, return line, resume on next()\n\n'
        '# Usage: process 100GB file with 8GB RAM — works perfectly\n'
        'for line in stream_lines("huge_log.txt"):\n'
        '    process(line)  # only one line lives in memory at any time\n\n'
        '# A generator is a function that remembers WHERE IT WAS in execution.\n'
        '# "yield" means: return this value, pause here, resume from here next time.'
    ) +
    H('h4', 'Generator Expressions — The Lazy List Comprehension') +
    PRE(
        '# List comprehension: creates all values in memory immediately\n'
        'squares_list = [x**2 for x in range(10_000_000)]   # 80MB in memory\n\n'
        '# Generator expression: creates values on demand, same syntax with ()\n'
        'squares_gen  = (x**2 for x in range(10_000_000))    # tiny (generator object)\n\n'
        '# Both work identically in a for loop:\n'
        'total = sum(x**2 for x in range(10_000_000))  # never stores all 10M values!\n\n'
        '# Rule for data engineering: use generator expression whenever you will\n'
        '# iterate through results ONCE (sum, filter, write to file, stream out).\n'
        '# Use list when you need to: index into results, iterate multiple times, or check len().'
    )
)

gen_l2 = (
    H('h4', 'Real-World DE Pattern: ETL Pipeline with Generators') +
    P('The most powerful use of generators in data engineering: chaining them into a pipeline. '
      'Each stage of the ETL is a generator that reads from the previous stage. '
      'The entire pipeline runs with O(1) memory — data flows through one record at a time.') +
    PRE(
        '# ETL Pipeline: read → parse → filter → transform → write\n'
        '# Each function is a generator. Data flows record-by-record.\n\n'
        'def read_csv(filepath):\n'
        '    """Stage 1: Read file line by line."""\n'
        '    with open(filepath) as f:\n'
        '        next(f)  # skip header\n'
        '        for line in f:\n'
        '            yield line.strip()\n\n'
        'def parse_rows(lines):\n'
        '    """Stage 2: Parse CSV text into dicts."""\n'
        '    for line in lines:  # lines is itself a generator!\n'
        '        parts = line.split(",")\n'
        '        yield {"user_id": parts[0], "amount": float(parts[1]), "date": parts[2]}\n\n'
        'def filter_active(rows):\n'
        '    """Stage 3: Keep only recent rows."""\n'
        '    cutoff = "2024-01-01"\n'
        '    for row in rows:\n'
        '        if row["date"] >= cutoff:\n'
        '            yield row\n\n'
        'def enrich(rows, lookup):\n'
        '    """Stage 4: Add metadata from lookup table."""\n'
        '    for row in rows:\n'
        '        row["region"] = lookup.get(row["user_id"], "unknown")\n'
        '        yield row\n\n'
        '# Chain: data flows through all stages lazily, one record at a time\n'
        'lookup = build_region_lookup()  # a dict — O(m) memory\n'
        'pipeline = enrich(\n'
        '    filter_active(\n'
        '        parse_rows(\n'
        '            read_csv("events.csv")  # 10GB file\n'
        '        )\n'
        '    ),\n'
        '    lookup\n'
        ')\n\n'
        'for record in pipeline:  # triggers execution — pulls one record at a time\n'
        '    write_to_warehouse(record)\n'
        '# Total memory: O(1) for the pipeline + O(m) for the lookup dict'
    )
)

gen_l3 = (
    H('h4', 'Decorators — Functions That Wrap Functions') +
    P('A <strong>decorator</strong> is a function that takes another function as input, '
      'wraps it with additional behavior, and returns the wrapped version. '
      'The <code>@</code> syntax is shorthand for <code>func = decorator(func)</code>.') +
    P('In data engineering: decorators handle retry logic, caching, metrics, logging, '
      'and access control — without cluttering the core business logic.') +
    PRE(
        'import time\nimport functools\n\n'
        '# Decorator: retry an operation up to N times on failure\n'
        'def retry(max_attempts=3, delay=1.0):\n'
        '    def decorator(func):\n'
        '        @functools.wraps(func)  # preserve original function metadata\n'
        '        def wrapper(*args, **kwargs):\n'
        '            for attempt in range(1, max_attempts + 1):\n'
        '                try:\n'
        '                    return func(*args, **kwargs)\n'
        '                except Exception as e:\n'
        '                    if attempt == max_attempts:\n'
        '                        raise  # re-raise on final attempt\n'
        '                    print(f"Attempt {attempt} failed: {e}. Retrying...")\n'
        '                    time.sleep(delay)\n'
        '        return wrapper\n'
        '    return decorator\n\n'
        '# Usage: apply retry behavior to any function with one line\n'
        '@retry(max_attempts=5, delay=2.0)\n'
        'def fetch_from_api(endpoint):\n'
        '    """Fetches data from a flaky external API."""\n'
        '    response = requests.get(endpoint)\n'
        '    response.raise_for_status()\n'
        '    return response.json()\n\n'
        '# Equivalent to: fetch_from_api = retry(5, 2.0)(fetch_from_api)'
    ) +
    H('h4', 'Context Managers — Guaranteed Resource Cleanup') +
    PRE(
        '# Context manager: database connection that always closes\n'
        'from contextlib import contextmanager\n\n'
        '@contextmanager\n'
        'def db_connection(conn_string):\n'
        '    conn = create_connection(conn_string)\n'
        '    try:\n'
        '        yield conn          # caller gets the connection here\n'
        '    finally:\n'
        '        conn.close()        # ALWAYS runs, even if exception occurs\n\n'
        '# Usage: connection guaranteed to close even on exception\n'
        'with db_connection("postgresql://...") as conn:\n'
        '    conn.execute("INSERT ...")'
    )
)

gen_l4 = (
    H('h4', 'Memory Profiling and Optimization Strategies') +
    P('In production data engineering, understanding memory at a deep level prevents outages. '
      'The three main memory killers in Python DE pipelines:') +
    UL(
        '<strong>Loading entire files/datasets into lists</strong>: Replace with generators + streaming',
        '<strong>Multiple copies of the same string</strong>: Python interns short strings but not long ones — use string interning or category dtypes in Pandas',
        '<strong>DataFrames with wrong dtypes</strong>: a DataFrame with int64 columns that hold values 0-100 uses 8x more memory than int8'
    ) +
    PRE(
        '# Memory profiling with memory_profiler\n'
        '# pip install memory-profiler\n'
        'from memory_profiler import profile\n\n'
        '@profile\n'
        'def load_and_process():\n'
        '    data = pd.read_csv("large.csv")     # baseline memory\n'
        '    # LINE 1: 2.0 GiB\n'
        '    data = optimize_dtypes(data)         # shrink dtypes\n'
        '    # LINE 2: 0.5 GiB — 75% reduction!\n'
        '    return data\n\n'
        '# Dtype optimization:\n'
        'def optimize_dtypes(df):\n'
        '    for col in df.select_dtypes("int64").columns:\n'
        '        df[col] = pd.to_numeric(df[col], downcast="integer")\n'
        '    for col in df.select_dtypes("float64").columns:\n'
        '        df[col] = pd.to_numeric(df[col], downcast="float")\n'
        '    for col in df.select_dtypes("object").columns:\n'
        '        if df[col].nunique() / len(df) < 0.5:  # <50% unique → category\n'
        '            df[col] = df[col].astype("category")\n'
        '    return df\n\n'
        '# Processing chunks: alternative to generators for files too large for memory\n'
        'for chunk in pd.read_csv("huge.csv", chunksize=100_000):\n'
        '    process(chunk)  # process 100K rows at a time'
    ) +
    P('<strong>FAANG interview question:</strong> "Your pipeline processes 500GB of logs daily. '
      'Memory on your EC2 instance is 32GB. Walk me through how you would process this." '
      'Correct answer: generators + chunked reading + streaming writes, never load the full dataset simultaneously.')
)

GEN_CONTENT = '<div class="lesson-levels">' + L(1, '🟢', 'Generators — The Memory Problem', gen_l1) + L(2, '🔵', 'ETL Pipeline with Generator Chaining', gen_l2) + L(3, '🟡', 'Decorators + Context Managers', gen_l3) + L(4, '🔴', 'Memory Profiling + 500GB Pipeline', gen_l4) + '</div>'


WEEKS4_PARTIAL = {
    "hash_maps": {
        "basics": HM_CONTENT,
        "key_concepts": [
            "dict provides O(1) average insert, lookup, delete. Uses hash table internally.",
            "Counter: frequency counting in O(n). most_common(k) returns top-k elements.",
            "defaultdict: auto-initializes missing keys — ideal for grouping records by key.",
            "Two-pass hash join: build lookup dict in O(n), query in O(m). Total O(n+m) vs O(n*m) nested loop.",
            "set: O(1) membership. Supports union | , intersection &, difference -. Use for dedup + set math.",
            "dict.fromkeys(list): deduplicate while preserving insertion order (unlike set()).",
            "Sliding window: maintain running state instead of recomputing from scratch. O(n) vs O(n*k).",
            "heapq: min-heap. Push/pop in O(log n). Use for top-K streaming, merge K sorted sequences.",
        ],
        "hints": [
            "Seeing 'x in my_list' inside a loop? That's O(n²). Convert to set first: O(n) total.",
            "Counter(iterable) counts in one line. Combine two counters: c1 + c2 adds counts, c1 & c2 keeps minimums.",
            "heapq is a MIN-heap. For max-heap: store values as negatives (-val, key) then negate on extraction.",
            "Sliding window: two-pointer left/right. Move right always; move left only when constraint violated.",
        ],
        "tasks": [
            "<strong>Step 1:</strong> Given a list of 1M user_ids with duplicates, find the top-5 most frequent users using Counter. Then dedup the list preserving order using dict.fromkeys().",
            "<strong>Step 2:</strong> Implement a hash join: two lists of dicts (orders and customers) sharing a customer_id field. Merge them in O(n+m) using a dict lookup.",
            "<strong>Step 3:</strong> Sliding window: find the max sum of any 3 consecutive days from 365 daily revenue values. Implement in O(n) — no nested loop.",
            "<strong>Step 4:</strong> Top-K streaming: simulate a stream of (user_id, purchase_amount) tuples. Find the top-10 spenders using heapq without storing the entire stream in memory.",
        ],
        "hard_problem": "Boss Problem (Google): You receive a stream of (user_id, search_query, timestamp) events, 100M events/day. (1) Find the top-100 most searched queries in the last 24 hours — you cannot load all 100M events into RAM. Use a heap + streaming approach. (2) Find all users who searched for the same query more than 5 times — are they bots? Use Counter + filter. (3) Find all pairs of users who searched for the SAME rare query (appears < 10 times globally). How do you efficiently match pairs? (4) Time complexity analysis: what is the big-O of each part?",
    },

    "generators": {
        "basics": GEN_CONTENT,
        "key_concepts": [
            "Generator function: uses 'yield' to pause/resume. Returns a generator object, not a list.",
            "Generator uses O(1) memory: it never holds all values at once — computes next value on demand.",
            "Generator expression: (expr for x in iterable) — identical syntax to list comp but lazy.",
            "Pipeline chaining: each ETL stage is a generator reading from the previous. Data flows one record at a time.",
            "Decorator: higher-order function that wraps another. '@retry' adds retry logic without changing core code.",
            "@functools.wraps preserves function name/docstring when writing decorators.",
            "Context manager: 'with' block guarantees cleanup (finally) even on exceptions.",
            "Memory optimization: dtype downcast (int64→int8), category dtype for low-cardinality strings.",
        ],
        "hints": [
            "Can you iterate through results with a single for loop? → use generator (saves memory).",
            "Need to index into results, get len(), or iterate multiple times? → convert to list first.",
            "Chunked pandas: pd.read_csv('file.csv', chunksize=100_000) processes file in chunks without full load.",
            "Generators are lazy — they do NOTHING until iterated. Chaining generators costs zero compute up front.",
        ],
        "tasks": [
            "<strong>Step 1:</strong> Write a generator that reads a CSV file line by line and yields parsed dict rows. Compare memory usage vs reading the full file into a list.",
            "<strong>Step 2:</strong> Build a 3-stage generator pipeline: read → filter (only rows where amount > 100) → transform (add a 'revenue_tier' field). Process a 1M-row file.",
            "<strong>Step 3:</strong> Write a @retry(max_attempts=3, delay=1) decorator. Apply it to a function that simulates random network failures. Verify it retries correctly.",
            "<strong>Step 4:</strong> Write optimize_dtypes(df). Apply it to a DataFrame with int64 and object columns. Report memory usage before and after with df.memory_usage(deep=True).sum().",
        ],
        "hard_problem": "Boss Problem (Netflix): Your nightly ETL reads from an S3 bucket containing 50,000 gzipped JSON files (total ~500GB uncompressed). Each file has user viewing events. (1) Write a generator pipeline: stream S3 object list → download each file → gunzip → parse JSON lines → filter by date → yield events. The pipeline should use <2GB RAM regardless of total file count. (2) For each event, do a dict lookup against a 20M-row user metadata table loaded in RAM. What is the maximum size this lookup dict can be? (3) If processing takes 14 hours, how do you parallelize using multiprocessing.Pool while keeping memory bounded?",
    },
}

print("WEEKS4_PARTIAL keys:", list(WEEKS4_PARTIAL.keys()))
print("HM basics len:", len(WEEKS4_PARTIAL['hash_maps']['basics']))
print("GEN basics len:", len(WEEKS4_PARTIAL['generators']['basics']))
