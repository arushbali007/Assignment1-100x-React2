"""YouTube API integration service"""
import httpx
from datetime import datetime
from typing import Optional, List
from uuid import UUID
import logging

from app.core.config import settings
from app.core.database import supabase_admin
from app.models.content import ContentType

logger = logging.getLogger(__name__)


class YouTubeService:
    """Service for fetching YouTube content"""

    def __init__(self):
        self.supabase = supabase_admin
        self.api_key = settings.YOUTUBE_API_KEY
        self.base_url = "https://www.googleapis.com/youtube/v3"

    async def get_channel_id(self, channel_handle: str) -> Optional[str]:
        """
        Get channel ID from channel handle or username

        Args:
            channel_handle: YouTube channel handle (e.g., @channelname) or username

        Returns:
            Channel ID or None
        """
        try:
            # Remove @ if present
            handle = channel_handle.lstrip('@')

            async with httpx.AsyncClient() as client:
                # Try searching by handle/username
                response = await client.get(
                    f"{self.base_url}/search",
                    params={
                        'part': 'snippet',
                        'q': handle,
                        'type': 'channel',
                        'key': self.api_key,
                        'maxResults': 1,
                    }
                )

                if response.status_code == 200:
                    data = response.json()
                    if data.get('items'):
                        return data['items'][0]['snippet']['channelId']

            return None

        except Exception as e:
            logger.error(f"Error getting channel ID for {channel_handle}: {e}")
            return None

    async def fetch_channel_videos(
        self,
        source_id: UUID,
        user_id: UUID,
        channel_id: str,
        max_results: int = 10
    ) -> int:
        """
        Fetch recent videos from a YouTube channel

        Args:
            source_id: UUID of the source
            user_id: UUID of the user
            channel_id: YouTube channel ID
            max_results: Maximum number of videos to fetch

        Returns:
            Number of new videos added
        """
        try:
            if not self.api_key:
                logger.error("YouTube API key not configured")
                return 0

            async with httpx.AsyncClient() as client:
                # Get channel uploads playlist ID
                channel_response = await client.get(
                    f"{self.base_url}/channels",
                    params={
                        'part': 'contentDetails,snippet',
                        'id': channel_id,
                        'key': self.api_key,
                    }
                )

                if channel_response.status_code != 200:
                    logger.error(f"Failed to fetch channel info: {channel_response.text}")
                    return 0

                channel_data = channel_response.json()
                if not channel_data.get('items'):
                    logger.error(f"Channel not found: {channel_id}")
                    return 0

                channel_info = channel_data['items'][0]
                uploads_playlist_id = channel_info['contentDetails']['relatedPlaylists']['uploads']
                channel_title = channel_info['snippet']['title']

                # Get videos from uploads playlist
                playlist_response = await client.get(
                    f"{self.base_url}/playlistItems",
                    params={
                        'part': 'snippet,contentDetails',
                        'playlistId': uploads_playlist_id,
                        'maxResults': max_results,
                        'key': self.api_key,
                    }
                )

                if playlist_response.status_code != 200:
                    logger.error(f"Failed to fetch playlist items: {playlist_response.text}")
                    return 0

                playlist_data = playlist_response.json()
                new_items = 0

                for item in playlist_data.get('items', []):
                    try:
                        snippet = item['snippet']
                        video_id = snippet['resourceId']['videoId']
                        video_url = f"https://www.youtube.com/watch?v={video_id}"

                        # Check if video already exists
                        existing = self.supabase.table('content').select('id').eq('url', video_url).eq('user_id', str(user_id)).execute()

                        if existing.data:
                            continue

                        # Parse published date
                        published_at = None
                        if snippet.get('publishedAt'):
                            published_at = datetime.fromisoformat(snippet['publishedAt'].replace('Z', '+00:00')).isoformat()

                        # Prepare metadata
                        metadata = {
                            'video_id': video_id,
                            'channel_id': channel_id,
                            'channel_title': channel_title,
                            'thumbnail': snippet.get('thumbnails', {}).get('high', {}).get('url', ''),
                        }

                        # Insert into database
                        content_data = {
                            'user_id': str(user_id),
                            'source_id': str(source_id),
                            'content_type': ContentType.VIDEO.value,
                            'title': snippet.get('title', 'Untitled')[:500],
                            'body': snippet.get('description', '')[:10000],
                            'url': video_url,
                            'author': channel_title[:200],
                            'published_at': published_at,
                            'metadata': metadata,
                        }

                        self.supabase.table('content').insert(content_data).execute()
                        new_items += 1

                    except Exception as e:
                        logger.error(f"Error processing YouTube video: {e}")
                        continue

                logger.info(f"Fetched {new_items} new videos from channel {channel_id}")
                return new_items

        except Exception as e:
            logger.error(f"Error fetching YouTube channel {channel_id}: {e}")
            raise

    async def fetch_all_youtube_sources(self, user_id: UUID) -> dict:
        """
        Fetch all active YouTube sources for a user

        Args:
            user_id: UUID of the user

        Returns:
            Dictionary with fetch results
        """
        try:
            # Get all active YouTube sources
            response = self.supabase.table('sources').select('*').eq('user_id', str(user_id)).eq('source_type', 'youtube').eq('is_active', True).execute()

            sources = response.data
            results = {
                'total_sources': len(sources),
                'successful': 0,
                'failed': 0,
                'total_new_items': 0,
            }

            for source in sources:
                try:
                    # Extract channel ID from identifier
                    channel_id = source.get('identifier')

                    if not channel_id:
                        logger.error(f"No channel ID for source {source['id']}")
                        results['failed'] += 1
                        continue

                    new_items = await self.fetch_channel_videos(
                        source_id=UUID(source['id']),
                        user_id=user_id,
                        channel_id=channel_id
                    )
                    results['successful'] += 1
                    results['total_new_items'] += new_items

                except Exception as e:
                    logger.error(f"Failed to fetch source {source['id']}: {e}")
                    results['failed'] += 1

            return results

        except Exception as e:
            logger.error(f"Error fetching YouTube sources: {e}")
            raise


# Global instance
youtube_service = YouTubeService()
