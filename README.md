# CreatorPulse

An AI-powered newsletter curator that aggregates content from multiple sources, detects trending topics, and generates personalized newsletter drafts matching your unique writing style.

## ✨ Features

- 🔐 **User Authentication** - Secure signup/login with JWT tokens
- 📱 **Multi-Source Aggregation** - Twitter, YouTube, RSS feeds, newsletters
- 🤖 **Automated Content Fetching** - Scheduled every 4 hours
- 🔍 **AI-Powered Trend Detection** - Google Trends + keyword analysis
- ✍️ **Writing Style Analysis** - Learn your unique voice using Groq LLM
- 📧 **AI Newsletter Generation** - Personalized drafts with Llama 3.3 70B
- 📨 **Email Delivery** - Send via Resend with test mode
- 📊 **Real-time Analytics** - Track opens, clicks, and engagement
- ⏰ **Automated Scheduling** - Daily drafts at 7 AM

## 🛠️ Tech Stack

- **Frontend:** Streamlit (Python)
- **Backend:** FastAPI (Python)
- **Database:** Supabase (PostgreSQL)
- **Task Scheduling:** APScheduler
- **LLM:** Groq Cloud (Llama 3.3 70B)
- **Email:** Resend API
- **APIs:** Twitter, YouTube, Google Trends

## 📁 Project Structure

```
Assignment/
├── backend/
│   ├── app/
│   │   ├── api/              # API endpoints
│   │   │   ├── auth.py
│   │   │   ├── sources.py
│   │   │   ├── content.py
│   │   │   ├── trends.py
│   │   │   ├── style_profiles.py
│   │   │   ├── drafts.py
│   │   │   └── newsletter_sends.py
│   │   ├── core/             # Configuration
│   │   │   ├── config.py
│   │   │   └── database.py
│   │   ├── models/           # Pydantic models
│   │   ├── services/         # Business logic
│   │   └── utils/            # Utilities
│   └── requirements.txt
├── frontend/
│   ├── streamlit_app.py      # Main UI
│   ├── utils.py              # API client
│   └── requirements.txt
├── migrations/               # Database migrations
│   ├── 001_initial_schema.sql
│   ├── 002_add_style_profiles.sql
│   └── 003_complete_schema.sql
├── .env.example
├── .gitignore
└── README.md
```

## 🚀 Quick Start

### Prerequisites

- **Python 3.9+**
- **Supabase Account** - [Sign up free](https://supabase.com)
- **Groq API Key** - [Get key](https://console.groq.com)
- **Resend API Key** - [Get key](https://resend.com)
- **Optional:** Twitter, YouTube API keys for full functionality

### Installation

1. **Clone the repository**
```bash
git clone <your-repo-url>
cd Assignment
```

2. **Create and activate virtual environment**
```bash
python -m venv venv

# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r backend/requirements.txt
pip install -r frontend/requirements.txt
```

4. **Set up environment variables**
```bash
cp .env.example .env
```

Edit `.env` with your API keys:
```env
# Required
SECRET_KEY=your-secret-key-here
SUPABASE_URL=your-supabase-project-url
SUPABASE_KEY=your-supabase-anon-key
GROQ_API_KEY=your-groq-api-key
RESEND_API_KEY=your-resend-api-key

# Optional (for full functionality)
YOUTUBE_API_KEY=your-youtube-api-key
TWITTER_BEARER_TOKEN=your-twitter-bearer-token
```

5. **Set up database**

Go to your Supabase project → SQL Editor → Run:
```bash
migrations/001_initial_schema.sql
migrations/002_add_style_profiles.sql
migrations/003_complete_schema.sql
```

Or run the complete schema:
```bash
migrations/003_complete_schema.sql  # This creates all tables
```

### Running the Application

**Terminal 1 - Backend:**
```bash
cd backend
uvicorn app.main:app --reload
```

**Terminal 2 - Frontend:**
```bash
cd frontend
streamlit run streamlit_app.py
```

The app will open at `http://localhost:8501`

## 📖 Usage Guide

### First Time Setup

1. **Sign Up** - Create your account
2. **Add Sources** - Go to Sources page, add Twitter/YouTube/RSS feeds
3. **Fetch Content** - Click "Fetch New Content" (or wait for automated fetch)
4. **Detect Trends** - Click "Detect Trends" to analyze your content
5. **Train Writing Style** (Optional) - Upload 2-3 past newsletters
6. **Generate Draft** - Go to Drafts → Generate New
7. **Send Email** - Preview draft → Send test email

### Daily Workflow

The system runs automatically:
- **Content Fetch:** Every 4 hours + at 6 AM, 12 PM, 6 PM
- **Trend Detection:** 7 AM and 7 PM
- **Draft Generation:** 7 AM daily

Or trigger manually from the UI!

## 🎯 Key Features

### 1. Source Management
- Add Twitter accounts, YouTube channels, RSS feeds
- Toggle active/inactive status
- Auto-fetch content on schedule

### 2. Content Aggregation
- Fetches tweets, videos, articles
- Deduplication by URL
- Metadata extraction (author, date, etc.)

### 3. Trend Detection
- Multi-factor scoring (content mentions + Google Trends + velocity)
- Top 3 trends highlighted
- Visual trend indicators

### 4. Writing Style Training
- Upload past newsletters
- AI extracts 10+ style characteristics
- Aggregated confidence scoring
- Primary profile selection

### 5. Draft Generation
- AI-powered with Groq LLM
- Matches your writing style
- Synthesizes trends + content
- HTML + plain text formats
- Configurable options

### 6. Email Delivery
- Send via Resend API
- Test mode with warning banner
- Custom from email/name
- Delivery tracking
- Open/click analytics (when supported)

## 📊 API Endpoints

### Authentication
- `POST /api/auth/signup` - Register user
- `POST /api/auth/login` - Login & get JWT
- `GET /api/auth/me` - Get current user

### Sources
- `POST /api/sources/` - Create source
- `GET /api/sources/` - List sources
- `PATCH /api/sources/{id}` - Update source
- `DELETE /api/sources/{id}` - Delete source

### Content
- `POST /api/content/fetch` - Fetch content
- `GET /api/content/` - List content
- `GET /api/content/stats` - Get statistics

### Trends
- `POST /api/trends/detect` - Detect trends
- `GET /api/trends/top` - Get top trends
- `GET /api/trends/` - List all trends

### Style Profiles
- `POST /api/style-profiles/` - Upload newsletter
- `GET /api/style-profiles/aggregated` - Get aggregated style
- `PATCH /api/style-profiles/{id}/primary` - Set primary

### Drafts
- `POST /api/drafts/generate` - Generate draft
- `GET /api/drafts/` - List drafts
- `PATCH /api/drafts/{id}` - Update draft

### Newsletter Sends
- `POST /api/newsletter-sends/send` - Send email
- `GET /api/newsletter-sends/stats` - Get send statistics

Full API docs: `http://localhost:8000/docs`

## 🧪 Testing

1. Start backend and frontend
2. Sign up a new account
3. Add a test RSS feed (e.g., TechCrunch)
4. Fetch content
5. Detect trends
6. Generate a draft
7. Send test email to yourself

## 🔒 Environment Variables

See `.env.example` for all required and optional variables.

**Required:**
- `SECRET_KEY` - JWT signing key
- `SUPABASE_URL` - Your Supabase project URL
- `SUPABASE_KEY` - Your Supabase anon key
- `GROQ_API_KEY` - For AI generation
- `RESEND_API_KEY` - For email sending

**Optional:**
- `YOUTUBE_API_KEY` - For YouTube integration
- `TWITTER_BEARER_TOKEN` - For Twitter integration
- `RESEND_FROM_EMAIL` - Custom sender email (default: onboarding@resend.dev)

## 🐛 Troubleshooting

**Backend won't start:**
- Check all required env vars are set
- Verify Python 3.9+ is installed
- Ensure database migrations ran successfully

**Frontend errors:**
- Make sure backend is running first
- Check API_BASE_URL in `frontend/utils.py`
- Verify you're logged in

**Email sending fails:**
- Verify Resend API key is correct
- Use `onboarding@resend.dev` or verified domain
- Try test mode first

**No content fetching:**
- Check API keys for Twitter/YouTube
- Verify sources are marked as active
- RSS feeds don't require API keys

## 📝 Development Status

- ✅ **Phase 1:** Authentication
- ✅ **Phase 2:** Source Management
- ✅ **Phase 3:** Content Aggregation
- ✅ **Phase 4:** Trend Detection
- ✅ **Phase 5:** Writing Style Training
- ✅ **Phase 6:** Newsletter Draft Generation
- ✅ **Phase 7:** Email Delivery
- ✅ **Phase 8 & 9:** Analytics Dashboard

**All core features are complete and functional!**

## 🤝 Contributing

This is an assignment/portfolio project. Feel free to fork and adapt for your own use.

## 📄 License

MIT License

## 🙏 Acknowledgments

- **Groq** - Ultra-fast LLM inference
- **Resend** - Modern email API
- **Supabase** - Backend as a Service
- **Streamlit** - Rapid UI development
