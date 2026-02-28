WEEK13 = {
    "star_method": {
        "basics": """<div class="lesson">
<h3>🧠 Hour 1 — STAR Method: Structuring Your Stories for FAANG</h3>
<p>Behavioral interviews at FAANG companies assess leadership principles. Amazon has 16 LPs; Meta, Google, and Microsoft each have their own frameworks. The STAR method is the universal structure for answering behavioral questions compellingly.</p>
<h4>STAR Framework</h4>
<pre>Situation: Set the scene — what was the context?
    "At Virtusa, we had a critical ETL pipeline that processed $2M/day in transactions..."

Task: What was YOUR specific responsibility?
    "I was the sole data engineer responsible for redesigning the pipeline..."

Action: What did YOU do? (Use I, not we. Be specific.)
    "I identified the bottleneck using Spark's execution plan... I implemented batch micro-aggregations...
     I deployed the fix using blue-green deployment to avoid downtime..."

Result: Quantifiable outcome.
    "Reduced processing time from 4 hours to 22 minutes (91% improvement).
     Pipeline failure rate dropped from 15% to 0.2%."</pre>
<h4>Mapping Stories to Amazon Leadership Principles</h4>
<table border="1" style="width:100%;border-collapse:collapse">
  <tr><th>LP</th><th>Question type</th><th>Best story themes</th></tr>
  <tr><td>Deliver Results</td><td>"Tell me about a time you met a challenging deadline"</td><td>Pipeline optimization, on-time delivery</td></tr>
  <tr><td>Ownership</td><td>"Tell me about a time you took ownership beyond your role"</td><td>Fixing someone else's bug, proactive monitoring</td></tr>
  <tr><td>Invent & Simplify</td><td>"Tell me about a technical innovation you drove"</td><td>New architecture, automation</td></tr>
  <tr><td>Dive Deep</td><td>"How did you debug a complex system issue?"</td><td>Production incident postmortems</td></tr>
  <tr><td>Bias for Action</td><td>"Tell me about a time you made a decision with incomplete data"</td><td>Incident response, outage mitigation</td></tr>
</table>
<h4>What Makes a FAANG-Level Answer</h4>
<ul>
  <li>✅ Quantified impact (time, money, percentage, scale)</li>
  <li>✅ YOUR specific actions (not the team's)</li>
  <li>✅ Technical depth that shows expertise</li>
  <li>✅ What you learned / would do differently</li>
  <li>❌ Vague: "We improved the pipeline"</li>
  <li>❌ No result: trailing off without an outcome</li>
  <li>❌ Too long: behavioral answers should be 2-3 minutes max</li>
</ul>
</div>""",
        "key_concepts": [
            "STAR: Situation, Task, Action, Result — always end with a quantified result.",
            "Use 'I' not 'we' — interviewers want to know YOUR contribution, not the team's.",
            "Prepare 5-7 versatile stories that can apply to multiple leadership principles.",
            "Technical behavioral answers should include the specific technology/approach you used.",
            "Quantify results: time saved, cost reduced, percentage improvement, scale achieved.",
            "End every story with what you learned — shows growth mindset and self-awareness.",
            "2-3 minute answer length — practice with a timer to avoid rambling."
        ],
        "hints": [
            "Write your stories in a spreadsheet: Column A = story, Columns B-N = which LP it maps to.",
            "Amazon's most frequently asked LP: 'Deliver Results' — have 2-3 stories ready for it.",
            "Conflicts with coworkers: focus on data-driven resolution and outcome, not personal criticism.",
            "Failure stories are expected — prepare one honest failure with strong lessons learned."
        ],
        "tasks": [
            "<strong>Step 1 — Mine 5 stories from your Virtusa work</strong>: major project, optimization, conflict, failure, innovation.",
            "<strong>Step 2 — Write each story in STAR format</strong> with specific quantified results.",
            "<strong>Step 3 — Map each story to 2-3 Amazon LPs</strong> in a spreadsheet.",
            "<strong>Step 4 — Record yourself saying one story</strong>: watch it back and check timing, clarity, and whether 'I vs we' is correct."
        ],
        "hard_problem": "Stretch Exercise: The hardest behavioral question — 'Tell me about a time you disagreed with your manager and what happened.' This tests your backbone, communication skills, and professionalism simultaneously. Write a full STAR answer where you: raised a data-driven concern professionally, the outcome benefitted from your input, AND you maintained a good working relationship. This is often a dealbreaker question at senior DE levels."
    },
    "mental_prep": {
        "basics": """<div class="lesson">
<h3>🏁 Hour 1 — Mental Preparation: The Final 48 Hours</h3>
<p>The night before and day of the interview, technical cramming hurts more than it helps. Your goal is to show up mentally sharp, confident, and in peak cognitive state. Here's the science-backed protocol.</p>
<h4>48 Hours Before: Light Review Mode</h4>
<ul>
  <li>Review only your personal notes — not new material</li>
  <li>Re-read your 5 behavioral stories once</li>
  <li>Draw your best system design (1-2 drawings) from memory</li>
  <li>No LeetCode grinding — it increases anxiety without improving performance</li>
</ul>
<h4>24 Hours Before: Reset Mode</h4>
<ul>
  <li>Exercise: 30-45 min moderate cardio — increases BDNF, sharpens cognition next day</li>
  <li>Sleep 8 hours — memory consolidation happens during deep sleep</li>
  <li>Avoid alcohol — disrupts REM sleep and slow-wave sleep</li>
  <li>Prepare logistics: confirm interview time/format, test Zoom/CoderPad link</li>
</ul>
<h4>Day Of: Performance Mode</h4>
<pre>Morning:
- Eat a real breakfast (glucose is brain fuel)
- 20-min light walk or stretch
- Read your notes ONCE — then put them away

In the interview:
- Think aloud: "Let me make sure I understand the problem..."
- Clarify before coding: "Can I assume the data fits in memory?"
- Show your work: narrate every decision ("I'm using DENSE_RANK because there should be no gaps...")
- Stuck? Say it: "Let me think through the edge cases..." (silence is NOT a signal of failure)
- Wrong answer? Own it: "That approach has a flaw — let me reconsider..."</pre>
<h4>The Interview Mindset Reframe</h4>
<p>You are not being tested — you are having a technical conversation with a peer. The interviewer WANTS you to succeed (hiring is expensive and painful). They are rooting for you to show your best self. Reframe nerves as excitement.</p>
</div>""",
        "key_concepts": [
            "No new material 48 hours before the interview — only review of existing notes.",
            "Sleep is more valuable than last-minute studying — memory consolidation happens during sleep.",
            "Think aloud during technical questions — interviewers need to see your reasoning process.",
            "Clarify before coding — this shows senior-level professionalism, not weakness.",
            "Being stuck is normal and expected — show your systematic debugging approach.",
            "Own mistakes immediately — 'that won't work because...' signals strong technical judgment.",
            "Behavioral: have exactly one story of failure ready — it shows self-awareness and growth."
        ],
        "hints": [
            "Have a glass of water with you — cognitive performance degrades with even mild dehydration.",
            "If nerves strike: box breathing (4-4-4-4: inhale-hold-exhale-hold) before starting.",
            "Read the problem twice before touching the keyboard — rushing on easy problems is the #1 mistake.",
            "End the interview by asking a thoughtful question: 'What does the data engineering roadmap look like for this team?'"
        ],
        "tasks": [
            "<strong>Final Review Sprint (1 hour):</strong> Window Functions cheat sheet → Gaps & Islands pattern → SCD Type 2 MERGE → Parquet internals → Kafka partition design → Spark Catalyst phases.",
            "<strong>Behavioral dry-run (30 min):</strong> Say each STAR story aloud — time each one at under 3 minutes.",
            "<strong>System design sketch (30 min):</strong> Draw the batch ETL and streaming architectures from memory.",
            "<strong>Mindset (rest of day):</strong> Close the books. Walk, exercise, eat well. You have done the work. Trust your preparation."
        ],
        "hard_problem": "Final Reflection: Write down the 3 concepts you feel LEAST confident about. For each one, write a 3-sentence explanation of it as if you are teaching it to a junior engineer. If you can explain it simply and accurately in 3 sentences, you understand it at interview level. If you can't, spend 30 minutes on just that one topic."
    },
    "ready": {
        "basics": """<div class="lesson">
<h3>🚀 Day 91 — You Are Ready. Go Get the Offer.</h3>
<p>13 weeks of deliberate practice. 91 days of consistency. You have covered more depth and breadth across data engineering than the vast majority of candidates who walk into FAANG interviews. This is your final checkpoint.</p>
<h4>The Complete FAANG DE Knowledge Map You Now Own</h4>
<pre>✅ SQL Analytics (Window Functions, Gaps & Islands, CTEs, Execution Plans, Indexes, Joins, NULL)
✅ Data Modeling (Star Schema, SCD Types, Normalization, NoSQL, Kimball Methodology)
✅ Python Logic (Hash Maps, Generators, Decorators, Memory, File I/O, Algorithms)
✅ Storage Internals (Parquet, Avro, Compression, S3 Partitioning, Delta Lake, Iceberg)
✅ Spark (Catalyst, Shuffle, Partitions, Broadcast Join, Memory, Skew, OOM)
✅ Orchestration (Airflow DAG, Scheduler, XCom, Backfill, Dynamic DAGs)
✅ Streaming (Kafka, Pub/Sub, Consumer Groups, Exactly-Once, Windowing)
✅ System Design (Batch ETL, CDC, Streaming Architecture, Back-of-Envelope)
✅ Quality (Data Contracts, dbt Tests, Observability, Idempotency, Schema Evolution)
✅ Behavioral (STAR Method, Amazon LPs, Conflict, Failure, Innovation stories)</pre>
<h4>Your Interview Day Execution Checklist</h4>
<pre>Coding Round:
□ Read the problem twice before touching the keyboard
□ Clarify: NULLs? Duplicates? Result format? Scale?
□ Write 3-5 rows of test data on paper/whiteboard
□ CTE-first for SQL; function-first for Python
□ State complexity: "This is O(N log N) because..."
□ Check edge cases after writing solution

System Design Round:
□ Clarify requirements and scale first
□ Back-of-envelope estimation before architecture
□ Draw from source to consumer (left to right on whiteboard)
□ Propose AND explain tradeoffs of each choice
□ Mention observability, failure modes, and costs

Behavioral Round:
□ STAR format for every answer
□ Quantified results in every answer
□ Use "I" not "we"
□ End with "What I learned was..."</pre>
<h4>Final Words</h4>
<p>You did not just prepare for an interview. You became a more capable, more knowledgeable data engineer. Whatever happens in the interview, that knowledge stays with you. Now go get what you worked for. 💪</p>
</div>""",
        "key_concepts": [
            "You have completed a comprehensive, expert-level FAANG Data Engineering curriculum.",
            "The knowledge you built is permanent — it serves you in the interview and every day after.",
            "Interviews test a sample of your knowledge under pressure — they are not comprehensive exams.",
            "Confidence comes from preparation — you have done the preparation.",
            "Technical depth + communication + systematic thinking = the FAANG DE trifecta.",
            "Failure in one interview is data, not a verdict — adjust and try again.",
            "The best data engineers never stop learning — this curriculum is a foundation, not a ceiling."
        ],
        "hints": [
            "Day of interview: review nothing new. Eat, exercise, breathe. Trust your preparation.",
            "In the interview: slow down. Rushing is the #1 mistake of over-prepared candidates.",
            "If you get a question you don't know: say so honestly, then reason through it out loud.",
            "After each interview: note every question asked — it helps when you interview again if needed."
        ],
        "tasks": [
            "Complete the Day 91 knowledge map audit — check off every topic you feel confident on.",
            "Run through your STAR stories one final time.",
            "Get 8 hours of sleep.",
            "Go get the offer. 🚀"
        ],
        "hard_problem": "The Ultimate Boss Problem: You are given 45 minutes to design a real-time ride-sharing analytics platform (like Uber). Inputs: driver location updates (100K/min), ride requests (10K/min), trip completions (5K/min). Outputs: live surge pricing per geo-cell (updated every 30 seconds), driver earnings dashboard (updated every minute), daily aggregate reports (by 6am). Design the full system: ingestion, processing, storage, serving, and monitoring. Include technology choices with justifications, failure modes, and cost estimate at 10x scale."
    }
}
