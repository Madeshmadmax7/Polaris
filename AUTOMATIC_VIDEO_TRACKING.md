# Course Video Progress System - Technical Documentation

## Overview

This system automatically tracks YouTube video progress for course chapters without any manual input. Users simply search for videos, watch them, and the system handles everything else automatically.

## User Flow

### 1. Create Study Plan
```
User Input: "DSA dynamic programming schedule"
↓
AI generates chapters with search queries:
{
  "chapter_number": 1,
  "title": "Introduction to Dynamic Programming",
  "youtube_search_query": "dynamic+programming+introduction",
  ...
}
```

### 2. Search & Watch
```
User clicks "🔍 Search on YouTube"
↓
Opens: youtube.com/results?search_query=dynamic+programming+introduction
↓
User clicks ANY video from results
↓
System automatically detects video!
```

### 3. Automatic Detection & Tracking
```
YouTube page loads
↓
youtubeTracker.js extracts:
- Video ID, Title, URL
- Duration (from video element)
- Channel/Creator name
↓
Sends to background script
↓
background.js matches video to chapter (keyword matching)
↓
If match found: Automatically sends to backend
  - video_url
  - video_duration_seconds
  - channel_name
↓
Backend stores video details
↓
Progress bar initialized with video duration
```

### 4. Real-Time Progress Updates
```
As user watches video:
↓
Existing tracking system logs watch time
↓
tracking.py receives logs
↓
_update_video_progress() matches title to chapter
↓
Updates watched_seconds in database
↓
Frontend polls /progress endpoint
↓
Progress bar updates dynamically
```

### 5. Video Switching
```
User switches to different video on same topic
↓
youtubeTracker.js detects new video
↓
Extracts new duration automatically
↓
background.js matches to same chapter (keywords still match)
↓
Sends new video details to backend
↓
Backend updates:
  - youtube_url → new URL
  - video_duration_seconds → new duration
  - creator_name → new channel
↓
watched_seconds resets to 0
↓
Progress bar updates with new duration
```

## Technical Components

### Frontend (LearningPage.jsx)

**Simplified UI:**
- No manual input forms
- Just "Search on YouTube" button
- Opens: `youtube.com/results?search_query={chapter.youtube_search_query}`
- Shows empty progress bar initially
- Updates dynamically as user watches

**Progress Display:**
```jsx
{hasVideo ? (
  <div>
    <span>{formatDuration(watchedSeconds)} / {formatDuration(videoDuration)}</span>
    <span>{Math.round(progressPercentage)}%</span>
    <div className="progress-bar">
      <div style={{ width: `${progressPercentage}%` }} />
    </div>
  </div>
) : (
  <div>Not started - 0%</div>
)}
```

### Extension (youtubeTracker.js)

**Automatic Extraction:**
```javascript
function getVideoDuration() {
  // Method 1: Video element
  const video = document.querySelector('video');
  if (video && video.duration) {
    return Math.floor(video.duration);
  }
  
  // Method 2: Duration text
  const durationEl = document.querySelector('.ytp-time-duration');
  if (durationEl) {
    return parseDurationText(durationEl.textContent);
  }
}

function getChannelName() {
  const channel = document.querySelector('ytd-channel-name a');
  return channel ? channel.textContent.trim() : null;
}
```

**Video Info Payload:**
```javascript
{
  type: 'YOUTUBE_VIDEO_INFO',
  data: {
    title: "Introduction to DP by Striver",
    videoId: "xyz123",
    classification: "productive",
    duration_seconds: 780,         // 13 minutes
    video_url: "https://youtube.com/watch?v=xyz123",
    channel_name: "take U forward"
  }
}
```

### Background Script (background.js)

**Chapter Matching Algorithm:**
```javascript
async function matchVideoToChapter(videoData) {
  // 1. Fetch all active study plans
  const plans = await fetchStudyPlans();
  
  // 2. Extract video title keywords
  const videoWords = new Set(videoData.title.toLowerCase().split(/\s+/));
  
  // 3. Check each incomplete chapter
  for (const chapter of allIncompleteChapters) {
    const chapterWords = new Set(chapter.title.toLowerCase().split(/\s+/));
    
    // 4. Calculate keyword overlap
    const commonWords = [...videoWords].filter(w => chapterWords.has(w));
    
    // 5. Match threshold: 2 keywords OR 40% of chapter keywords
    const threshold = Math.max(2, Math.floor(chapterWords.size * 0.4));
    
    if (commonWords.length >= threshold) {
      // 6. Automatically send video details to backend
      await setChapterVideo(plan.id, chapter.index, videoData);
      return { matched: true, chapter };
    }
  }
}
```

**Automatic Backend Update:**
```javascript
// Automatically called when match found
POST /api/ai/study-plan/{plan_id}/chapter/{chapter_number}/set-video
Body: {
  video_url: "https://youtube.com/watch?v=xyz123",
  video_duration_seconds: 780,
  video_id: "xyz123",
  video_title: "Introduction to DP by Striver",
  creator_name: "take U forward"
}
```

### Backend (tracking.py)

**Automatic Progress Updates:**
```python
def _update_video_progress(db: Session, user_id: str, video_title: str, duration_seconds: int):
    """Update chapter progress if watching a course video."""
    # Find matching chapter by keywords
    chapters = db.query(ChapterProgress).filter(
        ChapterProgress.user_id == user_id,
        ChapterProgress.is_completed == False
    ).all()
    
    video_keywords = set(video_title.lower().split())
    
    for chapter in chapters:
        chapter_keywords = set(chapter.chapter_title.lower().split())
        common = chapter_keywords & video_keywords
        
        if len(common) >= 2:
            # Update watched seconds (cumulative)
            chapter.watched_seconds += duration_seconds
            
            # Auto-complete at 90%
            if chapter.video_duration_seconds > 0:
                watch_pct = (chapter.watched_seconds / chapter.video_duration_seconds) * 100
                if watch_pct >= 90:
                    chapter.is_completed = True
                    chapter.completed_at = datetime.now(timezone.utc)
            
            db.commit()
            break
```

## Data Flow Diagram

```
User Action         Extension              Background              Backend
    │                   │                       │                      │
    │  1. Click Search  │                       │                      │
    ├──────────────────►│                       │                      │
    │                   │                       │                      │
    │  2. Watch Video   │                       │                      │
    ├──────────────────►│                       │                      │
    │                   │ 3. Extract duration   │                      │
    │                   │    Extract channel    │                      │
    │                   ├──────────────────────►│                      │
    │                   │                       │ 4. Match to chapter  │
    │                   │                       │    (keyword match)   │
    │                   │                       ├─────────────────────►│
    │                   │                       │                      │ 5. Store video details
    │                   │                       │◄─────────────────────┤
    │                   │◄──────────────────────┤ 6. Confirm match     │
    │                   │                       │                      │
    │  7. Continue watching                     │                      │
    ├──────────────────►│                       │                      │
    │                   │ 8. Track watch time   │                      │
    │                   ├──────────────────────►│                      │
    │                   │                       ├─────────────────────►│ 9. Update watched_seconds
    │                   │                       │                      │
    │  10. Poll progress                        │                      │
    ├──────────────────────────────────────────────────────────────────►│
    │◄──────────────────────────────────────────────────────────────────┤ 11. Return progress
    │  12. UI updates   │                       │                      │
```

## Keyword Matching Examples

### Example 1: Perfect Match
```
Chapter: "Introduction to Dynamic Programming"
Video: "Dynamic Programming Introduction Tutorial by Abdul Bari"

Chapter words: {introduction, to, dynamic, programming}
Video words: {dynamic, programming, introduction, tutorial, ...}
Common: {introduction, dynamic, programming}
Match: ✓ (3 keywords)
```

### Example 2: Good Match
```
Chapter: "Fibonacci Series using DP"
Video: "Fibonacci with Memoization - Dynamic Programming"

Chapter words: {fibonacci, series, using, dp}
Video words: {fibonacci, with, memoization, dynamic, programming}
Common: {fibonacci, dynamic (matches dp)}
Match: ✓ (2 keywords)
```

### Example 3: No Match
```
Chapter: "Introduction to Dynamic Programming"
Video: "Binary Search Tree Tutorial"

Chapter words: {introduction, dynamic, programming}
Video words: {binary, search, tree, tutorial}
Common: {}
Match: ✗ (0 keywords)
```

## Auto-Completion Logic

```python
# Chapter auto-completes at 90% watched
watch_percentage = (watched_seconds / video_duration_seconds) * 100

if watch_percentage >= 90 and not is_completed:
    is_completed = True
    completed_at = now()
    
    # Check if all chapters complete
    if all_chapters_completed:
        plan.quiz_unlocked = True
```

**Example:**
- Video duration: 780 seconds (13 min)
- 90% threshold: 702 seconds (11.7 min)
- User watches: 705 seconds (11.75 min)
- Result: Auto-completes ✓

## API Endpoints

### Set Chapter Video (Auto-called)
```
POST /api/ai/study-plan/{plan_id}/chapter/{chapter_number}/set-video
Authorization: Bearer {token}
Content-Type: application/json

{
  "video_url": "https://youtube.com/watch?v=xyz123",
  "video_duration_seconds": 780,
  "video_id": "xyz123",
  "video_title": "Video Title",
  "creator_name": "Channel Name"
}

Response:
{
  "success": true,
  "youtube_url": "...",
  "video_duration_seconds": 780,
  "creator_name": "Channel Name"
}
```

### Update Progress (Auto-called by tracker)
```
POST /api/ai/study-plan/{plan_id}/chapter/{chapter_number}/update-progress
Authorization: Bearer {token}
Content-Type: application/json

{
  "watched_seconds": 360
}

Response:
{
  "success": true,
  "watched_seconds": 360,
  "progress_percentage": 46.15,
  "is_completed": false
}
```

### Get Progress (Polled by frontend)
```
GET /api/ai/study-plan/{plan_id}/progress
Authorization: Bearer {token}

Response:
{
  "chapters": [
    {
      "chapter_index": 1,
      "chapter_title": "Introduction to DP",
      "youtube_url": "https://...",
      "video_duration_seconds": 780,
      "watched_seconds": 360,
      "progress_percentage": 46.15,
      "creator_name": "Striver",
      "is_completed": false
    }
  ],
  "total_chapters": 5,
  "completed_chapters": 1
}
```

## Error Handling

### Video Not Detected
- Fallback: User can search again with different keywords
- Or manually mark complete if needed

### Duration Not Extracted
- Retries every 5 seconds
- Fallback: Estimated duration from AI (in chapter data)

### No Chapter Match
- Video tracked normally as YouTube activity
- Doesn't affect course progress

### Multiple Matches
- Prioritizes first incomplete chapter
- Or chapter with most keyword matches

## Performance Considerations

- **Caching**: Study plans cached in extension for 30 seconds
- **Polling**: Progress updated every 30 seconds (automatic)
- **Batching**: Tracking logs batched every 3 seconds
- **Debouncing**: Video detection waits 2 seconds for page load

## Advantages Over Manual System

1. **Zero Manual Input**: No URL/duration entry needed
2. **Flexible**: Watch ANY video on same topic
3. **Real-Time**: Progress updates automatically
4. **Smart Switching**: Handles video changes seamlessly
5. **Keyword-Based**: Works even if exact video unavailable
6. **Automatic Duration**: No need to check video length

## Future Enhancements

- YouTube Data API v3 integration for accurate durations
- Machine learning for better chapter-video matching
- Support for playlists
- Resume playback tracking
- Watch history integration
