"""Keyword extraction service for content analysis"""
from typing import List, Dict, Tuple
from collections import Counter
import re
import logging
from uuid import UUID

from app.core.database import supabase_admin

logger = logging.getLogger(__name__)


class KeywordExtractionService:
    """Service for extracting keywords from content"""

    def __init__(self):
        self.supabase = supabase_admin

        # Common stop words to filter out
        self.stop_words = {
            'the', 'be', 'to', 'of', 'and', 'a', 'in', 'that', 'have', 'i',
            'it', 'for', 'not', 'on', 'with', 'he', 'as', 'you', 'do', 'at',
            'this', 'but', 'his', 'by', 'from', 'they', 'we', 'say', 'her', 'she',
            'or', 'an', 'will', 'my', 'one', 'all', 'would', 'there', 'their',
            'what', 'so', 'up', 'out', 'if', 'about', 'who', 'get', 'which', 'go',
            'me', 'when', 'make', 'can', 'like', 'time', 'no', 'just', 'him', 'know',
            'take', 'people', 'into', 'year', 'your', 'good', 'some', 'could', 'them',
            'see', 'other', 'than', 'then', 'now', 'look', 'only', 'come', 'its', 'over',
            'think', 'also', 'back', 'after', 'use', 'two', 'how', 'our', 'work', 'first',
            'well', 'way', 'even', 'new', 'want', 'because', 'any', 'these', 'give', 'day',
            'most', 'us', 'is', 'was', 'are', 'been', 'has', 'had', 'were', 'said', 'did',
            'having', 'may', 'should', 'am', 'being', 'does', 'did', 'doing'
        }

    def extract_keywords_from_text(self, text: str, min_length: int = 3, max_keywords: int = 20) -> List[str]:
        """
        Extract keywords from text using simple word frequency

        Args:
            text: Text to extract keywords from
            min_length: Minimum keyword length
            max_keywords: Maximum number of keywords to return

        Returns:
            List of keywords sorted by frequency
        """
        try:
            if not text:
                return []

            # Convert to lowercase and extract words
            text = text.lower()

            # Remove URLs
            text = re.sub(r'http\S+|www.\S+', '', text)

            # Remove special characters but keep hashtags and @mentions
            words = re.findall(r'#\w+|@\w+|\b[a-z]{' + str(min_length) + r',}\b', text)

            # Filter out stop words (but keep hashtags and mentions)
            keywords = []
            for word in words:
                if word.startswith('#') or word.startswith('@'):
                    keywords.append(word)
                elif word not in self.stop_words:
                    keywords.append(word)

            # Count frequency
            word_counts = Counter(keywords)

            # Return top keywords
            top_keywords = [word for word, count in word_counts.most_common(max_keywords)]

            return top_keywords

        except Exception as e:
            logger.error(f"Error extracting keywords from text: {e}")
            return []

    def extract_keywords_from_content(self, user_id: UUID, days: int = 7, min_mentions: int = 2) -> List[Tuple[str, int, List[UUID]]]:
        """
        Extract trending keywords from user's content

        Args:
            user_id: User ID
            days: Number of days to look back
            min_mentions: Minimum number of mentions to be considered

        Returns:
            List of tuples (keyword, mention_count, content_ids)
        """
        try:
            # Get recent content
            from datetime import datetime, timedelta
            cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()

            response = self.supabase.table('content').select('id, title, body').eq('user_id', str(user_id)).gte('created_at', cutoff_date).execute()

            if not response.data:
                logger.info(f"No recent content found for user {user_id}")
                return []

            # Extract keywords from all content
            keyword_content_map = {}  # keyword -> list of content IDs

            for item in response.data:
                text = ""
                if item.get('title'):
                    text += item['title'] + " "
                if item.get('body'):
                    text += item['body']

                keywords = self.extract_keywords_from_text(text)

                for keyword in keywords:
                    if keyword not in keyword_content_map:
                        keyword_content_map[keyword] = []
                    keyword_content_map[keyword].append(UUID(item['id']))

            # Filter by minimum mentions and sort by frequency
            trending_keywords = []
            for keyword, content_ids in keyword_content_map.items():
                mention_count = len(content_ids)
                if mention_count >= min_mentions:
                    # Remove duplicates from content_ids
                    unique_content_ids = list(set(content_ids))
                    trending_keywords.append((keyword, mention_count, unique_content_ids))

            # Sort by mention count (descending)
            trending_keywords.sort(key=lambda x: x[1], reverse=True)

            logger.info(f"Extracted {len(trending_keywords)} trending keywords for user {user_id}")
            return trending_keywords

        except Exception as e:
            logger.error(f"Error extracting keywords from content: {e}")
            return []

    def extract_hashtags_and_mentions(self, user_id: UUID, days: int = 7) -> Dict[str, List[Tuple[str, int]]]:
        """
        Extract trending hashtags and mentions from Twitter content

        Args:
            user_id: User ID
            days: Number of days to look back

        Returns:
            Dictionary with 'hashtags' and 'mentions' lists
        """
        try:
            from datetime import datetime, timedelta
            cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()

            # Get Twitter content only
            response = self.supabase.table('content').select('body').eq('user_id', str(user_id)).eq('content_type', 'tweet').gte('created_at', cutoff_date).execute()

            if not response.data:
                return {'hashtags': [], 'mentions': []}

            hashtags = []
            mentions = []

            for item in response.data:
                if not item.get('body'):
                    continue

                text = item['body']

                # Extract hashtags
                found_hashtags = re.findall(r'#\w+', text.lower())
                hashtags.extend(found_hashtags)

                # Extract mentions
                found_mentions = re.findall(r'@\w+', text.lower())
                mentions.extend(found_mentions)

            # Count and sort
            hashtag_counts = Counter(hashtags).most_common(20)
            mention_counts = Counter(mentions).most_common(20)

            return {
                'hashtags': hashtag_counts,
                'mentions': mention_counts
            }

        except Exception as e:
            logger.error(f"Error extracting hashtags and mentions: {e}")
            return {'hashtags': [], 'mentions': []}

    def get_keyword_suggestions(self, user_id: UUID, days: int = 7) -> List[str]:
        """
        Get keyword suggestions based on user's content

        Args:
            user_id: User ID
            days: Number of days to look back

        Returns:
            List of suggested keywords
        """
        try:
            trending_keywords = self.extract_keywords_from_content(user_id, days, min_mentions=2)

            # Return top 30 keywords
            suggestions = [kw[0] for kw in trending_keywords[:30]]

            return suggestions

        except Exception as e:
            logger.error(f"Error getting keyword suggestions: {e}")
            return []


# Global instance
keyword_extraction_service = KeywordExtractionService()
