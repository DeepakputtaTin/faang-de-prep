# Week 3 — Day 4: NoSQL Modeling
**Date:** 2026-02-28  
**Status:** ✅ Complete

---

## Why NoSQL Exists

Relational databases scale **vertically** (bigger machine) — but there's a ceiling.  
At Google/Amazon scale you need **horizontal scale** (more machines), and SQL wasn't built for that.

Two root causes:
- **Scale** — PostgreSQL lives on one server. Google has petabytes across thousands of servers
- **Speed** — JOINs + ACID transactions have overhead that kills latency at 100M requests/second

---

## The 4 Types of NoSQL

| Type | Examples | Best For |
|---|---|---|
| Key-Value | Redis, DynamoDB | Caching, sessions, simple lookups |
| Wide-Column ⭐ | Cassandra, HBase | Time-series, high write throughput |
| Document | MongoDB | Flexible schemas, nested JSON data |
| Graph | Neo4j | Social networks, fraud detection |

---

## The #1 Rule of NoSQL

> **"Know your ACCESS PATTERNS first — then design your schema around them."**

- SQL → normalize data, JOINs figure out the queries
- NoSQL → design for how you will READ the data. No joins exist.

---

## Wide-Column (Cassandra) — FAANG Favorite ⭐

### Two Core Concepts

**Partition Key**
- Determines **WHICH NODE** in the cluster stores the data
- Cassandra hashes the partition key → routes to specific node
- All rows with same partition key live on the same node
- Bad choice = one node gets 90% of traffic = **hot partition = system dies**
- Good choices: `user_id`, `device_id` (high cardinality, even distribution)

**Clustering Key**
- Determines **SORT ORDER** of rows within a partition
- Data is physically stored pre-sorted on disk
- Enables fast range queries within a partition

**The one-liner to memorize:**
> *"Partition key = WHICH node. Clustering key = ORDER within that node."*

### Cassandra Table Syntax

```sql
CREATE TABLE watch_history (
    user_id    UUID,
    watch_date TIMESTAMP,
    show_name  VARCHAR,
    duration   INT,
    PRIMARY KEY (user_id, watch_date)  -- (partition_key, clustering_key)
) WITH CLUSTERING ORDER BY (watch_date DESC);
```

**PostgreSQL equivalent** (for practice):
```sql
CREATE TABLE watch_history (
    user_id    UUID,
    watch_date TIMESTAMP,
    show_name  VARCHAR,
    duration   INT,
    PRIMARY KEY (user_id, watch_date)
);
CREATE INDEX ON watch_history (watch_date DESC);
```

> ⚠️ `WITH CLUSTERING ORDER BY` is Cassandra-only syntax. PostgreSQL uses indexes instead.

---

## The 3 Golden Rules of Cassandra Modeling

1. **Model for queries, not entities** — know what you'll READ before designing what you store
2. **Denormalize everything** — no joins in Cassandra. Duplicate data is intentional.
3. **Avoid hot partitions** — partition by `user_id` not `country`. Even distribution = healthy cluster.

---

## Lab — Instagram Likes (Two Access Patterns)

**Rule:** In Cassandra, each access pattern gets its own table.

```sql
-- Pattern 1: "Get all likes FOR A POST, sorted by time"
CREATE TABLE likes_by_post (
    post_id  UUID,
    liked_at TIMESTAMP,
    user_id  UUID,
    PRIMARY KEY (post_id, liked_at)
) WITH CLUSTERING ORDER BY (liked_at DESC);

-- Pattern 2: "Get all posts liked BY A USER"
CREATE TABLE likes_by_user (
    user_id  UUID,
    liked_at TIMESTAMP,
    post_id  UUID,
    PRIMARY KEY (user_id, liked_at)
) WITH CLUSTERING ORDER BY (liked_at DESC);
```

**Key insight:** When Alice likes a post → write to BOTH tables simultaneously.  
Duplication is intentional. Storage is cheap. Joins don't exist.

---

## Boss Problem — Twitter Timeline Design

**Problem:** 100M users, each follows 300 people, each tweets 5x/day. Serve timeline in <100ms.

### Option A — Fan-out on Write
When someone tweets → push to ALL followers' timeline tables immediately.

```sql
CREATE TABLE timeline (
    user_id    UUID,       -- partition key: "whose timeline?"
    tweeted_at TIMESTAMP,  -- clustering key: sorted by time
    tweet_id   UUID,
    author_id  UUID,
    content    TEXT,
    PRIMARY KEY (user_id, tweeted_at)
) WITH CLUSTERING ORDER BY (tweeted_at DESC);
```

### Option B — Fan-out on Read
When you open Twitter → query all 300 followed users' tweets in real-time and merge.

```sql
CREATE TABLE tweets_by_user (
    author_id  UUID,
    tweeted_at TIMESTAMP,
    tweet_id   UUID,
    content    TEXT,
    PRIMARY KEY (author_id, tweeted_at)
) WITH CLUSTERING ORDER BY (tweeted_at DESC);
```

### The Tradeoff

| | Fan-out on Write | Fan-out on Read |
|---|---|---|
| Write cost | 🔴 High — 1 tweet → 100K writes | 🟢 Low — 1 write only |
| Read cost | 🟢 Low — 1 query, instant | 🔴 High — 300 queries + merge |
| Read latency | 🟢 <10ms | 🔴 Risky at scale |
| Celebrity problem | 🔴 400M writes per tweet | 🟢 No problem |

### ⭐ Interview Gold Answer — Hybrid Approach
> *"Fan-out on write for regular users since reads are 10x more frequent than writes. For celebrities (>1M followers), fan-out on write is too expensive — pull their tweets at read time and merge both results."*

---

## Cassandra vs PostgreSQL — When to Use Which

| Scenario | PostgreSQL | Cassandra |
|---|---|---|
| Complex ad-hoc queries | ✅ | ❌ |
| Millions of writes/second | ❌ | ✅ |
| Time-series data | ❌ | ✅ |
| ACID transactions | ✅ | ❌ |
| Geo-distributed data | ❌ | ✅ |
| Flexible analytics | ✅ | ❌ |

---

## LeetCode — LC 49: Group Anagrams

**Pattern:** Hashmap grouping by sorted key

```python
from collections import defaultdict

class Solution(object):
    def groupAnagrams(self, strs):
        anag = defaultdict(list)
        for i in strs:
            sorted_strs = ''.join(sorted(i))  # "eat" → "aet"
            anag[sorted_strs].append(i)
        return list(anag.values())

# Time:  O(n × k log k) — n words, each sorted in k log k
# Space: O(n × k)       — storing all words in hashmap
```

**Key insight:** Anagrams always produce the same string when sorted.  
Use sorted string as hashmap key → group automatically.

**DE connection:** Same pattern used for deduplicating records by a normalized/canonical key.

---

## Interview Keywords Mastered Today

- Partition key, clustering key, hot partition
- Fan-out on write, fan-out on read, hybrid approach
- Denormalization, access pattern design
- Wide-column, document, key-value, graph databases
- `WITH CLUSTERING ORDER BY` (Cassandra syntax)
- `defaultdict(list)` — hashmap grouping pattern

---

## Commit

```bash
git add .
git commit -m "week-03: day 4 complete - NoSQL modeling, Cassandra design, Twitter boss problem, LC49"
git push
```
