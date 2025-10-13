"""Scheduler service for automated content fetching"""
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime
import logging

from app.core.database import get_supabase
from app.services.content_service import content_service
from app.services.trend_service import trend_service
from app.services.draft_service import DraftService
from app.models.draft import DraftCreate

logger = logging.getLogger(__name__)


class SchedulerService:
    """Service for scheduling automated tasks"""

    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.supabase = get_supabase()

    async def fetch_content_for_all_users(self):
        """
        Fetch content for all users with active sources
        This runs on a schedule
        """
        try:
            logger.info("Starting scheduled content fetch for all users")

            # Get all unique user IDs with active sources
            response = self.supabase.table('sources').select('user_id').eq('is_active', True).execute()

            if not response.data:
                logger.info("No active sources found")
                return

            # Get unique user IDs
            user_ids = list(set([item['user_id'] for item in response.data]))

            logger.info(f"Fetching content for {len(user_ids)} users")

            total_items = 0
            for user_id in user_ids:
                try:
                    from uuid import UUID
                    results = await content_service.fetch_all_content(UUID(user_id))
                    total_items += results.get('total_new_items', 0)
                    logger.info(f"Fetched {results.get('total_new_items', 0)} items for user {user_id}")
                except Exception as e:
                    logger.error(f"Error fetching content for user {user_id}: {e}")

            logger.info(f"Scheduled fetch complete. Total new items: {total_items}")

        except Exception as e:
            logger.error(f"Error in scheduled content fetch: {e}")

    async def detect_trends_for_all_users(self):
        """
        Detect trends for all users with content
        This runs on a schedule
        """
        try:
            logger.info("Starting scheduled trend detection for all users")

            # Get all unique user IDs with content
            response = self.supabase.table('content').select('user_id').execute()

            if not response.data:
                logger.info("No content found")
                return

            # Get unique user IDs
            user_ids = list(set([item['user_id'] for item in response.data]))

            logger.info(f"Detecting trends for {len(user_ids)} users")

            total_trends = 0
            for user_id in user_ids:
                try:
                    from uuid import UUID
                    results = await trend_service.detect_and_save_trends(UUID(user_id))
                    total_trends += results.get('detected', 0)
                    logger.info(f"Detected {results.get('detected', 0)} trends for user {user_id}")
                except Exception as e:
                    logger.error(f"Error detecting trends for user {user_id}: {e}")

            logger.info(f"Scheduled trend detection complete. Total trends: {total_trends}")

        except Exception as e:
            logger.error(f"Error in scheduled trend detection: {e}")

    async def generate_drafts_for_all_users(self):
        """
        Generate newsletter drafts for all users with trends
        This runs on a schedule (daily at 7 AM)
        """
        try:
            logger.info("Starting scheduled draft generation for all users")

            # Get all unique user IDs with trends
            response = self.supabase.table('trends').select('user_id').execute()

            if not response.data:
                logger.info("No trends found")
                return

            # Get unique user IDs
            user_ids = list(set([item['user_id'] for item in response.data]))

            logger.info(f"Generating drafts for {len(user_ids)} users")

            total_drafts = 0
            draft_service = DraftService(self.supabase)

            for user_id in user_ids:
                try:
                    # Check if today's draft already exists
                    request = DraftCreate(
                        force_regenerate=False,
                        include_trends=True,
                        max_trends=3
                    )
                    draft = await draft_service.generate_draft(user_id, request)
                    total_drafts += 1
                    logger.info(f"Generated draft for user {user_id}: {draft.subject}")
                except Exception as e:
                    logger.error(f"Error generating draft for user {user_id}: {e}")

            logger.info(f"Scheduled draft generation complete. Total drafts: {total_drafts}")

        except Exception as e:
            logger.error(f"Error in scheduled draft generation: {e}")

    def start(self):
        """
        Start the scheduler with predefined jobs
        """
        try:
            # Schedule content fetching every 4 hours
            self.scheduler.add_job(
                self.fetch_content_for_all_users,
                trigger=CronTrigger(hour='*/4'),  # Every 4 hours
                id='fetch_content',
                name='Fetch content from all sources',
                replace_existing=True
            )

            # Schedule content fetching at specific times (morning, afternoon, evening)
            # This ensures fresh content at key times
            self.scheduler.add_job(
                self.fetch_content_for_all_users,
                trigger=CronTrigger(hour='6,12,18'),  # 6 AM, 12 PM, 6 PM
                id='fetch_content_daily',
                name='Fetch content at key times',
                replace_existing=True
            )

            # Schedule trend detection twice daily (morning and evening)
            self.scheduler.add_job(
                self.detect_trends_for_all_users,
                trigger=CronTrigger(hour='7,19'),  # 7 AM, 7 PM
                id='detect_trends_daily',
                name='Detect trends twice daily',
                replace_existing=True
            )

            # Schedule draft generation daily at 7 AM
            self.scheduler.add_job(
                self.generate_drafts_for_all_users,
                trigger=CronTrigger(hour='7'),  # 7 AM
                id='generate_drafts_daily',
                name='Generate newsletter drafts daily',
                replace_existing=True
            )

            self.scheduler.start()
            logger.info("Scheduler started successfully")

            # Log scheduled jobs
            jobs = self.scheduler.get_jobs()
            for job in jobs:
                logger.info(f"Scheduled job: {job.name} - Next run: {job.next_run_time}")

        except Exception as e:
            logger.error(f"Error starting scheduler: {e}")
            raise

    def stop(self):
        """
        Stop the scheduler
        """
        try:
            self.scheduler.shutdown()
            logger.info("Scheduler stopped")
        except Exception as e:
            logger.error(f"Error stopping scheduler: {e}")

    def get_jobs(self):
        """
        Get list of scheduled jobs
        """
        return self.scheduler.get_jobs()


# Global instance
scheduler_service = SchedulerService()
