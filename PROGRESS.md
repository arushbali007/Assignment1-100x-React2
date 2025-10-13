# CreatorPulse - Development Progress

## Project Info
- **Tech Stack**: FastAPI + Streamlit + Supabase + Groq Cloud + Resend
- **Started**: 2025-10-13
- **Current Status**: All Phases Complete ✅
- **Completed**: 2025-10-13

---

## ✅ Phase 1: Project Setup & Authentication (COMPLETE)

### What Was Built:
1. **Backend (FastAPI)**
   - Core configuration with Pydantic settings
   - Supabase client connection
   - User authentication endpoints (signup, login, /me, logout)
   - JWT token generation & verification
   - Password hashing with bcrypt
   - Authentication middleware

2. **Frontend (Streamlit)**
   - Login page with validation
   - Signup page with password confirmation
   - Protected dashboard with navigation
   - Session management
   - User profile display

3. **Database (Supabase)**
   - 7 tables: users, sources, content, trends, drafts, feedback, newsletter_sends
   - Row-level security policies
   - Indexes for performance
   - Auto-updated timestamps

4. **Configuration**
   - Environment variables configured
   - All API keys set up (Groq, Resend, Supabase)
   - Git repository initialized

### Files Created:
- `backend/app/core/config.py` - Settings management
- `backend/app/core/database.py` - Supabase client
- `backend/app/main.py` - FastAPI app
- `backend/app/models/user.py` - User models
- `backend/app/utils/security.py` - Security utilities
- `backend/app/services/auth_service.py` - Auth service
- `backend/app/api/auth.py` - Auth endpoints
- `backend/app/api/dependencies.py` - Auth middleware
- `frontend/streamlit_app.py` - Streamlit UI
- `frontend/utils.py` - API client
- `migrations/001_initial_schema.sql` - Database schema

### API Endpoints:
- POST `/api/auth/signup` - Register user
- POST `/api/auth/login` - Login & get JWT
- GET `/api/auth/me` - Get current user (protected)
- POST `/api/auth/logout` - Logout

---

## ✅ Phase 2: Source Management (COMPLETE)

### What Was Built:
1. **Source Model (Pydantic)**
   - Source types enum (Twitter, YouTube, RSS, Newsletter)
   - URL validation per source type
   - Automatic identifier extraction from URLs
   - Full CRUD schemas

2. **Source Service**
   - Create, read, update, delete operations
   - Filter by type and active status
   - Pagination support
   - Source statistics/counts

3. **Source API Endpoints**
   - POST `/api/sources/` - Create source
   - GET `/api/sources/` - List sources with filters
   - GET `/api/sources/stats` - Get source statistics
   - GET `/api/sources/{id}` - Get specific source
   - PATCH `/api/sources/{id}` - Update source
   - DELETE `/api/sources/{id}` - Delete source

4. **Streamlit UI**
   - Two-tab interface (My Sources / Add New Source)
   - Source statistics dashboard
   - Filter by type and status
   - Add new sources with validation
   - Toggle active/inactive status
   - Delete sources
   - Context-specific help for each source type

### Files Created/Modified:
- `backend/app/models/source.py` - Source Pydantic models
- `backend/app/services/source_service.py` - Source business logic
- `backend/app/api/sources.py` - Source API endpoints
- `backend/app/models/user.py` - Added UserInDB model
- `frontend/utils.py` - Added source management functions
- `frontend/streamlit_app.py` - Added source management UI
- `backend/requirements.txt` - Updated dependencies

### Dependency Updates:
- Upgraded supabase: 2.3.0 → 2.10.0
- Upgraded postgrest: 0.13.2 → 0.18.0
- Upgraded httpx: 0.24.1 → 0.27.2
- Upgraded websockets: 12.0 → 15.0.1
- Upgraded pydantic: 2.5.0 → 2.12.0

---

## ✅ Phase 3: Content Aggregation (COMPLETE)

### What Was Built:
1. **Content Models (Pydantic)**
   - ContentType enum (Tweet, Video, Article, Newsletter)
   - Full CRUD schemas for content
   - Pagination support

2. **RSS Feed Parser Service**
   - Parses RSS/Atom feeds using feedparser
   - Extracts title, body, author, published date
   - Deduplication by URL
   - Batch processing for all user RSS sources

3. **YouTube API Integration**
   - Fetches channel videos via YouTube Data API v3
   - Gets video metadata (title, description, thumbnails)
   - Channel info and upload playlists
   - Configurable video count per fetch

4. **Twitter API Integration**
   - Fetches user tweets via Twitter API v2
   - Tweet metadata with public metrics
   - Author information and entities
   - Configurable tweet count per fetch

5. **Content Aggregation Service**
   - Coordinates fetching from all source types
   - Aggregated statistics across sources
   - Error handling per source type
   - User-specific content isolation

6. **Content API Endpoints**
   - POST `/api/content/fetch` - Trigger content fetch
   - GET `/api/content/` - List content with filters & pagination
   - GET `/api/content/stats` - Get content statistics
   - GET `/api/content/{id}` - Get specific content
   - DELETE `/api/content/{id}` - Delete content

7. **Scheduler (APScheduler)**
   - Automated content fetching every 4 hours
   - Additional fetches at 6 AM, 12 PM, 6 PM
   - Runs for all users with active sources
   - Integrated into FastAPI lifespan

8. **Streamlit Content UI**
   - Content statistics dashboard
   - Manual fetch button
   - Filter by content type
   - Paginated content display
   - Content preview with metadata
   - Delete functionality

### Files Created/Modified:
- `backend/app/models/content.py` - Content Pydantic models
- `backend/app/services/rss_service.py` - RSS feed parser
- `backend/app/services/youtube_service.py` - YouTube integration
- `backend/app/services/twitter_service.py` - Twitter integration
- `backend/app/services/content_service.py` - Content aggregation coordinator
- `backend/app/services/scheduler_service.py` - APScheduler setup
- `backend/app/api/content.py` - Content API endpoints
- `backend/app/main.py` - Added content router & scheduler
- `frontend/utils.py` - Added content management functions
- `frontend/streamlit_app.py` - Added content viewing page
- `backend/requirements.txt` - Updated httpx version

### API Endpoints:
- POST `/api/content/fetch` - Fetch content from all sources
- GET `/api/content/` - Get paginated content list
- GET `/api/content/stats` - Get content statistics
- GET `/api/content/{id}` - Get specific content
- DELETE `/api/content/{id}` - Delete content

---

## ✅ Phase 4: Trend Detection (COMPLETE)

### What Was Built:
1. **Trend Models (Pydantic)**
   - Trend creation, update, and response schemas
   - Trend score calculation (0-100)
   - Velocity tracking for growth rate
   - Related content tracking

2. **Google Trends Integration**
   - pytrends library integration
   - Interest over time analysis
   - Trending searches retrieval
   - Related queries extraction
   - Batch processing for multiple keywords

3. **Keyword Extraction Service**
   - Extract keywords from content text
   - Filter stop words
   - Hashtag and mention extraction from Twitter
   - Frequency-based keyword ranking
   - Minimum mention threshold filtering

4. **Trend Detection Algorithm**
   - Multi-factor trend scoring:
     - 40% content mentions (normalized)
     - 40% Google Trends score
     - 20% velocity (growth rate)
   - Velocity calculation (last 3 days vs previous 4 days)
   - Top N trends selection
   - Automatic deduplication

5. **Trend Service**
   - Detect trends from aggregated content
   - Calculate trend scores
   - Save trends to database
   - Get top 3 trends
   - Trend statistics

6. **Trend API Endpoints**
   - POST `/api/trends/detect` - Trigger trend detection
   - GET `/api/trends/top` - Get top N trends
   - GET `/api/trends/stats` - Get trend statistics
   - GET `/api/trends/` - List all trends with pagination
   - GET `/api/trends/{id}` - Get specific trend
   - DELETE `/api/trends/{id}` - Delete trend

7. **Scheduler Integration**
   - Automated trend detection twice daily (7 AM, 7 PM)
   - Runs for all users with content
   - Integrated with existing scheduler

8. **Streamlit Trends UI**
   - Trend statistics dashboard
   - Top 3 trends highlight with visual indicators
   - Manual trend detection button
   - Paginated trends list
   - Detailed trend metrics:
     - Overall score with color coding
     - Google Trends score
     - Content mentions count
     - Velocity (growth rate)
     - Related content IDs
   - Delete functionality

### Files Created/Modified:
- `backend/app/models/trend.py` - Trend Pydantic models
- `backend/app/services/google_trends_service.py` - Google Trends integration
- `backend/app/services/keyword_extraction_service.py` - Keyword extraction
- `backend/app/services/trend_service.py` - Trend detection & ranking
- `backend/app/api/trends.py` - Trend API endpoints
- `backend/app/main.py` - Added trends router
- `backend/app/services/scheduler_service.py` - Added trend detection schedule
- `frontend/utils.py` - Added trend management functions
- `frontend/streamlit_app.py` - Added trends viewing page

### API Endpoints:
- POST `/api/trends/detect` - Detect and save trends
- GET `/api/trends/top` - Get top N trending topics
- GET `/api/trends/stats` - Get trend statistics
- GET `/api/trends/` - Get paginated trends list
- GET `/api/trends/{id}` - Get specific trend
- DELETE `/api/trends/{id}` - Delete trend

---

## ✅ Phase 5: Writing Style Training (COMPLETE)

### What Was Built:
1. **Style Profile Models (Pydantic)**
   - StyleProfileCreate, StyleProfileUpdate, StyleProfileResponse schemas
   - StyleAnalysis schema with 10+ style characteristics
   - StyleSummary for aggregated style analysis
   - Pagination support for profile lists

2. **Style Analysis Service (Groq LLM)**
   - AI-powered writing style analysis using Groq Cloud
   - Llama 3.3 70B model for deep analysis
   - Extracts 10 key style characteristics:
     - Tone (professional, casual, witty, etc.)
     - Voice (first-person, we-voice, expert, etc.)
     - Sentence structure patterns
     - Vocabulary complexity level
     - Opening and closing styles
     - Formatting preferences
     - Use of humor
     - Call-to-action style
     - Personal touches
   - Statistical analysis (avg sentence/paragraph length)
   - Key phrase extraction
   - Aggregate multiple profiles into unified style

3. **Style Profile Service**
   - Create and analyze style profiles from newsletter text
   - Get user's style profiles with pagination
   - Primary profile management
   - Delete profiles with auto-reassignment of primary
   - Aggregated style summary across all profiles
   - Style confidence scoring based on sample count

4. **Style Profile API Endpoints**
   - POST `/api/style-profiles/` - Upload and analyze newsletter
   - GET `/api/style-profiles/` - List profiles with pagination
   - GET `/api/style-profiles/primary` - Get primary profile
   - GET `/api/style-profiles/aggregated` - Get aggregated style
   - GET `/api/style-profiles/stats` - Get statistics
   - GET `/api/style-profiles/{id}` - Get specific profile
   - PATCH `/api/style-profiles/{id}/primary` - Set as primary
   - DELETE `/api/style-profiles/{id}` - Delete profile

5. **Streamlit Writing Style UI**
   - Three-tab interface:
     - **Style Summary Tab**: Aggregated analysis with confidence scoring
     - **My Profiles Tab**: View and manage uploaded newsletters
     - **Upload Newsletter Tab**: Paste and analyze new newsletters
   - Style statistics dashboard
   - Real-time AI analysis feedback
   - Primary profile indicator (⭐)
   - Text preview for each newsletter
   - Confidence visualization with progress bar
   - Set/unset primary profile
   - Delete profiles

6. **Database Migration**
   - Created `style_profiles` table
   - Columns: newsletter_text, newsletter_title, style_data (JSONB), is_primary
   - Indexes on user_id, is_primary, created_at
   - Row-level security policies
   - Auto-updated timestamps

### Files Created/Modified:
- `backend/app/models/style_profile.py` - Style profile Pydantic models
- `backend/app/services/style_analysis_service.py` - Groq LLM integration
- `backend/app/services/style_profile_service.py` - Profile management
- `backend/app/api/style_profiles.py` - API endpoints
- `backend/app/main.py` - Added style_profiles router
- `frontend/utils.py` - Added style profile functions
- `frontend/streamlit_app.py` - Added Writing Style page
- `migrations/002_add_style_profiles.sql` - Database migration
- `migrations/README.md` - Updated with new migration

### API Endpoints:
- POST `/api/style-profiles/` - Upload & analyze newsletter
- GET `/api/style-profiles/` - Get paginated profiles
- GET `/api/style-profiles/primary` - Get primary profile
- GET `/api/style-profiles/aggregated` - Get aggregated style
- GET `/api/style-profiles/stats` - Get statistics
- GET `/api/style-profiles/{id}` - Get specific profile
- PATCH `/api/style-profiles/{id}/primary` - Set primary
- DELETE `/api/style-profiles/{id}` - Delete profile

### Key Features:
- ✅ AI-powered style analysis with Groq Cloud (Llama 3.3 70B)
- ✅ 10+ style characteristics extracted
- ✅ Multi-newsletter aggregation for better accuracy
- ✅ Confidence scoring (improves with more samples)
- ✅ Primary profile selection
- ✅ Statistical analysis (sentence/paragraph lengths)
- ✅ Key phrase extraction
- ✅ Fallback analysis if LLM fails
- ✅ JSON-based style data storage (JSONB)
- ✅ User-friendly Streamlit interface

---

## ✅ Phase 6: Newsletter Draft Generation (COMPLETE)

### What Was Built:
1. **Draft Models (Pydantic)**
   - DraftStatus enum (pending, reviewed, edited, sent, archived)
   - NewsletterBlock for structured content sections
   - DraftContent for full newsletter structure
   - DraftMetadata for generation tracking
   - Full CRUD schemas with pagination support

2. **Newsletter Generation Service (Groq LLM)**
   - AI-powered draft generation using Groq Cloud (Llama 3.3 70B)
   - Synthesizes trends and recent content into cohesive narrative
   - Style-aware generation matching user's writing voice
   - Structured newsletter with:
     - Compelling subject line (50-70 characters)
     - Personalized greeting & introduction
     - 2-3 main content blocks (3-5 paragraphs each)
     - Optional "Trends to Watch" section
     - Closing paragraph & call-to-action
     - Professional sign-off
   - HTML email generation with responsive design
   - Plain text alternative generation
   - Fallback template-based generation if LLM fails
   - Context building from trends, content, and style profiles

3. **Draft Service**
   - Coordinate draft generation with database operations
   - Pull top trends, recent content, and style profiles
   - Save drafts with metadata to database
   - Prevent duplicate daily drafts
   - Full CRUD operations
   - Draft statistics and filtering

4. **Draft API Endpoints**
   - POST `/api/drafts/generate` - Generate new draft
   - GET `/api/drafts/` - List drafts with pagination & filters
   - GET `/api/drafts/stats` - Get draft statistics
   - GET `/api/drafts/{id}` - Get specific draft
   - PATCH `/api/drafts/{id}` - Update draft status/content
   - DELETE `/api/drafts/{id}` - Delete draft

5. **Scheduler Integration**
   - Automated daily draft generation at 7 AM
   - Runs for all users with detected trends
   - Smart duplicate prevention

6. **Streamlit Draft UI**
   - Two-tab interface:
     - **My Drafts Tab**: View, filter, and manage drafts
     - **Generate New Tab**: Create new drafts with options
   - Draft statistics dashboard (5 metrics)
   - Status management buttons (review, send, archive, delete)
   - HTML preview with iframe rendering
   - Plain text alternative view
   - Filter by status (all, pending, reviewed, sent, archived)
   - Generation options:
     - Include/exclude trends section
     - Configurable max trends (1-5)
     - Force regenerate option
   - Prerequisites checking (trends & style profiles)
   - Generation metadata display (time, trends used, content count)
   - Paginated draft list (5 per page)

### Files Created/Modified:
- `backend/app/models/draft.py` - Draft Pydantic models
- `backend/app/services/newsletter_generation_service.py` - AI generation service
- `backend/app/services/draft_service.py` - Draft management service
- `backend/app/api/drafts.py` - Draft API endpoints
- `backend/app/main.py` - Added drafts router
- `backend/app/services/scheduler_service.py` - Added draft generation schedule
- `frontend/utils.py` - Added draft management functions
- `frontend/streamlit_app.py` - Added draft viewing and generation page

### API Endpoints:
- POST `/api/drafts/generate` - Generate new newsletter draft
- GET `/api/drafts/` - Get paginated drafts with filters
- GET `/api/drafts/stats` - Get draft statistics
- GET `/api/drafts/{id}` - Get specific draft
- PATCH `/api/drafts/{id}` - Update draft
- DELETE `/api/drafts/{id}` - Delete draft

### Key Features:
- ✅ AI-powered personalized newsletter generation
- ✅ Style-aware content matching user's writing voice
- ✅ Trend-driven content synthesis
- ✅ Professional HTML email templates with responsive design
- ✅ Draft lifecycle management (pending/reviewed/sent/archived)
- ✅ Real-time HTML preview in Streamlit
- ✅ Automated daily generation via scheduler
- ✅ Generation metadata tracking
- ✅ Configurable trend inclusion & count
- ✅ Smart duplicate prevention
- ✅ Plain text alternative generation
- ✅ Fallback generation if LLM fails

---

## ✅ Phase 7: Review & Delivery (COMPLETE)

### What Was Built:
1. **Email Delivery Service (Resend Integration)**
   - Resend API integration for email sending
   - Send newsletter to single recipient
   - Send test emails with [TEST] banner and warning
   - Bulk sending to multiple recipients
   - Email validation
   - HTML + plain text support
   - Custom from email/name configuration

2. **Newsletter Send Tracking Models**
   - SendStatus enum (pending, sending, sent, failed, bounced, delivered, opened, clicked)
   - SendCreate, BulkSendCreate schemas
   - SendUpdate for status tracking
   - NewsletterSendResponse with full metadata
   - SendStats for analytics (open rate, click rate, etc.)
   - BulkSendResult for batch operations

3. **Newsletter Send Service**
   - Send single newsletter with status tracking
   - Bulk send to multiple recipients
   - Message ID tracking from Resend
   - Delivery, open, and click tracking support
   - Test vs. production send differentiation
   - Automatic draft status update on send
   - Error handling and retry logic
   - Send statistics and analytics

4. **Newsletter Send API Endpoints**
   - POST `/api/newsletter-sends/send` - Send to single recipient
   - POST `/api/newsletter-sends/send-bulk` - Send to multiple recipients
   - GET `/api/newsletter-sends/` - List sends with pagination & filters
   - GET `/api/newsletter-sends/stats` - Get send statistics
   - GET `/api/newsletter-sends/{id}` - Get specific send
   - PATCH `/api/newsletter-sends/{id}` - Update send status (for tracking)

5. **Streamlit Send UI**
   - Send email form in draft preview
   - Test mode toggle with warning banner
   - Custom from email/name fields
   - Recipient email input with validation
   - Real-time send feedback and status
   - Auto-update draft status after sending
   - Message ID display on success
   - Helpful tips for Resend configuration

### Files Created/Modified:
- `backend/app/services/email_service.py` - Resend email service
- `backend/app/models/newsletter_send.py` - Send tracking models
- `backend/app/services/newsletter_send_service.py` - Send management service
- `backend/app/api/newsletter_sends.py` - Send API endpoints
- `backend/app/core/config.py` - Added RESEND_FROM_EMAIL setting
- `backend/app/main.py` - Added newsletter_sends router
- `frontend/utils.py` - Added send email functions
- `frontend/streamlit_app.py` - Added send email UI in draft preview

### API Endpoints:
- POST `/api/newsletter-sends/send` - Send newsletter email
- POST `/api/newsletter-sends/send-bulk` - Bulk send to multiple recipients
- GET `/api/newsletter-sends/` - List all sends with filters
- GET `/api/newsletter-sends/stats` - Get send statistics
- GET `/api/newsletter-sends/{id}` - Get specific send
- PATCH `/api/newsletter-sends/{id}` - Update send status

### Key Features:
- ✅ Resend API integration for email delivery
- ✅ Test email mode with warning banners
- ✅ Single and bulk send support
- ✅ Complete send tracking (pending → sent → delivered → opened → clicked)
- ✅ Custom from email/name configuration
- ✅ HTML + plain text email support
- ✅ Message ID tracking
- ✅ Send statistics and analytics
- ✅ Automatic draft status updates
- ✅ User-friendly send UI in Streamlit
- ✅ Email validation
- ✅ Error handling and user feedback

---

## ✅ Phase 8 & 9: Dashboard & Analytics (COMPLETE)

### What Was Built:
1. **Real-time Dashboard Analytics**
   - Live metrics for sources, content, drafts, sent emails
   - Open rate tracking
   - Send statistics (successful, failed, test sends)
   - Quick action buttons for common workflows:
     - Add Source
     - Fetch Content
     - Detect Trends
     - Generate Draft

2. **Send Analytics in Newsletter Sends**
   - Delivery tracking (pending → sent → delivered)
   - Open tracking (opened_at timestamp)
   - Click tracking (clicked_at timestamp)
   - Message ID tracking from Resend
   - Success/failure status monitoring
   - Test vs. production send differentiation

3. **Statistics APIs**
   - GET `/api/sources/stats` - Source statistics
   - GET `/api/content/stats` - Content statistics
   - GET `/api/drafts/stats` - Draft statistics
   - GET `/api/newsletter-sends/stats` - Send analytics

4. **Streamlit Dashboard Updates**
   - Five-metric header (Sources, Content, Drafts, Sent, Open Rate)
   - Color-coded status indicators
   - Real-time data refresh
   - Contextual quick actions
   - User-friendly error handling

### Files Modified:
- `frontend/streamlit_app.py` - Updated dashboard with real analytics
- `frontend/utils.py` - Added get_send_stats() function
- `backend/app/api/newsletter_sends.py` - Stats endpoint implemented
- `backend/app/services/newsletter_send_service.py` - Analytics calculations

### Key Features:
- ✅ Real-time usage statistics
- ✅ Email open rate tracking
- ✅ Delivery status monitoring
- ✅ Send success/failure tracking
- ✅ Test vs. production differentiation
- ✅ Quick action buttons on dashboard
- ✅ Aggregated analytics across all endpoints
- ✅ User-friendly metric displays

---

## 🎉 PROJECT COMPLETE

All 9 phases have been successfully implemented:
- ✅ Phase 1: Project Setup & Authentication
- ✅ Phase 2: Source Management
- ✅ Phase 3: Content Aggregation
- ✅ Phase 4: Trend Detection
- ✅ Phase 5: Writing Style Training
- ✅ Phase 6: Newsletter Draft Generation
- ✅ Phase 7: Review & Delivery
- ✅ Phase 8 & 9: Dashboard & Analytics

### Ready for Testing
The application is now complete and ready for end-to-end testing.

---

## Important Notes

### API Keys Configured:
- ✅ Groq Cloud API
- ✅ Resend API
- ✅ Supabase (URL + Key)

### Database:
- ✅ All 7 tables created in Supabase
- ✅ RLS policies enabled

### To Resume Development:
1. Make sure you're in the Assignment directory
2. Backend: `cd backend && source venv/bin/activate && uvicorn app.main:app --reload`
3. Frontend: `cd frontend && streamlit run streamlit_app.py`

### Testing Checklist:
- [ ] Signup new user
- [ ] Login with credentials
- [ ] View dashboard
- [ ] Logout and re-login

---

## 🚀 Ready to Test!

### Testing Checklist:
1. **Authentication**
   - [ ] Signup new user
   - [ ] Login with credentials
   - [ ] View user profile
   - [ ] Logout and re-login

2. **Source Management**
   - [ ] Add RSS feed (e.g., TechCrunch)
   - [ ] Add Twitter account (if API key configured)
   - [ ] Add YouTube channel (if API key configured)
   - [ ] Toggle source active/inactive
   - [ ] Delete a source

3. **Content Aggregation**
   - [ ] Fetch content manually
   - [ ] View fetched content
   - [ ] Filter by content type
   - [ ] Verify deduplication works

4. **Trend Detection**
   - [ ] Detect trends manually
   - [ ] View top 3 trends
   - [ ] Check trend scores and metrics
   - [ ] Verify Google Trends integration

5. **Writing Style Training**
   - [ ] Upload 2-3 past newsletters
   - [ ] View style analysis results
   - [ ] Check aggregated style summary
   - [ ] Set primary profile

6. **Draft Generation**
   - [ ] Generate newsletter draft
   - [ ] Preview HTML in browser
   - [ ] Check plain text version
   - [ ] Update draft status (review, archive)

7. **Email Delivery**
   - [ ] Send test email to yourself
   - [ ] Verify [TEST] banner appears
   - [ ] Send production email
   - [ ] Check send status in UI

8. **Analytics Dashboard**
   - [ ] View dashboard metrics
   - [ ] Check open rate calculations
   - [ ] Use quick action buttons
   - [ ] Verify real-time updates

9. **Scheduler (Background)**
   - [ ] Wait for automated content fetch (every 4 hours)
   - [ ] Wait for automated trend detection (7 AM/7 PM)
   - [ ] Wait for automated draft generation (7 AM daily)

### Start the Application:
```bash
# Terminal 1 - Backend
cd backend
uvicorn app.main:app --reload

# Terminal 2 - Frontend
cd frontend
streamlit run streamlit_app.py
```

### Troubleshooting:
- Check README.md for detailed setup instructions
- Verify all environment variables are set in .env
- Ensure database migrations are applied
- Review API documentation at http://localhost:8000/docs
