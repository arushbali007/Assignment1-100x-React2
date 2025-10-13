import requests
import streamlit as st
from typing import Optional, Dict

API_BASE_URL = "http://localhost:8000/api"


def signup_user(email: str, password: str, full_name: str = "", timezone: str = "UTC") -> Dict:
    """Sign up a new user"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/auth/signup",
            json={
                "email": email,
                "password": password,
                "full_name": full_name,
                "timezone": timezone
            }
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        if hasattr(e, 'response') and e.response is not None:
            error_detail = e.response.json().get("detail", "Unknown error")
            raise Exception(error_detail)
        raise Exception(f"Connection error: {str(e)}")


def login_user(email: str, password: str) -> Dict:
    """Login user and get token"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/auth/login",
            json={
                "email": email,
                "password": password
            }
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        if hasattr(e, 'response') and e.response is not None:
            error_detail = e.response.json().get("detail", "Unknown error")
            raise Exception(error_detail)
        raise Exception(f"Connection error: {str(e)}")


def get_current_user(token: str) -> Optional[Dict]:
    """Get current user profile"""
    try:
        response = requests.get(
            f"{API_BASE_URL}/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException:
        return None


def logout_user():
    """Logout user by clearing session"""
    for key in list(st.session_state.keys()):
        del st.session_state[key]


def is_authenticated() -> bool:
    """Check if user is authenticated"""
    return "access_token" in st.session_state and st.session_state.access_token is not None


# Source Management Functions

def get_headers() -> Dict:
    """Get authorization headers"""
    token = st.session_state.get("access_token")
    return {"Authorization": f"Bearer {token}"}


def create_source(source_data: Dict) -> Dict:
    """Create a new source"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/sources/",
            json=source_data,
            headers=get_headers()
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        if hasattr(e, 'response') and e.response is not None:
            error_detail = e.response.json().get("detail", "Unknown error")
            raise Exception(error_detail)
        raise Exception(f"Connection error: {str(e)}")


def get_sources(source_type: Optional[str] = None, is_active: Optional[bool] = None) -> Dict:
    """Get all sources with optional filters"""
    try:
        params = {}
        if source_type:
            params["source_type"] = source_type
        if is_active is not None:
            params["is_active"] = is_active

        response = requests.get(
            f"{API_BASE_URL}/sources/",
            params=params,
            headers=get_headers()
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        if hasattr(e, 'response') and e.response is not None:
            error_detail = e.response.json().get("detail", "Unknown error")
            raise Exception(error_detail)
        raise Exception(f"Connection error: {str(e)}")


def get_source_stats() -> Dict:
    """Get source statistics"""
    try:
        response = requests.get(
            f"{API_BASE_URL}/sources/stats",
            headers=get_headers()
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"twitter": 0, "youtube": 0, "rss": 0, "newsletter": 0, "total": 0}


def update_source(source_id: str, update_data: Dict) -> Dict:
    """Update a source"""
    try:
        response = requests.patch(
            f"{API_BASE_URL}/sources/{source_id}",
            json=update_data,
            headers=get_headers()
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        if hasattr(e, 'response') and e.response is not None:
            error_detail = e.response.json().get("detail", "Unknown error")
            raise Exception(error_detail)
        raise Exception(f"Connection error: {str(e)}")


def delete_source(source_id: str) -> bool:
    """Delete a source"""
    try:
        response = requests.delete(
            f"{API_BASE_URL}/sources/{source_id}",
            headers=get_headers()
        )
        response.raise_for_status()
        return True
    except requests.exceptions.RequestException as e:
        if hasattr(e, 'response') and e.response is not None:
            error_detail = e.response.json().get("detail", "Unknown error")
            raise Exception(error_detail)
        raise Exception(f"Connection error: {str(e)}")


# Content Management Functions

def fetch_content() -> Dict:
    """Trigger content fetch from all active sources"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/content/fetch",
            headers=get_headers()
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        if hasattr(e, 'response') and e.response is not None:
            error_detail = e.response.json().get("detail", "Unknown error")
            raise Exception(error_detail)
        raise Exception(f"Connection error: {str(e)}")


def get_content(content_type: Optional[str] = None, source_id: Optional[str] = None, page: int = 1, page_size: int = 20) -> Dict:
    """Get paginated content list"""
    try:
        params = {
            "page": page,
            "page_size": page_size
        }
        if content_type:
            params["content_type"] = content_type
        if source_id:
            params["source_id"] = source_id

        response = requests.get(
            f"{API_BASE_URL}/content/",
            params=params,
            headers=get_headers()
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        if hasattr(e, 'response') and e.response is not None:
            error_detail = e.response.json().get("detail", "Unknown error")
            raise Exception(error_detail)
        raise Exception(f"Connection error: {str(e)}")


def get_content_stats() -> Dict:
    """Get content statistics"""
    try:
        response = requests.get(
            f"{API_BASE_URL}/content/stats",
            headers=get_headers()
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"total": 0, "by_type": {}}


def delete_content(content_id: str) -> bool:
    """Delete content"""
    try:
        response = requests.delete(
            f"{API_BASE_URL}/content/{content_id}",
            headers=get_headers()
        )
        response.raise_for_status()
        return True
    except requests.exceptions.RequestException as e:
        if hasattr(e, 'response') and e.response is not None:
            error_detail = e.response.json().get("detail", "Unknown error")
            raise Exception(error_detail)
        raise Exception(f"Connection error: {str(e)}")


# Trend Management Functions

def detect_trends() -> Dict:
    """Trigger trend detection"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/trends/detect",
            headers=get_headers()
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        if hasattr(e, 'response') and e.response is not None:
            error_detail = e.response.json().get("detail", "Unknown error")
            raise Exception(error_detail)
        raise Exception(f"Connection error: {str(e)}")


def get_top_trends(limit: int = 3) -> Dict:
    """Get top N trending topics"""
    try:
        response = requests.get(
            f"{API_BASE_URL}/trends/top",
            params={"limit": limit},
            headers=get_headers()
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        if hasattr(e, 'response') and e.response is not None:
            error_detail = e.response.json().get("detail", "Unknown error")
            raise Exception(error_detail)
        raise Exception(f"Connection error: {str(e)}")


def get_trend_stats() -> Dict:
    """Get trend statistics"""
    try:
        response = requests.get(
            f"{API_BASE_URL}/trends/stats",
            headers=get_headers()
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"total_trends": 0, "active_trends": 0, "avg_score": 0.0, "top_keywords": []}


def get_trends(page: int = 1, page_size: int = 20) -> Dict:
    """Get paginated trends list"""
    try:
        params = {
            "page": page,
            "page_size": page_size
        }
        response = requests.get(
            f"{API_BASE_URL}/trends/",
            params=params,
            headers=get_headers()
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        if hasattr(e, 'response') and e.response is not None:
            error_detail = e.response.json().get("detail", "Unknown error")
            raise Exception(error_detail)
        raise Exception(f"Connection error: {str(e)}")


def delete_trend(trend_id: str) -> bool:
    """Delete trend"""
    try:
        response = requests.delete(
            f"{API_BASE_URL}/trends/{trend_id}",
            headers=get_headers()
        )
        response.raise_for_status()
        return True
    except requests.exceptions.RequestException as e:
        if hasattr(e, 'response') and e.response is not None:
            error_detail = e.response.json().get("detail", "Unknown error")
            raise Exception(error_detail)
        raise Exception(f"Connection error: {str(e)}")


# Style Profile Management Functions

def create_style_profile(newsletter_text: str, newsletter_title: Optional[str] = None) -> Dict:
    """Create and analyze a style profile from newsletter text"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/style-profiles/",
            json={
                "newsletter_text": newsletter_text,
                "newsletter_title": newsletter_title
            },
            headers=get_headers()
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        if hasattr(e, 'response') and e.response is not None:
            error_detail = e.response.json().get("detail", "Unknown error")
            raise Exception(error_detail)
        raise Exception(f"Connection error: {str(e)}")


def get_style_profiles(page: int = 1, page_size: int = 10) -> Dict:
    """Get paginated style profiles list"""
    try:
        params = {
            "page": page,
            "page_size": page_size
        }
        response = requests.get(
            f"{API_BASE_URL}/style-profiles/",
            params=params,
            headers=get_headers()
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        if hasattr(e, 'response') and e.response is not None:
            error_detail = e.response.json().get("detail", "Unknown error")
            raise Exception(error_detail)
        raise Exception(f"Connection error: {str(e)}")


def get_primary_profile() -> Optional[Dict]:
    """Get the primary style profile"""
    try:
        response = requests.get(
            f"{API_BASE_URL}/style-profiles/primary",
            headers=get_headers()
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return None


def get_aggregated_style() -> Dict:
    """Get aggregated style summary from all profiles"""
    try:
        response = requests.get(
            f"{API_BASE_URL}/style-profiles/aggregated",
            headers=get_headers()
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        if hasattr(e, 'response') and e.response is not None:
            error_detail = e.response.json().get("detail", "Unknown error")
            raise Exception(error_detail)
        raise Exception(f"Connection error: {str(e)}")


def get_style_stats() -> Dict:
    """Get style profile statistics"""
    try:
        response = requests.get(
            f"{API_BASE_URL}/style-profiles/stats",
            headers=get_headers()
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"total_profiles": 0, "analyzed_profiles": 0, "has_primary": False}


def set_primary_profile(profile_id: str) -> Dict:
    """Set a style profile as primary"""
    try:
        response = requests.patch(
            f"{API_BASE_URL}/style-profiles/{profile_id}/primary",
            headers=get_headers()
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        if hasattr(e, 'response') and e.response is not None:
            error_detail = e.response.json().get("detail", "Unknown error")
            raise Exception(error_detail)
        raise Exception(f"Connection error: {str(e)}")


def delete_style_profile(profile_id: str) -> bool:
    """Delete a style profile"""
    try:
        response = requests.delete(
            f"{API_BASE_URL}/style-profiles/{profile_id}",
            headers=get_headers()
        )
        response.raise_for_status()
        return True
    except requests.exceptions.RequestException as e:
        if hasattr(e, 'response') and e.response is not None:
            error_detail = e.response.json().get("detail", "Unknown error")
            raise Exception(error_detail)
        raise Exception(f"Connection error: {str(e)}")


# Draft Management Functions

def generate_draft(force_regenerate: bool = False, include_trends: bool = True, max_trends: int = 3) -> Dict:
    """Generate a new newsletter draft"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/drafts/generate",
            json={
                "force_regenerate": force_regenerate,
                "include_trends": include_trends,
                "max_trends": max_trends
            },
            headers=get_headers()
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        if hasattr(e, 'response') and e.response is not None:
            error_detail = e.response.json().get("detail", "Unknown error")
            raise Exception(error_detail)
        raise Exception(f"Connection error: {str(e)}")


def get_drafts(page: int = 1, page_size: int = 10, status: Optional[str] = None) -> Dict:
    """Get paginated drafts list"""
    try:
        params = {
            "page": page,
            "page_size": page_size
        }
        if status:
            params["status"] = status

        response = requests.get(
            f"{API_BASE_URL}/drafts/",
            params=params,
            headers=get_headers()
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        if hasattr(e, 'response') and e.response is not None:
            error_detail = e.response.json().get("detail", "Unknown error")
            raise Exception(error_detail)
        raise Exception(f"Connection error: {str(e)}")


def get_draft(draft_id: str) -> Dict:
    """Get specific draft by ID"""
    try:
        response = requests.get(
            f"{API_BASE_URL}/drafts/{draft_id}",
            headers=get_headers()
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        if hasattr(e, 'response') and e.response is not None:
            error_detail = e.response.json().get("detail", "Unknown error")
            raise Exception(error_detail)
        raise Exception(f"Connection error: {str(e)}")


def update_draft(draft_id: str, update_data: Dict) -> Dict:
    """Update draft"""
    try:
        response = requests.patch(
            f"{API_BASE_URL}/drafts/{draft_id}",
            json=update_data,
            headers=get_headers()
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        if hasattr(e, 'response') and e.response is not None:
            error_detail = e.response.json().get("detail", "Unknown error")
            raise Exception(error_detail)
        raise Exception(f"Connection error: {str(e)}")


def delete_draft(draft_id: str) -> bool:
    """Delete draft"""
    try:
        response = requests.delete(
            f"{API_BASE_URL}/drafts/{draft_id}",
            headers=get_headers()
        )
        response.raise_for_status()
        return True
    except requests.exceptions.RequestException as e:
        if hasattr(e, 'response') and e.response is not None:
            error_detail = e.response.json().get("detail", "Unknown error")
            raise Exception(error_detail)
        raise Exception(f"Connection error: {str(e)}")


def get_draft_stats() -> Dict:
    """Get draft statistics"""
    try:
        response = requests.get(
            f"{API_BASE_URL}/drafts/stats",
            headers=get_headers()
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {
            "total_drafts": 0,
            "pending_drafts": 0,
            "reviewed_drafts": 0,
            "sent_drafts": 0,
            "archived_drafts": 0
        }


# Newsletter Send Functions

def send_newsletter(draft_id: str, recipient_email: str, is_test: bool = False, from_email: Optional[str] = None, from_name: Optional[str] = None) -> Dict:
    """Send newsletter to a single recipient"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/newsletter-sends/send",
            json={
                "draft_id": draft_id,
                "recipient_email": recipient_email,
                "is_test": is_test,
                "from_email": from_email,
                "from_name": from_name
            },
            headers=get_headers()
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        if hasattr(e, 'response') and e.response is not None:
            error_detail = e.response.json().get("detail", "Unknown error")
            raise Exception(error_detail)
        raise Exception(f"Connection error: {str(e)}")


def get_newsletter_sends(page: int = 1, page_size: int = 10, status: Optional[str] = None, draft_id: Optional[str] = None) -> Dict:
    """Get paginated newsletter sends"""
    try:
        params = {
            "page": page,
            "page_size": page_size
        }
        if status:
            params["status"] = status
        if draft_id:
            params["draft_id"] = draft_id

        response = requests.get(
            f"{API_BASE_URL}/newsletter-sends/",
            params=params,
            headers=get_headers()
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        if hasattr(e, 'response') and e.response is not None:
            error_detail = e.response.json().get("detail", "Unknown error")
            raise Exception(error_detail)
        raise Exception(f"Connection error: {str(e)}")


def get_send_stats() -> Dict:
    """Get newsletter send statistics"""
    try:
        response = requests.get(
            f"{API_BASE_URL}/newsletter-sends/stats",
            headers=get_headers()
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {
            "total_sends": 0,
            "successful_sends": 0,
            "failed_sends": 0,
            "open_rate": 0.0,
            "click_rate": 0.0
        }
