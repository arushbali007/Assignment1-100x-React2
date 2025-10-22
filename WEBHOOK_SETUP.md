# Resend Webhook Setup Guide

## Overview
Phase 3 adds webhook support for tracking email delivery, opens, and clicks via Resend.

## Setup Steps

### 1. Deploy Your Backend (Required)

Webhooks need a publicly accessible URL. Choose one:

**Option A: Local Testing with ngrok (Recommended for development)**
```bash
# Install ngrok: https://ngrok.com/download
ngrok http 8000

# Copy the HTTPS URL (e.g., https://abc123.ngrok.io)
```

**Option B: Production Deployment**
Deploy to Heroku, Railway, Render, or your preferred hosting service.

### 2. Configure Resend Webhooks

1. Go to [Resend Dashboard](https://resend.com/webhooks)
2. Click "Add Endpoint"
3. Enter your webhook URL:
   - Local: `https://your-ngrok-url.ngrok.io/api/webhooks/resend`
   - Production: `https://your-domain.com/api/webhooks/resend`
4. Subscribe to these events:
   - ✅ `email.delivered`
   - ✅ `email.opened`
   - ✅ `email.clicked`
   - ✅ `email.bounced`
   - ✅ `email.complained`
5. Click "Create"
6. Copy the "Signing Secret"

### 3. Add Webhook Secret to .env

```bash
# Add to .env file:
RESEND_WEBHOOK_SECRET=whsec_your_secret_here
```

### 4. Restart Backend

```bash
cd backend
uvicorn app.main:app --reload
```

### 5. Test Webhook

Send a test email via the UI:
1. Go to Drafts page
2. Generate a draft
3. Click "Send Newsletter"
4. Open the email in your inbox
5. Click a link in the email

### 6. Verify Tracking

Check the Dashboard - you should see:
- Open rate updated when you open the email
- Click rate updated when you click a link
- Engagement metric reflects real data

## Troubleshooting

### Webhook not receiving events
- Check Resend Dashboard > Webhooks > "Recent Deliveries"
- Verify your URL is publicly accessible
- Check backend logs for webhook errors

### Signature verification failing
- Ensure `RESEND_WEBHOOK_SECRET` matches the Resend dashboard
- Check for whitespace in the secret

### Database not updating
- Check backend logs for SQL errors
- Verify `message_id` in webhook payload matches database record

## Database Schema

The following columns are updated by webhooks:
- `delivered_at` - When email confirmed delivered
- `opened_at` - When email first opened
- `clicked_at` - When link first clicked
- `status` - Updated to delivered/opened/clicked/bounced/complained

## API Endpoint

**POST** `/api/webhooks/resend`
- Receives Resend webhook events
- Verifies signature with `RESEND_WEBHOOK_SECRET`
- Updates `newsletter_sends` table
- Returns `{"status": "success", "event": "opened"}`

**GET** `/api/webhooks/health`
- Health check for webhook service
- Returns `{"status": "healthy"}`

## Security

- Webhook signature verification enabled when `RESEND_WEBHOOK_SECRET` is set
- Uses HMAC SHA256 for signature validation
- Rejects requests with invalid signatures (401 Unauthorized)

## Development Mode

If `RESEND_WEBHOOK_SECRET` is not set, signature verification is skipped.
⚠️ **Do not use in production without signature verification!**

---

**Phase Status:** ✅ Complete
**Next Phase:** Phase 5 - Feedback Backend
