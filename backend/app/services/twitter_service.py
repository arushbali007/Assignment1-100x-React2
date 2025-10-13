"""Twitter/X API integration service"""
import httpx
from datetime import datetime
from typing import Optional, List
from uuid import UUID
import logging

from app.core.config import settings
from app.core.database import supabase_admin
from app.models.content import ContentType

logger = logging.getLogger(__name__)


class TwitterService:
    """Service for fetching Twitter/X content"""

    def __init__(self):
        self.supabase = supabase_admin
        self.bearer_token = settings.TWITTER_BEARER_TOKEN
        self.base_url = "https://api.twitter.com/2"

    async def get_user_id(self, username: str) -> Optional[str]:
        """
        Get Twitter user ID from username

        Args:
            username: Twitter username (without @)

        Returns:
            User ID or None
        """
        try:
            if not self.bearer_token:
                logger.error("Twitter bearer token not configured")
                return None

            username = username.lstrip('@')

            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/users/by/username/{username}",
                    headers={'Authorization': f'Bearer {self.bearer_token}'}
                )

                if response.status_code == 200:
                    data = response.json()
                    return data['data']['id']
                else:
                    logger.error(f"Failed to get Twitter user ID: {response.text}")
                    return None

        except Exception as e:
            logger.error(f"Error getting Twitter user ID for {username}: {e}")
            return None

    async def fetch_user_tweets(
        self,
        source_id: UUID,
        user_id: UUID,
        twitter_user_id: str,
        max_results: int = 10
    ) -> int:
        """
        Fetch recent tweets from a Twitter user

        Args:
            source_id: UUID of the source
            user_id: UUID of the user
            twitter_user_id: Twitter user ID
            max_results: Maximum number of tweets to fetch (5-100)

        Returns:
            Number of new tweets added
        """
        try:
            if not self.bearer_token:
                logger.error("Twitter bearer token not configured")
                return 0

            # Ensure max_results is within valid range
            max_results = max(5, min(100, max_results))

            async with httpx.AsyncClient() as client:
                # Get user's tweets
                response = await client.get(
                    f"{self.base_url}/users/{twitter_user_id}/tweets",
                    headers={'Authorization': f'Bearer {self.bearer_token}'},
                    params={
                        'max_results': max_results,
                        'tweet.fields': 'created_at,author_id,public_metrics,entities',
                        'expansions': 'author_id',
                        'user.fields': 'username,name',
                    }
                )

                if response.status_code != 200:
                    logger.error(f"Failed to fetch tweets: {response.text}")
                    return 0

                data = response.json()
                tweets = data.get('data', [])
                includes = data.get('includes', {})
                users = {user['id']: user for user in includes.get('users', [])}

                new_items = 0

                for tweet in tweets:
                    try:
                        tweet_id = tweet['id']
                        tweet_url = f"https://twitter.com/i/web/status/{tweet_id}"

                        # Check if tweet already exists
                        existing = self.supabase.table('content').select('id').eq('url', tweet_url).eq('user_id', str(user_id)).execute()

                        if existing.data:
                            continue

                        # Get author info
                        author_id = tweet.get('author_id')
                        author_name = None
                        author_username = None

                        if author_id and author_id in users:
                            author_name = users[author_id].get('name')
                            author_username = users[author_id].get('username')

                        # Parse created date
                        created_at = None
                        if tweet.get('created_at'):
                            created_at = datetime.fromisoformat(tweet['created_at'].replace('Z', '+00:00')).isoformat()

                        # Prepare metadata
                        metadata = {
                            'tweet_id': tweet_id,
                            'author_id': author_id,
                            'author_username': author_username,
                            'public_metrics': tweet.get('public_metrics', {}),
                            'entities': tweet.get('entities', {}),
                        }

                        # Insert into database
                        content_data = {
                            'user_id': str(user_id),
                            'source_id': str(source_id),
                            'content_type': ContentType.TWEET.value,
                            'title': None,  # Tweets don't have titles
                            'body': tweet.get('text', '')[:10000],
                            'url': tweet_url,
                            'author': author_name[:200] if author_name else None,
                            'published_at': created_at,
                            'metadata': metadata,
                        }

                        self.supabase.table('content').insert(content_data).execute()
                        new_items += 1

                    except Exception as e:
                        logger.error(f"Error processing tweet: {e}")
                        continue

                logger.info(f"Fetched {new_items} new tweets from user {twitter_user_id}")
                return new_items

        except Exception as e:
            logger.error(f"Error fetching tweets from user {twitter_user_id}: {e}")
            raise

    async def fetch_all_twitter_sources(self, user_id: UUID) -> dict:
        """
        Fetch all active Twitter sources for a user

        Args:
            user_id: UUID of the user

        Returns:
            Dictionary with fetch results
        """
        try:
            # Get all active Twitter sources
            response = self.supabase.table('sources').select('*').eq('user_id', str(user_id)).eq('source_type', 'twitter').eq('is_active', True).execute()

            sources = response.data
            results = {
                'total_sources': len(sources),
                'successful': 0,
                'failed': 0,
                'total_new_items': 0,
            }

            for source in sources:
                try:
                    # Extract Twitter user ID from identifier
                    twitter_user_id = source.get('identifier')

                    if not twitter_user_id:
                        logger.error(f"No Twitter user ID for source {source['id']}")
                        results['failed'] += 1
                        continue

                    new_items = await self.fetch_user_tweets(
                        source_id=UUID(source['id']),
                        user_id=user_id,
                        twitter_user_id=twitter_user_id
                    )
                    results['successful'] += 1
                    results['total_new_items'] += new_items

                except Exception as e:
                    logger.error(f"Failed to fetch source {source['id']}: {e}")
                    results['failed'] += 1

            return results

        except Exception as e:
            logger.error(f"Error fetching Twitter sources: {e}")
            raise


# Global instance
twitter_service = TwitterService()
