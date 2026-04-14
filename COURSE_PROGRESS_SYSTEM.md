# Course Video Progress Tracking System

## Overview

This system allows users to create courses with chapters, search for YouTube videos, track watch progress, and unlock quizzes upon completion. The system integrates seamlessly with the existing tracking infrastructure without modifying the core tracking logic.

## Key Features

### 1. Course Creation with Video Search
- Users can create study plans with chapters
- Each chapter can have a custom YouTube video selected
- Search query format: `chapter+title+creator` (e.g., `introduction+dynamic+programming+striver`)
- Automatic keyword matching for video association

### 2. Video Progress Tracking
- Real-time progress tracking as videos are watched
- Progress bar showing watched time vs total duration
- Automatic completion when 90% of video is watched
- Integration with existing YouTube tracking system

### 3. Progress Visualization
- Frontend: Full progress bars for each chapter with time display
- Extension: Mini progress bars showing completion percentage
- Overall course progress aggregation

### 4. Quiz Unlock System
- Quizzes automatically unlock when all chapters are completed
- Based on watch progress, not manual marking
- Visual indicators in both frontend and extension

## How It Works

### Backend Architecture

#### Models (models.py)
```python
class ChapterProgress:
    video_duration_seconds: int  # Total video length
    watched_seconds: int         # Progress tracking
    creator_name: str            # e.g., "striver", "kunal kushwaha"
    youtube_url: str             # Video URL
```

#### Routes (routes/ai.py)
- `POST /ai/study-plan/{plan_id}/chapter/{chapter_number}/set-video`
  - Sets video URL, duration, and creator for a chapter
- `POST /ai/study-plan/{plan_id}/chapter/{chapter_number}/update-progress`
  - Updates watched seconds (called automatically by tracking system)
- `GET /ai/study-plan/{plan_id}/progress`
  - Returns full progress data including percentages

#### Tracking Integration (routes/tracking.py)
- Existing tracking logs YouTube watch time
- New function `_update_video_progress()` runs as background task
- Matches video titles to chapter titles using keyword matching
- Updates watched_seconds cumulatively
- Auto-completes chapters at 90% watch progress

### Frontend Architecture

#### Video Selection Flow
1. User creates study plan (generates chapters from AI)
2. For each chapter, user clicks "Select Video"
3. System generates search query: `chapter_title + creator_name`
4. Opens YouTube search in new tab
5. User copies video URL and duration
6. System stores video information

#### Progress Display
- Real-time progress bars for each chapter
- Shows: `watched_seconds / video_duration_seconds`
- Color-coded: incomplete (gray), in-progress (gradient), completed (green)
- Manual override: "Mark Complete" button still available

### Extension Integration

#### Popup Display
- Shows top 3 chapters with progress bars
- Mini progress bars (3px height)
- Real-time updates every 3 seconds
- Links to full course view in dashboard

## User Flow Example

### Creating a Course on "Dynamic Programming"

1. **Create Study Plan**
   - Goal: "Master Dynamic Programming"
   - AI generates chapters:
     - Chapter 1: "Introduction to Dynamic Programming"
     - Chapter 2: "Memoization Techniques"
     - Chapter 3: "Tabulation Methods"

2. **Select Videos**
   - **Chapter 1:**
     - Click "Select Video"
     - Creator: "striver"
     - Search opens: `introduction+dynamic+programming+striver`
     - Find video: https://youtube.com/watch?v=xyz
     - Duration: 15 minutes
     - System stores: URL, duration (900 seconds), creator

3. **Watch Videos**
   - Open video link
   - Existing tracking system logs watch time
   - Background task updates `watched_seconds`
   - Progress bar shows: 450s / 900s = 50%
   - Continue watching...
   - At 810s / 900s = 90% → Auto-completes!

4. **Track Progress**
   - Frontend: Full progress visualization
   - Extension: Mini progress bars
   - Overall: 1/3 chapters completed (33%)

5. **Complete Course**
   - Watch all 3 chapters to 90%+
   - Quiz automatically unlocks
   - Take quiz to test knowledge

## Technical Details

### Video Matching Algorithm
```python
def match_video_to_chapter(video_title, chapter_title):
    # Extract keywords from both titles
    video_keywords = set(video_title.lower().split())
    chapter_keywords = set(chapter_title.lower().split())
    
    # Match if at least 2 keywords overlap
    common = video_keywords & chapter_keywords
    return len(common) >= 2
```

### Auto-Completion Logic
```python
watch_percentage = (watched_seconds / video_duration_seconds) * 100
if watch_percentage >= 90:
    chapter.is_completed = True
    check_quiz_unlock()
```

### Progress Calculation
```python
progress_percentage = (watched_seconds / video_duration_seconds) * 100
```

## Database Migration

Run the migration script to add new columns:
```bash
cd backend
python migrate_video_progress.py lifeos.db
```

This adds:
- `video_duration_seconds INTEGER DEFAULT 0`
- `watched_seconds INTEGER DEFAULT 0`
- `creator_name VARCHAR(100)`

## API Endpoints

### Set Chapter Video
```http
POST /api/ai/study-plan/{plan_id}/chapter/{chapter_number}/set-video
Content-Type: application/json

{
  "video_url": "https://youtube.com/watch?v=xyz",
  "video_duration_seconds": 900,
  "creator_name": "striver"
}
```

### Update Watch Progress
```http
POST /api/ai/study-plan/{plan_id}/chapter/{chapter_number}/update-progress
Content-Type: application/json

{
  "watched_seconds": 450
}
```

### Get Progress
```http
GET /api/ai/study-plan/{plan_id}/progress

Response:
{
  "chapters": [
    {
      "chapter_index": 1,
      "chapter_title": "Introduction to DP",
      "youtube_url": "https://...",
      "video_duration_seconds": 900,
      "watched_seconds": 450,
      "progress_percentage": 50.0,
      "creator_name": "striver",
      "is_completed": false
    }
  ],
  "total_chapters": 3,
  "completed_chapters": 0
}
```

## Important Notes

### No Changes to Existing Tracking
- ✅ Existing tracking logic remains unchanged
- ✅ YouTube tracking continues to work as before
- ✅ Only adds background task for progress updates
- ✅ Non-blocking: if update fails, tracking still succeeds

### No Overlays
- ✅ No video overlays or interruptions
- ✅ Progress tracked via existing tracking system
- ✅ All UI in dashboard and extension, not on video pages

### Automatic Operation
- ✅ Video duration extracted from user input
- ✅ Progress updates happen automatically
- ✅ Quiz unlocks automatically
- ✅ Keyword matching is automatic

## Future Enhancements

1. **YouTube Data API Integration**
   - Automatic duration extraction
   - Video thumbnail display
   - Automatic video search

2. **Advanced Matching**
   - Fuzzy string matching
   - Video ID association
   - Creator channel verification

3. **Enhanced Progress**
   - Video segment tracking
   - Rewatch detection
   - Speed adjustment tracking

4. **Recommendations**
   - Alternative video suggestions
   - Creator recommendations
   - Related course suggestions
