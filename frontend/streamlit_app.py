import streamlit as st
from utils import (
    signup_user, login_user, logout_user, is_authenticated, get_current_user,
    create_source, get_sources, get_source_stats, update_source, delete_source,
    fetch_content, get_content, get_content_stats, delete_content,
    detect_trends, get_top_trends, get_trend_stats, get_trends, delete_trend,
    create_style_profile, get_style_profiles, get_primary_profile, get_aggregated_style,
    get_style_stats, set_primary_profile, delete_style_profile,
    generate_draft, get_drafts, get_draft, update_draft, delete_draft, get_draft_stats,
    send_newsletter, get_newsletter_sends, get_send_stats
)

st.set_page_config(
    page_title="CreatorPulse",
    page_icon="📰",
    layout="wide"
)

# Initialize session state
if "access_token" not in st.session_state:
    st.session_state.access_token = None
if "user" not in st.session_state:
    st.session_state.user = None


def show_login_page():
    """Display login page"""
    st.title("📰 CreatorPulse")
    st.subheader("Login to Your Account")

    with st.form("login_form"):
        email = st.text_input("Email", placeholder="your@email.com")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Login", use_container_width=True)

        if submit:
            if not email or not password:
                st.error("Please fill in all fields")
            else:
                try:
                    with st.spinner("Logging in..."):
                        result = login_user(email, password)
                        st.session_state.access_token = result["access_token"]
                        st.session_state.user = result["user"]
                        st.success("Login successful!")
                        st.rerun()
                except Exception as e:
                    st.error(f"Login failed: {str(e)}")

    st.markdown("---")
    st.markdown("Don't have an account?")
    if st.button("Sign Up", use_container_width=True):
        st.session_state.show_signup = True
        st.rerun()


def show_signup_page():
    """Display signup page"""
    st.title("📰 CreatorPulse")
    st.subheader("Create Your Account")

    with st.form("signup_form"):
        full_name = st.text_input("Full Name (Optional)")
        email = st.text_input("Email", placeholder="your@email.com")
        password = st.text_input("Password", type="password", help="Minimum 6 characters")
        confirm_password = st.text_input("Confirm Password", type="password")

        col1, col2 = st.columns([1, 1])
        with col1:
            timezone = st.selectbox("Timezone", ["UTC", "America/New_York", "America/Los_Angeles", "Europe/London", "Asia/Kolkata"])

        submit = st.form_submit_button("Sign Up", use_container_width=True)

        if submit:
            if not email or not password:
                st.error("Email and password are required")
            elif len(password) < 6:
                st.error("Password must be at least 6 characters")
            elif password != confirm_password:
                st.error("Passwords do not match")
            else:
                try:
                    with st.spinner("Creating account..."):
                        result = signup_user(email, password, full_name, timezone)
                        st.session_state.access_token = result["access_token"]
                        st.session_state.user = result["user"]
                        st.success("Account created successfully!")
                        st.rerun()
                except Exception as e:
                    st.error(f"Signup failed: {str(e)}")

    st.markdown("---")
    st.markdown("Already have an account?")
    if st.button("Login", use_container_width=True):
        st.session_state.show_signup = False
        st.rerun()


def show_dashboard():
    """Display main dashboard for authenticated users"""
    # Sidebar
    with st.sidebar:
        st.title("📰 CreatorPulse")

        if st.session_state.user:
            st.write(f"👤 **{st.session_state.user.get('email', 'User')}**")
            if st.session_state.user.get('full_name'):
                st.write(f"*{st.session_state.user['full_name']}*")

        st.markdown("---")

        # Navigation
        st.header("Navigation")
        page = st.radio(
            "Go to",
            ["Dashboard", "Sources", "Content", "Trends", "Writing Style", "Drafts", "Settings"],
            label_visibility="collapsed"
        )

        st.markdown("---")

        if st.button("🚪 Logout", use_container_width=True):
            logout_user()
            st.rerun()

    # Main content
    st.title(f"📊 {page}")

    if page == "Dashboard":
        st.markdown("""
        Welcome to **CreatorPulse**!

        Your AI-powered newsletter curator is ready to help you create amazing content.

        ### Quick Stats
        """)

        # Get real stats
        try:
            source_stats = get_source_stats()
            total_sources = source_stats.get("total", 0)
        except:
            total_sources = 0

        try:
            content_stats = get_content_stats()
            total_content = content_stats.get("total", 0)
        except:
            total_content = 0

        try:
            draft_stats = get_draft_stats()
            total_drafts = draft_stats.get("total_drafts", 0)
        except:
            total_drafts = 0

        try:
            send_stats = get_send_stats()
            total_sent = send_stats.get("successful_sends", 0)
            open_rate = send_stats.get("open_rate", 0)
        except:
            total_sent = 0
            open_rate = 0

        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            st.metric("Sources", total_sources, help="Connected content sources")
        with col2:
            st.metric("Content", total_content, help="Aggregated content items")
        with col3:
            st.metric("Drafts", total_drafts, help="Generated newsletter drafts")
        with col4:
            st.metric("Sent", total_sent, help="Newsletters sent successfully")
        with col5:
            st.metric("Open Rate", f"{open_rate:.1f}%", help="Average email open rate")

        st.markdown("---")

        # Activity Summary
        st.markdown("### 📊 Activity Summary")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("#### Recent Activity")
            if total_sources == 0:
                st.info("🚀 **Get Started:**\n\n1. Add content sources\n2. Fetch content\n3. Detect trends\n4. Generate drafts\n5. Send newsletters!")
            else:
                activity = []
                if total_sources > 0:
                    activity.append(f"✅ {total_sources} source(s) configured")
                if total_content > 0:
                    activity.append(f"✅ {total_content} content item(s) aggregated")
                if total_drafts > 0:
                    activity.append(f"✅ {total_drafts} draft(s) generated")
                if total_sent > 0:
                    activity.append(f"✅ {total_sent} newsletter(s) sent")

                for item in activity:
                    st.markdown(item)

        with col2:
            st.markdown("#### Quick Actions")
            if st.button("➕ Add Source", use_container_width=True):
                st.session_state.quick_nav = "Sources"
                st.rerun()
            if st.button("🔄 Fetch Content", use_container_width=True):
                try:
                    with st.spinner("Fetching content..."):
                        result = fetch_content()
                        st.success(result.get("message", "Content fetched!"))
                        st.rerun()
                except Exception as e:
                    st.error(f"Failed: {str(e)}")
            if st.button("🔍 Detect Trends", use_container_width=True):
                try:
                    with st.spinner("Detecting trends..."):
                        result = detect_trends()
                        st.success(result.get("message", "Trends detected!"))
                        st.rerun()
                except Exception as e:
                    st.error(f"Failed: {str(e)}")
            if st.button("✨ Generate Draft", use_container_width=True):
                try:
                    with st.spinner("Generating draft..."):
                        result = generate_draft()
                        st.success("Draft generated!")
                        st.rerun()
                except Exception as e:
                    st.error(f"Failed: {str(e)}")

    elif page == "Sources":
        show_sources_page()

    elif page == "Content":
        show_content_page()

    elif page == "Trends":
        show_trends_page()

    elif page == "Writing Style":
        show_writing_style_page()

    elif page == "Drafts":
        show_drafts_page()

    elif page == "Settings":
        st.markdown("### Account Settings")

        if st.session_state.user:
            with st.form("settings_form"):
                st.text_input("Email", value=st.session_state.user.get('email', ''), disabled=True)
                st.text_input("Full Name", value=st.session_state.user.get('full_name', ''))
                st.selectbox("Timezone", ["UTC", "America/New_York", "America/Los_Angeles", "Europe/London", "Asia/Kolkata"],
                           index=0)

                if st.form_submit_button("Save Changes"):
                    st.success("Settings updated successfully!")


def show_sources_page():
    """Display source management page"""
    st.markdown("### Manage Your Content Sources")
    st.markdown("Add and manage Twitter accounts, YouTube channels, and RSS feeds to aggregate content from.")

    # Tabs for different actions
    tab1, tab2 = st.tabs(["📋 My Sources", "➕ Add New Source"])

    with tab1:
        # Display source stats
        try:
            stats = get_source_stats()
            col1, col2, col3, col4, col5 = st.columns(5)
            with col1:
                st.metric("Total", stats.get("total", 0))
            with col2:
                st.metric("Twitter", stats.get("twitter", 0), help="Twitter/X accounts")
            with col3:
                st.metric("YouTube", stats.get("youtube", 0), help="YouTube channels")
            with col4:
                st.metric("RSS", stats.get("rss", 0), help="RSS feeds")
            with col5:
                st.metric("Newsletter", stats.get("newsletter", 0), help="Newsletter archives")
        except Exception as e:
            st.error(f"Failed to load stats: {str(e)}")

        st.markdown("---")

        # Filter options
        col1, col2 = st.columns([2, 1])
        with col1:
            filter_type = st.selectbox(
                "Filter by type",
                ["All", "Twitter", "YouTube", "RSS", "Newsletter"],
                key="source_filter_type"
            )
        with col2:
            filter_active = st.selectbox(
                "Status",
                ["All", "Active", "Inactive"],
                key="source_filter_active"
            )

        # Convert filter values
        source_type_param = None if filter_type == "All" else filter_type.lower()
        is_active_param = None if filter_active == "All" else (filter_active == "Active")

        # Load and display sources
        try:
            result = get_sources(source_type=source_type_param, is_active=is_active_param)
            sources = result.get("sources", [])

            if not sources:
                st.info("No sources found. Add your first source in the 'Add New Source' tab!")
            else:
                st.markdown(f"**{len(sources)} source(s) found**")

                for source in sources:
                    with st.expander(f"{'✅' if source['is_active'] else '❌'} {source['name']} ({source['source_type'].upper()})"):
                        col1, col2 = st.columns([3, 1])

                        with col1:
                            st.write(f"**URL:** {source['source_url']}")
                            if source.get('source_identifier'):
                                st.write(f"**Identifier:** {source['source_identifier']}")
                            st.write(f"**Status:** {'Active' if source['is_active'] else 'Inactive'}")
                            st.write(f"**Added:** {source['created_at'][:10]}")

                        with col2:
                            # Toggle active status
                            new_status = not source['is_active']
                            status_label = "Deactivate" if source['is_active'] else "Activate"

                            if st.button(status_label, key=f"toggle_{source['id']}"):
                                try:
                                    update_source(source['id'], {"is_active": new_status})
                                    st.success(f"Source {status_label.lower()}d!")
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Failed to update: {str(e)}")

                            # Delete button
                            if st.button("🗑️ Delete", key=f"delete_{source['id']}", type="secondary"):
                                try:
                                    delete_source(source['id'])
                                    st.success("Source deleted!")
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Failed to delete: {str(e)}")

        except Exception as e:
            st.error(f"Failed to load sources: {str(e)}")

    with tab2:
        # Add new source form
        st.markdown("### Add a New Source")

        with st.form("add_source_form"):
            source_type = st.selectbox(
                "Source Type",
                ["Twitter", "YouTube", "RSS", "Newsletter"],
                help="Select the type of content source you want to add"
            )

            col1, col2 = st.columns(2)

            with col1:
                name = st.text_input(
                    "Display Name",
                    placeholder="e.g., TechCrunch, MrBeast Channel",
                    help="A friendly name for this source"
                )

            with col2:
                source_identifier = st.text_input(
                    "Identifier (Optional)",
                    placeholder="@username or channel ID",
                    help="Will be auto-extracted from URL if not provided"
                )

            source_url = st.text_input(
                "Source URL",
                placeholder="https://...",
                help="Full URL to the Twitter profile, YouTube channel, RSS feed, or newsletter archive"
            )

            # Help text based on source type
            if source_type == "Twitter":
                st.info("📱 **Twitter:** Enter the profile URL (e.g., https://twitter.com/username or https://x.com/username)")
            elif source_type == "YouTube":
                st.info("🎥 **YouTube:** Enter the channel URL (e.g., https://youtube.com/@channelname or https://youtube.com/channel/ID)")
            elif source_type == "RSS":
                st.info("📡 **RSS:** Enter the feed URL (e.g., https://example.com/feed.xml)")
            elif source_type == "Newsletter":
                st.info("📧 **Newsletter:** Enter the newsletter archive URL")

            is_active = st.checkbox("Active", value=True, help="Whether to actively fetch content from this source")

            submitted = st.form_submit_button("Add Source", use_container_width=True, type="primary")

            if submitted:
                if not name or not source_url:
                    st.error("Name and URL are required!")
                else:
                    try:
                        source_data = {
                            "source_type": source_type.lower(),
                            "source_url": source_url,
                            "name": name,
                            "is_active": is_active,
                            "metadata": {}
                        }

                        if source_identifier:
                            source_data["source_identifier"] = source_identifier

                        with st.spinner("Adding source..."):
                            result = create_source(source_data)
                            st.success(f"✅ Source '{name}' added successfully!")
                            st.balloons()
                            # Wait a moment before rerunning to show the success message
                            import time
                            time.sleep(1)
                            st.rerun()

                    except Exception as e:
                        st.error(f"Failed to add source: {str(e)}")


def show_content_page():
    """Display content aggregation page"""
    st.markdown("### Aggregated Content")
    st.markdown("View and manage content fetched from your sources.")

    # Content stats
    try:
        stats = get_content_stats()
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            st.metric("Total", stats.get("total", 0))
        with col2:
            st.metric("Tweets", stats.get("by_type", {}).get("tweet", 0), help="Twitter/X posts")
        with col3:
            st.metric("Videos", stats.get("by_type", {}).get("video", 0), help="YouTube videos")
        with col4:
            st.metric("Articles", stats.get("by_type", {}).get("article", 0), help="RSS articles")
        with col5:
            st.metric("Newsletters", stats.get("by_type", {}).get("newsletter", 0))
    except Exception as e:
        st.error(f"Failed to load stats: {str(e)}")

    st.markdown("---")

    # Fetch content button
    col1, col2 = st.columns([3, 1])
    with col2:
        if st.button("🔄 Fetch New Content", use_container_width=True, type="primary"):
            try:
                with st.spinner("Fetching content from all sources..."):
                    result = fetch_content()
                    st.success(result.get("message", "Content fetched!"))
                    st.rerun()
            except Exception as e:
                st.error(f"Failed to fetch content: {str(e)}")

    # Filter options
    col1, col2 = st.columns([2, 1])
    with col1:
        filter_type = st.selectbox(
            "Filter by type",
            ["All", "Tweet", "Video", "Article", "Newsletter"],
            key="content_filter_type"
        )

    # Convert filter values
    content_type_param = None if filter_type == "All" else filter_type.lower()

    # Pagination state
    if "content_page" not in st.session_state:
        st.session_state.content_page = 1

    # Load and display content
    try:
        result = get_content(
            content_type=content_type_param,
            page=st.session_state.content_page,
            page_size=10
        )

        items = result.get("items", [])
        total = result.get("total", 0)
        pages = result.get("pages", 1)

        if total == 0:
            st.info("📭 No content found. Click 'Fetch New Content' to aggregate content from your sources!")
        else:
            st.markdown(f"**Showing {len(items)} of {total} items (Page {st.session_state.content_page} of {pages})**")

            for item in items:
                content_type_emoji = {
                    "tweet": "🐦",
                    "video": "🎥",
                    "article": "📄",
                    "newsletter": "📧"
                }
                emoji = content_type_emoji.get(item['content_type'], "📌")

                with st.expander(f"{emoji} {item.get('title') or item.get('body', '')[:80]+'...'}"):
                    col1, col2 = st.columns([4, 1])

                    with col1:
                        if item.get('title'):
                            st.markdown(f"**{item['title']}**")

                        if item.get('body'):
                            # Limit body display
                            body = item['body']
                            if len(body) > 500:
                                body = body[:500] + "..."
                            st.write(body)

                        st.markdown(f"🔗 [View Original]({item['url']})")

                        if item.get('author'):
                            st.write(f"👤 **Author:** {item['author']}")

                        if item.get('published_at'):
                            st.write(f"📅 **Published:** {item['published_at'][:10]}")

                        st.write(f"🏷️ **Type:** {item['content_type'].upper()}")

                    with col2:
                        if st.button("🗑️ Delete", key=f"delete_content_{item['id']}", type="secondary"):
                            try:
                                delete_content(item['id'])
                                st.success("Content deleted!")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Failed to delete: {str(e)}")

            # Pagination controls
            st.markdown("---")
            col1, col2, col3 = st.columns([1, 2, 1])

            with col1:
                if st.session_state.content_page > 1:
                    if st.button("⬅️ Previous"):
                        st.session_state.content_page -= 1
                        st.rerun()

            with col2:
                st.markdown(f"<div style='text-align: center'>Page {st.session_state.content_page} of {pages}</div>", unsafe_allow_html=True)

            with col3:
                if st.session_state.content_page < pages:
                    if st.button("Next ➡️"):
                        st.session_state.content_page += 1
                        st.rerun()

    except Exception as e:
        st.error(f"Failed to load content: {str(e)}")


def show_trends_page():
    """Display trends page"""
    st.markdown("### Trending Topics")
    st.markdown("Discover what's trending in your content.")

    # Trend stats
    try:
        stats = get_trend_stats()
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Trends", stats.get("total_trends", 0))
        with col2:
            st.metric("Active Trends", stats.get("active_trends", 0), help="Trends detected in last 7 days")
        with col3:
            st.metric("Avg Score", f"{stats.get('avg_score', 0):.1f}", help="Average trend score (0-100)")
    except Exception as e:
        st.error(f"Failed to load stats: {str(e)}")

    st.markdown("---")

    # Top 3 Trends Highlight
    st.markdown("### 🔥 Top 3 Trending Topics")
    try:
        top_trends_result = get_top_trends(limit=3)
        top_trends = top_trends_result.get("trends", [])

        if not top_trends:
            st.info("📊 No trends detected yet. Click 'Detect Trends' below after you have some content!")
        else:
            for i, trend in enumerate(top_trends, 1):
                with st.container():
                    col1, col2, col3 = st.columns([3, 1, 1])
                    with col1:
                        st.markdown(f"**{i}. {trend['keyword']}**")
                    with col2:
                        score_color = "🟢" if trend['score'] >= 70 else "🟡" if trend['score'] >= 40 else "🔴"
                        st.markdown(f"{score_color} Score: **{trend['score']:.1f}**/100")
                    with col3:
                        st.markdown(f"📊 {trend['content_mentions']} mentions")

                    # Show additional details
                    with st.expander("View Details"):
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.write(f"**Google Trends:** {trend.get('google_trends_score', 0):.1f}")
                        with col2:
                            velocity = trend.get('velocity', 0)
                            velocity_emoji = "📈" if velocity > 0 else "📉" if velocity < 0 else "➡️"
                            st.write(f"**Velocity:** {velocity_emoji} {velocity:.2f}")
                        with col3:
                            st.write(f"**Content IDs:** {len(trend.get('related_content_ids', []))}")

                        st.write(f"**Detected:** {trend.get('detected_at', trend.get('created_at', ''))[:10]}")

                    st.markdown("---")

    except Exception as e:
        st.error(f"Failed to load top trends: {str(e)}")

    # Detect trends button
    col1, col2 = st.columns([3, 1])
    with col2:
        if st.button("🔍 Detect Trends", use_container_width=True, type="primary"):
            try:
                with st.spinner("Analyzing content and detecting trends..."):
                    result = detect_trends()
                    st.success(result.get("message", "Trends detected!"))
                    st.rerun()
            except Exception as e:
                st.error(f"Failed to detect trends: {str(e)}")

    st.markdown("---")
    st.markdown("### 📊 All Detected Trends")

    # Pagination state
    if "trends_page" not in st.session_state:
        st.session_state.trends_page = 1

    # Load and display trends
    try:
        result = get_trends(
            page=st.session_state.trends_page,
            page_size=10
        )

        items = result.get("items", [])
        total = result.get("total", 0)
        pages = result.get("pages", 1)

        if total == 0:
            st.info("📭 No trends found. Click 'Detect Trends' to analyze your content!")
        else:
            st.markdown(f"**Showing {len(items)} of {total} trends (Page {st.session_state.trends_page} of {pages})**")

            for item in items:
                score_color = "🟢" if item['score'] >= 70 else "🟡" if item['score'] >= 40 else "🔴"

                with st.expander(f"{score_color} {item['keyword']} (Score: {item['score']:.1f})"):
                    col1, col2 = st.columns([4, 1])

                    with col1:
                        st.markdown(f"### {item['keyword']}")

                        col_a, col_b, col_c = st.columns(3)
                        with col_a:
                            st.metric("Overall Score", f"{item['score']:.1f}/100")
                        with col_b:
                            st.metric("Content Mentions", item['content_mentions'])
                        with col_c:
                            st.metric("Google Trends", f"{item.get('google_trends_score', 0):.1f}")

                        velocity = item.get('velocity', 0)
                        velocity_emoji = "📈" if velocity > 0 else "📉" if velocity < 0 else "➡️"
                        st.write(f"**Velocity:** {velocity_emoji} {velocity:.2f} (growth rate)")

                        st.write(f"**Related Content:** {len(item.get('related_content_ids', []))} pieces")
                        st.write(f"**Detected:** {item.get('detected_at', '')[:10]}")

                    with col2:
                        if st.button("🗑️ Delete", key=f"delete_trend_{item['id']}", type="secondary"):
                            try:
                                delete_trend(item['id'])
                                st.success("Trend deleted!")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Failed to delete: {str(e)}")

            # Pagination controls
            st.markdown("---")
            col1, col2, col3 = st.columns([1, 2, 1])

            with col1:
                if st.session_state.trends_page > 1:
                    if st.button("⬅️ Previous"):
                        st.session_state.trends_page -= 1
                        st.rerun()

            with col2:
                st.markdown(f"<div style='text-align: center'>Page {st.session_state.trends_page} of {pages}</div>", unsafe_allow_html=True)

            with col3:
                if st.session_state.trends_page < pages:
                    if st.button("Next ➡️"):
                        st.session_state.trends_page += 1
                        st.rerun()

    except Exception as e:
        st.error(f"Failed to load trends: {str(e)}")


def show_writing_style_page():
    """Display writing style training page"""
    st.markdown("### ✍️ Writing Style Training")
    st.markdown("Upload past newsletters to train the AI on your unique writing style.")

    # Style stats
    try:
        stats = get_style_stats()
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Profiles", stats.get("total_profiles", 0), help="Number of newsletters analyzed")
        with col2:
            st.metric("Analyzed", stats.get("analyzed_profiles", 0), help="Successfully analyzed newsletters")
        with col3:
            has_primary = "Yes" if stats.get("has_primary", False) else "No"
            st.metric("Primary Set", has_primary, help="Whether you have a primary style profile")
    except Exception as e:
        st.error(f"Failed to load stats: {str(e)}")

    st.markdown("---")

    # Tabs for different actions
    tab1, tab2, tab3 = st.tabs(["📊 Style Summary", "📚 My Profiles", "➕ Upload Newsletter"])

    with tab1:
        st.markdown("### Your Writing Style Analysis")

        try:
            aggregated = get_aggregated_style()

            if not aggregated:
                st.info("📝 Upload at least one past newsletter to see your style analysis!")
            else:
                # Display aggregated style characteristics
                col1, col2 = st.columns(2)

                with col1:
                    st.markdown("#### Style Characteristics")
                    st.write(f"**Tone:** {aggregated.get('tone', 'N/A')}")
                    st.write(f"**Voice:** {aggregated.get('voice', 'N/A')}")
                    st.write(f"**Avg Sentence Length:** {aggregated.get('avg_sentence_length', 0):.1f} words")
                    st.write(f"**Avg Paragraph Length:** {aggregated.get('avg_paragraph_length', 0):.1f} words")

                with col2:
                    st.markdown("#### Confidence")
                    confidence = aggregated.get('style_confidence', 0)
                    sample_count = aggregated.get('sample_count', 0)

                    # Progress bar for confidence
                    st.progress(confidence)
                    st.write(f"**{confidence*100:.0f}%** confidence based on {sample_count} sample(s)")

                    if confidence < 0.5:
                        st.warning("💡 Upload more newsletters to improve confidence!")
                    elif confidence < 0.8:
                        st.info("👍 Good! A few more samples will help.")
                    else:
                        st.success("✨ Excellent confidence level!")

                st.markdown("---")

                # Key characteristics
                characteristics = aggregated.get('key_characteristics', [])
                if characteristics:
                    st.markdown("#### Key Characteristics")
                    for char in characteristics:
                        st.markdown(f"- {char}")

                # Common phrases
                common_phrases = aggregated.get('common_phrases', [])[:5]
                if common_phrases:
                    st.markdown("#### Common Phrases")
                    for phrase in common_phrases:
                        st.code(phrase, language=None)

        except Exception as e:
            st.error(f"Failed to load style summary: {str(e)}")

    with tab2:
        st.markdown("### Your Newsletter Profiles")

        # Pagination state
        if "style_page" not in st.session_state:
            st.session_state.style_page = 1

        try:
            result = get_style_profiles(
                page=st.session_state.style_page,
                page_size=5
            )

            profiles = result.get("profiles", [])
            total = result.get("total", 0)
            pages = result.get("total_pages", 1)

            if total == 0:
                st.info("📭 No style profiles yet. Upload your first newsletter in the 'Upload Newsletter' tab!")
            else:
                st.markdown(f"**{total} profile(s) found**")

                for profile in profiles:
                    is_primary = profile.get('is_primary', False)
                    title_prefix = "⭐" if is_primary else "📄"

                    title = profile.get('newsletter_title') or f"Newsletter from {profile.get('created_at', '')[:10]}"

                    with st.expander(f"{title_prefix} {title}"):
                        col1, col2 = st.columns([3, 1])

                        with col1:
                            if profile.get('newsletter_title'):
                                st.markdown(f"**Title:** {profile['newsletter_title']}")

                            st.write(f"**Status:** {'⭐ Primary' if is_primary else 'Secondary'}")
                            st.write(f"**Uploaded:** {profile.get('created_at', '')[:10]}")

                            if profile.get('analyzed_at'):
                                st.write(f"**Analyzed:** {profile['analyzed_at'][:10]}")

                            # Show style data if available
                            style_data = profile.get('style_data', {})
                            if style_data:
                                st.markdown("**Style Analysis:**")
                                col_a, col_b = st.columns(2)
                                with col_a:
                                    st.write(f"• Tone: {style_data.get('tone', 'N/A')}")
                                    st.write(f"• Voice: {style_data.get('voice', 'N/A')}")
                                with col_b:
                                    st.write(f"• Humor: {style_data.get('use_of_humor', 'N/A')}")
                                    st.write(f"• CTA Style: {style_data.get('call_to_action_style', 'N/A')}")

                            # Show text preview
                            text_preview = profile.get('newsletter_text', '')[:200] + "..."
                            st.markdown("**📝 Preview:**")
                            st.text(text_preview)

                        with col2:
                            # Set as primary button
                            if not is_primary:
                                if st.button("⭐ Set Primary", key=f"primary_{profile['id']}"):
                                    try:
                                        set_primary_profile(profile['id'])
                                        st.success("Set as primary!")
                                        st.rerun()
                                    except Exception as e:
                                        st.error(f"Failed: {str(e)}")

                            # Delete button
                            if st.button("🗑️ Delete", key=f"delete_style_{profile['id']}", type="secondary"):
                                try:
                                    delete_style_profile(profile['id'])
                                    st.success("Profile deleted!")
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Failed to delete: {str(e)}")

                # Pagination controls
                if pages > 1:
                    st.markdown("---")
                    col1, col2, col3 = st.columns([1, 2, 1])

                    with col1:
                        if st.session_state.style_page > 1:
                            if st.button("⬅️ Previous", key="prev_style"):
                                st.session_state.style_page -= 1
                                st.rerun()

                    with col2:
                        st.markdown(f"<div style='text-align: center'>Page {st.session_state.style_page} of {pages}</div>", unsafe_allow_html=True)

                    with col3:
                        if st.session_state.style_page < pages:
                            if st.button("Next ➡️", key="next_style"):
                                st.session_state.style_page += 1
                                st.rerun()

        except Exception as e:
            st.error(f"Failed to load profiles: {str(e)}")

    with tab3:
        st.markdown("### Upload a Past Newsletter")
        st.markdown("Paste the content of a newsletter you've written in the past. The AI will analyze your writing style.")

        with st.form("upload_newsletter_form"):
            newsletter_title = st.text_input(
                "Newsletter Title (Optional)",
                placeholder="e.g., Weekly Digest #42",
                help="A title to help you identify this newsletter"
            )

            newsletter_text = st.text_area(
                "Newsletter Content",
                placeholder="Paste your full newsletter content here...",
                height=300,
                help="Paste the complete text of your newsletter (minimum 100 characters)"
            )

            st.info("💡 **Tip:** Upload 3-5 past newsletters for the best style analysis!")

            submitted = st.form_submit_button("📤 Upload & Analyze", use_container_width=True, type="primary")

            if submitted:
                if not newsletter_text:
                    st.error("Newsletter content is required!")
                elif len(newsletter_text) < 100:
                    st.error("Newsletter content must be at least 100 characters long.")
                else:
                    try:
                        with st.spinner("Analyzing your writing style... This may take a moment."):
                            result = create_style_profile(
                                newsletter_text=newsletter_text,
                                newsletter_title=newsletter_title if newsletter_title else None
                            )
                            st.success("✅ Newsletter uploaded and analyzed successfully!")
                            st.balloons()

                            # Show quick analysis result
                            style_data = result.get('style_data', {})
                            if style_data:
                                st.markdown("#### Quick Analysis:")
                                col1, col2 = st.columns(2)
                                with col1:
                                    st.write(f"**Tone:** {style_data.get('tone', 'N/A')}")
                                    st.write(f"**Voice:** {style_data.get('voice', 'N/A')}")
                                with col2:
                                    st.write(f"**Sentence Length:** {style_data.get('avg_sentence_length', 0):.1f} words")
                                    st.write(f"**Paragraph Length:** {style_data.get('avg_paragraph_length', 0):.1f} words")

                            # Wait before rerunning
                            import time
                            time.sleep(2)
                            st.rerun()

                    except Exception as e:
                        st.error(f"Failed to upload newsletter: {str(e)}")


def show_drafts_page():
    """Display newsletter drafts page"""
    st.markdown("### 📧 Newsletter Drafts")
    st.markdown("Generate, review, and manage AI-powered newsletter drafts.")

    # Draft stats
    try:
        stats = get_draft_stats()
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            st.metric("Total Drafts", stats.get("total_drafts", 0))
        with col2:
            st.metric("Pending", stats.get("pending_drafts", 0), help="Awaiting review")
        with col3:
            st.metric("Reviewed", stats.get("reviewed_drafts", 0))
        with col4:
            st.metric("Sent", stats.get("sent_drafts", 0), help="Sent to recipients")
        with col5:
            avg_time = stats.get("avg_generation_time")
            time_str = f"{avg_time:.1f}s" if avg_time else "N/A"
            st.metric("Avg Gen Time", time_str, help="Average generation time")
    except Exception as e:
        st.error(f"Failed to load stats: {str(e)}")

    st.markdown("---")

    # Tabs for different views
    tab1, tab2 = st.tabs(["📋 My Drafts", "✨ Generate New"])

    with tab1:
        st.markdown("### Your Newsletter Drafts")

        # Filter options
        col1, col2 = st.columns([3, 1])
        with col1:
            filter_status = st.selectbox(
                "Filter by status",
                ["All", "Pending", "Reviewed", "Edited", "Sent", "Archived"],
                key="draft_filter_status"
            )
        with col2:
            # Generate button in header
            if st.button("✨ Generate New", use_container_width=True, type="primary"):
                st.session_state.show_generate_form = True
                st.rerun()

        # Convert filter
        status_param = None if filter_status == "All" else filter_status.lower()

        # Pagination state
        if "drafts_page" not in st.session_state:
            st.session_state.drafts_page = 1

        # Load and display drafts
        try:
            result = get_drafts(
                page=st.session_state.drafts_page,
                page_size=5,
                status=status_param
            )

            drafts = result.get("drafts", [])
            total = result.get("total", 0)
            pages = (total + 4) // 5  # Calculate total pages

            if total == 0:
                st.info("📭 No drafts found. Generate your first newsletter draft!")
            else:
                st.markdown(f"**Showing {len(drafts)} of {total} drafts (Page {st.session_state.drafts_page} of {pages})**")

                for draft in drafts:
                    status = draft.get('status', 'pending')
                    status_emoji = {
                        'pending': '⏳',
                        'reviewed': '✅',
                        'edited': '✏️',
                        'sent': '📧',
                        'archived': '📦'
                    }.get(status, '📄')

                    with st.expander(f"{status_emoji} {draft['subject']} ({status.upper()})"):
                        col1, col2 = st.columns([3, 1])

                        with col1:
                            st.markdown(f"### {draft['subject']}")
                            st.write(f"**Status:** {status.upper()}")
                            st.write(f"**Created:** {draft.get('created_at', '')[:10]}")

                            if draft.get('reviewed_at'):
                                st.write(f"**Reviewed:** {draft['reviewed_at'][:10]}")
                            if draft.get('sent_at'):
                                st.write(f"**Sent:** {draft['sent_at'][:10]}")

                            # Metadata
                            metadata = draft.get('metadata', {})
                            if metadata:
                                col_a, col_b, col_c = st.columns(3)
                                with col_a:
                                    gen_time = metadata.get('generation_time_seconds', 0)
                                    st.write(f"⏱️ **Gen Time:** {gen_time:.1f}s")
                                with col_b:
                                    content_count = metadata.get('content_items_used', 0)
                                    st.write(f"📝 **Content:** {content_count} items")
                                with col_c:
                                    trends = metadata.get('trends_used', [])
                                    st.write(f"📈 **Trends:** {len(trends)}")

                            # Show preview button
                            if st.button("👁️ Preview", key=f"preview_{draft['id']}"):
                                st.session_state.preview_draft_id = draft['id']
                                st.rerun()

                        with col2:
                            # Mark as reviewed
                            if status == 'pending':
                                if st.button("✅ Mark Reviewed", key=f"review_{draft['id']}"):
                                    try:
                                        update_draft(draft['id'], {"status": "reviewed"})
                                        st.success("Marked as reviewed!")
                                        st.rerun()
                                    except Exception as e:
                                        st.error(f"Failed: {str(e)}")

                            # Mark as sent
                            if status in ['pending', 'reviewed', 'edited']:
                                if st.button("📧 Mark Sent", key=f"sent_{draft['id']}"):
                                    try:
                                        update_draft(draft['id'], {"status": "sent"})
                                        st.success("Marked as sent!")
                                        st.rerun()
                                    except Exception as e:
                                        st.error(f"Failed: {str(e)}")

                            # Archive
                            if status not in ['archived', 'sent']:
                                if st.button("📦 Archive", key=f"archive_{draft['id']}", type="secondary"):
                                    try:
                                        update_draft(draft['id'], {"status": "archived"})
                                        st.success("Archived!")
                                        st.rerun()
                                    except Exception as e:
                                        st.error(f"Failed: {str(e)}")

                            # Delete
                            if st.button("🗑️ Delete", key=f"delete_draft_{draft['id']}", type="secondary"):
                                try:
                                    delete_draft(draft['id'])
                                    st.success("Draft deleted!")
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Failed: {str(e)}")

                # Show draft preview if requested
                if "preview_draft_id" in st.session_state:
                    st.markdown("---")
                    st.markdown("### 📄 Draft Preview")

                    try:
                        draft_detail = get_draft(st.session_state.preview_draft_id)

                        if draft_detail:
                            # Subject
                            st.markdown(f"**Subject:** {draft_detail['subject']}")
                            st.markdown("---")

                            # HTML content preview
                            st.markdown("#### Email Preview")
                            with st.container():
                                # Render HTML in an iframe-style display
                                st.components.v1.html(
                                    draft_detail.get('html_content', ''),
                                    height=600,
                                    scrolling=True
                                )

                            st.markdown("---")

                            # Plain text alternative
                            with st.expander("📝 View Plain Text Version"):
                                st.text(draft_detail.get('plain_content', ''))

                            st.markdown("---")

                            # Send Email Section
                            st.markdown("### 📧 Send Newsletter")

                            col1, col2 = st.columns([2, 1])

                            with col1:
                                with st.form(f"send_email_form_{draft_detail['id']}"):
                                    recipient_email = st.text_input(
                                        "Recipient Email",
                                        placeholder="recipient@example.com",
                                        help="Enter the recipient's email address"
                                    )

                                    is_test = st.checkbox(
                                        "Send as Test ([TEST] will be added to subject)",
                                        value=True,
                                        help="Test sends add a warning banner to the email"
                                    )

                                    col_a, col_b = st.columns(2)
                                    with col_a:
                                        from_name = st.text_input(
                                            "From Name (Optional)",
                                            placeholder="Your Name",
                                            help="Sender name (defaults to CreatorPulse)"
                                        )
                                    with col_b:
                                        from_email = st.text_input(
                                            "From Email (Optional)",
                                            placeholder="onboarding@resend.dev",
                                            help="Sender email (use Resend verified domain)"
                                        )

                                    send_button = st.form_submit_button(
                                        "📧 Send Email" if not is_test else "🧪 Send Test Email",
                                        use_container_width=True,
                                        type="primary"
                                    )

                                    if send_button:
                                        if not recipient_email:
                                            st.error("Please enter a recipient email address")
                                        else:
                                            try:
                                                with st.spinner("Sending email..."):
                                                    result = send_newsletter(
                                                        draft_id=draft_detail['id'],
                                                        recipient_email=recipient_email,
                                                        is_test=is_test,
                                                        from_email=from_email if from_email else None,
                                                        from_name=from_name if from_name else None
                                                    )

                                                    st.success(f"✅ Email sent successfully!")
                                                    st.info(f"Message ID: {result.get('message_id', 'N/A')}")

                                                    # Update draft status to sent if not test
                                                    if not is_test:
                                                        update_draft(draft_detail['id'], {"status": "sent"})

                                                    # Wait before rerunning
                                                    import time
                                                    time.sleep(2)
                                                    st.rerun()

                                            except Exception as e:
                                                st.error(f"Failed to send email: {str(e)}")
                                                st.error("Make sure your Resend API key is configured and the from email is verified.")

                            with col2:
                                st.info("💡 **Tips:**\n\n- Use test mode to preview emails\n- Verify sender email in Resend\n- Default: onboarding@resend.dev")

                            st.markdown("---")

                            # Close preview button
                            if st.button("❌ Close Preview"):
                                del st.session_state.preview_draft_id
                                st.rerun()

                    except Exception as e:
                        st.error(f"Failed to load draft: {str(e)}")
                        if st.button("❌ Close"):
                            del st.session_state.preview_draft_id
                            st.rerun()

                # Pagination controls
                if pages > 1:
                    st.markdown("---")
                    col1, col2, col3 = st.columns([1, 2, 1])

                    with col1:
                        if st.session_state.drafts_page > 1:
                            if st.button("⬅️ Previous", key="prev_drafts"):
                                st.session_state.drafts_page -= 1
                                st.rerun()

                    with col2:
                        st.markdown(f"<div style='text-align: center'>Page {st.session_state.drafts_page} of {pages}</div>", unsafe_allow_html=True)

                    with col3:
                        if st.session_state.drafts_page < pages:
                            if st.button("Next ➡️", key="next_drafts"):
                                st.session_state.drafts_page += 1
                                st.rerun()

        except Exception as e:
            st.error(f"Failed to load drafts: {str(e)}")

    with tab2:
        st.markdown("### ✨ Generate New Newsletter Draft")
        st.markdown("Let AI create a personalized newsletter draft based on your trends and writing style.")

        # Check prerequisites
        try:
            # Check for trends
            trend_stats = get_trend_stats()
            has_trends = trend_stats.get("total_trends", 0) > 0

            # Check for style profiles
            style_stats = get_style_stats()
            has_style = style_stats.get("total_profiles", 0) > 0

            # Show status
            col1, col2 = st.columns(2)
            with col1:
                if has_trends:
                    st.success(f"✅ {trend_stats['total_trends']} trends detected")
                else:
                    st.warning("⚠️ No trends detected yet")

            with col2:
                if has_style:
                    st.success(f"✅ {style_stats['total_profiles']} style profile(s)")
                else:
                    st.info("💡 No style profiles (optional)")

            st.markdown("---")

            # Generation form
            with st.form("generate_draft_form"):
                st.markdown("#### Draft Options")

                col1, col2 = st.columns(2)

                with col1:
                    include_trends = st.checkbox(
                        "Include 'Trends to Watch' section",
                        value=True,
                        help="Add a dedicated section highlighting trending topics"
                    )

                with col2:
                    max_trends = st.slider(
                        "Maximum trends to include",
                        min_value=1,
                        max_value=5,
                        value=3,
                        help="How many top trends to focus on"
                    )

                force_regenerate = st.checkbox(
                    "Force regenerate (even if today's draft exists)",
                    value=False,
                    help="Generate a new draft even if one was created today"
                )

                st.markdown("---")

                # Prerequisites warning
                if not has_trends:
                    st.warning("⚠️ **No trends detected!** Generate drafts work best with detected trends. Visit the Trends page to detect trends first.")

                if not has_style:
                    st.info("💡 **No style profiles found.** Upload past newsletters in the Writing Style page for better personalization.")

                submitted = st.form_submit_button(
                    "✨ Generate Draft",
                    use_container_width=True,
                    type="primary",
                    disabled=not has_trends
                )

                if submitted:
                    try:
                        with st.spinner("🤖 AI is crafting your newsletter... This may take 10-30 seconds."):
                            result = generate_draft(
                                force_regenerate=force_regenerate,
                                include_trends=include_trends,
                                max_trends=max_trends
                            )

                            st.success("✅ Newsletter draft generated successfully!")
                            st.balloons()

                            # Show quick preview
                            st.markdown("---")
                            st.markdown("### Quick Preview")
                            st.markdown(f"**Subject:** {result.get('subject', '')}")

                            metadata = result.get('metadata', {})
                            col1, col2 = st.columns(2)
                            with col1:
                                gen_time = metadata.get('generation_time_seconds', 0)
                                st.write(f"⏱️ **Generation Time:** {gen_time:.1f}s")
                            with col2:
                                trends_used = metadata.get('trends_used', [])
                                st.write(f"📈 **Trends Used:** {', '.join(trends_used[:3])}")

                            st.info("👉 View the full draft in the 'My Drafts' tab!")

                            # Wait before rerunning
                            import time
                            time.sleep(2)
                            st.rerun()

                    except Exception as e:
                        st.error(f"Failed to generate draft: {str(e)}")
                        st.error("Make sure you have trends detected and content aggregated.")

        except Exception as e:
            st.error(f"Error checking prerequisites: {str(e)}")


# Main app logic
if not is_authenticated():
    if "show_signup" not in st.session_state:
        st.session_state.show_signup = False

    if st.session_state.show_signup:
        show_signup_page()
    else:
        show_login_page()
else:
    show_dashboard()
