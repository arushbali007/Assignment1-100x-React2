"""Trend detection and ranking service"""
from typing import List, Dict, Optional
from uuid import UUID
from datetime import datetime, timedelta
import logging

from app.core.database import supabase_admin
from app.services.keyword_extraction_service import keyword_extraction_service
from app.services.google_trends_service import google_trends_service
from app.models.trend import TrendResponse

logger = logging.getLogger(__name__)


class TrendService:
    """Service for detecting and ranking trends"""

    def __init__(self):
        self.supabase = supabase_admin

    def calculate_trend_score(
        self,
        content_mentions: int,
        google_trends_score: float,
        velocity: float = 0.0
    ) -> float:
        """
        Calculate overall trend score

        Formula:
        - 40% content mentions (normalized)
        - 40% Google Trends score
        - 20% velocity (rate of change)

        Args:
            content_mentions: Number of mentions in user's content
            google_trends_score: Google Trends score (0-100)
            velocity: Rate of change in mentions

        Returns:
            Trend score (0-100)
        """
        try:
            # Normalize content mentions (assuming max 50 mentions is a strong signal)
            normalized_mentions = min(content_mentions / 50.0 * 100, 100)

            # Normalize velocity (assuming max velocity of 5 is very fast growth)
            normalized_velocity = min(abs(velocity) / 5.0 * 100, 100) if velocity else 0

            # Calculate weighted score
            score = (
                normalized_mentions * 0.4 +
                google_trends_score * 0.4 +
                normalized_velocity * 0.2
            )

            return round(score, 2)

        except Exception as e:
            logger.error(f"Error calculating trend score: {e}")
            return 0.0

    def calculate_velocity(self, user_id: UUID, keyword: str) -> float:
        """
        Calculate velocity (rate of change) for a keyword

        Compares mentions in last 3 days vs previous 4 days

        Args:
            user_id: User ID
            keyword: Keyword to check

        Returns:
            Velocity score (positive = growing, negative = declining)
        """
        try:
            now = datetime.now()
            recent_cutoff = (now - timedelta(days=3)).isoformat()
            older_cutoff = (now - timedelta(days=7)).isoformat()

            # Get content from last 3 days
            recent_response = self.supabase.table('content').select('id, title, body').eq('user_id', str(user_id)).gte('created_at', recent_cutoff).execute()

            # Get content from 4-7 days ago
            older_response = self.supabase.table('content').select('id, title, body').eq('user_id', str(user_id)).gte('created_at', older_cutoff).lt('created_at', recent_cutoff).execute()

            # Count mentions
            recent_mentions = 0
            for item in recent_response.data:
                text = f"{item.get('title', '')} {item.get('body', '')}".lower()
                if keyword.lower() in text:
                    recent_mentions += 1

            older_mentions = 0
            for item in older_response.data:
                text = f"{item.get('title', '')} {item.get('body', '')}".lower()
                if keyword.lower() in text:
                    older_mentions += 1

            # Calculate velocity
            if older_mentions == 0:
                velocity = float(recent_mentions) if recent_mentions > 0 else 0.0
            else:
                velocity = (recent_mentions - older_mentions) / older_mentions

            return round(velocity, 2)

        except Exception as e:
            logger.error(f"Error calculating velocity for '{keyword}': {e}")
            return 0.0

    async def detect_trends(self, user_id: UUID, max_trends: int = 10) -> List[Dict]:
        """
        Detect trending topics from user's content

        Args:
            user_id: User ID
            max_trends: Maximum number of trends to detect

        Returns:
            List of trend dictionaries
        """
        try:
            logger.info(f"Detecting trends for user {user_id}")

            # Step 1: Extract keywords from user's content
            trending_keywords = keyword_extraction_service.extract_keywords_from_content(
                user_id=user_id,
                days=7,
                min_mentions=2
            )

            if not trending_keywords:
                logger.info(f"No trending keywords found for user {user_id}")
                return []

            # Step 2: Get top keywords
            top_keywords = [kw[0] for kw in trending_keywords[:max_trends * 2]]  # Get more to filter later

            # Step 3: Get Google Trends scores
            google_scores = google_trends_service.batch_get_interest(top_keywords[:20])  # Limit API calls

            # Step 4: Calculate trend scores
            trends = []
            for keyword, mention_count, content_ids in trending_keywords[:max_trends * 2]:
                # Get Google Trends score
                google_score = google_scores.get(keyword, 0.0)

                # Calculate velocity
                velocity = self.calculate_velocity(user_id, keyword)

                # Calculate overall trend score
                trend_score = self.calculate_trend_score(
                    content_mentions=mention_count,
                    google_trends_score=google_score,
                    velocity=velocity
                )

                trends.append({
                    'keyword': keyword,
                    'score': trend_score,
                    'google_trends_score': google_score,
                    'content_mentions': mention_count,
                    'velocity': velocity,
                    'related_content_ids': [str(cid) for cid in content_ids]
                })

            # Step 5: Sort by score and return top trends
            trends.sort(key=lambda x: x['score'], reverse=True)
            top_trends = trends[:max_trends]

            logger.info(f"Detected {len(top_trends)} trends for user {user_id}")
            return top_trends

        except Exception as e:
            logger.error(f"Error detecting trends: {e}")
            return []

    async def save_trends(self, user_id: UUID, trends: List[Dict]) -> int:
        """
        Save detected trends to database

        Args:
            user_id: User ID
            trends: List of trend dictionaries

        Returns:
            Number of trends saved
        """
        try:
            if not trends:
                return 0

            saved_count = 0
            detected_at = datetime.now().isoformat()

            for trend_data in trends:
                try:
                    # Check if trend already exists for this user and keyword
                    existing = self.supabase.table('trends').select('id').eq('user_id', str(user_id)).eq('keyword', trend_data['keyword']).execute()

                    if existing.data:
                        # Update existing trend
                        self.supabase.table('trends').update({
                            'score': trend_data['score'],
                            'google_trends_score': trend_data['google_trends_score'],
                            'content_mentions': trend_data['content_mentions'],
                            'velocity': trend_data['velocity'],
                            'related_content_ids': trend_data['related_content_ids'],
                            'detected_at': detected_at
                        }).eq('id', existing.data[0]['id']).execute()
                    else:
                        # Insert new trend
                        self.supabase.table('trends').insert({
                            'user_id': str(user_id),
                            'keyword': trend_data['keyword'],
                            'score': trend_data['score'],
                            'google_trends_score': trend_data['google_trends_score'],
                            'content_mentions': trend_data['content_mentions'],
                            'velocity': trend_data['velocity'],
                            'related_content_ids': trend_data['related_content_ids'],
                            'detected_at': detected_at,
                            'metadata': {}
                        }).execute()

                    saved_count += 1

                except Exception as e:
                    logger.error(f"Error saving trend '{trend_data['keyword']}': {e}")
                    continue

            logger.info(f"Saved {saved_count} trends for user {user_id}")
            return saved_count

        except Exception as e:
            logger.error(f"Error saving trends: {e}")
            return 0

    async def get_top_trends(self, user_id: UUID, limit: int = 3) -> List[TrendResponse]:
        """
        Get top N trends for a user

        Args:
            user_id: User ID
            limit: Number of trends to return (default: 3)

        Returns:
            List of top trends
        """
        try:
            # Get trends from last 7 days, sorted by score
            cutoff_date = (datetime.now() - timedelta(days=7)).isoformat()

            response = self.supabase.table('trends').select('*').eq('user_id', str(user_id)).gte('detected_at', cutoff_date).order('score', desc=True).limit(limit).execute()

            if not response.data:
                return []

            # Parse the response data and convert to TrendResponse objects
            trends = []
            for item in response.data:
                try:
                    # Parse datetime strings
                    if isinstance(item.get('detected_at'), str):
                        item['detected_at'] = datetime.fromisoformat(item['detected_at'].replace('Z', '+00:00'))
                    if isinstance(item.get('created_at'), str):
                        item['created_at'] = datetime.fromisoformat(item['created_at'].replace('Z', '+00:00'))

                    # Ensure related_content_ids is a list of strings (UUIDs)
                    related_ids = item.get('related_content_ids')
                    if related_ids is None or related_ids == []:
                        item['related_content_ids'] = []
                    elif isinstance(related_ids, list):
                        # Convert any UUID objects to strings, then back to UUID objects for the model
                        item['related_content_ids'] = [
                            UUID(str(id_val)) if not isinstance(id_val, UUID) else id_val
                            for id_val in related_ids
                        ]
                    else:
                        item['related_content_ids'] = []

                    trends.append(TrendResponse(**item))
                except Exception as e:
                    logger.error(f"Error parsing trend item: {e}, item: {item}")
                    continue

            return trends

        except Exception as e:
            logger.error(f"Error getting top trends: {e}")
            return []

    async def get_trend_stats(self, user_id: UUID) -> Dict:
        """
        Get trend statistics for a user

        Args:
            user_id: User ID

        Returns:
            Dictionary with trend statistics
        """
        try:
            # Get all trends
            response = self.supabase.table('trends').select('*').eq('user_id', str(user_id)).execute()

            if not response.data:
                return {
                    'total_trends': 0,
                    'active_trends': 0,
                    'avg_score': 0.0,
                    'top_keywords': []
                }

            total_trends = len(response.data)

            # Get active trends (detected in last 7 days)
            cutoff_date = (datetime.now() - timedelta(days=7)).isoformat()
            active_trends = [t for t in response.data if t['detected_at'] >= cutoff_date]
            active_count = len(active_trends)

            # Calculate average score
            scores = [t['score'] for t in active_trends]
            avg_score = sum(scores) / len(scores) if scores else 0.0

            # Get top keywords
            top_keywords = [t['keyword'] for t in sorted(active_trends, key=lambda x: x['score'], reverse=True)[:5]]

            return {
                'total_trends': total_trends,
                'active_trends': active_count,
                'avg_score': round(avg_score, 2),
                'top_keywords': top_keywords
            }

        except Exception as e:
            logger.error(f"Error getting trend stats: {e}")
            return {
                'total_trends': 0,
                'active_trends': 0,
                'avg_score': 0.0,
                'top_keywords': []
            }

    async def detect_and_save_trends(self, user_id: UUID) -> Dict:
        """
        Detect trends and save them to database (convenience method)

        Args:
            user_id: User ID

        Returns:
            Dictionary with detection results
        """
        try:
            # Detect trends
            trends = await self.detect_trends(user_id, max_trends=10)

            if not trends:
                return {
                    'detected': 0,
                    'saved': 0,
                    'top_3': []
                }

            # Save trends
            saved_count = await self.save_trends(user_id, trends)

            # Get top 3
            top_3 = await self.get_top_trends(user_id, limit=3)

            return {
                'detected': len(trends),
                'saved': saved_count,
                'top_3': [{'keyword': t.keyword, 'score': t.score} for t in top_3]
            }

        except Exception as e:
            logger.error(f"Error in detect_and_save_trends: {e}")
            return {
                'detected': 0,
                'saved': 0,
                'top_3': []
            }


# Global instance
trend_service = TrendService()
