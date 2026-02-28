# Week 3 — Day 5: Case Study — Social Media System Design
**Date:** 2026-02-28  
**Status:** ✅ Complete

---

## The 5-Step Framework (Use in Every Interview)

> Always follow this order. Never jump straight to architecture.

1. **Clarify Requirements** — functional + non-functional
2. **Back of Envelope Math** — validate scale before designing
3. **Choose Databases** — polyglot persistence decision
4. **Data Model** — tables, keys, access patterns
5. **Write Path + Read Path** — explicit flows for both

---

## Case Study 1 — Twitter System Design

### Step 1 — Requirements

**Functional:**
- Post tweets (280 chars)
- Follow other users
- Home timeline — 20 most recent tweets from people you follow
- Like and retweet
- Search by hashtag

**Non-Functional:**
- 100M daily active users
- 500M tweets/day
- Read-heavy — reads 10x more frequent than writes
- Timeline <100ms latency

---

### Step 2 — Back of Envelope Math

```
1 day ≈ 100,000 seconds  (round aggressively!)

Tweets/second:   500M ÷ 100K = 5,000 tps avg
Peak tps:        5,000 × 5   = 25,000 tps

Storage/day:     500M × 1KB  = 500GB/day
Storage/year:    500GB × 365 = 180TB/year

Timeline reads:  100M × 10   = 1B reads/day
Reads/second:    1B ÷ 100K   = 10,000 rps avg
Peak rps:        10,000 × 5  = 50,000 rps
```

**Conclusion:** 50K rps + 180TB/year → needs horizontal scale → NoSQL + polyglot persistence

---

### Step 3 — Polyglot Persistence

| Layer | Database | Why |
|---|---|---|
| User profiles, follows | PostgreSQL | Relational, ACID, low volume |
| Tweets, timelines, likes | Cassandra | High write throughput, predictable queries |
| Timeline caching | Redis | 50K rps needs <1ms response |
| Analytics | Snowflake | OLAP, Star Schema, ad-hoc queries |

> *"No single database wins everything. Use the right tool for each job."*

---

### Step 4 — Data Model

#### PostgreSQL — User Data & Relationships

```sql
CREATE TABLE users (
    user_id         UUID PRIMARY KEY,
    username        VARCHAR(50) UNIQUE NOT NULL,
    email           VARCHAR(100) UNIQUE NOT NULL,
    follower_count  INT DEFAULT 0,
    following_count INT DEFAULT 0,
    created_at      TIMESTAMP DEFAULT NOW()
);

CREATE TABLE follows (
    follower_id UUID REFERENCES users(user_id),
    followee_id UUID REFERENCES users(user_id),
    followed_at TIMESTAMP DEFAULT NOW(),
    PRIMARY KEY (follower_id, followee_id)
);
```

#### Cassandra — Tweets, Timelines, Likes

```sql
-- Source of truth for tweets
CREATE TABLE tweets_by_user (
    user_id    UUID,
    tweeted_at TIMESTAMP,
    tweet_id   UUID,
    content    TEXT,
    like_count INT,
    PRIMARY KEY (user_id, tweeted_at)
) WITH CLUSTERING ORDER BY (tweeted_at DESC);

-- Pre-computed home timeline (fan-out on write)
CREATE TABLE timeline (
    owner_id   UUID,
    tweeted_at TIMESTAMP,
    tweet_id   UUID,
    author_id  UUID,
    content    TEXT,
    PRIMARY KEY (owner_id, tweeted_at)
) WITH CLUSTERING ORDER BY (tweeted_at DESC);

-- Likes — two access patterns = two tables!
CREATE TABLE likes_by_tweet (
    tweet_id UUID,
    liked_at TIMESTAMP,
    user_id  UUID,
    PRIMARY KEY (tweet_id, liked_at)
) WITH CLUSTERING ORDER BY (liked_at DESC);

CREATE TABLE likes_by_user (
    user_id  UUID,
    liked_at TIMESTAMP,
    tweet_id UUID,
    PRIMARY KEY (user_id, liked_at)
) WITH CLUSTERING ORDER BY (liked_at DESC);

-- Hashtag search
CREATE TABLE tweets_by_hashtag (
    hashtag    TEXT,
    tweeted_at TIMESTAMP,
    tweet_id   UUID,
    author_id  UUID,
    content    TEXT,
    PRIMARY KEY (hashtag, tweeted_at)
) WITH CLUSTERING ORDER BY (tweeted_at DESC);
```

#### Redis — Caching Layer

```
user:{user_id}:timeline → cached last 20 tweets  (TTL: 5 min)
user:{user_id}:profile  → cached profile data    (TTL: 1 hour)
tweet:{tweet_id}:likes  → cached like count      (TTL: 1 min)
```

---

### Step 5 — Write Path & Read Path

**Write Path (when Deepak tweets):**
```
1. Write to tweets_by_user (Cassandra) — source of truth
2. Fetch follower list from PostgreSQL
3. Regular user (<1M followers)?
        → Fan-out on write → push to all followers' timeline table
   Celebrity (>1M followers)?
        → Skip fan-out → pull at read time instead
4. Extract hashtags → write to tweets_by_hashtag
5. Invalidate Redis cache for affected timelines
```

**Read Path (when follower opens Twitter):**
```
1. Check Redis cache first
   → Cache hit  → return in <1ms ✅
   → Cache miss → continue
2. Fetch from Cassandra timeline table
3. Following any celebrities?
        → Fetch their tweets from tweets_by_user
        → Merge + sort by tweeted_at DESC
        → Take top 20
4. Store result in Redis (TTL: 5 min)
5. Return to user <100ms ✅
```

---

### Step 6 — Analytics Layer

```
Cassandra → Kafka (CDC) → Spark → Delta Lake (S3)
                                          ↓
                                    Snowflake (OLAP)
                                          ↓
                                    Star Schema:
                                    dim_users (SCD Type 2!)
                                    dim_tweets
                                    fact_engagements
                                          ↓
                                    Dashboards
```

---

## Case Study 2 — Instagram Stories (Boss Problem)

### Clarifying Questions to Always Ask

1. Read-heavy or write-heavy?
2. Can followers reply to stories?
3. Do stories persist in highlights after 24 hours?
4. Scale of followers — celebrity vs regular?
5. Do we need analytics (view counts, who viewed)?
6. Global or single region?

**Answers for this problem:**
- Read-heavy — 2B views vs 500M posts (4x reads)
- Replies via direct message only
- Yes — highlights never expire ⭐ (great catch in interview!)
- Celebrities have 400M followers
- Yes — track who viewed, who liked
- Global

---

### Math

```
Stories/second:  500M ÷ 100K = 5,000 sps avg
Peak:            5,000 × 5   = 25,000 sps

Storage/day:     500M × 1KB  = 500GB/day
Storage/year:    500GB × 365 = 180TB/year

Views/day:       500M × 4    = 2B/day
Views/second:    2B ÷ 100K   = 20,000 rps avg
Peak:            20K × 5     = 100,000 rps
```

---

### Polyglot Persistence

| Layer | Database | Why |
|---|---|---|
| User profiles, follows | PostgreSQL | Relational, ACID |
| Stories, likes, replies | Cassandra | Time-series, high writes |
| 24hr caching, timeline | Redis | TTL support, <1ms reads |
| Analytics | Snowflake | OLAP, Star Schema |

---

### Data Model

#### PostgreSQL

```sql
CREATE TABLE users (
    user_id    UUID PRIMARY KEY,
    username   VARCHAR(50) UNIQUE NOT NULL,
    email      VARCHAR(100) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE follows (
    follower_id UUID REFERENCES users(user_id),
    followee_id UUID REFERENCES users(user_id),
    followed_at TIMESTAMP DEFAULT NOW(),
    PRIMARY KEY (follower_id, followee_id)
);
```

#### Cassandra

```sql
-- Stories by user (source of truth)
-- ⭐ USING TTL 86400 = auto-delete after 24 hours!
CREATE TABLE stories_by_user (
    user_id    UUID,
    posted_at  TIMESTAMP,
    story_id   UUID,
    media_url  TEXT,
    is_highlight BOOLEAN,
    PRIMARY KEY (user_id, posted_at)
) WITH CLUSTERING ORDER BY (posted_at DESC);

-- Insert with TTL for auto-expiry
-- INSERT INTO stories_by_user ... USING TTL 86400;
-- TTL = 86400 seconds = 24 hours
-- Highlighted stories: insert WITHOUT TTL

-- Story views (who viewed my story?)
CREATE TABLE story_views (
    story_id  UUID,
    viewed_at TIMESTAMP,
    viewer_id UUID,
    PRIMARY KEY (story_id, viewed_at)
) WITH CLUSTERING ORDER BY (viewed_at DESC);

-- Story likes
CREATE TABLE story_likes (
    story_id UUID,
    liked_at TIMESTAMP,
    user_id  UUID,
    PRIMARY KEY (story_id, liked_at)
) WITH CLUSTERING ORDER BY (liked_at DESC);

-- Story replies
CREATE TABLE story_replies (
    story_id   UUID,
    replied_at TIMESTAMP,
    user_id    UUID,
    message    TEXT,
    PRIMARY KEY (story_id, replied_at)
) WITH CLUSTERING ORDER BY (replied_at DESC);

-- Pre-computed story timeline
CREATE TABLE story_timeline (
    viewer_id UUID,
    posted_at TIMESTAMP,
    story_id  UUID,
    author_id UUID,
    media_url TEXT,
    PRIMARY KEY (viewer_id, posted_at)
) WITH CLUSTERING ORDER BY (posted_at DESC);
```

#### Redis

```
user:{user_id}:stories        → cached story list     (TTL: 5 min)
story:{story_id}:views        → cached view count     (TTL: 1 min)
story:{story_id}:expiry       → TTL: 86400 (24 hours)
user:{user_id}:timeline       → cached timeline       (TTL: 5 min)
```

---

### Write Path (when user posts a story)

```
1. Write to stories_by_user WITH TTL 86400 (Cassandra)
   → If highlighted: write WITHOUT TTL (never expires)
2. Fetch follower list from PostgreSQL
3. Regular user (<1M followers)?
        → Fan-out on write → push to all followers' story_timeline
   Celebrity (>1M followers)?
        → Skip fan-out → pull at read time
4. Cache in Redis with TTL 86400
5. Invalidate affected timeline caches
```

### Read Path (when follower opens Instagram)

```
1. Check Redis cache
   → Cache hit + story < 24hrs → serve instantly ✅
   → Cache miss → continue
2. Fetch from Cassandra story_timeline
3. Following any celebrities?
        → Fetch from stories_by_user
        → Merge + sort by posted_at DESC
4. Store result in Redis
5. Return to user
```

---

### ⭐ The 24-Hour Auto-Delete — Interview Gold

> *"Cassandra has a built-in TTL feature. Set TTL=86400 on insert and Cassandra automatically purges the row after 24 hours. No cron job, no scheduled deletion, no extra pipeline needed. For highlighted stories, insert WITHOUT TTL so they persist forever."*

```sql
-- Regular story (expires in 24 hours)
INSERT INTO stories_by_user (user_id, posted_at, story_id, media_url)
VALUES (?, ?, ?, ?)
USING TTL 86400;

-- Highlighted story (never expires)
INSERT INTO stories_by_user (user_id, posted_at, story_id, media_url, is_highlight)
VALUES (?, ?, ?, ?, true);
-- No TTL = persists forever
```

---

### Celebrity Problem Solution

```
Regular user  (<1M followers) → fan-out on WRITE
Celebrity     (>1M followers) → fan-out on READ
At read time                  → merge both + sort + top 20
```

---

### Analytics Layer

```
Cassandra → Kafka → Spark → S3 (Delta Lake)
                                    ↓
                              Snowflake
                                    ↓
                            Star Schema:
                            dim_users (SCD Type 2)
                            dim_story
                            fact_engagement
                                    ↓
                            Dashboards
```

---

## Key Interview Lines to Memorize

- *"I'd use polyglot persistence — the right database for each job."*
- *"Cassandra TTL=86400 handles 24-hour expiry natively — no cron job needed."*
- *"Fan-out on write for regular users, fan-out on read for celebrities, merge at read time."*
- *"Cache-aside pattern: check Redis first, fall back to Cassandra, populate on miss."*
- *"Always clarify requirements before touching architecture — never assume scale."*

---

## Interview Keywords Mastered Today

- Polyglot persistence
- Fan-out on write, fan-out on read, hybrid approach
- Cache-aside pattern
- TTL (Time To Live) — Cassandra + Redis
- Write path, read path
- Celebrity problem
- Back of envelope estimation
- 1 day ≈ 100,000 seconds
- Peak multiplier (3-5x average)
- SCD Type 2 on dim_users

---

## Whiteboard Tips

1. **Talk while you write** — never silent >30 seconds
2. **Draw arrows** for data flow — visual > text list
3. **Label PRIMARY KEY explicitly** on every Cassandra table
4. **Box your math** — make calculations visible
5. **State assumptions out loud** — "I'm assuming 1KB per story"
6. **Celebrity problem** — always mention it in social media design

---

## Commit

```bash
git add .
git commit -m "week-03: day 5 complete - Twitter + Instagram Stories system design, polyglot persistence, fan-out patterns"
git push
```
