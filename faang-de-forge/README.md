# 🚀 DE Forge — FAANG Data Engineering Prep Platform

A **13-week, 91-day** structured study platform for FAANG-level Data Engineering interviews.
Built as a fully self-contained static website with an AI coaching chatbot.

---

## 📦 Package Structure

```
faang-de-forge/
│
│  ── WEB APP (run these to launch the site) ──────────────────
├── index.html          (7 KB)    Main app entry point
├── styles.css          (35 KB)   Dark/light theme + full UI
├── app.js              (23 KB)   App logic, routing, progress tracking
├── chatbot.css         (16 KB)   AI chatbot styles
├── chatbot.js          (31 KB)   AI chatbot (Groq / OpenRouter / Gemini)
├── data.js             (986 KB)  Full 13-week curriculum content database
│
├── start.bat                     Double-click to launch (Windows)
├── README.md                     This file
│
│  ── BUILD SCRIPTS (used to regenerate data.js) ───────────────
├── build-scripts/
│   ├── kb_week1.py               Week 1 knowledge base (SQL Analytics)
│   ├── kb_week2.py               Week 2 knowledge base (SQL Optimization)
│   ├── kb_week3.py               Week 3 knowledge base (Data Modeling)
│   ├── kb_weeks4to12.py          Weeks 4–12 knowledge base
│   ├── kb_week13.py              Week 13 knowledge base (Behavioral)
│   ├── kb_week1_new.py           Week 1 updated content
│   ├── kb_week2_part1.py         Week 2 supplementary content
│   ├── enrich_data.py            Data enrichment pipeline (v1)
│   ├── enrich_data_deep.py       Data enrichment pipeline (v2, current)
│   ├── clean_data.py             Data cleaning utility
│   ├── extract_data.py           Data extraction from XLSX
│   ├── inspect_topics.py         Debug: inspect topic coverage
│   ├── build_kb_week1.py         Week 1 content builder
│   ├── build_kb_week2.py         Week 2 content builder
│   ├── build_kb_week3_p1.py      Week 3 content builder (part 1)
│   ├── build_kb_week3_combine.py Week 3 combiner
│   ├── week3_content_p1.py       Week 3 content data (part 1)
│   ├── week3_content_p2.py       Week 3 content data (part 2)
│   ├── weeks4to12_content_p1.py  Weeks 4–12 content (part 1)
│   ├── weeks4to12_content_p2.py  Weeks 4–12 content (part 2)
│   ├── weeks4to12_content_p3.py  Weeks 4–12 content (part 3)
│   └── ...                       Other step scripts
│
│  ── SOURCE DATA (reference / rebuild from these) ─────────────
└── source-data/
    ├── FAANG_DE_Prep_v3.xlsx     Original study plan spreadsheet
    ├── enriched_data.json        Full enriched dataset (1 MB)
    ├── data.json                 Raw extracted data
    ├── clean_data.json           Cleaned/normalized data
    ├── topics_map.json           Topic → week/day mapping
    ├── week3_data.pkl            Week 3 generated content (pickle)
    └── weeks4to12_data.pkl       Weeks 4–12 generated content (pickle)
```

**Total: ~3 MB, 41 files — Pure static site, zero build step to run.**

---

## ▶️ How to Run

### Option 1 — Double-click (Windows, easiest)
```
Double-click start.bat  →  browser opens automatically at http://localhost:8000
```

### Option 2 — Python (any OS)
```bash
cd faang-de-forge
python -m http.server 8000
# Open http://localhost:8000
```

### Option 3 — VS Code
Install the **Live Server** extension → right-click `index.html` → **Open with Live Server**

> ⚠️ Must be served via HTTP (not opened as `file://`) due to browser security restrictions.

---

## 🤖 AI Chatbot Setup (Free — No Credit Card)

Click the 🤖 robot button and choose your provider:

| Provider | Model | Free Limit | Get Key |
|---|---|---|---|
| ⚡ **Groq** *(recommended)* | LLaMA 3.3 70B | 30 rpm, 14,400/day | [console.groq.com/keys](https://console.groq.com/keys) |
| 🔓 **OpenRouter** | Gemma 3 27B (free) | ~20 rpm | [openrouter.ai/keys](https://openrouter.ai/keys) |
| 🔵 **Gemini** | Flash Lite | 30 rpm | [aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey) |

> Your API key is stored **only in your browser** (localStorage). It never leaves your machine.

### Groq Quick Start (5 minutes)
1. Go to [console.groq.com/keys](https://console.groq.com/keys)
2. Sign up with Google/GitHub (free, no card)
3. Click **"Create API Key"** → copy it (starts with `gsk_`)
4. Click the 🤖 robot button → Groq is pre-selected → paste key → **✓ Save Key & Start Chatting**

---

## 📚 Curriculum (91 days)

| Week | Theme | Key Topics |
|---|---|---|
| 1 | SQL Analytics | Window Functions, Rolling Windows, Gaps & Islands |
| 2 | SQL Optimization | Recursive CTEs, Execution Plans, Indexing, Joins, NULL Handling |
| 3 | Data Modeling | Normalization, Dimensional Modeling, SCD Types, NoSQL |
| 4 | Python Logic | Hash Maps, Generators, Decorators |
| 5 | Python Systems | File I/O, Parquet, S3 Patterns |
| 6 | Storage Internals | Row vs Columnar, Delta Lake, Iceberg |
| 7 | Spark Internals | Catalyst Optimizer, Shuffle, Broadcast Joins, Skew |
| 8 | Advanced Modeling | Data Vault, Late-Arriving Data |
| 9 | Quality & Contracts | dbt Tests, Great Expectations, Observability |
| 10 | Orchestration | Airflow DAGs, XComs, Patterns |
| 11 | Streaming | Kafka Pub/Sub, Consumer Groups, Exactly-Once |
| 12 | System Design | Batch ETL, CDC, Back-of-Envelope Math |
| 13 | Behavioral | STAR Method, Amazon Leadership Principles |

---

## ✨ Features

- **Progressive content** — 4 levels per topic: Concept → Example → Real-World → FAANG Scale
- **Daily schedule** — Warmup, 4 study hours, practice problems, hard problems
- **Sidebar navigation** — Week theme + topic name per day (e.g., "Monday / Window Function Basics")
- **Progress tracking** — Mark days complete, streak counter, % per week
- **Context-aware AI** — Chatbot knows what topic you're studying right now
- **Dark / Light mode** — Toggle via settings icon (top-right)
- **Keyboard shortcut** — `Ctrl + /` to open/close the chatbot

---

## 🔄 How to Regenerate Content

If you want to add/update content for any week:

```bash
# 1. Edit the KB file for the week
nano build-scripts/kb_week1.py

# 2. Run the enrichment pipeline
python build-scripts/enrich_data_deep.py

# 3. The pipeline writes to data.js automatically
```

The source of truth is the `.xlsx` spreadsheet + the `kb_*.py` knowledge base files.

---

## 🛠️ Tech Stack

Pure **vanilla HTML + CSS + JavaScript**. Zero frameworks, zero build tools, zero runtime dependencies.
Works offline once loaded (only the AI chatbot needs internet).
