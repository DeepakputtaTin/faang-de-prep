# Week 3 — Day 6: Mock Design Round — Netflix Continue Watching
**Date:** 2026-03-01
**Status:** ✅ Complete
**Mock Score:** 9.5/10 🏆

---

## The Problem

> You're a Data Engineer at Netflix. Design the complete data architecture
> for Netflix's "Continue Watching" feature.
> - 200M subscribers worldwide
> - Remembers episode + exact timestamp where user stopped
> - Updates in real-time as they watch
> - Works across all devices (phone, TV, laptop)

---

## Step 1 — Clarifying Questions (Always First!)

**Questions to ask before designing anything:**

1. Multiple devices at same time? → Yes, sync across ALL devices in real-time
2. How many shows in "Continue Watching"? → Last 10 shows max
3. Does it expire? → 90 days of inactivity → drops off
4. Read heavy or write heavy? → Write heavy — position updates every 30 sec
5. Consistency requirement? → Eventual consistency fine, 1-2 sec lag acceptable
6. Geography? → Global — US, Europe, Asia Pacific
7. DAU + watch time? → 150M DAU, 2 hrs/day avg watch time
8. Peak hours? → 7PM-11PM local time per region

---

## Step 2 — Back of Envelope Math

```
1 day ≈ 100,000 seconds

Users/second:    150M ÷ 100K  = 1,500 users/sec avg
Peak users/sec:  1,500 × 5    = 7,500 users/sec (7-11PM)

Write heavy (every 30 sec while watching):
Writes/day:      150M × 2hrs × 120 updates/hr = 36 Billion writes/day
Writes/sec:      36B ÷ 100K  = 360,000 writes/sec avg 😱

Read (app open / device switch):
Reads/day:       150M × 5 app opens = 750M reads/day
Reads/sec:       750M ÷ 100K = 7,500 reads/sec

Write:Read ratio = 48:1 — extreme write heavy!
```

**Conclusion:**
- 360K writes/sec → can't hit Cassandra every 30 sec directly
- Solution: **Redis buffer → flush to Cassandra every 5 min**
- 180TB+/year storage → needs distributed, horizontal scale

---

## Step 3 — Polyglot Persistence

| Functional Need | Database | Why |
|---|---|---|
| User profiles, movie details | PostgreSQL | Relational, ACID, low volume |
| Watch history, last 10, 90-day history | Cassandra | Time-series, high write throughput |
| Real-time position updates, sessions | Redis | In-memory, <1ms, TTL support |
| Analytics | Snowflake | OLAP, Star Schema |

---

## Step 4 — Data Model

### PostgreSQL

```sql
CREATE TABLE user_profile (
    user_id           UUID PRIMARY KEY,
    username          VARCHAR(50) UNIQUE NOT NULL,
    subscription_type VARCHAR(20),   -- basic/standard/premium
    region            VARCHAR(20),   -- US, APAC, EU
    created_at        TIMESTAMP DEFAULT NOW()
);

CREATE TABLE movie_details (
    movie_id   UUID PRIMARY KEY,
    title      VARCHAR(200),
    creator    VARCHAR(100),
    runtime    INT,              -- total duration in seconds
    genre      VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW()
);
```

### Cassandra

```sql
-- Primary watch history table
-- ⭐ progress_sec = WHERE user stopped — CORE of Continue Watching!
CREATE TABLE user_watch_history (
    user_id      UUID,
    watched_at   TIMESTAMP,
    movie_id     UUID,
    progress_sec INT,       -- seconds into video (e.g. 3420 = 57 mins in)
    device_type  TEXT,      -- phone/TV/laptop
    PRIMARY KEY (user_id, watched_at)
) WITH CLUSTERING ORDER BY (watched_at DESC)
  AND default_time_to_live = 7776000;  -- 90 days TTL (90 × 86400)

-- Last 10 movies = same table, LIMIT 10
-- 90 day history = same table, TTL handles auto-deletion

-- Watch position by device (cross-device sync)
CREATE TABLE watch_position_by_device (
    user_id      UUID,
    movie_id     UUID,
    device_type  TEXT,
    progress_sec INT,
    updated_at   TIMESTAMP,
    PRIMARY KEY ((user_id, movie_id), device_type)
) WITH CLUSTERING ORDER BY (device_type ASC);
```

### ⭐ The Critical Column Everyone Forgets

```
progress_sec INT — seconds into the video where user stopped

Without this → "Continue Watching" just shows the show title
With this    → resumes from exactly 57 minutes 23 seconds in

This is THE most important column in the entire design.
Never forget it!
```

### Redis

```
# Real-time position buffer (updated every 30 sec)
last_timestamp:{user_id}:{movie_id} → progress_sec  (TTL: 24hr)

# Continue Watching list cache
continue_watching:{user_id} → [last 10 shows + positions]  (TTL: 1hr)

# User session + device
session:{user_id} → {device_type, region, login_time}  (TTL: session)

# Region-based content availability
region:{region_code} → available_show_ids  (TTL: 1hr)
```

---

## Step 5 — Write Path + Read Path

### Write Path (when user watches content)

```
1. User logs in
   → Fetch user_profile from PostgreSQL
   → Source movie_list based on region

2. User selects movie
   → Based on region, Cassandra displays available shows

3. User starts watching
   → Every 30 seconds:
        Redis last_timestamp:{user_id}:{movie_id} updated (heavy writing)
        (Buffer in Redis — NOT hitting Cassandra every 30 sec!)

4. User stops/pauses at particular timestamp
   → Final cache value flushed to Cassandra user_watch_history
   → progress_sec saved permanently

5. Background flush job (every 5 min)
   → Batch write Redis buffer → Cassandra
   → Handles crash recovery (if user closes app abruptly)
```

### Read Path (when user opens Netflix)

```
1. User logs in / opens app
   → Check Redis: continue_watching:{user_id}
   → Cache hit → serve last 10 shows with progress in <1ms ✅

2. Cache miss
   → Fetch from Cassandra user_watch_history
        WHERE user_id = X
        ORDER BY watched_at DESC
        LIMIT 10
   → Populate Redis cache (TTL: 1hr)

3. User clicks "Continue Watching" on a show
   → Check Redis last_timestamp:{user_id}:{movie_id}
   → Resume from progress_sec ✅

4. Every 30 sec while watching
   → Redis cache updates
   → Background flush to Cassandra

5. 90 days inactivity
   → Cassandra TTL = 7,776,000 sec auto-deletes row ✅
   → No cron job needed!
```

### Cross-Device Sync (bonus point!)

```
User watching on TV → switches to phone:
1. TV updates Redis every 30 sec
2. Phone opens app → reads from Redis last_timestamp
3. Phone resumes from exact same second as TV ✅
4. Eventual consistency (1-2 sec lag) is acceptable per requirements
```

---

## Step 6 — Analytics Layer

```
Cassandra → Kafka (CDC) → Spark → S3 (Delta Lake)
                                          ↓
                                    Snowflake
                                          ↓
                                    Star Schema:
                                    dim_users
                                    dim_movies
                                    fact_watch_history
                                      → last_10_movies
                                      → 90_days_history
                                      → content_type
                                      → region_login
                                          ↓
                                    Dashboards
```

**Analytics questions answered:**
- What was user watching? → fact_watch_history + dim_movies
- What type of content users liked? → genre analysis on dim_movies
- How many mins/day user is watching? → SUM(progress_sec) per user per day

---

## Key Interview Lines to Memorize

> *"I'd buffer position updates in Redis every 30 seconds — 36 billion direct Cassandra writes/day is too expensive. Redis absorbs the write storm, we flush to Cassandra every 5 minutes."*

> *"The most critical column is progress_sec — without it, Continue Watching is just a show list, not a resume feature."*

> *"90-day TTL on Cassandra insert handles expiry natively — no cron job, no scheduled deletion pipeline needed."*

> *"Cross-device sync works through Redis — TV writes position every 30 sec, phone reads it on open. Eventual consistency with 1-2 sec lag is acceptable here."*

---

## Common Mistakes in This Problem

| Mistake | Impact | Fix |
|---|---|---|
| Forgetting progress_sec | Core feature doesn't work | Always ask "what data enables the feature?" |
| Writing to Cassandra every 30 sec | 360K writes/sec kills cluster | Redis buffer + periodic flush |
| Peak multiplier too low (2x) | Under-provision for prime time | Always use 3-5x peak multiplier |
| No cross-device sync design | Misses multi-device requirement | Redis as shared real-time state |
| No TTL for 90-day expiry | Manual deletion pipeline needed | default_time_to_live in Cassandra |

---

## Week 3 Complete — Full Summary

| Day | Topic | Status |
|---|---|---|
| Day 1 | Dimensional Modeling (Star/Snowflake) | ✅ |
| Day 2 | SCD Types 1, 2, 3 | ✅ |
| Day 3 | Normalization (1NF → 3NF) | ✅ |
| Day 4 | NoSQL Modeling + Cassandra | ✅ |
| Day 5 | Social Media Case Study (Twitter + Instagram) | ✅ |
| Day 6 | Mock Design Round (Netflix) — 9.5/10 | ✅ 🏆 |

---

## The Week 3 Mental Model

```
Raw Data (flat table)
      ↓
  Normalize (3NF) → remove anomalies, clean OLTP
      ↓
  Model (Star Schema) → denormalize for analytics
      ↓
  Scale (NoSQL) → Cassandra for high write throughput
      ↓
  Cache (Redis) → absorb write storms, sub-ms reads
      ↓
  Analyze (Snowflake) → Star Schema + SCD Type 2
      ↓
  Serve → dashboards, ML features, product decisions
```

This is the complete data engineering stack. You built it from scratch in 6 days. 💪

---

## Commit

```bash
git add .
git commit -m "week-03: day 6 complete - Netflix Continue Watching mock design, 9.5/10, week 3 DONE"
git push
```
