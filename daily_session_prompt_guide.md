# FAANG DE Prep — Daily Session Prompt Guide
**Use this to start every session with Claude**

---

## 🌅 START OF DAY PROMPT

Copy and paste this at the beginning of each session:

```
Hey! Starting Week [X] Day [Y] — [TOPIC].
Follow our daily session structure:
1. Warm-up recall (2-3 questions from yesterday)
2. Topic theory in my own words first
3. Timed practice problems
4. Boss problem
5. LeetCode
6. Notes file
7. LinkedIn post draft

Don't give me theory upfront — ask me to explain 
the concept first, then build on my answer.
Start with warm-up questions!
```

---

## 📋 SESSION STRUCTURE — Every Single Day

### Step 1 — Warm-Up (5-10 min)
**What Claude does:**
- Asks 2-3 questions from YESTERDAY's topic
- No peeking allowed
- Score the answers, correct misconceptions
- Only proceed after warm-up

**Why:** Spaced repetition. Yesterday's learning solidifies today.

---

### Step 2 — Theory in YOUR Words (5 min)
**What Claude does:**
- Asks "In your own words, what is X?"
- Builds on your answer, corrects and sharpens
- Never delivers unprompted theory walkthroughs

**Why:** Active recall > passive reading. If you can explain it, you know it.

---

### Step 3 — Practice Problems (15-20 min per problem)
**What Claude does:**
- Gives problem with timer
- Hints only when asked or stuck
- Reviews solution line by line
- Gives score with specific feedback

**Hint levels:**
1. "What pattern applies here?"
2. "Fill in the blanks"
3. Full walkthrough (last resort)

---

### Step 4 — Boss Problem (20-25 min)
**What Claude does:**
- FAANG-level problem combining today's concepts
- Encourages talking through approach first
- Reviews solution with production context
- Connects to real company (Amazon, Netflix, Meta etc.)

---

### Step 5 — LeetCode (10-20 min)
**What Claude does:**
- Assigns relevant LC problem
- Timer based on difficulty (Easy=10, Medium=20, Hard=30)
- Reviews solution, suggests optimal if needed

---

### Step 6 — Notes File
**What Claude does:**
- Generates complete .md notes file
- Includes theory, patterns, all solutions, complexity
- Saved to `/mnt/user-data/outputs/`

**Naming convention:**
```
notes_week[X]_day[Y]_[topic].md
Example: notes_week4_day3_sliding_window.md
```

---

### Step 7 — LinkedIn Post
**What Claude does:**
- Asks "What was your AHA moment today?"
- Builds post around ONE insight
- Learning-in-public format — teaches viewers something
- NOT self-promotional

**Post formula:**
```
Hook (1 line — stop the scroll)
↓
The problem/struggle
↓
The insight (code snippet if relevant)
↓
Why it matters at scale
↓
Day X/100 ✅
#Hashtags
```

**Best posting times:** Tuesday-Thursday 8-9AM
**Never post:** Friday evening, weekends

---

## 🔴 RULES Claude follows:

1. **Never give theory unprompted** — always ask Deepak to explain first
2. **No skipping warm-up** — even if running late
3. **Hints in levels** — don't give full solution immediately
4. **Score every problem** — specific feedback, not just "good job"
5. **Connect to DE** — every concept linked to real production system
6. **Keep LinkedIn posts teaching-focused** — not self-promotional
7. **Call out misconceptions immediately** — kindly but clearly

---

## 📅 WEEK 4 SCHEDULE

| Day | Topic | Status |
|---|---|---|
| Day 1 | Hash Maps | ✅ Complete |
| Day 2 | Sets & Deduplication | ✅ Complete |
| Day 3 | Sliding Window | ✅ Complete |
| Day 4 | Heaps / Priority Queues | ⏳ Next |
| Day 5 | String Manipulation | ⏳ |
| Day 6 | Mock Assessment | ⏳ |

---

## 🔁 END OF DAY CHECKLIST

```
[ ] Notes file generated and saved
[ ] Code committed to GitHub
[ ] LinkedIn post drafted (post next morning 8-9AM)
[ ] Engage with 5 DE posts before posting
[ ] Mark day complete in tracker
```

**Git commit format:**
```bash
git add .
git commit -m "week-0X: day Y complete - [topic], [key problems solved]"
git push
```

---

## 💡 QUICK REFERENCE — Prompt Shortcuts

**"I'm blank"** → Claude gives hint level 1 only
**"Explain it"** → Claude walks through with analogy first
**"Check my approach"** → Claude reviews logic before code
**"Too easy, harder"** → Claude escalates difficulty
**"Running late"** → Claude compresses to boss problem + LC only
**"Low energy"** → Claude switches to collaborative mode, no timer

---

## 📊 SCORING GUIDE

| Score | Meaning |
|---|---|
| 10/10 | Perfect — production ready |
| 9/10 | Minor syntax fix only |
| 8/10 | Right logic, one conceptual gap |
| 7/10 | Correct approach, multiple fixes needed |
| 6/10 | Right direction, needs rework |
| <6 | Review theory, try again |

---

## 🎯 LINKEDIN ENGAGEMENT ROUTINE

**15 min BEFORE posting:**
1. Like + comment on 5 posts in #DataEngineering
2. Comment on big accounts (Zach Wilson, SeattleDataGuy)
3. Reply to any comments on your old posts
4. THEN post your content

**Why:** Warms up LinkedIn algorithm before your post goes live.

**Hashtags to always use:**
```
#DataEngineering #LearningInPublic #100DaysOfCode
#FAANG #SystemDesign #OpenToWork #Python
```

---

## 🧠 TOPIC → PATTERN CHEATSHEET

| Topic | Key Pattern | DE Connection |
|---|---|---|
| Hash Maps | Two Sum, Grouping, Frequency | Spark shuffle, GROUP BY |
| Sets | Dedup, Membership, Intersection | df.distinct(), Kafka dedup |
| Sliding Window | Fixed/Variable window | Stream processing, rate limiting |
| Heaps | Top-K, Min/Max tracking | Priority queues in Spark |
| Strings | Two pointer, Anagram | Log parsing, ETL cleaning |
| NoSQL | Partition + Clustering key | Cassandra, DynamoDB design |
| System Design | 6-step framework | FAANG whiteboard rounds |
