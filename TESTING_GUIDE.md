# LifeOS - Testing Guide for Unified Learning Flow

## 🎯 What Was Updated

### Backend
- Simplified PDF processing (removed FAISS/embeddings)
- Unified API: single call generates chapters + quiz
- Chapter progress tracking system
- Quiz unlock mechanism after all chapters completed

### Frontend
- Complete redesign of Learning Page
- Chapter-by-chapter view with YouTube links
- Progress tracking UI
- Interactive quiz with auto-grading
- Result display with explanations

## 🚀 How to Test

### 1. Start the Backend
```bash
cd backend
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

### 2. Start the Frontend
```bash
cd frontend
npm run dev
```

### 3. Test the Complete Flow

#### Step 1: Upload a PDF
1. Go to the Learning page
2. Click "Upload PDF"
3. Select any PDF file (e.g., course syllabus, study material)
4. ✅ Should upload instantly (no FAISS processing delay)
5. You'll see the filename in the Documents list

#### Step 2: Create Study Plan
1. Fill in the "What do you want to learn?" field
   - Example: "Master React.js hooks"
2. Set duration (default: 14 days)
3. Optionally select the uploaded PDF
4. Click "Generate Study Plan"
5. ✅ Backend makes SINGLE API call to LLM
6. ✅ Response includes:
   - Title & overview
   - Multiple chapters with YouTube links
   - Quiz questions (locked initially)

#### Step 3: View Chapters
1. Click on your newly created study plan
2. You'll see:
   - Overview text
   - List of chapters (numbered)
   - Each chapter shows:
     - Title & description
     - Key topics (badges)
     - Duration estimate
     - "Watch on YouTube" button
     - "Mark Complete" button

#### Step 4: Watch Videos & Mark Complete
1. Click "Watch on YouTube" for Chapter 1
   - Opens YouTube video in new tab
   - ✅ Extension should classify this as "productive" (if extension is loaded)
2. After watching, come back and click "Mark Complete"
3. ✅ Chapter card should get a checkmark and colored border
4. Repeat for all chapters

#### Step 5: Unlock Quiz
1. Mark ALL chapters as complete
2. ✅ You should see an alert: "🎉 All chapters completed! Quiz is now unlocked."
3. The quiz section at the bottom should now show "Start Quiz" button

#### Step 6: Take the Quiz
1. Click "Start Quiz"
2. Answer all 5-10 multiple-choice questions
3. Select one option for each question
4. Click "Submit Quiz"
5. ✅ Backend auto-grades your answers

#### Step 7: View Results
1. See your score percentage (e.g., 83.3%)
2. View detailed results for each question:
   - ✓ or ✗ indicator
   - Your answer vs correct answer (if wrong)
   - Explanation for each question
3. If score >= 70%: "Great job! You've mastered this topic! 🚀"
4. If score < 70%: "Keep studying! Review the chapters again. 💪"

## 🔍 Key Things to Verify

### PDF Upload
- [ ] Upload is instant (no long processing time)
- [ ] Only filename is shown (no "chunks" or "indexed" status)
- [ ] Document appears in documents list

### Study Plan Generation
- [ ] Single API call (check browser Network tab: only 1 POST to `/api/ai/study-plan`)
- [ ] Response includes both `chapters` and `quiz` arrays
- [ ] Chapters have real YouTube URLs
- [ ] Quiz has proper structure (question, options[], correct_answer, explanation)

### Chapter Progress
- [ ] Can mark chapters complete
- [ ] Checkmark appears on completed chapters
- [ ] Progress counter updates (e.g., "3/5 completed")
- [ ] Quiz remains locked until ALL chapters done

### Quiz System
- [ ] Quiz locked initially (shows "🔒 Complete all chapters to unlock")
- [ ] Unlocks only after all chapters marked complete
- [ ] Can select answers (radio buttons)
- [ ] Submit button validates all questions answered
- [ ] Results show correct score calculation
- [ ] Explanations display properly

### UI/UX
- [ ] Clean, modern interface
- [ ] Responsive layout
- [ ] Proper loading states ("Uploading...", "Generating plan...")
- [ ] Success/error alerts work
- [ ] Back button returns to study plan view

## 🐛 Common Issues & Solutions

### Issue: PDF upload takes too long
**Solution**: Make sure backend migration ran successfully. Old FAISS code should be removed.

### Issue: Quiz doesn't unlock
**Solution**: Check that ALL chapters are marked complete. Backend checks `all_chapters_completed` flag.

### Issue: Study plan generation fails
**Solution**: Check backend logs. Ensure OpenAI/Groq API key is set in environment variables.

### Issue: Frontend shows old "chunks" data
**Solution**: Clear browser cache or hard refresh (Ctrl+Shift+R)

### Issue: YouTube links don't work
**Solution**: AI generates URLs - some may be placeholders. In production, should use real educational video URLs.

## 📊 API Endpoints Reference

### Upload PDF
```http
POST /api/ai/upload
Content-Type: multipart/form-data
```

### Create Study Plan (Unified)
```http
POST /api/ai/study-plan
{
  "goal": "Learn React hooks",
  "duration_days": 14,
  "document_id": "uuid" (optional)
}
```

### Get Progress
```http
GET /api/ai/study-plan/{plan_id}/progress
```

### Mark Chapter Complete
```http
POST /api/ai/study-plan/{plan_id}/chapter/{chapter_number}/complete
```

### Submit Quiz
```http
POST /api/ai/study-plan/{plan_id}/quiz/submit
{
  "0": 2,  // question_index: selected_option
  "1": 0,
  "2": 3
}
```

## ✅ Success Criteria

Your unified learning flow is working correctly when:

1. ✅ PDF uploads instantly (< 2 seconds)
2. ✅ Study plan generates with chapters + quiz in ONE API call
3. ✅ Can navigate to YouTube videos and watch them
4. ✅ Chapter completion tracking works
5. ✅ Quiz unlocks only after ALL chapters completed
6. ✅ Quiz auto-grades and shows detailed results
7. ✅ Entire flow is smooth and intuitive

## 🎓 Next Steps

After successful testing:
1. Add more educational content sources (not just YouTube)
2. Improve AI prompt for better chapter quality
3. Add chapter notes/summary feature
4. Implement spaced repetition for quiz retakes
5. Add study plan sharing/export
6. Track time spent on each chapter
7. Add gamification (badges, streaks)

---

**Note**: Tracking & blocking logic remains completely unchanged as per requirements.
