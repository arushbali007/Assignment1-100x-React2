"""Google Trends API integration service"""
from pytrends.request import TrendReq
from typing import Optional, List, Dict
import logging
from datetime import datetime, timedelta
import time

logger = logging.getLogger(__name__)


class GoogleTrendsService:
    """Service for fetching Google Trends data"""

    def __init__(self):
        """Initialize pytrends with retry logic"""
        self.pytrends = None
        self._initialize_client()

    def _initialize_client(self):
        """Initialize the pytrends client"""
        try:
            self.pytrends = TrendReq(hl='en-US', tz=360, timeout=(10, 25), retries=2, backoff_factor=0.1)
            logger.info("Google Trends client initialized")
        except Exception as e:
            logger.error(f"Failed to initialize Google Trends client: {e}")

    def get_interest_over_time(self, keywords: List[str], timeframe: str = 'now 7-d') -> Dict[str, float]:
        """
        Get interest over time for keywords

        Args:
            keywords: List of keywords to check (max 5 at a time)
            timeframe: Timeframe for trends (default: last 7 days)

        Returns:
            Dictionary mapping keywords to their average interest score (0-100)
        """
        try:
            if not keywords:
                return {}

            # Google Trends API limit is 5 keywords at a time
            keywords = keywords[:5]

            # Build payload
            self.pytrends.build_payload(
                kw_list=keywords,
                timeframe=timeframe,
                geo='',  # Worldwide
                gprop=''  # Web search
            )

            # Get interest over time
            interest_df = self.pytrends.interest_over_time()

            if interest_df.empty:
                logger.warning(f"No trend data found for keywords: {keywords}")
                return {kw: 0.0 for kw in keywords}

            # Calculate average interest for each keyword
            results = {}
            for keyword in keywords:
                if keyword in interest_df.columns:
                    avg_interest = float(interest_df[keyword].mean())
                    results[keyword] = round(avg_interest, 2)
                else:
                    results[keyword] = 0.0

            logger.info(f"Retrieved Google Trends data for {len(keywords)} keywords")
            return results

        except Exception as e:
            logger.error(f"Error fetching Google Trends data: {e}")
            # Return zeros on error
            return {kw: 0.0 for kw in keywords}

    def get_trending_searches(self, country: str = 'united_states') -> List[str]:
        """
        Get current trending searches

        Args:
            country: Country code (default: united_states)

        Returns:
            List of trending search terms
        """
        try:
            trending_df = self.pytrends.trending_searches(pn=country)

            if trending_df.empty:
                logger.warning(f"No trending searches found for {country}")
                return []

            # Get top 20 trending searches
            trending_searches = trending_df[0].tolist()[:20]
            logger.info(f"Retrieved {len(trending_searches)} trending searches")
            return trending_searches

        except Exception as e:
            logger.error(f"Error fetching trending searches: {e}")
            return []

    def get_related_queries(self, keyword: str) -> Dict[str, List[str]]:
        """
        Get related queries for a keyword

        Args:
            keyword: Keyword to check

        Returns:
            Dictionary with 'top' and 'rising' related queries
        """
        try:
            self.pytrends.build_payload(
                kw_list=[keyword],
                timeframe='now 7-d',
                geo='',
                gprop=''
            )

            related_queries = self.pytrends.related_queries()

            if not related_queries or keyword not in related_queries:
                return {'top': [], 'rising': []}

            result = {'top': [], 'rising': []}

            # Extract top queries
            if related_queries[keyword]['top'] is not None:
                top_df = related_queries[keyword]['top']
                if not top_df.empty:
                    result['top'] = top_df['query'].tolist()[:10]

            # Extract rising queries
            if related_queries[keyword]['rising'] is not None:
                rising_df = related_queries[keyword]['rising']
                if not rising_df.empty:
                    result['rising'] = rising_df['query'].tolist()[:10]

            logger.info(f"Retrieved related queries for '{keyword}'")
            return result

        except Exception as e:
            logger.error(f"Error fetching related queries for '{keyword}': {e}")
            return {'top': [], 'rising': []}

    def batch_get_interest(self, keywords: List[str], timeframe: str = 'now 7-d') -> Dict[str, float]:
        """
        Get interest scores for multiple keywords (handles batching)

        Args:
            keywords: List of keywords
            timeframe: Timeframe for trends

        Returns:
            Dictionary mapping keywords to their interest scores
        """
        try:
            if not keywords:
                return {}

            results = {}

            # Process in batches of 5 (Google Trends limit)
            for i in range(0, len(keywords), 5):
                batch = keywords[i:i+5]
                batch_results = self.get_interest_over_time(batch, timeframe)
                results.update(batch_results)

                # Rate limiting: sleep between batches
                if i + 5 < len(keywords):
                    time.sleep(2)

            return results

        except Exception as e:
            logger.error(f"Error in batch_get_interest: {e}")
            return {kw: 0.0 for kw in keywords}

    def compare_keywords(self, keywords: List[str], timeframe: str = 'now 7-d') -> Dict[str, dict]:
        """
        Compare multiple keywords and get detailed metrics

        Args:
            keywords: List of keywords to compare (max 5)
            timeframe: Timeframe for comparison

        Returns:
            Dictionary with keyword metrics
        """
        try:
            if not keywords or len(keywords) > 5:
                logger.warning(f"Invalid keyword count: {len(keywords)}. Must be 1-5.")
                return {}

            # Get interest over time
            interest_scores = self.get_interest_over_time(keywords, timeframe)

            # Build detailed response
            results = {}
            for keyword in keywords:
                results[keyword] = {
                    'avg_interest': interest_scores.get(keyword, 0.0),
                    'is_trending': interest_scores.get(keyword, 0.0) > 50  # Threshold
                }

            return results

        except Exception as e:
            logger.error(f"Error comparing keywords: {e}")
            return {}


# Global instance
google_trends_service = GoogleTrendsService()
