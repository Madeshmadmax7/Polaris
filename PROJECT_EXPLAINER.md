# POLARIS / LifeOS — Complete Project Explainer
### Everything You Need to Explain the System End-to-End

---

## Table of Contents
1. [What Is This Project?](#1-what-is-this-project)
2. [Why It Matters — Societal Impact](#2-why-it-matters--societal-impact)
3. [System Architecture Overview](#3-system-architecture-overview)
4. [The Chrome Extension](#4-the-chrome-extension)
5. [Backend — FastAPI + MySQL](#5-backend--fastapi--mysql)
6. [The Productivity Scoring System](#6-the-productivity-scoring-system)
7. [NLP-Based Chapter Matching](#7-nlp-based-chapter-matching)
8. [AI Study Plan & Adaptive Quiz](#8-ai-study-plan--adaptive-quiz)
9. [Gamification System](#9-gamification-system)
10. [Parental Control Module](#10-parental-control-module)
11. [Frontend — React/Vite](#11-frontend--reactvite)
12. [New Features Added](#12-new-features-added)
13. [Full Data Flow — Request to Response](#13-full-data-flow--request-to-response)
14. [Database Schema](#14-database-schema)
15. [Quick-Answer Cheat Sheet](#15-quick-answer-cheat-sheet)

---

## 1. What Is This Project?

**Polaris (LifeOS)** is an AI-powered personal productivity and learning assistant. It has three components that work together:

| Component | Technology | Job |
|---|---|---|
| Chrome Extension | Manifest V3 JavaScript | Track every tab, classify websites, detect YouTube learning, block distractions |
| Backend | FastAPI + Python + MySQL | Store all data, compute scores, run NLP matching, call LLM for plans |
| Frontend | React + Vite | Dashboard, analytics, learning plans, quizzes, parental control |

**Core problem it solves:** Students spend hours online but most of it is passive consumption. There is no system that automatically connects what you watch on YouTube to a structured study plan, scores your digital behaviour, and nudges you toward better habits — until Polaris.

---

## 2. Why It Matters — Societal Impact

### 2.1 The Digital Wellbeing Crisis
- The average person switches apps/tabs **every 40 seconds** (UC Irvine study)
- Students spend 3–5 hours/day on distraction content (social media, entertainment YouTube)
- This fragmented attention causes **cognitive fatigue**, reduced memory retention, and poor academic outcomes
- 68% of students report they cannot study for more than 20 minutes without checking their phone

### 2.2 How Polaris Addresses This

| Problem | How Polaris Solves It |
|---|---|
| Unaware of time wasted | Real-time tracking classifies every website as productive/neutral/distracting and shows daily breakdown |
| Passive YouTube watching | NLP auto-matches any YouTube video you open to your study plan — turns random watching into structured learning |
| No feedback loop | Productivity Score (0–100) + XP bar gives instant feedback; you see your score drop in real-time when distracted |
| Kids' screen time unmonitored | Parental control module: parent sets limits, views child's dashboard, adjusts focus hours remotely |
| One-size-fits-all quizzes | Adaptive difficulty: if you score ≥80% on last 5 quizzes, next plan generates harder questions automatically |
| No record of what you learned | AI summary auto-generated for every completed chapter — bullet points of key takeaways |
| Boredom-driven cheating | Quiz integrity: 3 max retakes with 24-hour cooldown. Tab-switch during quiz auto-submits with penalty |

### 2.3 Who Benefits
- **Students (Primary):** Structured learning with gamification to stay motivated
- **Parents:** Transparent view of their child's digital habits without invading privacy
- **Self-learners:** Anyone learning programming, DSA, languages on YouTube gets automatic chapter tracking
- **Institutions:** Could be deployed at school level to monitor and improve digital learning habits

### 2.4 Why This Is Different From Screen Time Apps
Most screen-time apps (Android Digital Wellbeing, iOS Screen Time) only *count* minutes. Polaris:
- **Distinguishes** YouTube coding tutorials from YouTube entertainment
- **Links** browsing behaviour to structured learning goals
- **Quantifies** learning progress as a score, not just minutes
- **Motivates** through XP, ranks, and weekly streaks — behavioural psychology principles

---

## 3. System Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    USER'S BROWSER                           │
│                                                             │
│  ┌──────────────────────────────────┐   ┌───────────────┐  │
│  │     Chrome Extension (MV3)       │   │  React App    │  │
│  │  - contentScript.js              │   │  (Port 5173)  │  │
│  │  - youtubeTracker.js             │◄──►  Dashboard    │  │
│  │  - focusTracker.js               │   │  Analytics    │  │
│  │  - blockOverlay.js               │   │  Learning     │  │
│  │  - scrollTracker.js              │   │  Parental     │  │
│  │  - background.js (service worker)│   └───────┬───────┘  │
│  └──────────────┬───────────────────┘           │          │
│                 │ HTTP (every 10s)               │ HTTP/WS  │
└─────────────────┼───────────────────────────────┼──────────┘
                  │                               │
                  ▼                               ▼
        ┌─────────────────────────────────────────────────┐
        │              FastAPI Backend (Port 8000)        │
        │                                                 │
        │  /tracking   /productivity   /ai   /auth        │
        │  /parental   /analytics                         │
        │                                                 │
        │  ┌─────────────┐  ┌──────────────────────┐     │
        │  │ NLP Model   │  │  LLM (Groq/OpenAI)   │     │
        │  │ MiniLM-L6   │  │  Plan + Quiz Gen     │     │
        │  │ (384-dim)   │  │  Chapter Summaries   │     │
        │  └─────────────┘  └──────────────────────┘     │
        │                                                 │
        │  ┌───────────────────────────────────────────┐  │
        │  │         MySQL Database                    │  │
        │  │  users, tracking_logs, daily_summaries,   │  │
        │  │  study_plans, chapter_progress,           │  │
        │  │  quiz_attempts, domain_categories         │  │
        │  └───────────────────────────────────────────┘  │
        └─────────────────────────────────────────────────┘
```

**Communication Methods:**
- Extension → Backend: `fetch()` HTTP POST every 10 seconds (tracking) + real-time progress updates
- Frontend → Backend: REST API calls (React fetch via `api.js`)
- Backend → Frontend: WebSocket (`ws://localhost:8000/ws/dashboard/{token}`) for live activity updates

---

## 4. The Chrome Extension

### 4.1 Manifest V3 Architecture
The extension uses Chrome Manifest V3 (latest standard). It has:
- **Service Worker** (`background.js`): Always-on background process that manages state, batches logs, handles auth
- **Content Scripts**: Injected into every page — `contentScript.js` (general sites), `youtubeTracker.js` (YouTube only), `focusTracker.js`, `scrollTracker.js`
- **Popup**: `popup.html/js` — XP bar + quick controls

### 4.2 How a Website is Classified

**Step 1 — Domain extraction**: URL is parsed to extract base domain (`github.com`, `youtube.com`)

**Step 2 — Rules check**: `rules.json` contains domain-to-category mappings:
- `productive`: GitHub, LeetCode, GeeksForGeeks, Stack Overflow, Coursera, Khan Academy, etc.
- `distracting`: Instagram, TikTok, Facebook, Twitter, Reddit (when not in CS context), etc.
- `neutral`: Everything else (Google search, Gmail, Wikipedia, etc.)

**Step 3 — YouTube special handling**: For youtube.com, the video title is extracted and checked against a list of ~200 learning keywords (DSA, programming languages, tutorial, course, etc.). If the title contains learning keywords → classified as `productive`. If not → `distracting`.

**Step 4 — Tracking log sent**: Every window focus change is batched and sent as a POST to `/tracking/log` with:
```json
{
  "domain": "youtube.com",
  "page_title": "Dynamic Programming - Knapsack Problem Explained",
  "category": "productive",
  "duration_seconds": 247,
  "tab_switches": 2,
  "is_active": true
}
```

### 4.3 YouTube Progress Tracking (youtubeTracker.js)

This is the most complex part. Every 10 seconds while watching a YouTube video, it:

1. **Detects video change**: Compares current `video_id` (from `?v=` URL param) with previously seen ID. YouTube is an SPA — no page reload on navigation.

2. **Extracts metadata**:
   - Title: tries 4 DOM selectors (handles old UI, new UI, meta tags, document.title)
   - Channel name: queries `yt-formatted-string#owner-name`
   - Video duration: reads `videoElement.duration`
   - Current position: reads `videoElement.currentTime`
   - Ad detection: checks `#movie_player.ad-showing` CSS class — pauses tracking during ads
   - Playback rate: reads `videoElement.playbackRate` (1.0 = normal, 2.0 = 2x speed)

3. **Sends progress update** to `/ai/study-plan/{plan_id}/chapter/{n}/update-progress`:
```json
{
  "watched_seconds": 892,
  "video_duration": 1247,
  "youtube_url": "https://youtube.com/watch?v=abc123",
  "youtube_title": "Knapsack Problem - Dynamic Programming",
  "creator_name": "Striver",
  "playback_rate": 1.5
}
```

4. **NLP Matching check**: The first time a new video is detected, the background script sends the title to the backend which uses the NLP model to find the best matching chapter in any of the user's active study plans.

### 4.4 Distraction Blocking

The extension uses Chrome's `declarativeNetRequest` API (`dynamicRules.js`) to block distraction sites. Rules are fetched from the backend parental settings and applied dynamically. When a blocked site is accessed, `blockOverlay.js` injects a full-screen overlay instead of the page content.

**Reward Mode Exception**: If the user's weekly XP average ≥ 70, they can unlock "Reward Mode" for N minutes — blocking is temporarily suspended while tracking continues.

### 4.5 Focus Tracker (focusTracker.js)

Runs on every page. Tracks:
- `document.hasFocus()` — whether browser window is in foreground
- `document.hidden` — whether tab is visible (Page Visibility API)

Reports these to the background script every 3 seconds. The combination of `isFocused AND isVisible` = "truly active". This data feeds into tab_switch counting.

---

## 5. Backend — FastAPI + MySQL

### 5.1 Application Structure
```
backend/app/
├── main.py           ← FastAPI app startup, migrations, model preload
├── config/
│   ├── database.py   ← MySQL connection (SQLAlchemy)
│   └── settings.py   ← ENV vars (API keys, DB URL, thresholds)
├── models/models.py  ← All SQLAlchemy ORM models
├── routes/
│   ├── auth.py       ← JWT login/register
│   ├── tracking.py   ← Activity log ingestion
│   ├── productivity.py ← Score computation + analytics endpoints
│   ├── ai.py         ← Study plans, chapters, quiz, NLP matching
│   └── parental.py   ← Parent-child relationship, limits
├── services/
│   ├── productivity_service.py  ← Score formulas
│   ├── matching_service.py      ← NLP embedding + cosine similarity
│   ├── ai_service.py            ← LLM calls (Groq/OpenAI)
│   ├── tracking_service.py      ← Log ingestion, dedup
│   └── rag_service.py           ← PDF reading (RAG context)
└── websocket/manager.py  ← WebSocket broadcast
```

### 5.2 Authentication
JWT Bearer tokens. `/auth/register` creates user with bcrypt-hashed password. `/auth/login` returns a token. All protected routes use `Depends(get_current_user)` which validates the JWT and looks up the user row.

### 5.3 Startup Migrations (main.py lifespan)
On every startup, the app runs `ALTER TABLE ... ADD COLUMN IF NOT EXISTS` for any new columns. This means the codebase is self-migrating — no Alembic needed. Example:
```python
# Migration 4: playback_rate
conn.execute("ALTER TABLE chapter_progress ADD COLUMN playback_rate FLOAT DEFAULT 1.0")
# Migration 5: ai_summary  
conn.execute("ALTER TABLE chapter_progress ADD COLUMN ai_summary TEXT NULL")
```

### 5.4 WebSocket (Real-time Dashboard)
When the extension sends a tracking log, the backend immediately broadcasts it via WebSocket to any connected frontend:
```python
await ws_manager.send_to_user(user_id, {
    "type": "live_tracking",
    "data": { "domain": "leetcode.com", "category": "productive", ... }
})
```
The Dashboard (`DashboardPage.jsx`) connects to `ws://localhost:8000/ws/dashboard/{token}` and listens for these events — showing a "Real-time Stream" card that updates live.

---

## 6. The Productivity Scoring System

This is the core analytical engine. Every time `GET /productivity/today` is called, it recomputes from raw tracking logs.

### 6.1 Step 1 — Aggregate Daily Logs

```
productive_seconds  = Σ duration where category="productive"
neutral_seconds     = Σ duration where category="neutral"
distracting_seconds = Σ duration where category="distracting"
total_active        = productive + neutral + distracting
total_tab_switches  = Σ tab_switches from all logs
```

### 6.2 Step 2 — Focus Factor

```
FocusFactor = (productive_seconds + neutral_seconds) / total_active_seconds
```

**Why this formula?**
Focus Factor measures "non-distracted fraction of total time". The rationale: neutral browsing (Wikipedia, email) is not productive but is not *harming* focus the way entertainment does. It gives a fair picture of whether the user is at least *not distracted*, even if they're not actively learning. Range: [0.0, 1.0].

**Example:**
```
productive=3600s, neutral=1200s, distracting=600s, total=5400s
FocusFactor = (3600 + 1200) / 5400 = 4800/5400 = 0.89
```

### 6.3 Step 3 — Productivity Score

```
weighted = productive_seconds × 1.0
         + neutral_seconds × 0.3
         - distracting_seconds × 0.5

raw_score = (weighted / total_active_seconds) × 100

quiz_bonus = quiz_average × 0.1    ← up to +10 points if quiz avg = 100%

productivity_score = CLAMP(raw_score + quiz_bonus, 0, 100)
```

**Why these weights?**

| Category | Weight | Reasoning |
|---|---|---|
| Productive | +1.0 | Full credit. Directly aligned with learning goal |
| Neutral | +0.3 | Partial credit. Not harmful, moderately useful |
| Distracting | −0.5 | Penalised. Actively consumes time that could be productive |
| Quiz bonus | +0.1× | Rewards actually learning, not just being "online studying" |

**The penalty asymmetry (−0.5 vs +1.0)** is intentional: it's harder to maintain a high score than to lose it. This reflects real-life focus mechanics — one 10-minute distraction can undo 20 minutes of productive work in cognitive terms.

**Example:**
```
productive=3600s, neutral=1200s, distracting=600s, total=5400s
quiz_average=75%

weighted = 3600×1.0 + 1200×0.3 - 600×0.5
         = 3600 + 360 - 300 = 3660

raw = (3660/5400) × 100 = 67.78

quiz_bonus = 75 × 0.1 = 7.5

score = CLAMP(75.28, 0, 100) = 75.28 → rounds to 75
```

### 6.4 Trend Detection

Every 3 days of data is compared:
```
recent_avg = avg(scores[-3:])   ← last 3 days
older_avg  = avg(scores[:3])    ← first 3 days in window

if recent > older × 1.10  → trend = "improving"
if recent < older × 0.90  → trend = "declining"
else                       → trend = "stable"
```

The 10% threshold prevents noise (a 2% change shouldn't be called "improving"). This is a common technique in moving average trend analysis.

### 6.5 Daily Summary Storage

Computed scores are stored in `daily_summaries` table (upsert pattern). This makes analytics queries fast — instead of re-aggregating thousands of tracking logs for a chart, the backend reads pre-aggregated rows.

---

## 7. NLP-Based Chapter Matching

This is the most technically sophisticated component. When you open a YouTube video, the system automatically detects which chapter of your study plan you're watching — without you telling it.

### 7.1 The Model: all-MiniLM-L6-v2

- Architecture: Sentence Transformer (BERT-based, lightweight)
- Embedding dimensions: 384 floats
- Why this model: It's fast (runs on CPU in ~50ms), small (~80MB), and produces semantically meaningful sentence embeddings. It's the industry standard for semantic search tasks of this scale.
- Loaded ONCE at startup via `preload_model()` — not per-request. This avoids the 2–3 second cold start per request.

### 7.2 What Gets Embedded

**Chapter text** (at plan creation time):
```python
text = chapter_title
     + description[:300]   # First 300 chars of chapter description
     + high_importance_keywords × 2  # Repeated for emphasis (importance ≥75)
     + medium_importance_keywords × 1
```

The LLM assigns `keyword_importance` scores (0–100) when generating the study plan. High-importance words (like "fibonacci", "knapsack", "recursion") are repeated in the embedding text. This makes the embedding more sensitive to the core concepts, less sensitive to words like "tutorial" or "explained".

**Video text** (at match time):
```python
text = video_title + video_description[:300]
```

### 7.3 Cosine Similarity

Because embeddings are L2-normalised at generation time (`normalize_embeddings=True`):
```
cosine_similarity(a, b) = a · b  (dot product only, no magnitude division needed)
```

The dot product of two unit vectors equals their cosine similarity. Ranges: −1 (opposite meaning) to +1 (identical meaning).

### 7.4 Thresholds

```
THRESHOLD_MATCH   = 0.75  → Auto-assign with high confidence
THRESHOLD_CONFIRM = 0.65  → Candidate match (needs more signals)
```

**Why 0.75?**
Early testing showed that 0.80 was too strict (missed valid matches when the video title used different terminology). 0.70 was too loose (a Spring Boot E-Commerce video would match "Spring Boot Database Integration" with 0.72 — a false positive). 0.75 was the empirically determined sweet spot for CS education content.

**Incomplete chapter tiebreaker:**
```python
score = cosine_similarity
if not chapter.is_completed:
    score += 0.05  # Small bonus to prefer assigning to chapters not yet done
```

This ensures that if two chapters are equally similar, the system prefers the one you haven't finished yet — guiding you to progress rather than re-watching completed content.

### 7.5 Full Matching Flow

```
User opens YouTube video
        │
        ▼
Extension extracts title → sends to background.js
        │
        ▼  POST /ai/auto-match
Backend receives title
        │
        ├─ Embed video title (384-dim vector)
        │
        ├─ For each of user's active study plans:
        │     For each chapter:
        │       similarity = dot(chapter_embedding, video_embedding)
        │       if similarity ≥ 0.65:
        │           score = similarity + (0.05 if not completed)
        │           track as candidate
        │
        ├─ Best candidate: highest score
        │
        ├─ If sim ≥ 0.75: match_type = "semantic" → auto-assign
        │  If 0.65 ≤ sim < 0.75: match_type = "needs_confirmation"
        │
        └─ Return {plan_id, chapter_number, similarity, match_type}
                │
                ▼
        Extension stores chapter match
                │
                ▼ (every 10 seconds)
        Progress update sent to /ai/study-plan/{id}/chapter/{n}/update-progress
```

---

## 8. AI Study Plan & Adaptive Quiz

### 8.1 Plan Generation (One LLM Call)

A single Groq/OpenAI API call generates the **complete** study plan including chapters + quiz questions + daily schedule. This is the "unified flow" — no separate calls.

**Dynamic chapter count:**
```python
chapters_target = max(duration_days, min(int(duration_days × 1.8), 30))
# 7-day plan  → max(7, min(12, 30)) = 12 chapters
# 14-day plan → max(14, min(25, 30)) = 25 chapters
# 30-day plan → max(30, min(54, 30)) = 30 chapters
```

**Dynamic quiz count:**
```python
quiz_target = max(10, min(40, duration_days × 3))
# 7-day  → max(10, min(40, 21)) = 21 questions
# 14-day → max(10, min(40, 42)) = 40 questions
```

**The LLM also assigns `keyword_importance` scores per chapter** — this is what feeds into the NLP matching system. The AI knows which words are topically critical vs generically educational.

### 8.2 Adaptive Difficulty

Before calling the LLM, the backend checks the user's last 5 quiz attempts:
```python
recent_attempts = db.query(QuizAttempt).filter(user_id).limit(5).all()
avg_score = mean([a.score for a in recent_attempts])

if avg_score >= 80:   difficulty = "hard"
elif avg_score < 50:  difficulty = "easy"
else:                 difficulty = "medium"
```

This difficulty is injected into the LLM prompt:
- **Easy**: "Definition-level, direct recall, beginner-friendly, no trick questions"
- **Medium**: "Mix of recall and scenario-based, test understanding and application"
- **Hard**: "Advanced — edge cases, compare-and-contrast, code analysis, common misconceptions as wrong options"

**Why 80/50 thresholds?**
- 80% pass rate suggests the current difficulty is too easy — push harder
- Below 50% means the user is struggling — reduce friction to maintain motivation
- The 50–80 zone is the "zone of proximal development" (Vygotsky's educational theory) — learning happens here

### 8.3 Quiz Retake Limits

```
MAX_RETAKES = 3
COOLDOWN_HOURS = 24
```

If a user has already submitted 3 attempts AND their most recent attempt was within the last 24 hours, the system returns HTTP 429:
```json
{
  "message": "Maximum retakes reached. Cooldown active.",
  "attempts_used": 3,
  "max_retakes": 3,
  "cooldown_remaining_hours": 2,
  "cooldown_remaining_minutes": 15
}
```

**Why 3 attempts / 24h?**
Spacing Effect (Ebbinghaus, 1885) — distributed practice is more effective than massed practice. Forcing a gap between retakes encourages the user to review material before reattempting, not just randomly guess until correct.

### 8.4 Quiz Integrity (Anti-Cheat)

The quiz runs in full-screen mode. A `visibilitychange` event listener detects if the user switches tabs during the quiz. If they do:
1. A warning counter increments
2. After 3 tab switches, the quiz is **automatically submitted** with current answers
3. The result is marked as `terminated: true` with `termination_reason: "Tab switched X times"`

This simulates controlled exam conditions.

### 8.5 AI Chapter Summary

When a chapter is marked as completed (`is_completed = true`), a background task automatically calls the LLM to generate a summary:

```python
prompt = f"""
The student just completed a YouTube chapter.
Chapter: "{chapter_title}"
Video watched: "{youtube_title}"

Generate 4-6 bullet points summarizing:
- What concept was covered
- Why it matters
- Key takeaways to remember

Format EXACTLY as:
• bullet 1
• bullet 2
...
"""
```

The summary is stored in `chapter_progress.ai_summary` (TEXT column). It appears in the Learning page as a collapsible "What I Learned" panel — gives the student a reflective review of each completed topic.

### 8.6 PDF-Based Plans (RAG)

If a user uploads a PDF (course notes, textbook chapter), the system extracts text using `rag_service.py`. Up to 4000 characters of this content is injected into the LLM prompt — the generated study plan chapters are then based on the actual document content rather than the LLM's general knowledge.

---

## 9. Gamification System

### 9.1 Daily XP (0–100)

XP represents your **daily focus energy**. It starts at 100 each day.

**Computation (Frontend, from Backend Data):**
```
XP = 100
   + (productive_minutes × 0.3)   ← earn XP for productive browsing
   - (neutral_minutes × 0.5)      ← lose XP for neutral browsing
   - (distraction_minutes × 2.0)  ← heavily penalised for distractions

XP = CLAMP(XP, 0, 100)
```

**Why 0.3 / 0.5 / 2.0?**
The model is intentionally asymmetric:
- Productive time earns XP slowly (+0.3/min = need ~167 min to max out from 0)
- Neutral time slowly drains (-0.5/min = 200 min neutral = -100 XP)
- Distraction time drains fast (-2.0/min = 50 min distraction = -100 XP)

This reflects the real cognitive cost: 10 minutes on Instagram breaks focus that took 30 minutes of reading to build.

**Example:**
```
99 min productive + 70 min neutral + 1 min distraction:
XP = 100 + (99×0.3) - (70×0.5) - (1×2.0)
   = 100 + 29.7 - 35.0 - 2.0
   = 92.7 → 93 XP
```

### 9.2 Rank System

| XP Range | Rank | Colour |
|---|---|---|
| 90–100 | Laser Focused | #22c55e (green) |
| 70–89 | Deep Worker | #34d399 (teal) |
| 50–69 | Balanced | #f59e0b (amber) |
| 30–49 | Drifting | #f97316 (orange) |
| 0–29 | Distracted | #ef4444 (red) |

The colours are not arbitrary — green/teal signal positive states, amber/orange are warnings, red is critical. This follows standard traffic-light UX convention that users understand intuitively.

### 9.3 Level System

```
level = floor(daily_XP / 10)   → Range 0–10
```

Simple and visible. Every 10 XP points = 1 level. A user at 73 XP is "Level 7".

### 9.4 Weekend Reward System

If a user's **weekly average XP ≥ 70** (consistently performed as "Deep Worker" level), they unlock the ability to activate "Reward Mode":
- Blocking is disabled for a configurable number of minutes
- Tracking continues (the system still records and scores)
- A timer shows how much reward time is left
- Can be deactivated early

This is the positive reinforcement loop: work hard all week → earn free time. Based on **positive reinforcement** (B.F. Skinner's operant conditioning) — the reward is earned, not given freely.

### 9.5 Focus Heatmap (GitHub-style)

365 days of activity visualised as a heatmap grid. Each cell colour intensity is based on total active minutes that day (from `daily_summaries`). Streak counter is shown above the heatmap.

---

## 10. Parental Control Module

### 10.1 Parent-Child Architecture
A parent account links to one or more child accounts in the `parental_relationships` table. The parent has full read access to the child's productivity data but cannot see content of specific pages (privacy respect).

### 10.2 What Parents Can Do
- View child's productivity score in real-time
- Set daily screen time limits (total, per category, per domain)
- Define "focus hours" (e.g., 6:00 PM–8:00 PM = no distracting sites)
- See the child's top visited domains and time spent
- Enable/disable distraction blocking remotely

### 10.3 What Parents Cannot See
- Specific page titles (only domains)
- Chat messages, emails, or any page content
- The child's quiz answers or study content

This was a deliberate design choice: trust-based monitoring rather than surveillance.

---

## 11. Frontend — React/Vite

### 11.1 Pages

| Page | Route | Purpose |
|---|---|---|
| Dashboard | `/` | Live activity, productivity score, site breakdown, course progress |
| Productivity | `/productivity` | 14-day/30-day score chart, daily logs, focus trends |
| Learning | `/learning` | Study plans, chapter cards, video assignment, quiz |
| Quizzes | `/quizzes` | Quick access to pending assessments |
| Analytics | `/analytics` | XP, rank, heatmap, avatar evolution, streak, velocity |
| Parental | `/parental` | Parent view of child dashboard |
| Skills | `/skills` | Tracked skills from study plans |
| Settings | `/settings` | Preferences, extension config |

### 11.2 State Management
No Redux. Uses React Context for global state:
- `XPContext` — daily XP, rank, reward mode (available everywhere via `useXP()`)
- `useAuth` — JWT token, current user object

### 11.3 Real-time Updates
`connectDashboardWS(token, callback)` in `api.js` establishes a WebSocket connection. The Dashboard component listens and updates the "Real-time Stream" card whenever the extension logs a new page visit.

### 11.4 Design Language
- Pure black/white theme (#000 backgrounds, white text)
- `font-family: 'Outfit', sans-serif`
- Tailwind CSS utility classes (Learning, Dashboard pages)
- Inline styles with `rgba(255,255,255,0.x)` for subtle borders/backgrounds (Analytics page)
- Orange (`#fb923c`) = streak only, Green (`#34d399`) = completion/success, Red (`#f87171`) = decline/warning

---

## 12. New Features Added

### 12.1 Learning Streak
**How it works:**
- A day counts as "active" if `productive_seconds > 0` in `daily_summaries` OR any `ChapterProgress.completed_at` falls on that day
- Days are deduplicated and sorted descending
- Current streak = consecutive active days ending today (or yesterday if today has no activity yet)
- Longest streak = maximum consecutive run in history

**Why two sources (summaries + chapter completions)?**
A student might complete a chapter (productive) but not have the daily summary recomputed yet. Using both ensures no day is missed.

### 12.2 Weekly Learning Report
**Percentage change formula:**
```
pct_change = ((this_week - prev_week) / prev_week) × 100

Returns null if prev_week = 0 (avoid division by zero)
```
Displays: productive minutes, chapters completed, active days, quiz average — each with ▲▼ indicator.

### 12.3 Learning Velocity Graph
**Rolling 7-day average:**
```python
for i, point in enumerate(result):
    window = result[max(0, i-6) : i+1]   # Up to 7 days
    point["rolling_avg"] = sum(p.chapters for p in window) / len(window)
```
Uses a **trailing window** (not centred) so the most recent data point reflects the most recent trend. The graph bars show daily completion, the dashed line shows the rolling average trend.

### 12.4 Topic Coverage
For each study plan, each chapter has:
```python
watch_pct = min(100, round((watched_seconds / max(video_duration, 1)) × 100))
relative_intensity = watched_seconds / max_daily_watch_in_plan
```
`relative_intensity` is 0–1 relative to the most-watched chapter in that plan. This normalises across plans of different length.

### 12.5 Playback Speed Tracking
The extension now reads `videoElement.playbackRate` and sends it with every progress update. This is stored in `chapter_progress.playback_rate`. Shown in Topic Coverage as "2x" badge. Useful insight: a student watching at 2x speed might be reviewing a chapter they already know.

### 12.6 AI Chapter Summary
Auto-triggered as a **background task** when a chapter is marked complete. The LLM generates 4–6 bullet points summarising what was covered. Stored in `chapter_progress.ai_summary` (TEXT column). Displayed as a collapsible panel in each completed chapter card.

---

## 13. Full Data Flow — Request to Response

### 13.1 User Opens a YouTube Video → Chapter Gets Matched

```
1. youtubeTracker.js detects new video (URL change in SPA)
2. Extracts: title, channel, videoId
3. Sends to background.js via chrome.runtime.sendMessage
4. background.js calls POST /ai/auto-match  { video_title: "..." }
5. Backend:
   a. Loads all user's active study plans + chapter embeddings from DB
   b. Embeds the video title using all-MiniLM-L6-v2
   c. Computes cosine similarity against all chapters
   d. Returns best match if similarity ≥ 0.65
6. Extension stores: currentChapterMatch = { plan_id, chapter_number }
7. Every 10 seconds: sends progress to /ai/study-plan/{id}/chapter/{n}/update-progress
8. Backend updates chapter_progress: watched_seconds, video_duration, youtube_title, playback_rate
```

### 13.2 User Completes a Chapter → Summary Generated

```
1. Either:
   a. User clicks "Mark Complete" button (progressPercentage ≥ 90%)
   b. watched_seconds/video_duration ≥ 0.95 (auto-detected)
2. PUT /ai/study-plan/{id}/chapter/{n}/update-progress  { just_completed: true }
3. Backend sets chapter_progress.is_completed = True, completed_at = NOW()
4. Background task spawned: _gen_summary_sync(plan_id, chapter_n, chapter_title, youtube_title)
5. _gen_summary_sync opens NEW DB session (can't share request session)
6. Calls generate_chapter_summary() → LLM API call
7. Stores result in chapter_progress.ai_summary
8. Frontend: user clicks "📋 What I Learned" → fetches GET /ai/study-plan/{id}/chapter/{n}/summary
```

### 13.3 User Creates a Study Plan

```
1. POST /ai/study-plan  { goal: "Learn Spring Boot in 7 days", duration_days: 7 }
2. Backend:
   a. Queries last 5 QuizAttempts → computes avg_score → sets difficulty
   b. Calls generate_study_plan_with_quiz(goal, 7, difficulty="medium")
   c. LLM returns JSON: {title, chapters[], quiz[], daily_schedule[]}
   d. Parses and validates JSON
   e. For each chapter: embeds chapter text → stores 384-dim vector in DB
   f. Stores StudyPlan row + ChapterProgress rows (one per chapter)
3. Returns full plan to frontend
4. Learning page renders chapter cards
```

---

## 14. Database Schema

### Key Tables

**`users`** — Auth, profile
```
id (UUID), email, username, hashed_password, role (student/parent), 
created_at, is_active
```

**`tracking_logs`** — Raw activity data
```
id, user_id, domain, page_title, category, duration_seconds,
tab_switches, is_active, timestamp
```

**`daily_summaries`** — Pre-aggregated daily scores
```
id, user_id, date, total_active_seconds, productive_seconds,
neutral_seconds, distracting_seconds, total_tab_switches,
focus_factor, productivity_score, quiz_average, top_domains (JSON)
```
Unique index on (user_id, date) — only one summary per user per day.

**`study_plans`** — AI-generated learning plans
```
id, user_id, title, goal, duration_days, plan_data (JSON containing
chapters[] + quiz[] + daily_schedule[]), status, created_at
```

**`chapter_progress`** — Per-chapter tracking
```
id, user_id, plan_id, chapter_index, chapter_title, chapter_embedding (JSON 384-floats),
youtube_url, youtube_title, creator_name, watched_seconds, video_duration,
watch_percentage, is_completed, completed_at,
playback_rate (NEW), ai_summary (NEW),
keyword_importance (JSON), pending_assignment (bool)
```

**`quiz_attempts`** — Quiz history
```
id, user_id, plan_id, score, correct_answers, total_questions,
answers (JSON), results (JSON), terminated, termination_reason,
completed_at
```

**`domain_categories`** — User-customised site classifications
```
id, user_id, domain_pattern, category, is_global
```

---

## 15. Quick-Answer Cheat Sheet

**Q: How does the system know what category a website is?**
> `rules.json` maps domains → categories. YouTube uses keyword matching on video title. Users can override via Settings.

**Q: Why not just use screen time limits like iOS?**
> Screen time limits only count minutes. Polaris *scores quality* of time, distinguishes productive vs distracting within the same app (YouTube tutorial vs YouTube entertainment), and connects activity to structured learning goals.

**Q: How accurate is the NLP matching?**
> Tested on CS education content. Threshold 0.75 gives ~95% precision on tech topics. The keyword_importance weighting (LLM assigns per chapter at generation time) significantly improves recall for topics with highly specific vocabulary (DSA, framework names).

**Q: What if the user deletes their YouTube history?**
> Tracking is in-session only. The extension doesn't read browser history — it only watches active tab URL changes in real-time.

**Q: How is privacy handled?**
> All tracking is server-side per user. Parents see domains and scores only — not page titles or content. The backend URL is `localhost:8000` by default (self-hosted). No third-party telemetry.

**Q: What is the quiz anti-cheat mechanism?**
> Full-screen mode + `visibilitychange` event listener. 3 tab switches = auto-submit with `terminated: true` flag. The score is recorded but marked as compromised. Maximum 3 retakes with 24-hour cooldown.

**Q: How does adaptive difficulty work?**
> Last 5 quiz attempt scores are averaged. ≥80% → hard mode (edge cases, misconceptions as options). <50% → easy mode (definition-level). 50–79% → medium. Applied to the *next* study plan created, not retroactively.

**Q: What is the Reward Mode?**
> If weekly XP average ≥ 70 (Deep Worker level), user can unlock N minutes of unblocked browsing. Tracking continues during reward mode. Designed as a psychological positive reinforcement mechanism.

**Q: Why store embeddings in MySQL JSON column instead of a vector DB?**
> The scale is per-user (max ~30 chapters per plan, few plans at a time). A full vector database (Pinecone, Milvus) would be overengineered. The linear scan over ~100 chapter embeddings per user takes <50ms in Python, well within acceptable latency.

**Q: What LLM is used?**
> Configurable via `.env`. Default: Groq (Llama-3 or Mixtral) — chosen for its free tier and very fast inference. OpenAI (GPT-4) is also supported. The `_call_llm()` wrapper abstracts the provider.

**Q: How is the daily schedule generated?**
> The LLM generates it as part of the unified prompt. Chapters are distributed across days proportionally. Example: 12 chapters over 7 days → roughly 1–2 chapters per day, with heavier days for shorter/easier topics.

**Q: What happens if the LLM returns malformed JSON?**
> The response is cleaned (markdown code blocks stripped), then `json.loads()` is attempted. If parsing fails, the error is logged and an HTTP 500 is returned. A retry mechanism could be added (currently manual retry by re-creating the plan).

---

*Built with: FastAPI · SQLAlchemy · MySQL · sentence-transformers · Groq/OpenAI · React · Vite · Tailwind · Chrome MV3*

*Core algorithms: Cosine Similarity NLP, Weighted Productivity Scoring, Rolling Average, Adaptive Difficulty Selection, JWT Auth, WebSocket Real-time Updates, BackgroundTasks, PDF RAG*
