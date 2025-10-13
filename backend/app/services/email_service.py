import resend
from typing import Optional, List
from datetime import datetime

from app.core.config import settings


class EmailService:
    """Service for sending emails via Resend"""

    def __init__(self):
        resend.api_key = settings.RESEND_API_KEY

    async def send_newsletter(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        plain_content: str,
        from_email: Optional[str] = None,
        from_name: Optional[str] = None
    ) -> dict:
        """
        Send newsletter email via Resend

        Args:
            to_email: Recipient email address
            subject: Email subject line
            html_content: HTML email body
            plain_content: Plain text email body
            from_email: Sender email (defaults to config)
            from_name: Sender name (defaults to "CreatorPulse")

        Returns:
            Dict with send result including message ID

        Raises:
            Exception if send fails
        """
        # Use default from address if not provided
        if not from_email:
            from_email = settings.RESEND_FROM_EMAIL or "onboarding@resend.dev"

        if not from_name:
            from_name = "CreatorPulse"

        # Format from address
        from_address = f"{from_name} <{from_email}>"

        try:
            # Send email via Resend
            params = {
                "from": from_address,
                "to": [to_email],
                "subject": subject,
                "html": html_content,
                "text": plain_content,
            }

            response = resend.Emails.send(params)

            return {
                "success": True,
                "message_id": response.get("id"),
                "to": to_email,
                "sent_at": datetime.utcnow().isoformat()
            }

        except Exception as e:
            raise Exception(f"Failed to send email via Resend: {str(e)}")

    async def send_test_email(
        self,
        to_email: str,
        draft_subject: str,
        draft_html: str,
        draft_plain: str
    ) -> dict:
        """
        Send a test email (prepends [TEST] to subject)

        Args:
            to_email: Test recipient email
            draft_subject: Draft subject line
            draft_html: Draft HTML content
            draft_plain: Draft plain text content

        Returns:
            Send result dictionary
        """
        test_subject = f"[TEST] {draft_subject}"

        # Add test banner to HTML
        test_banner_html = """
        <div style="background-color: #fff3cd; border: 2px solid #ffc107; padding: 15px; margin-bottom: 20px; border-radius: 5px; text-align: center;">
            <strong>⚠️ TEST EMAIL</strong> - This is a test of your newsletter draft
        </div>
        """
        test_html = test_banner_html + draft_html

        # Add test banner to plain text
        test_banner_plain = "=" * 60 + "\n⚠️ TEST EMAIL - This is a test of your newsletter draft\n" + "=" * 60 + "\n\n"
        test_plain = test_banner_plain + draft_plain

        return await self.send_newsletter(
            to_email=to_email,
            subject=test_subject,
            html_content=test_html,
            plain_content=test_plain
        )

    async def send_bulk_newsletter(
        self,
        to_emails: List[str],
        subject: str,
        html_content: str,
        plain_content: str,
        from_email: Optional[str] = None,
        from_name: Optional[str] = None
    ) -> dict:
        """
        Send newsletter to multiple recipients

        Args:
            to_emails: List of recipient email addresses
            subject: Email subject line
            html_content: HTML email body
            plain_content: Plain text email body
            from_email: Sender email
            from_name: Sender name

        Returns:
            Dict with results for each recipient
        """
        results = {
            "total": len(to_emails),
            "successful": 0,
            "failed": 0,
            "details": []
        }

        for email in to_emails:
            try:
                result = await self.send_newsletter(
                    to_email=email,
                    subject=subject,
                    html_content=html_content,
                    plain_content=plain_content,
                    from_email=from_email,
                    from_name=from_name
                )
                results["successful"] += 1
                results["details"].append({
                    "email": email,
                    "success": True,
                    "message_id": result.get("message_id")
                })
            except Exception as e:
                results["failed"] += 1
                results["details"].append({
                    "email": email,
                    "success": False,
                    "error": str(e)
                })

        return results

    def validate_email(self, email: str) -> bool:
        """
        Basic email validation

        Args:
            email: Email address to validate

        Returns:
            True if valid, False otherwise
        """
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
