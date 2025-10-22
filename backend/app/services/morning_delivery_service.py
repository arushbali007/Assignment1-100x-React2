"""
Morning delivery service - Automated email delivery at user's configured time
"""
from datetime import datetime, time as time_type
import pytz
from typing import List, Optional
from app.core.database import get_supabase
from app.services.email_service import EmailService
from app.services.draft_service import DraftService
from app.services.trend_service import TrendService


class MorningDeliveryService:
    """Handle automated morning email delivery"""

    def __init__(self):
        self.db = get_supabase()
        self.email_service = EmailService()
        self.draft_service = DraftService(self.db)
        self.trend_service = TrendService()

    async def send_morning_emails_for_all_users(self):
        """
        Check all users and send morning emails to those who are due

        This runs every hour via scheduler. For each user:
        1. Check if delivery is enabled
        2. Check if it's their delivery time in their timezone
        3. Check if today is a delivery day
        4. Send email with latest draft + trends
        """
        print(f"[Morning Delivery] Checking users at {datetime.utcnow()}")

        # Get all users with delivery enabled
        response = self.db.table("users").select("*").eq("delivery_enabled", True).execute()

        if not response.data:
            print("[Morning Delivery] No users with delivery enabled")
            return

        users = response.data
        print(f"[Morning Delivery] Found {len(users)} users with delivery enabled")

        for user in users:
            try:
                await self._process_user_delivery(user)
            except Exception as e:
                print(f"[Morning Delivery] Error processing user {user['id']}: {e}")
                continue

    async def _process_user_delivery(self, user: dict):
        """Process delivery for a single user"""
        user_id = user["id"]
        user_email = user["email"]
        user_timezone = user.get("timezone", "UTC")
        delivery_time = user.get("delivery_time", "08:00:00")
        delivery_days = user.get("delivery_days", "weekdays")

        # Check if it's time to send
        if not self._should_send_now(user_timezone, delivery_time, delivery_days):
            return

        print(f"[Morning Delivery] Sending to {user_email}")

        # Get latest draft (today's or most recent)
        drafts_response = await self.draft_service.get_drafts(
            user_id=user_id,
            page=1,
            page_size=1,
            status=None  # Get any status
        )

        if not drafts_response.drafts or len(drafts_response.drafts) == 0:
            print(f"[Morning Delivery] No drafts found for {user_email}")
            return

        draft = drafts_response.drafts[0]

        # Get top 3 trends
        trends_response = await self.trend_service.get_top_trends(
            user_id=user_id,
            limit=3
        )
        trends = trends_response if trends_response else []

        # Generate email content
        email_html = self._generate_morning_email_html(
            draft=draft,
            trends=trends,
            user_name=user_email.split("@")[0]
        )

        email_subject = f"📬 Your Morning Newsletter: {draft.subject}"

        # Send email
        try:
            result = await self.email_service.send_newsletter(
                to_email=user_email,
                subject=email_subject,
                html_content=email_html,
                plain_content=f"Your draft: {draft.subject}\n\n{draft.plain_content}"
            )

            # Record send in newsletter_sends table
            send_data = {
                "user_id": user_id,
                "draft_id": draft.id,
                "recipient_email": user_email,
                "status": "sent",
                "is_test": False,
                "message_id": result.get("message_id"),
                "from_email": "onboarding@resend.dev",
                "from_name": "CreatorPulse",
                "sent_at": datetime.utcnow().isoformat(),
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }

            self.db.table("newsletter_sends").insert(send_data).execute()

            print(f"[Morning Delivery] ✅ Sent to {user_email}")

        except Exception as e:
            print(f"[Morning Delivery] ❌ Failed to send to {user_email}: {e}")

    def _should_send_now(
        self,
        user_timezone: str,
        delivery_time: str,
        delivery_days: str
    ) -> bool:
        """
        Check if we should send email now based on user's timezone and preferences

        Args:
            user_timezone: User's timezone (e.g., 'America/New_York')
            delivery_time: Delivery time (e.g., '08:00:00')
            delivery_days: Days to send ('weekdays', 'daily', or 'Mon,Wed,Fri')

        Returns:
            True if we should send now
        """
        try:
            # Get current time in user's timezone
            tz = pytz.timezone(user_timezone)
            user_now = datetime.now(tz)

            # Parse delivery time
            delivery_hour, delivery_minute = map(int, delivery_time.split(":")[:2])

            # Check if current hour matches delivery hour
            # We check every hour, so if it's 8:XX and delivery is 8:00, send it
            if user_now.hour != delivery_hour:
                return False

            # Check day of week
            weekday = user_now.strftime("%A")  # Monday, Tuesday, etc.

            if delivery_days == "daily":
                return True
            elif delivery_days == "weekdays":
                # Monday = 0, Sunday = 6
                return user_now.weekday() < 5  # Mon-Fri
            elif delivery_days == "weekends":
                return user_now.weekday() >= 5  # Sat-Sun
            else:
                # Custom days like "Mon,Wed,Fri"
                days = [d.strip() for d in delivery_days.split(",")]
                return any(weekday.startswith(d) for d in days)

        except Exception as e:
            print(f"[Morning Delivery] Error checking send time: {e}")
            return False

    def _generate_morning_email_html(
        self,
        draft: any,
        trends: List[any],
        user_name: str
    ) -> str:
        """
        Generate HTML email with draft + trends digest

        Args:
            draft: Newsletter draft
            trends: Top trends
            user_name: User's name

        Returns:
            HTML email content
        """
        trends_html = ""
        if trends:
            trends_items = []
            for trend in trends[:3]:
                keyword = trend.get("keyword", "Trending")
                score = trend.get("score", 0)
                mentions = trend.get("content_mentions", 0)
                trends_items.append(f"""
                    <li style="margin-bottom: 10px;">
                        <strong>{keyword}</strong>
                        <span style="color: #666; font-size: 14px;">
                            (Score: {score:.1f}, {mentions} mentions)
                        </span>
                    </li>
                """)
            trends_html = f"""
                <div style="background: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0;">
                    <h3 style="margin-top: 0; color: #2563eb;">🔥 Trending Topics Today</h3>
                    <ul style="list-style: none; padding-left: 0;">
                        {"".join(trends_items)}
                    </ul>
                </div>
            """

        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
        </head>
        <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">

            <!-- Header -->
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; border-radius: 12px; text-align: center; margin-bottom: 30px;">
                <h1 style="color: white; margin: 0; font-size: 28px;">📬 Good Morning, {user_name}!</h1>
                <p style="color: rgba(255,255,255,0.9); margin: 10px 0 0 0;">Your daily newsletter digest is ready</p>
            </div>

            {trends_html}

            <!-- Draft Preview -->
            <div style="background: white; padding: 20px; border: 1px solid #e5e7eb; border-radius: 8px;">
                <h2 style="color: #1f2937; margin-top: 0;">📄 Today's Newsletter Draft</h2>
                <h3 style="color: #2563eb;">{draft.subject}</h3>

                <div style="margin-top: 20px; padding-top: 20px; border-top: 1px solid #e5e7eb;">
                    {draft.html_content}
                </div>
            </div>

            <!-- CTA -->
            <div style="text-align: center; margin: 30px 0;">
                <p style="color: #666; font-size: 14px;">
                    Review and send this draft from your
                    <a href="http://localhost:5173/drafts" style="color: #2563eb; text-decoration: none;">
                        CreatorPulse Dashboard →
                    </a>
                </p>
            </div>

            <!-- Footer -->
            <div style="text-align: center; padding: 20px; color: #9ca3af; font-size: 12px;">
                <p>Sent by CreatorPulse - Your AI Newsletter Assistant</p>
                <p>
                    To change delivery preferences, visit your
                    <a href="http://localhost:5173/settings" style="color: #2563eb;">settings</a>
                </p>
            </div>

        </body>
        </html>
        """

        return html


# Global instance
morning_delivery_service = MorningDeliveryService()
