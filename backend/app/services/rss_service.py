"""RSS feed parser service"""
import feedparser
from datetime import datetime
from typing import Optional, List
from uuid import UUID
import logging
import ssl
import certifi

from app.core.database import supabase_admin
from app.models.content import ContentType

logger = logging.getLogger(__name__)

# Fix SSL certificate verification issues on macOS
if hasattr(ssl, '_create_unverified_context'):
    ssl._create_default_https_context = ssl._create_unverified_context


class RSSService:
    """Service for fetching RSS feeds"""

    def __init__(self):
        self.supabase = supabase_admin

    async def fetch_feed(self, source_id: UUID, user_id: UUID, feed_url: str) -> int:
        """
        Fetch RSS feed and store content

        Args:
            source_id: UUID of the source
            user_id: UUID of the user
            feed_url: URL of the RSS feed

        Returns:
            Number of new items added
        """
        try:
            # Parse the feed
            feed = feedparser.parse(feed_url)

            if feed.bozo:
                logger.warning(f"Feed parsing warning for {feed_url}: {feed.bozo_exception}")

            new_items = 0

            # Process each entry
            for entry in feed.entries:
                try:
                    # Extract data from entry
                    title = entry.get('title', 'Untitled')
                    link = entry.get('link', '')

                    if not link:
                        continue

                    # Check if content already exists (by URL)
                    existing = self.supabase.table('content').select('id').eq('url', link).eq('user_id', str(user_id)).execute()

                    if existing.data:
                        continue

                    # Get content body
                    body = None
                    if 'content' in entry:
                        body = entry.content[0].get('value', '')
                    elif 'summary' in entry:
                        body = entry.summary
                    elif 'description' in entry:
                        body = entry.description

                    # Get author
                    author = entry.get('author', None)

                    # Get published date
                    published_at = None
                    if 'published_parsed' in entry and entry.published_parsed:
                        published_at = datetime(*entry.published_parsed[:6]).isoformat()
                    elif 'updated_parsed' in entry and entry.updated_parsed:
                        published_at = datetime(*entry.updated_parsed[:6]).isoformat()

                    # Prepare metadata
                    metadata = {
                        'tags': [tag.term for tag in entry.get('tags', [])],
                        'feed_title': feed.feed.get('title', ''),
                    }

                    # Insert into database
                    content_data = {
                        'user_id': str(user_id),
                        'source_id': str(source_id),
                        'content_type': ContentType.ARTICLE.value,
                        'title': title[:500] if title else None,  # Limit title length
                        'body': body[:10000] if body else None,  # Limit body length
                        'url': link,
                        'author': author[:200] if author else None,
                        'published_at': published_at,
                        'metadata': metadata,
                    }

                    self.supabase.table('content').insert(content_data).execute()
                    new_items += 1

                except Exception as e:
                    logger.error(f"Error processing RSS entry: {e}")
                    continue

            logger.info(f"Fetched {new_items} new items from RSS feed {feed_url}")
            return new_items

        except Exception as e:
            logger.error(f"Error fetching RSS feed {feed_url}: {e}")
            raise

    async def fetch_all_rss_sources(self, user_id: UUID) -> dict:
        """
        Fetch all active RSS sources for a user

        Args:
            user_id: UUID of the user

        Returns:
            Dictionary with fetch results
        """
        try:
            # Get all active RSS sources
            response = self.supabase.table('sources').select('*').eq('user_id', str(user_id)).eq('source_type', 'rss').eq('is_active', True).execute()

            sources = response.data
            results = {
                'total_sources': len(sources),
                'successful': 0,
                'failed': 0,
                'total_new_items': 0,
            }

            for source in sources:
                try:
                    new_items = await self.fetch_feed(
                        source_id=UUID(source['id']),
                        user_id=user_id,
                        feed_url=source['source_url']  # Fixed: use 'source_url' not 'url'
                    )
                    results['successful'] += 1
                    results['total_new_items'] += new_items
                except Exception as e:
                    logger.error(f"Failed to fetch source {source['id']}: {e}")
                    results['failed'] += 1

            return results

        except Exception as e:
            logger.error(f"Error fetching RSS sources: {e}")
            raise


# Global instance
rss_service = RSSService()
