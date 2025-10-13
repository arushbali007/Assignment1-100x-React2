#!/bin/bash
# Script to restart backend with fresh .env

echo "🔄 Restarting Backend Server..."

# Kill any existing uvicorn processes
pkill -9 -f "uvicorn app.main:app"

echo "✅ Stopped existing server"
echo ""
echo "Now run these commands:"
echo ""
echo "cd /Users/arushbali/Downloads/Assignment/backend"
echo "source ../venv/bin/activate"
echo "uvicorn app.main:app --reload"
echo ""
echo "📧 Email will use: onboarding@resend.dev"
