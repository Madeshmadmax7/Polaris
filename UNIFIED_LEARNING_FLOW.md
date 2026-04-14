# LifeOS - Unified Learning Flow (New Implementation)

## 🎯 Overview

Complete refactor of the AI/Learning system to match your requirements:
- **Fast PDF uploads** (text extraction only, no embeddings/FAISS)
- **Single API call** generates everything: YouTube chapters + quiz
- **Chapter-by-chapter learning** with completion tracking
- **Quiz unlocks** after all chapters are completed
- **Tracking & blocking logic unchanged**

---

## 📋 What Changed

### 1. **PDF Upload - Simplified**
- **Before**: PDF → chunking → embeddings → FAISS (slow, complex)
- **After**: PDF → text extraction → store in DB (instant!)
- Only shows filename in UI
- No FAISS, no vectors, just plain text storage

### 2. **Study Plan Generation**
- **Single unified API call** `/api/ai/study-plan`
- Input: PDF content (if uploaded) + user goal
- Output JSON:
  ```json
  {
    "title": "Learn Python Programming",
    "overview": "Complete Python course with videos",
    "chapters": [
      {
        "chapter_number": 1,
        "title": "Python Basics",
        "description": "Variables, data types, operators",
        "youtube_url": "https://www.youtube.com/watch?v=...",
        "duration_estimate": "15 min",
        "key_topics": ["Variables", "Print", "Input"]
      }
    ],
    "quiz": [
      {
        "question": "What is a variable in Python?",
        "options": ["A", "B", "C", "D"],
        "correct_answer": 0,
        "explanation": "..."
      }
    ]
  }
  ```

### 3. **Chapter Progress Tracking**
- New `ChapterProgress` model tracks which videos are watched
- Mark chapters as completed via API
- Frontend shows progress per chapter

### 4. **Quiz Flow**
- Quiz is **locked** until all chapters are completed
- Shows "Complete all chapters to unlock quiz" message
- Once unlocked, display 5-10 MCQ questions
- Auto-grades and shows score

---

## 🔌 API Endpoints

### Document Upload
```http
POST /api/ai/upload
Content-Type: multipart/form-data

file: <PDF file>

Response:
{
  "id": "uuid",
  "filename": "syllabus.pdf",
  "file_type": "pdf",
  "created_at": "2026-02-22T..."
}
```

### Create Study Plan (Unified)
```http
POST /api/ai/study-plan
Content-Type: application/json

{
  "goal": "Learn React.js fundamentals",
  "duration_days": 14,
  "document_id": "uuid" (optional)
}

Response:
{
  "id": "uuid",
  "title": "React.js Fundamentals",
  "goal": "Learn React.js fundamentals",
  "plan_data": {
    "title": "...",
    "overview": "...",
    "chapters": [/* YouTube chapters */],
    "quiz": [/* MCQ questions */]
  },
  "duration_days": 14,
  "created_at": "..."
}
```

### Get Study Plan with Progress
```http
GET /api/ai/study-plan/{plan_id}

Response includes chapter completion status:
{
  "id": "uuid",
  "plan_data": {
    "chapters": [
      {
        "chapter_number": 1,
        "title": "...",
        "youtube_url": "...",
        "is_completed": true,
        "completed_at": "2026-02-22T..."
      }
    ]
  },
  "quiz_unlocked": false
}
```

### Mark Chapter Complete
```http
POST /api/ai/study-plan/{plan_id}/chapter/{chapter_number}/complete

Response:
{
  "success": true,
  "chapter_completed": true,
  "all_chapters_completed": false,
  "quiz_unlocked": false
}
```

### Get Chapter Progress
```http
GET /api/ai/study-plan/{plan_id}/progress

Response:
{
  "chapters": [
    {
      "chapter_index": 1,
      "chapter_title": "...",
      "youtube_url": "...",
      "is_completed": true,
      "completed_at": "..."
    }
  ],
  "total_chapters": 5,
  "completed_chapters": 2
}
```

### Submit Quiz
```http
POST /api/ai/study-plan/{plan_id}/quiz/submit
Content-Type: application/json

{
  "0": 2,  // question_index: selected_option
  "1": 0,
  "2": 3
}

Response:
{
  "score": 66.67,
  "total_questions": 6,
  "correct_answers": 4,
  "results": [
    {
      "question_number": 0,
      "correct": true,
      "user_answer": 2,
      "correct_answer": 2,
      "explanation": "..."
    }
  ]
}
```

---

## 🎨 Frontend Integration Guide

### 1. **PDF Upload Page**
```jsx
// Show only filename, no complex status
<input type="file" onChange={uploadPDF} />
{uploading && <p>Uploading...</p>}
{document && <p>✓ {document.filename}</p>}
```

### 2. **Create Study Plan**
```jsx
// After upload, show study plan form
<form onSubmit={createStudyPlan}>
  <input name="goal" placeholder="What do you want to learn?" />
  <input name="duration_days" type="number" />
  <button>Generate Study Plan</button>
</form>
```

### 3. **Study Plan Page (New)**
```jsx
// Show chapters with YouTube links
<div className="chapters">
  {plan.plan_data.chapters.map(chapter => (
    <div key={chapter.chapter_number}>
      <h3>{chapter.title}</h3>
      <p>{chapter.description}</p>
      <a href={chapter.youtube_url} target="_blank">
        Watch on YouTube
      </a>
      {chapter.is_completed ? (
        <span>✓ Completed</span>
      ) : (
        <button onClick={() => markComplete(chapter.chapter_number)}>
          Mark Complete
        </button>
      )}
    </div>
  ))}
</div>

{plan.quiz_unlocked ? (
  <button onClick={startQuiz}>Start Quiz</button>
) : (
  <p>Complete all chapters to unlock quiz</p>
)}
```

### 4. **Quiz Page**
```jsx
// Show quiz questions after unlocked
<div className="quiz">
  {quiz.map((q, idx) => (
    <div key={idx}>
      <p>{q.question}</p>
      {q.options.map((opt, i) => (
        <label key={i}>
          <input 
            type="radio" 
            name={`q${idx}`} 
            value={i}
            onChange={(e) => setAnswers({...answers, [idx]: i})}
          />
          {opt}
        </label>
      ))}
    </div>
  ))}
  <button onClick={submitQuiz}>Submit Quiz</button>
</div>

// Show results
<div className="results">
  <h2>Score: {result.score}%</h2>
  {result.results.map(r => (
    <div key={r.question_number}>
      {r.correct ? '✓' : '✗'} Question {r.question_number + 1}
      <p>{r.explanation}</p>
    </div>
  ))}
</div>
```

---

## 🚀 Migration & Deployment

### Run Migration
```bash
cd backend
python migrate_db.py
```

### Restart Backend
```bash
cd backend
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

### Test Flow
1. Upload a PDF → should be instant
2. Create study plan → should return chapters + quiz in one call
3. Click chapter YouTube link → should classify as "productive"
4. Mark chapters complete → quiz should unlock after all done
5. Take quiz → should show score and results

---

## ✅ Requirements Met

✅ **Requirement 1**: PDF upload shows only filename, extracts text instantly, stores in DB  
✅ **Requirement 2**: Study plan includes YouTube chapters, can navigate and watch, mark complete  
✅ **Requirement 3**: Quiz unlocks after all chapters, 5-10 MCQs, auto-grades with score  
✅ **Single API Call**: `/api/ai/study-plan` returns chapters + YouTube links + quiz in one response  
✅ **Tracking/Blocking Unchanged**: All existing productivity tracking and parental controls preserved  

---

## 📝 Notes

- **YouTube Links**: AI generates real video URLs from popular educational channels
- **Productive Classification**: Frontend should auto-classify YouTube study videos as "productive"
- **Chapter Sidebar**: Implement a new sidebar page showing all chapters with progress
- **Quiz Storage**: Quiz attempts are saved in `quiz_attempts` table for history
- **No Standalone Quiz**: Removed old quiz generation endpoint, quiz is always part of study plan

---

## 🔧 Database Schema Changes

### New Tables
- `chapter_progress`: Tracks which chapters user has completed

### Modified Tables
- `documents`: Simplified (removed `chunk_count`, `faiss_index_path`, added `content`)
- `study_plans`: Added `quiz_unlocked` field

### Removed Tables
- `document_chunks`: No longer needed (no chunking)

---

## 🎯 Next Steps (Frontend)

1. Update LearningPage to show study plans with chapters
2. Create ChapterView component for video links
3. Add "Mark Complete" button for each chapter
4. Show quiz after all chapters completed
5. Update API calls to use new endpoints
6. Remove old quiz generation UI

Backend is ready! Frontend updates needed to match the new flow.
