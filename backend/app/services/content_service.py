"""Content aggregation service - coordinates fetching from all sources"""
from uuid import UUID
from typing import Optional, List
import logging

from app.core.database import supabase_admin
from app.services.rss_service import rss_service
from app.services.youtube_service import youtube_service
from app.services.twitter_service import twitter_service
from app.models.content import ContentInDB, ContentResponse

logger = logging.getLogger(__name__)


class ContentService:
    """Service for managing content"""

    def __init__(self):
        self.supabase = supabase_admin

    async def fetch_all_content(self, user_id: UUID) -> dict:
        """
        Fetch content from all active sources

        Args:
            user_id: UUID of the user

        Returns:
            Dictionary with aggregated results
        """
        try:
            results = {
                'rss': {},
                'youtube': {},
                'twitter': {},
                'total_new_items': 0,
            }

            # Fetch RSS feeds
            try:
                rss_results = await rss_service.fetch_all_rss_sources(user_id)
                results['rss'] = rss_results
                results['total_new_items'] += rss_results.get('total_new_items', 0)
            except Exception as e:
                logger.error(f"Error fetching RSS feeds: {e}")
                results['rss'] = {'error': str(e)}

            # Fetch YouTube videos
            try:
                youtube_results = await youtube_service.fetch_all_youtube_sources(user_id)
                results['youtube'] = youtube_results
                results['total_new_items'] += youtube_results.get('total_new_items', 0)
            except Exception as e:
                logger.error(f"Error fetching YouTube videos: {e}")
                results['youtube'] = {'error': str(e)}

            # Fetch Twitter tweets
            try:
                twitter_results = await twitter_service.fetch_all_twitter_sources(user_id)
                results['twitter'] = twitter_results
                results['total_new_items'] += twitter_results.get('total_new_items', 0)
            except Exception as e:
                logger.error(f"Error fetching Twitter tweets: {e}")
                results['twitter'] = {'error': str(e)}

            logger.info(f"Fetched {results['total_new_items']} total new items for user {user_id}")
            return results

        except Exception as e:
            logger.error(f"Error in fetch_all_content: {e}")
            raise

    async def get_content_list(
        self,
        user_id: UUID,
        content_type: Optional[str] = None,
        source_id: Optional[UUID] = None,
        limit: int = 50,
        offset: int = 0
    ) -> tuple[List[ContentResponse], int]:
        """
        Get paginated list of content

        Args:
            user_id: UUID of the user
            content_type: Filter by content type (optional)
            source_id: Filter by source ID (optional)
            limit: Number of items per page
            offset: Offset for pagination

        Returns:
            Tuple of (content list, total count)
        """
        try:
            # Build query
            query = self.supabase.table('content').select('*', count='exact').eq('user_id', str(user_id))

            if content_type:
                query = query.eq('content_type', content_type)

            if source_id:
                query = query.eq('source_id', str(source_id))

            # Execute query with pagination
            response = query.order('published_at', desc=True).range(offset, offset + limit - 1).execute()

            # Convert to response models
            content_list = [ContentResponse(**item) for item in response.data]
            total = response.count if response.count else 0

            return content_list, total

        except Exception as e:
            logger.error(f"Error getting content list: {e}")
            raise

    async def get_content_by_id(self, user_id: UUID, content_id: UUID) -> Optional[ContentResponse]:
        """
        Get specific content by ID

        Args:
            user_id: UUID of the user
            content_id: UUID of the content

        Returns:
            Content or None if not found
        """
        try:
            response = self.supabase.table('content').select('*').eq('user_id', str(user_id)).eq('id', str(content_id)).execute()

            if response.data:
                return ContentResponse(**response.data[0])

            return None

        except Exception as e:
            logger.error(f"Error getting content {content_id}: {e}")
            raise

    async def delete_content(self, user_id: UUID, content_id: UUID) -> bool:
        """
        Delete content

        Args:
            user_id: UUID of the user
            content_id: UUID of the content

        Returns:
            True if deleted, False otherwise
        """
        try:
            response = self.supabase.table('content').delete().eq('user_id', str(user_id)).eq('id', str(content_id)).execute()

            return len(response.data) > 0

        except Exception as e:
            logger.error(f"Error deleting content {content_id}: {e}")
            raise

    async def get_content_stats(self, user_id: UUID) -> dict:
        """
        Get content statistics for a user

        Args:
            user_id: UUID of the user

        Returns:
            Dictionary with statistics
        """
        try:
            # Get total count
            total_response = self.supabase.table('content').select('id', count='exact').eq('user_id', str(user_id)).execute()
            total = total_response.count if total_response.count else 0

            # Get counts by type
            stats = {'total': total, 'by_type': {}}

            for content_type in ['tweet', 'video', 'article', 'newsletter']:
                type_response = self.supabase.table('content').select('id', count='exact').eq('user_id', str(user_id)).eq('content_type', content_type).execute()
                count = type_response.count if type_response.count else 0
                stats['by_type'][content_type] = count

            return stats

        except Exception as e:
            logger.error(f"Error getting content stats: {e}")
            raise


# Global instance
content_service = ContentService()
