import json, random, sys
sys.path.insert(0, '.')

from kb_week1 import WEEK1
from kb_week2 import WEEK2
from kb_week3 import WEEK3
from kb_weeks4to12 import WEEKS4_TO_7
from kb_week13 import WEEK13

# ─── Merge all KB dicts ───────────────────────────────
KB = {}
KB.update(WEEK1)
KB.update(WEEK2)
KB.update(WEEK3)
KB.update(WEEKS4_TO_7)
KB.update(WEEK13)

# ─── Topic → KB key mapping ───────────────────────────
TOPIC_MAP = {
    # Week 1 – SQL Analytics
    "window function basics":   "window_function_basics",
    "rolling windows":          "rolling_windows",
    "lead/lag pattern":         "lead_lag",
    "gaps & islands (logic)":   "gaps_islands_logic",
    "gaps & islands (complex)": "gaps_islands_complex",
    "rest & review":            "rest_review",
    # Week 2 – SQL Optimization
    "recursive ctes":           "recursive_ctes",
    "execution plans":          "query_optimization",
    "query optimization":       "query_optimization",
    "indexing strategies":      "indexing",
    "indexing":                 "indexing",
    "joins deep dive":          "complex_joins_nulls",
    "complex joins & nulls":    "complex_joins_nulls",
    "null handling":            "complex_joins_nulls",
    "performance review":       "performance_review",
    # Week 3 – Data Modeling
    "dimensional modeling basics": "dimensional_modeling",
    "dimensional modeling":        "dimensional_modeling",
    "scd types (1, 2, 3)":         "slowly_changing_dimensions",
    "slowly changing dimensions":   "slowly_changing_dimensions",
    "scd type 2":                   "slowly_changing_dimensions",
    "normalization":                "normalization",
    "fact tables":                  "dimensional_modeling",
    "dimension tables":             "dimensional_modeling",
    "surrogate keys":               "dimensional_modeling",
    "nosql patterns":               "nosql_patterns",
    "nosql modeling":               "nosql_patterns",
    "schema design interview":      "schema_design_interview",
    "mock design round":            "schema_design_interview",
    "case study: social media":     "schema_design_interview",
    # Week 4 – Python Logic
    "hash maps (dicts)":        "hash_maps",
    "sets & deduplication":     "hash_maps",
    "sliding window":           "hash_maps",
    "heaps / priority queues":  "hash_maps",
    "string manipulation":      "hash_maps",
    # Week 5 – Python Systems
    "generators":               "generators",
    "recursive parsing":        "generators",
    "file i/o":                 "generators",
    "memory management":        "generators",
    "decorators":               "generators",
    # Week 6 – Storage
    "row vs columnar":          "row_vs_columnar",
    "compression":              "row_vs_columnar",
    "s3 partitioning":          "row_vs_columnar",
    "small file problem":       "row_vs_columnar",
    "data formats":             "row_vs_columnar",
    "delta lake / iceberg":     "row_vs_columnar",
    # Week 7 – Spark
    "logical plan":             "spark_logical_plan",
    "the shuffle":              "spark_logical_plan",
    "partitions vs tasks":      "spark_logical_plan",
    "broadcasting":             "spark_logical_plan",
    "handling skew":            "spark_logical_plan",
    # Week 9 – Quality
    "data quality":             "data_quality",
    "idempotency":              "data_quality",
    "schema evolution":         "data_quality",
    "unit testing":             "data_quality",
    "governance":               "data_quality",
    "dbt intro + mock #2":      "data_quality",
    # Week 10 – Orchestration
    "dag architecture":         "dag_architecture",
    "operators & sensors":      "dag_architecture",
    "xcoms":                    "dag_architecture",
    "backfilling":              "dag_architecture",
    "dynamic dags":             "dag_architecture",
    # Week 11 – Streaming
    "pub/sub model":            "kafka_pub_sub",
    "kafka internals":          "kafka_pub_sub",
    "consumer groups":          "kafka_pub_sub",
    "semantics":                "kafka_pub_sub",
    "windowing":                "kafka_pub_sub",
    "deep dive":                "kafka_pub_sub",
    # Week 12 – System Design
    "back-of-envelope math":    "system_design_batch_etl",
    "pattern: batch etl":       "system_design_batch_etl",
    "pattern: streaming":       "kafka_pub_sub",
    "pattern: cdc":             "system_design_batch_etl",
    "trade-offs":               "system_design_batch_etl",
    # Week 13 – Behavioral
    "story mining":             "star_method",
    "star method":              "star_method",
    "conflict & failure":       "star_method",
    "resume walkthrough":       "mental_prep",
    "mock interview":           "mental_prep",
    "mental prep":              "mental_prep",
    "ready":                    "ready",
    # Generic catch-alls
    "mock assessment":          "window_function_basics",
    "mock assessment + mock #1":  "spark_logical_plan",
    "mock design + cloud de":     "dag_architecture",
    "full mock design + mock #3": "system_design_batch_etl",
    "lab day":                  "spark_logical_plan",
    "lab + resume polish":      "dag_architecture",
}

GENERIC = {
    "basics": """<div class="lesson-levels">
<div class="level level-1"><div class="level-badge">🟢 Level 1 — The Concept</div><div class="rich">
<h4>What Is {topic}?</h4>
<p>Data Engineering at FAANG scale requires mastering <strong>{topic}</strong> from first principles. Before writing any code, understand: <em>what problem does this solve? Why does it exist?</em></p>
<p>Think of it like this: every tool in data engineering exists because someone hit a real-world scaling or correctness problem. Understanding <strong>the problem</strong> first makes the solution obvious.</p>
<h4>The Core Questions to Answer</h4>
<ul>
  <li>What problem does {topic} solve that simpler approaches can't?</li>
  <li>What are the 2-3 most important properties or guarantees it provides?</li>
  <li>Where does it fit in a typical DE pipeline?</li>
</ul>
</div></div>
<div class="level level-2"><div class="level-badge">🔵 Level 2 — First Example</div><div class="rich">
<h4>Hello World: {topic}</h4>
<p>Start with the simplest possible working example. No optimization yet — just get it working and understand the output.</p>
<pre># Start here: implement the most basic version of {topic}
# Then run it, verify the output, and understand each line.
# Only then move to Level 3 complexity.</pre>
<h4>Key Syntax to Know</h4>
<ul>
  <li>The most common command or pattern for {topic}</li>
  <li>The most important configuration parameter</li>
  <li>How to verify it's working correctly</li>
</ul>
</div></div>
<div class="level level-3"><div class="level-badge">🟡 Level 3 — Real-World Application</div><div class="rich">
<h4>Production-Grade {topic}</h4>
<p>At scale, {topic} requires understanding tradeoffs: what breaks at 10× load? What's the failure mode?</p>
<h4>Critical Tradeoffs</h4>
<ul>
  <li><strong>Speed vs Correctness:</strong> Can you sacrifice some accuracy for throughput?</li>
  <li><strong>Memory vs CPU:</strong> What's the bottleneck at 100M rows?</li>
  <li><strong>Complexity vs Simplicity:</strong> Is the advanced approach worth it at your scale?</li>
</ul>
<pre># Real-world pattern:
# Step 1: Validate input data quality
# Step 2: Process in batches (not all at once → OOM risk)
# Step 3: Handle failures gracefully (retry, DLQ)
# Step 4: Emit metrics for observability</pre>
</div></div>
<div class="level level-4"><div class="level-badge">🔴 Level 4 — FAANG Scale</div><div class="rich">
<h4>FAANG Production Patterns for {topic}</h4>
<ul>
  <li><strong>Scale:</strong> What breaks at 1 billion rows? What does your solution handle at that scale?</li>
  <li><strong>Reliability:</strong> Is your implementation idempotent? What's your retry strategy?</li>
  <li><strong>Observability:</strong> Structured logs, row-count metrics, p99 latency SLO, error rate alerts</li>
  <li><strong>Cost:</strong> Estimate storage and compute cost — FAANG engineers always think about $$$</li>
</ul>
<pre># FAANG interview answer template:
# "My approach for {topic}:
# 1. For correctness: [describe your idempotency/consistency strategy]
# 2. For scale: [describe distributed/partitioned approach]
# 3. For reliability: [describe retry logic and failure handling]
# 4. For monitoring: [describe metrics and alerting]"
</pre>
</div></div>
</div>""",
    "key_concepts": [
        "{topic}: understand the core abstraction before memorizing syntax.",
        "Scalability: what breaks at 10× load — CPU, memory, network, or disk?",
        "Idempotency: a pipeline run twice must produce the same result as run once.",
        "Observability: metrics, structured logs, and SLOs before shipping to production.",
        "Tradeoffs: every design choice sacrifices something — name both sides explicitly.",
        "Failure recovery: retries, DLQs, circuit breakers, and partial failure handling.",
        "Cost: estimate storage and compute cost for the expected data volume."
    ],
    "hints": [
        "Clarify the scale: how many rows? How many events/second? What's the target latency?",
        "Start with the simplest correct solution, then optimize — avoid premature optimization.",
        "Mention the failure scenario even if the interviewer doesn't ask — it signals production experience.",
        "Name the specific technology you'd use (Spark, Kafka, Airflow) and justify the choice."
    ],
    "tasks": [
        "<strong>Step 1:</strong> Define the problem in one sentence and identify the primary constraint (throughput? latency? cost?).",
        "<strong>Step 2:</strong> Sketch the architecture — source, processing, storage, serving.",
        "<strong>Step 3:</strong> Identify 3 failure modes and describe how you handle each.",
        "<strong>Step 4:</strong> Estimate the data volume and compute requirements using back-of-envelope math."
    ],
    "hard_problem": "Boss Problem: Design a complete production-ready system for {topic} that handles 100M events/day. Include architecture, technology choices with justifications, idempotency strategy, monitoring, and a cost estimate."
}

REST_REVIEW = {
    "basics": """<div class="lesson">
<h3>☀️ Rest & Review — Active Consolidation Day</h3>
<p>Today is strategic rest. Research on spaced repetition shows that consolidation during rest produces significantly better long-term retention than continuous studying. Use this day with intention.</p>
<h4>Active Review Protocol</h4>
<ul>
  <li><strong>Flashcards (20 min):</strong> Cover your notes and answer key questions aloud from memory.</li>
  <li><strong>Error review (20 min):</strong> Revisit the hardest problem from this week — attempt it again from scratch.</li>
  <li><strong>Concept map (20 min):</strong> Draw the week's topics as a visual relationship map.</li>
  <li><strong>Preview (15 min):</strong> Skim next week's Monday topic to prime your brain for new concepts.</li>
</ul>
<h4>The Testing Effect</h4>
<p>Retrieval practice (trying to recall) is 3× more effective than re-reading. Close your notes and answer: What are the 3 most important concepts from this week? What would break if you got them wrong in an interview?</p>
</div>""",
    "key_concepts": [
        "Spaced repetition: reviewing at intervals beats massed practice for long-term retention.",
        "Active recall beats passive re-reading — always try to retrieve before looking up.",
        "Error analysis: the problems you got wrong are the highest-value review items.",
        "Teaching effect: explaining a concept to someone else reveals exactly what you don't understand.",
        "Preview priming: reading next week's topic tonight improves retention when you study it in depth.",
        "Sleep consolidation: the brain replays learned material during deep sleep — protect your sleep.",
        "Stress management: chronic stress impairs working memory and problem-solving — rest is productive."
    ],
    "hints": [
        "Write out the hardest concept from this week in your own words — without looking at notes.",
        "Try one new LeetCode problem related to this week's theme — but just one.",
        "Connect this week's topics to topics from previous weeks — build the mental graph.",
        "Push your notes and code to GitHub — future you will thank present you."
    ],
    "tasks": [
        "<strong>Active recall:</strong> Write the most important pattern from this week from memory.",
        "<strong>Re-attempt:</strong> Take the hardest problem from this week and solve it again without hints.",
        "<strong>Concept map:</strong> Draw all this week's topics and how they connect.",
        "<strong>Preview:</strong> Read next Monday's topic for 15 minutes."
    ],
    "hard_problem": "Connect-the-dots challenge: Write one paragraph explaining how THIS week's topic connects to what you learned in the previous week. How would you use both together in a real system design interview?"
}

def get_kb(topic, theme):
    key = topic.lower().strip()
    kb_key = TOPIC_MAP.get(key)
    if kb_key and kb_key in KB:
        return KB[kb_key]
    # Partial match
    for k, v in TOPIC_MAP.items():
        if k in key or key in k:
            if v in KB:
                return KB[v]
    # Theme-based fallback
    theme_lower = theme.lower()
    if 'rest' in theme_lower:
        return REST_REVIEW
    if 'behavioral' in theme_lower:
        return KB.get('star_method', GENERIC)
    if 'streaming' in theme_lower or 'kafka' in theme_lower:
        return KB.get('kafka_pub_sub', GENERIC)
    if 'spark' in theme_lower:
        return KB.get('spark_logical_plan', GENERIC)
    if 'orchestration' in theme_lower or 'airflow' in theme_lower:
        return KB.get('dag_architecture', GENERIC)
    if 'storage' in theme_lower:
        return KB.get('row_vs_columnar', GENERIC)
    if 'quality' in theme_lower or 'contract' in theme_lower:
        return KB.get('data_quality', GENERIC)
    if 'modeling' in theme_lower:
        return KB.get('dimensional_modeling', GENERIC)
    if 'system design' in theme_lower:
        return KB.get('system_design_batch_etl', GENERIC)
    return GENERIC

def load_data(fp):
    with open(fp, encoding='utf-8') as f: return json.load(f)

def save_data(data, fp):
    with open(fp, 'w', encoding='utf-8') as f: json.dump(data, f, indent=4)
    with open('data.js', 'w', encoding='utf-8') as f:
        f.write('const studyDataFromJS = ' + json.dumps(data) + ';')

def enrich_data():
    data = load_data('clean_data.json')
    past_topics, enriched = [], []

    for day in data:
        topic  = day.get('SpecificTopic', 'Data Engineering')
        action = day.get('ActionItem_Deliverable', '')
        theme  = day.get('Theme', '')

        warmup = ("No previous topics yet — focus on today's core concepts!"
                  if not past_topics
                  else f"<strong>⚡ Warm-Up Review:</strong> Explain <em>{random.choice(past_topics)}</em> — describe its biggest performance tradeoff in 3 sentences, from memory, without notes.")
        if topic not in past_topics and topic.lower() not in ('rest & review', 'ready'):
            past_topics.append(topic)

        base = get_kb(topic, theme)

        basics = str(base['basics']).replace('{topic}', topic)

        key_concepts = [str(c).replace('{topic}', topic) for c in base['key_concepts']]

        hints = list(base['hints'])
        if action and action not in ('—', ''):
            hints.insert(0, f"<strong>🎯 Daily Action Focus:</strong> {action} — trace through 2-3 edge cases before writing any code.")

        tasks = [str(t).replace('{topic}', topic) for t in base.get('tasks', [])]

        hard_problem = str(base['hard_problem']).replace('{topic}', topic)

        lc = day.get('LeetCodeProblem')
        if not lc or lc == '—':
            lc = None

        day['Warmup'] = warmup
        day['Basics'] = basics
        day['KeyConcepts'] = key_concepts
        day['Tasks'] = tasks
        day['PracticeProblem'] = {'problem': f"<strong>📋 Daily Objective:</strong> {action}", 'hints': hints}
        day['HardProblem'] = hard_problem
        day['LeetCodeProblem'] = (f"<strong>{lc}</strong> — Analyze Big-O Time &amp; Space before starting." if lc else None)

        enriched.append(day)

    save_data(enriched, 'enriched_data.json')
    print(f"✅ Enriched {len(enriched)} days with expert-level 4-hour structured content.")

if __name__ == '__main__':
    enrich_data()
