import json
import time
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from groq import Groq

from app.core.config import settings
from app.models.draft import DraftContent, NewsletterBlock, DraftMetadata
from app.models.trend import TrendResponse
from app.models.content import ContentResponse


class NewsletterGenerationService:
    """Generate personalized newsletter drafts using Groq LLM"""

    def __init__(self):
        self.client = Groq(api_key=settings.GROQ_API_KEY)
        self.model = "llama-3.3-70b-versatile"

    async def generate_newsletter(
        self,
        trends: List[TrendResponse],
        recent_content: List[ContentResponse],
        style_summary: Optional[dict] = None,
        user_name: Optional[str] = None,
        include_trends_section: bool = True,
        max_trends: int = 3
    ) -> tuple[DraftContent, DraftMetadata]:
        """
        Generate newsletter draft from trends and content

        Args:
            trends: List of trending topics
            recent_content: Recent aggregated content
            style_summary: User's writing style profile
            user_name: User's name for personalization
            include_trends_section: Whether to include "Trends to Watch" section
            max_trends: Maximum number of trends to include

        Returns:
            Tuple of (DraftContent, DraftMetadata)
        """
        start_time = time.time()

        # Limit trends
        top_trends = trends[:max_trends] if trends else []

        # Build context for LLM
        context = self._build_generation_context(
            trends=top_trends,
            recent_content=recent_content,
            style_summary=style_summary,
            user_name=user_name
        )

        # Generate newsletter using LLM
        draft_data = await self._generate_with_llm(
            context=context,
            include_trends_section=include_trends_section
        )

        # Parse and structure the response
        draft_content = self._parse_llm_response(draft_data, top_trends, recent_content)

        # Build metadata
        generation_time = time.time() - start_time
        metadata = DraftMetadata(
            generation_time_seconds=round(generation_time, 2),
            trends_used=[t.keyword for t in top_trends],
            content_items_used=len(recent_content),
            style_profile_id=None,  # Will be set by draft service
            model_name=self.model
        )

        return draft_content, metadata

    def _build_generation_context(
        self,
        trends: List[TrendResponse],
        recent_content: List[ContentResponse],
        style_summary: Optional[dict],
        user_name: Optional[str]
    ) -> Dict[str, Any]:
        """Build context dictionary for LLM prompt"""

        # Format trends
        trends_data = []
        for trend in trends:
            trends_data.append({
                "keyword": trend.keyword,
                "score": round(trend.score, 1),
                "velocity": trend.velocity,
                "mentions": trend.content_mentions
            })

        # Format recent content (limit to 15 most recent)
        content_data = []
        for content in recent_content[:15]:
            content_data.append({
                "type": content.content_type,
                "title": content.title,
                "body": content.body[:300] if content.body else "",  # Truncate for token limit
                "author": content.author,
                "url": content.url
            })

        # Format style profile (style_summary is already a dict)
        style_data = None
        if style_summary:
            style_data = {
                "tone": style_summary.get("tone"),
                "voice": style_summary.get("voice"),
                "sentence_structure": style_summary.get("sentence_structure"),
                "vocabulary_level": style_summary.get("vocabulary_level"),
                "opening_style": style_summary.get("opening_style"),
                "closing_style": style_summary.get("closing_style"),
                "formatting": style_summary.get("formatting"),
                "humor_usage": style_summary.get("humor_usage"),
                "cta_style": style_summary.get("cta_style"),
                "personal_touches": style_summary.get("personal_touches")
            }

        return {
            "today": date.today().strftime("%B %d, %Y"),
            "user_name": user_name or "Creator",
            "trends": trends_data,
            "content": content_data,
            "style": style_data
        }

    async def _generate_with_llm(
        self,
        context: Dict[str, Any],
        include_trends_section: bool
    ) -> Dict[str, Any]:
        """Call Groq LLM to generate newsletter content"""

        # Build comprehensive prompt
        prompt = self._build_generation_prompt(context, include_trends_section)

        try:
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert newsletter writer who creates engaging, personalized content. "
                                   "You synthesize trends and content into compelling narratives that match the writer's unique style. "
                                   "Always return valid JSON in the exact format requested."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=4000,
                response_format={"type": "json_object"}
            )

            response_text = completion.choices[0].message.content
            return json.loads(response_text)

        except Exception as e:
            print(f"LLM generation error: {e}")
            # Fallback to template-based generation
            return self._generate_fallback(context, include_trends_section)

    def _build_generation_prompt(
        self,
        context: Dict[str, Any],
        include_trends_section: bool
    ) -> str:
        """Build the LLM prompt for newsletter generation"""

        style_info = ""
        if context.get("style"):
            style = context["style"]
            style_info = f"""
WRITING STYLE PROFILE:
- Tone: {style['tone']}
- Voice: {style['voice']}
- Sentence Structure: {style['sentence_structure']}
- Vocabulary Level: {style['vocabulary_level']}
- Opening Style: {style['opening_style']}
- Closing Style: {style['closing_style']}
- Formatting: {style['formatting']}
- Humor Usage: {style['humor_usage']}
- CTA Style: {style['cta_style']}
- Personal Touches: {style['personal_touches']}

YOU MUST match this writing style exactly. Adopt the tone, voice, and formatting preferences.
"""

        trends_info = ""
        if context.get("trends"):
            trends_info = "TOP TRENDING TOPICS:\n"
            for i, trend in enumerate(context["trends"], 1):
                trends_info += f"{i}. {trend['keyword']} (Score: {trend['score']}, Velocity: {trend['velocity']}, Mentions: {trend['mentions']})\n"

        content_info = ""
        if context.get("content"):
            content_info = "RECENT CONTENT TO SYNTHESIZE:\n"
            for i, item in enumerate(context["content"][:10], 1):
                content_info += f"{i}. [{item['type']}] {item['title']}\n"
                if item['body']:
                    content_info += f"   {item['body'][:150]}...\n"

        trends_section_instruction = ""
        if include_trends_section:
            trends_section_instruction = """
- "trends_section": {
    "title": "Trends to Watch",
    "content": "Brief overview of emerging trends (2-3 sentences per trend)",
    "source_ids": [],
    "trend_id": null
  }
"""

        prompt = f"""Generate a personalized newsletter draft for {context['user_name']} based on the following information:

DATE: {context['today']}

{style_info}

{trends_info}

{content_info}

TASK:
Create an engaging newsletter that:
1. Synthesizes the trending topics and content into a cohesive narrative
2. Matches the specified writing style exactly (tone, voice, structure)
3. Provides valuable insights and actionable takeaways
4. Maintains reader engagement throughout
5. Includes a compelling subject line

Return a JSON object with this EXACT structure:
{{
  "subject": "Compelling subject line (50-70 characters)",
  "greeting": "Opening greeting matching the style",
  "intro": "Introduction paragraph (2-4 sentences) that hooks the reader",
  "blocks": [
    {{
      "title": "Section title",
      "content": "Section content (3-5 paragraphs)",
      "source_ids": [],
      "trend_id": null
    }}
  ],{trends_section_instruction}
  "closing": "Closing paragraph (2-3 sentences)",
  "cta": "Call to action (optional, 1 sentence)",
  "signature": "Sign-off matching the style"
}}

IMPORTANT:
- Create 2-3 main content blocks focusing on the most interesting trends/content
- Each block should be 3-5 paragraphs
- Match the writing style profile exactly
- Be engaging, insightful, and valuable
- Return ONLY valid JSON, no other text
"""

        return prompt

    def _parse_llm_response(
        self,
        response_data: Dict[str, Any],
        trends: List[TrendResponse],
        content: List[ContentResponse]
    ) -> DraftContent:
        """Parse LLM response into DraftContent model"""

        # Parse main blocks
        blocks = []
        for block_data in response_data.get("blocks", []):
            # Convert source_ids to strings (LLM may return integers)
            source_ids = block_data.get("source_ids", [])
            source_ids_str = [str(sid) for sid in source_ids] if source_ids else []

            # Convert trend_id to string if present (LLM may return integer)
            trend_id = block_data.get("trend_id")
            trend_id_str = str(trend_id) if trend_id is not None else None

            block = NewsletterBlock(
                title=block_data.get("title", "Untitled"),
                content=block_data.get("content", ""),
                source_ids=source_ids_str,
                trend_id=trend_id_str
            )
            blocks.append(block)

        # Parse trends section
        trends_section = None
        if response_data.get("trends_section"):
            ts = response_data["trends_section"]

            # Convert source_ids to strings
            ts_source_ids = ts.get("source_ids", [])
            ts_source_ids_str = [str(sid) for sid in ts_source_ids] if ts_source_ids else []

            # Convert trend_id to string if present
            ts_trend_id = ts.get("trend_id")
            ts_trend_id_str = str(ts_trend_id) if ts_trend_id is not None else None

            trends_section = NewsletterBlock(
                title=ts.get("title", "Trends to Watch"),
                content=ts.get("content", ""),
                source_ids=ts_source_ids_str,
                trend_id=ts_trend_id_str
            )

        return DraftContent(
            subject=response_data.get("subject", f"Your Newsletter - {date.today().strftime('%B %d')}"),
            greeting=response_data.get("greeting", "Hello!"),
            intro=response_data.get("intro", ""),
            blocks=blocks,
            trends_section=trends_section,
            closing=response_data.get("closing", ""),
            cta=response_data.get("cta"),
            signature=response_data.get("signature", "Best regards")
        )

    def _generate_fallback(
        self,
        context: Dict[str, Any],
        include_trends_section: bool
    ) -> Dict[str, Any]:
        """Fallback template-based generation if LLM fails"""

        trends = context.get("trends", [])
        content_items = context.get("content", [])

        # Simple template
        subject = f"Your Weekly Update - {context['today']}"

        greeting = f"Hi {context['user_name']},"

        intro = "Here's what's trending in your space this week. I've pulled together the most interesting insights from your sources."

        # Create blocks from trends
        blocks = []
        for i, trend in enumerate(trends[:2], 1):
            blocks.append({
                "title": f"Trending: {trend['keyword']}",
                "content": f"This topic is gaining momentum with a score of {trend['score']} and {trend['mentions']} mentions across your sources. It's definitely worth paying attention to.",
                "source_ids": [],
                "trend_id": None
            })

        # Add content block
        if content_items:
            content_block = "Here are some highlights from your recent content:\n\n"
            for item in content_items[:3]:
                content_block += f"• {item['title']}\n"

            blocks.append({
                "title": "Recent Highlights",
                "content": content_block,
                "source_ids": [],
                "trend_id": None
            })

        trends_section = None
        if include_trends_section and trends:
            ts_content = "Keep an eye on these emerging topics:\n\n"
            for trend in trends:
                ts_content += f"• {trend['keyword']} (Score: {trend['score']})\n"

            trends_section = {
                "title": "Trends to Watch",
                "content": ts_content,
                "source_ids": [],
                "trend_id": None
            }

        closing = "That's all for now. Stay curious and keep creating!"

        signature = f"Best,\n{context['user_name']}"

        return {
            "subject": subject,
            "greeting": greeting,
            "intro": intro,
            "blocks": blocks,
            "trends_section": trends_section,
            "closing": closing,
            "cta": "Reply and let me know what you think!",
            "signature": signature
        }

    def convert_to_html(self, draft: DraftContent) -> str:
        """Convert draft content to HTML email format"""

        html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{draft.subject}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            background-color: #ffffff;
            padding: 40px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .greeting {{
            font-size: 18px;
            margin-bottom: 20px;
        }}
        .intro {{
            font-size: 16px;
            margin-bottom: 30px;
            color: #555;
        }}
        .block {{
            margin-bottom: 35px;
        }}
        .block-title {{
            font-size: 22px;
            font-weight: 600;
            color: #1a1a1a;
            margin-bottom: 15px;
        }}
        .block-content {{
            font-size: 16px;
            line-height: 1.7;
            color: #444;
            white-space: pre-wrap;
        }}
        .trends-section {{
            background-color: #f8f9fa;
            padding: 25px;
            border-radius: 6px;
            margin-bottom: 35px;
            border-left: 4px solid #007bff;
        }}
        .closing {{
            font-size: 16px;
            margin-top: 35px;
            margin-bottom: 20px;
            color: #555;
        }}
        .cta {{
            background-color: #007bff;
            color: #ffffff;
            padding: 12px 24px;
            text-decoration: none;
            border-radius: 5px;
            display: inline-block;
            margin: 20px 0;
            font-weight: 500;
        }}
        .signature {{
            font-size: 16px;
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #eee;
            white-space: pre-wrap;
        }}
        .footer {{
            text-align: center;
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #eee;
            font-size: 14px;
            color: #888;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="greeting">{draft.greeting}</div>
        <div class="intro">{draft.intro}</div>

"""

        # Add main content blocks
        for block in draft.blocks:
            html += f"""
        <div class="block">
            <div class="block-title">{block.title}</div>
            <div class="block-content">{block.content}</div>
        </div>
"""

        # Add trends section if exists
        if draft.trends_section:
            html += f"""
        <div class="trends-section">
            <div class="block-title">{draft.trends_section.title}</div>
            <div class="block-content">{draft.trends_section.content}</div>
        </div>
"""

        # Add closing
        html += f"""
        <div class="closing">{draft.closing}</div>
"""

        # Add CTA if exists
        if draft.cta:
            html += f"""
        <a href="#" class="cta">{draft.cta}</a>
"""

        # Add signature
        html += f"""
        <div class="signature">{draft.signature}</div>

        <div class="footer">
            Generated with CreatorPulse
        </div>
    </div>
</body>
</html>"""

        return html

    def convert_to_plain_text(self, draft: DraftContent) -> str:
        """Convert draft content to plain text format"""

        text = f"{draft.greeting}\n\n"
        text += f"{draft.intro}\n\n"

        # Add main blocks
        for block in draft.blocks:
            text += f"{'=' * 60}\n"
            text += f"{block.title}\n"
            text += f"{'=' * 60}\n\n"
            text += f"{block.content}\n\n"

        # Add trends section
        if draft.trends_section:
            text += f"{'=' * 60}\n"
            text += f"{draft.trends_section.title}\n"
            text += f"{'=' * 60}\n\n"
            text += f"{draft.trends_section.content}\n\n"

        # Add closing
        text += f"{draft.closing}\n\n"

        # Add CTA
        if draft.cta:
            text += f"→ {draft.cta}\n\n"

        # Add signature
        text += f"{draft.signature}\n"
        text += f"\n{'─' * 60}\n"
        text += "Generated with CreatorPulse\n"

        return text
