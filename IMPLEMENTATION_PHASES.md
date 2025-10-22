# 🚀 CreatorPulse: Safe Phased Implementation Plan

## 📋 Table of Contents
1. [Current Working Baseline](#baseline)
2. [Safety Principles](#safety)
3. [Phase Breakdown](#phases)
4. [Rollback Strategies](#rollback)

---

## 🎯 Current Working Baseline {#baseline}

**✅ WORKING FEATURES (DO NOT BREAK):**
- User authentication (signup/login/JWT)
- Source management (Twitter/YouTube/RSS/Newsletter)
- Content aggregation (scheduled every 4 hours)
- Trend detection (scheduled 7 AM, 7 PM)
- Style profile training
- Draft generation (scheduled 7 AM)
- Manual email sending via UI
- React frontend with all pages working

**Git Status:** Clean working tree on `main` branch

---

## 🛡️ Safety Principles {#safety}

### Rule 1: Branch-Per-Phase
- Each phase = separate git branch
- Format: `phase-X-feature-name`
- Never commit directly to `main`
- Merge only after testing

### Rule 2: Additive Changes Only
- Add NEW files, don't modify existing (when possible)
- Add NEW endpoints, don't change existing
- Add NEW database columns, don't alter existing
- Add NEW UI components, don't replace working ones

### Rule 3: Feature Flags
- All new features behind feature flags
- Environment variable control: `ENABLE_FEATURE_X=true`
- Can disable if something breaks

### Rule 4: Database Safety
- All migrations reversible
- Use `ALTER TABLE ADD COLUMN` (not DROP/RENAME)
- Keep old columns until verified working

### Rule 5: Testing Before Merge
- Test all OLD features still work
- Test NEW feature works
- Document test steps in phase doc

### Rule 6: Self-Contained Documentation
- Each phase has standalone instructions
- Can be executed by new context/session
- Includes: files to modify, exact changes, test steps

---

## 📦 PHASE BREAKDOWN {#phases}

---

## ✅ PHASE 0: Setup & Documentation (15 min)
**Goal:** Prepare for safe development

**Branch:** `main` (preparatory work)

**Tasks:**
1. Create `.env.example` backup
2. Document current API endpoints
3. Create phase tracking file
4. Tag current state: `git tag v0.9-pre-enhancement`

**Files to Create:**
- `IMPLEMENTATION_PHASES.md` (this file)
- `PHASE_TRACKER.md` (checklist)
- `.env.backup`

**No code changes - Documentation only**

**✅ Completion Criteria:**
- [ ] Git tag created
- [ ] Documentation files committed
- [ ] Backup created

---

## 🟢 PHASE 1: Review Time Tracking (Low Risk)
**Goal:** Track how long users take to review drafts

**Branch:** `phase-1-review-time-tracking`

**Why This First:** Easiest, no breaking changes, just adds timestamps

**Changes Required:**

### 1.1 Database Migration (Additive)
**File:** `migrations/020_add_review_timestamps.sql`
```sql
-- Add review timestamps to drafts table (NON-BREAKING)
ALTER TABLE drafts ADD COLUMN IF NOT EXISTS reviewed_at TIMESTAMP;
ALTER TABLE drafts ADD COLUMN IF NOT EXISTS approved_at TIMESTAMP;

-- Index for performance
CREATE INDEX IF NOT EXISTS idx_drafts_reviewed_at ON drafts(reviewed_at);
CREATE INDEX IF NOT EXISTS idx_drafts_approved_at ON drafts(approved_at);
```

### 1.2 Update Draft Model (Additive)
**File:** `backend/app/models/draft.py`
**Action:** Add two optional fields
```python
reviewed_at: Optional[datetime] = None
approved_at: Optional[datetime] = None
```

### 1.3 Update Draft Service (Additive)
**File:** `backend/app/services/draft_service.py`
**Action:** Update `update_draft()` method to set timestamps
```python
# When status changes to 'reviewed': set reviewed_at
# When status changes to 'sent': set approved_at
```

### 1.4 Update Dashboard Stats (Enhancement)
**File:** `frontend/src/pages/Dashboard.tsx`
**Action:** Calculate and display avg review time
```typescript
// Calculate: approved_at - created_at for sent drafts
```

**Test Plan:**
1. Generate new draft
2. Change status to 'reviewed' → verify `reviewed_at` set
3. Send draft → verify `approved_at` set
4. Check dashboard shows avg review time
5. **OLD TEST:** Generate draft without reviewing → should still work

**Rollback:** Drop columns if issues

**✅ Completion Criteria:**
- [ ] Migration runs successfully
- [ ] Timestamps populate on status changes
- [ ] Dashboard shows review time
- [ ] Old functionality unchanged

**Effort:** 2 hours

---

## 🟢 PHASE 2: Draft Acceptance Rate Fix (Low Risk)
**Goal:** Track proper acceptance metric (approved vs rejected)

**Branch:** `phase-2-acceptance-rate`

**Why Now:** Builds on Phase 1 timestamps, still low risk

**Changes Required:**

### 2.1 Database Migration (Additive)
**File:** `migrations/021_add_draft_outcome.sql`
```sql
-- Add outcome tracking (NON-BREAKING)
ALTER TABLE drafts ADD COLUMN IF NOT EXISTS outcome VARCHAR(20);
-- Possible values: 'accepted', 'rejected', null (pending)

-- Add rejection reason (optional)
ALTER TABLE drafts ADD COLUMN IF NOT EXISTS rejection_reason TEXT;
```

### 2.2 Update Draft Model (Additive)
**File:** `backend/app/models/draft.py`
```python
outcome: Optional[str] = None  # 'accepted', 'rejected', null
rejection_reason: Optional[str] = None
```

### 2.3 Update Draft Service Logic
**File:** `backend/app/services/draft_service.py`
```python
# When draft sent → outcome = 'accepted'
# Add new method: reject_draft(draft_id, reason)
```

### 2.4 Add Reject Button to UI
**File:** `frontend/src/pages/Drafts.tsx`
**Action:** Add "Reject Draft" button with reason dialog

### 2.5 Update Dashboard Calculation
**File:** `backend/app/services/draft_service.py` → `get_stats()`
```python
acceptance_rate = accepted_count / (accepted_count + rejected_count) * 100
```

**Test Plan:**
1. Generate draft
2. Click "Reject" → verify outcome='rejected'
3. Generate draft
4. Send draft → verify outcome='accepted'
5. Check dashboard acceptance rate calculation
6. **OLD TEST:** All existing draft operations still work

**Rollback:** Set outcome column to null

**✅ Completion Criteria:**
- [ ] Can reject drafts with reason
- [ ] Acceptance rate calculated correctly
- [ ] UI shows reject option
- [ ] Old send flow unchanged

**Effort:** 3 hours

---

## 🟡 PHASE 3: Webhook Infrastructure (Medium Risk)
**Goal:** Create webhook endpoint for Resend events

**Branch:** `phase-3-webhook-infrastructure`

**Why Now:** Foundational for analytics, isolated endpoint (won't break existing)

**Changes Required:**

### 3.1 Create Webhook Endpoint (NEW FILE)
**File:** `backend/app/api/webhooks.py` (NEW)
```python
from fastapi import APIRouter, Header, HTTPException
from typing import Optional
import hmac
import hashlib

router = APIRouter()

@router.post("/resend")
async def resend_webhook(
    payload: dict,
    svix_id: str = Header(...),
    svix_timestamp: str = Header(...),
    svix_signature: str = Header(...)
):
    """
    Handle Resend webhook events:
    - email.delivered
    - email.opened
    - email.clicked
    - email.bounced
    """
    # Verify signature
    # Update newsletter_sends table based on event type
    pass
```

### 3.2 Add Webhook to Main App
**File:** `backend/app/main.py`
```python
from app.api import webhooks

app.include_router(webhooks.router, prefix="/api/webhooks", tags=["webhooks"])
```

### 3.3 Add Webhook Secret to Config
**File:** `backend/app/core/config.py`
```python
RESEND_WEBHOOK_SECRET: Optional[str] = os.getenv("RESEND_WEBHOOK_SECRET", "")
```

### 3.4 Update Newsletter Send Service (Enhancement)
**File:** `backend/app/services/newsletter_send_service.py`
**Action:** Add method to update send record from webhook
```python
async def update_from_webhook(message_id: str, event_type: str, timestamp: datetime):
    """Update send record based on webhook event"""
    pass
```

### 3.5 Add Feature Flag
**File:** `.env`
```
ENABLE_WEBHOOKS=false  # Set to true after testing
```

**Test Plan:**
1. Start server → verify `/api/webhooks/resend` endpoint exists
2. Use curl/Postman to send test webhook payload
3. Verify signature validation works
4. Verify database updates correctly
5. **OLD TEST:** Manual email sending still works
6. **OLD TEST:** All other endpoints unchanged

**Rollback:** Remove webhook router from main.py

**✅ Completion Criteria:**
- [ ] Webhook endpoint responds to POST
- [ ] Signature validation works
- [ ] Database updates on webhook events
- [ ] Feature flag controls behavior
- [ ] No impact on existing email sending

**Effort:** 4 hours

---

## 🟡 PHASE 4: Configure Resend Webhooks (Medium Risk)
**Goal:** Connect Resend to our webhook endpoint

**Branch:** `phase-4-resend-configuration`

**Why Now:** Depends on Phase 3, enables real analytics

**Changes Required:**

### 4.1 Deploy Webhook Endpoint (Manual)
- Use ngrok for local testing: `ngrok http 8000`
- Or deploy to production server
- Get public URL: `https://your-domain.com/api/webhooks/resend`

### 4.2 Configure Resend Dashboard (Manual)
1. Go to https://resend.com/webhooks
2. Add webhook URL: `https://your-domain.com/api/webhooks/resend`
3. Subscribe to events:
   - `email.delivered`
   - `email.opened`
   - `email.clicked`
   - `email.bounced`
4. Copy webhook secret → add to `.env` as `RESEND_WEBHOOK_SECRET`

### 4.3 Enable Feature Flag
**File:** `.env`
```
ENABLE_WEBHOOKS=true
```

### 4.4 Test End-to-End
1. Send test email via UI
2. Open email in inbox
3. Click link in email
4. Check database: `opened_at` and `clicked_at` should populate
5. Check dashboard: open rate and click rate should update

**Test Plan:**
1. Send test email
2. Monitor webhook endpoint logs
3. Open email → verify webhook fires
4. Click link → verify webhook fires
5. Check database timestamps updated
6. **OLD TEST:** All existing functionality works

**Rollback:**
- Disable webhook in Resend dashboard
- Set `ENABLE_WEBHOOKS=false`

**✅ Completion Criteria:**
- [ ] Webhook receiving events from Resend
- [ ] opened_at/clicked_at populate in real-time
- [ ] Dashboard shows accurate open/click rates
- [ ] No disruption to email sending

**Effort:** 2 hours

---

## 🔴 PHASE 5: Feedback Backend (High Complexity)
**Goal:** Add thumbs up/down feedback system

**Branch:** `phase-5-feedback-backend`

**Why Now:** Independent feature, won't affect existing draft flow

**Changes Required:**

### 5.1 Create Feedback Endpoints (NEW FILE)
**File:** `backend/app/api/feedback.py` (NEW)
```python
from fastapi import APIRouter, Depends
from app.models.feedback import FeedbackCreate, FeedbackResponse

router = APIRouter()

@router.post("/", response_model=FeedbackResponse)
async def submit_feedback(feedback: FeedbackCreate, current_user = Depends(get_current_user)):
    """Submit thumbs up/down feedback on draft"""
    pass

@router.get("/draft/{draft_id}")
async def get_draft_feedback(draft_id: str, current_user = Depends(get_current_user)):
    """Get feedback for specific draft"""
    pass

@router.get("/stats")
async def get_feedback_stats(current_user = Depends(get_current_user)):
    """Get user's feedback statistics"""
    pass
```

### 5.2 Create Feedback Models (NEW FILE)
**File:** `backend/app/models/feedback.py` (NEW)
```python
class FeedbackCreate(BaseModel):
    draft_id: str
    feedback_type: str  # 'thumbs_up', 'thumbs_down'
    rating: Optional[int] = None  # 1-5
    comment: Optional[str] = None

class FeedbackResponse(BaseModel):
    id: str
    draft_id: str
    feedback_type: str
    created_at: datetime
```

### 5.3 Create Feedback Service (NEW FILE)
**File:** `backend/app/services/feedback_service.py` (NEW)
```python
async def create_feedback(user_id: str, draft_id: str, feedback_type: str, ...):
    """Store feedback in database"""
    pass

async def get_draft_feedback(user_id: str, draft_id: str):
    """Retrieve feedback for draft"""
    pass

async def calculate_feedback_stats(user_id: str):
    """Calculate thumbs up/down ratios"""
    pass
```

### 5.4 Add Feedback Router to Main
**File:** `backend/app/main.py`
```python
from app.api import feedback
app.include_router(feedback.router, prefix="/api/feedback", tags=["feedback"])
```

### 5.5 Verify Feedback Table Exists
**Check:** `migrations/` should have feedback table
**If missing, create:** `migrations/022_ensure_feedback_table.sql`

**Test Plan:**
1. POST to `/api/feedback/` → verify record created
2. GET feedback for draft → verify retrieval
3. GET stats → verify calculations
4. **OLD TEST:** Draft generation/sending unchanged
5. **OLD TEST:** All existing endpoints work

**Rollback:** Remove feedback router from main.py

**✅ Completion Criteria:**
- [ ] Can submit feedback via API
- [ ] Can retrieve feedback
- [ ] Stats endpoint works
- [ ] No impact on existing features

**Effort:** 4 hours

---

## 🔴 PHASE 6: Feedback Frontend (High Complexity)
**Goal:** Add thumbs up/down UI to drafts page

**Branch:** `phase-6-feedback-frontend`

**Why Now:** Depends on Phase 5 backend

**Changes Required:**

### 6.1 Create Feedback Component (NEW FILE)
**File:** `frontend/src/components/FeedbackButtons.tsx` (NEW)
```typescript
interface FeedbackButtonsProps {
  draftId: string;
  onFeedbackSubmitted?: () => void;
}

export function FeedbackButtons({ draftId, onFeedbackSubmitted }: FeedbackButtonsProps) {
  // Thumbs up/down buttons
  // API call to submit feedback
  // Visual feedback on click
  return (
    <div className="flex gap-2">
      <Button onClick={handleThumbsUp}>👍</Button>
      <Button onClick={handleThumbsDown}>👎</Button>
    </div>
  );
}
```

### 6.2 Add API Methods (Enhancement)
**File:** `frontend/src/lib/api.ts`
```typescript
export const api = {
  // ... existing methods ...

  feedback: {
    submit: (data: FeedbackData) =>
      fetch(`${API_BASE_URL}/feedback/`, { method: 'POST', body: JSON.stringify(data) }),
    getDraftFeedback: (draftId: string) =>
      fetch(`${API_BASE_URL}/feedback/draft/${draftId}`),
    getStats: () =>
      fetch(`${API_BASE_URL}/feedback/stats`)
  }
};
```

### 6.3 Add Feedback to Drafts Page (Enhancement)
**File:** `frontend/src/pages/Drafts.tsx`
```typescript
import { FeedbackButtons } from '@/components/FeedbackButtons';

// Add after draft preview header:
<FeedbackButtons draftId={selectedDraft.id} onFeedbackSubmitted={refetchDrafts} />
```

### 6.4 Add Feedback Stats to Dashboard (Enhancement)
**File:** `frontend/src/pages/Dashboard.tsx`
```typescript
// Add new metric card:
<Card>
  <CardHeader>Positive Feedback</CardHeader>
  <CardContent>{feedbackStats.thumbsUpRate}%</CardContent>
</Card>
```

**Test Plan:**
1. Open drafts page
2. Click thumbs up → verify API call succeeds
3. Click thumbs down → verify API call succeeds
4. Check dashboard → verify feedback stats display
5. **OLD TEST:** All existing draft operations work
6. **OLD TEST:** Can still generate/send drafts

**Rollback:** Remove FeedbackButtons import and usage

**✅ Completion Criteria:**
- [ ] Thumbs up/down buttons visible
- [ ] Clicking submits feedback
- [ ] Visual feedback on submission
- [ ] Dashboard shows feedback stats
- [ ] No breaking changes to draft flow

**Effort:** 3 hours

---

## 🔴 PHASE 7: Auto-Diff Tracking (High Complexity)
**Goal:** Track what users edit in drafts

**Branch:** `phase-7-auto-diff-tracking`

**Why Now:** Independent feature, enhances feedback system

**Changes Required:**

### 7.1 Database Migration (Additive)
**File:** `migrations/023_add_edit_history.sql`
```sql
-- Store original and edited versions
ALTER TABLE drafts ADD COLUMN IF NOT EXISTS original_content TEXT;
ALTER TABLE drafts ADD COLUMN IF NOT EXISTS edit_history JSONB DEFAULT '[]'::jsonb;

-- Update feedback table to store diffs
ALTER TABLE feedback ADD COLUMN IF NOT EXISTS content_diff JSONB;
```

### 7.2 Create Diff Utility (NEW FILE)
**File:** `backend/app/utils/diff_utils.py` (NEW)
```python
from difflib import unified_diff

def calculate_diff(original: str, edited: str) -> dict:
    """Calculate diff between original and edited content"""
    # Returns: { added_lines, removed_lines, changed_sections }
    pass

def store_edit_history(draft_id: str, diff: dict):
    """Append diff to draft's edit_history"""
    pass
```

### 7.3 Update Draft Service (Enhancement)
**File:** `backend/app/services/draft_service.py`
```python
async def update_draft(draft_id: str, updates: dict, user_id: str):
    # When content is edited:
    # 1. Get original content
    # 2. Calculate diff
    # 3. Store in edit_history
    # 4. Update draft
    pass
```

### 7.4 Store Diff on Feedback Submission
**File:** `backend/app/services/feedback_service.py`
```python
async def create_feedback(...):
    # When feedback submitted:
    # 1. Get draft's edit_history
    # 2. Store in feedback.content_diff
    pass
```

### 7.5 Add Diff Viewer Component (NEW FILE)
**File:** `frontend/src/components/DiffViewer.tsx` (NEW)
```typescript
// Visual diff display with syntax highlighting
// Shows added (green) and removed (red) lines
```

### 7.6 Add to Drafts Page (Optional)
**File:** `frontend/src/pages/Drafts.tsx`
```typescript
// Add "View Changes" button that shows diff modal
<Button onClick={() => setShowDiff(true)}>View Changes</Button>
{showDiff && <DiffViewer original={draft.original_content} edited={draft.html_content} />}
```

**Test Plan:**
1. Generate draft
2. Edit content in UI
3. Save changes → verify diff calculated
4. Check draft.edit_history → verify diff stored
5. Submit feedback → verify diff attached
6. **OLD TEST:** Draft editing still works normally

**Rollback:** Don't use diff columns, leave them empty

**✅ Completion Criteria:**
- [ ] Diffs calculated on edit
- [ ] Edit history stored in database
- [ ] Diffs attached to feedback
- [ ] Optional: UI shows diff viewer
- [ ] No breaking changes to edit flow

**Effort:** 5 hours

---

## 🔴 PHASE 8: Morning Delivery Automation (CRITICAL)
**Goal:** Auto-send draft emails at 8 AM user's local time

**Branch:** `phase-8-morning-delivery`

**Why Now:** Most complex, saved for after other features stable

**Changes Required:**

### 8.1 Database Migration (Additive)
**File:** `migrations/024_add_delivery_preferences.sql`
```sql
-- Add delivery preferences to users table
ALTER TABLE users ADD COLUMN IF NOT EXISTS delivery_enabled BOOLEAN DEFAULT true;
ALTER TABLE users ADD COLUMN IF NOT EXISTS delivery_time TIME DEFAULT '08:00:00';
ALTER TABLE users ADD COLUMN IF NOT EXISTS delivery_timezone VARCHAR(50) DEFAULT 'UTC';
```

### 8.2 Create Email Template (NEW FILE)
**File:** `backend/app/templates/morning_email.html` (NEW)
```html
<!-- Email template for morning delivery -->
<!-- Includes: Draft preview + Trends digest -->
```

### 8.3 Create Delivery Service (NEW FILE)
**File:** `backend/app/services/morning_delivery_service.py` (NEW)
```python
async def send_morning_emails():
    """Send morning emails to all users at their local 8 AM"""
    # 1. Get users with delivery_enabled=true
    # 2. Calculate if it's 8 AM in their timezone
    # 3. Get their latest draft
    # 4. Get top 3 trends
    # 5. Generate email with draft + trends
    # 6. Send via email service
    pass

async def should_send_for_user(user) -> bool:
    """Check if it's 8 AM in user's timezone"""
    pass
```

### 8.4 Add Scheduler Job
**File:** `backend/app/services/scheduler_service.py`
```python
# Add new scheduled job - runs every hour
scheduler.add_job(
    send_morning_emails_for_all_users,
    "cron",
    hour="*",  # Every hour, check which users need delivery
    id="morning_delivery",
    replace_existing=True
)
```

### 8.5 Add User Preferences API (NEW FILE)
**File:** `backend/app/api/user_preferences.py` (NEW)
```python
@router.patch("/delivery-settings")
async def update_delivery_settings(
    settings: DeliverySettings,
    current_user = Depends(get_current_user)
):
    """Update user's delivery preferences"""
    pass
```

### 8.6 Add Settings Page (NEW FILE)
**File:** `frontend/src/pages/Settings.tsx` (NEW)
```typescript
// Settings page with:
// - Enable/disable morning delivery toggle
// - Time picker (default 8 AM)
// - Timezone selector
```

### 8.7 Add Feature Flag
**File:** `.env`
```
ENABLE_MORNING_DELIVERY=false  # Set true after testing
```

**Test Plan:**
1. Set delivery_time to current time + 5 minutes
2. Wait for scheduler to run
3. Verify email received at specified time
4. Check email contains draft + trends
5. Disable via settings → verify no email sent
6. **OLD TEST:** Manual draft generation still works
7. **OLD TEST:** Manual email sending still works

**Rollback:**
- Set `ENABLE_MORNING_DELIVERY=false`
- Remove scheduler job
- Set all users' `delivery_enabled=false`

**✅ Completion Criteria:**
- [ ] Emails sent at user's local 8 AM
- [ ] Email includes draft + trends
- [ ] Users can enable/disable in settings
- [ ] Users can customize time/timezone
- [ ] No impact on manual operations

**Effort:** 8 hours

---

## 🟢 PHASE 9: CSV Bulk Upload (Medium Risk)
**Goal:** Upload multiple newsletters via CSV for style training

**Branch:** `phase-9-csv-bulk-upload`

**Why Now:** Independent feature, nice-to-have enhancement

**Changes Required:**

### 9.1 Create CSV Upload Endpoint
**File:** `backend/app/api/style_profiles.py` (Enhancement)
```python
from fastapi import UploadFile, File

@router.post("/bulk-upload")
async def bulk_upload_csv(
    file: UploadFile = File(...),
    current_user = Depends(get_current_user)
):
    """
    Upload CSV with columns: title, content
    Creates multiple style profiles at once
    """
    # Parse CSV
    # Create profile for each row
    # Return summary
    pass
```

### 9.2 Create CSV Parser Utility (NEW FILE)
**File:** `backend/app/utils/csv_parser.py` (NEW)
```python
import csv
from io import StringIO

def parse_newsletter_csv(file_content: bytes) -> list[dict]:
    """Parse CSV file with newsletter samples"""
    # Expected columns: title, content
    # Returns list of {title, content} dicts
    pass
```

### 9.3 Add Upload UI Component (NEW FILE)
**File:** `frontend/src/components/CsvUploadDialog.tsx` (NEW)
```typescript
// Dialog with file input
// Shows preview of CSV contents
// Submit button to upload
```

### 9.4 Add to Style Profiles Page (or Dashboard)
**File:** `frontend/src/pages/Dashboard.tsx` or create new page
```typescript
// Add "Bulk Upload Newsletters" button
// Opens CsvUploadDialog
```

**CSV Format Example:**
```csv
title,content
"Newsletter #42: AI Trends","Hey everyone! This week in AI..."
"Newsletter #43: Product Updates","Happy Friday! We shipped..."
```

**Test Plan:**
1. Create test CSV with 5 newsletters
2. Upload via UI
3. Verify 5 style profiles created
4. Check aggregated style includes all
5. **OLD TEST:** Single text upload still works
6. **OLD TEST:** Style analysis still works

**Rollback:** Remove endpoint from router

**✅ Completion Criteria:**
- [ ] Can upload CSV file
- [ ] Multiple profiles created from CSV
- [ ] UI shows upload progress
- [ ] No breaking changes to existing style upload

**Effort:** 4 hours

---

## 🟢 PHASE 10: Firecrawl Integration (Low Priority)
**Goal:** Add web page crawling capability

**Branch:** `phase-10-firecrawl`

**Why Last:** Mentioned as "hint", not critical for MVP

**Changes Required:**

### 10.1 Add Firecrawl Dependency
**File:** `backend/requirements.txt`
```
firecrawl-py==0.0.16
```

### 10.2 Create Firecrawl Service (NEW FILE)
**File:** `backend/app/services/firecrawl_service.py` (NEW)
```python
from firecrawl import FirecrawlApp

class FirecrawlService:
    def __init__(self, api_key: str):
        self.app = FirecrawlApp(api_key=api_key)

    async def scrape_url(self, url: str) -> dict:
        """Scrape content from URL"""
        pass

    async def crawl_site(self, url: str, limit: int = 10) -> list:
        """Crawl multiple pages from site"""
        pass
```

### 10.3 Add Firecrawl Source Type
**File:** `backend/app/services/source_service.py`
```python
# Add 'web_crawl' as new source type
# When fetching, use FirecrawlService
```

### 10.4 Add Config
**File:** `backend/app/core/config.py`
```python
FIRECRAWL_API_KEY: Optional[str] = os.getenv("FIRECRAWL_API_KEY", "")
```

### 10.5 Add UI Support
**File:** `frontend/src/pages/Sources.tsx`
```typescript
// Add "Web Crawler" option to source type dropdown
```

**Test Plan:**
1. Add web crawler source with URL
2. Trigger content fetch
3. Verify pages scraped and stored
4. **OLD TEST:** All existing source types work

**Rollback:** Don't add web_crawl sources

**✅ Completion Criteria:**
- [ ] Can add web crawler sources
- [ ] Pages scraped successfully
- [ ] Content stored like other types
- [ ] Optional: No breaking changes

**Effort:** 5 hours

---

## 🔄 Rollback Strategies {#rollback}

### Immediate Rollback (During Development)
```bash
# If something breaks during phase development:
git checkout main
git branch -D phase-X-feature-name
```

### Post-Merge Rollback
```bash
# If merged but issues found:
git revert <merge-commit-hash>
git push origin main
```

### Database Rollback
```sql
-- For each phase migration, create reverse:
-- migrations/020_add_review_timestamps.sql → migrations/020_rollback.sql

ALTER TABLE drafts DROP COLUMN IF EXISTS reviewed_at;
ALTER TABLE drafts DROP COLUMN IF EXISTS approved_at;
```

### Feature Flag Rollback
```env
# Disable feature without code changes:
ENABLE_WEBHOOKS=false
ENABLE_MORNING_DELIVERY=false
```

---

## 📊 Phase Execution Checklist

### Before Each Phase:
- [ ] Create new branch from `main`
- [ ] Ensure `main` is working and tested
- [ ] Read phase documentation completely
- [ ] Identify all files to be modified

### During Each Phase:
- [ ] Make changes incrementally
- [ ] Commit after each logical change
- [ ] Test after each commit
- [ ] Document any issues encountered

### After Each Phase:
- [ ] Run full test suite (manual or automated)
- [ ] Test all OLD features still work
- [ ] Test NEW features work
- [ ] Update `PHASE_TRACKER.md`
- [ ] Merge to `main` via PR
- [ ] Tag release: `git tag vX.Y-phase-N`
- [ ] Deploy to staging/production
- [ ] Monitor for 24 hours

---

## 🎯 Smart Context Management

### If Context Window Runs Out:

Each phase is designed to be **self-contained** with:
1. **Exact file paths** - No need to search
2. **Specific changes** - Copy-paste ready
3. **Test steps** - Verify independently
4. **Rollback steps** - Undo if needed

### Recovery Instructions:

If starting a new session mid-phase:
1. Read `IMPLEMENTATION_PHASES.md` (this file)
2. Check `PHASE_TRACKER.md` for current phase
3. Read the phase section
4. Check git branch: `git branch --show-current`
5. Review uncommitted changes: `git status`
6. Continue from where left off

---

## 📈 Estimated Timeline

| Phase | Effort | Risk | Priority |
|-------|--------|------|----------|
| 0. Setup | 15 min | None | - |
| 1. Review Time | 2 hrs | Low | High |
| 2. Acceptance Rate | 3 hrs | Low | High |
| 3. Webhook Infra | 4 hrs | Med | Critical |
| 4. Resend Config | 2 hrs | Med | Critical |
| 5. Feedback Backend | 4 hrs | High | Critical |
| 6. Feedback Frontend | 3 hrs | High | Critical |
| 7. Auto-Diff | 5 hrs | High | Medium |
| 8. Morning Delivery | 8 hrs | High | Critical |
| 9. CSV Upload | 4 hrs | Med | Medium |
| 10. Firecrawl | 5 hrs | Low | Low |

**Total:** ~40 hours (1 week of focused work)

**Recommended Pace:** 1-2 phases per day

---

## ✅ Success Criteria

After all phases complete, you should have:

- [ ] ✅ Review time tracked and displayed
- [ ] ✅ Accurate acceptance rate metric
- [ ] ✅ Open/click tracking working via webhooks
- [ ] ✅ Thumbs up/down feedback system
- [ ] ✅ Edit diff tracking
- [ ] ✅ Automated 8 AM email delivery
- [ ] ✅ CSV bulk upload for style training
- [ ] ✅ Firecrawl integration (optional)
- [ ] ✅ All original features still working
- [ ] ✅ Zero breaking changes to existing flows

---

## 🎉 Final Notes

**Remember:**
- Take breaks between phases
- Test thoroughly before merging
- When in doubt, don't merge
- Feature flags are your friend
- Documentation is future you's friend

**You've got this! 🚀**

Each phase is designed to be safe, incremental, and reversible.
Follow the plan, test thoroughly, and you'll have a complete, working product.
