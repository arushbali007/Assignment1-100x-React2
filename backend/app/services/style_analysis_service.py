"""Style Analysis Service using Groq LLM"""
import json
import re
from typing import Optional
from groq import Groq
from app.core.config import settings
from app.models.style_profile import StyleAnalysis


class StyleAnalysisService:
    """Service for analyzing writing style using Groq LLM"""

    def __init__(self):
        self.client = Groq(api_key=settings.GROQ_API_KEY)
        self.model = "llama-3.3-70b-versatile"  # High-quality model for analysis

    async def analyze_writing_style(self, newsletter_text: str) -> StyleAnalysis:
        """
        Analyze writing style from newsletter text using Groq LLM

        Args:
            newsletter_text: The text content of the newsletter

        Returns:
            StyleAnalysis object with detailed style characteristics
        """

        # Calculate basic statistics
        sentences = re.split(r'[.!?]+', newsletter_text)
        sentences = [s.strip() for s in sentences if s.strip()]
        avg_sentence_length = sum(len(s.split()) for s in sentences) / len(sentences) if sentences else 0

        paragraphs = [p.strip() for p in newsletter_text.split('\n\n') if p.strip()]
        avg_paragraph_length = sum(len(p.split()) for p in paragraphs) / len(paragraphs) if paragraphs else 0

        # Extract key phrases (simple approach - can be enhanced)
        words = newsletter_text.lower().split()
        phrases = []
        for i in range(len(words) - 2):
            phrase = ' '.join(words[i:i+3])
            if len(phrase) > 10:  # Avoid very short phrases
                phrases.append(phrase)
        # Get most common phrases (simplified)
        key_phrases = list(set(phrases))[:10]

        # Use Groq LLM to analyze style
        prompt = f"""Analyze the writing style of this newsletter and provide a detailed style profile.

Newsletter Text:
{newsletter_text[:3000]}  # Limit to avoid token limits

Please analyze and respond in JSON format with these fields:
- tone: Overall tone (e.g., professional, casual, conversational, witty, authoritative)
- voice: Voice characteristics (e.g., first-person, we-voice, expert, friendly mentor)
- sentence_structure: Typical sentence structure patterns (e.g., short and punchy, varied lengths, complex clauses)
- vocabulary_level: Vocabulary complexity (e.g., simple, moderate, advanced, technical)
- opening_style: How the newsletter opens (e.g., personal anecdote, question, bold statement, news hook)
- closing_style: How the newsletter closes (e.g., call-to-action, summary, reflection, open question)
- formatting_preferences: Preferred formatting patterns (e.g., bullet points, numbered lists, bold headers, emojis)
- use_of_humor: Level and type of humor (e.g., witty, sarcastic, punny, none, subtle)
- call_to_action_style: How CTAs are presented (e.g., direct, soft, embedded, strong)
- personal_touches: Personal elements or signatures (e.g., personal stories, opinions, experiences, sign-off style)

Respond ONLY with valid JSON. No markdown, no explanations, just the JSON object."""

        try:
            # Call Groq API
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert writing style analyst. Analyze text and return detailed style characteristics in JSON format."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                model=self.model,
                temperature=0.3,  # Lower temperature for more consistent analysis
                max_tokens=1000,
                response_format={"type": "json_object"}
            )

            # Parse response
            response_text = chat_completion.choices[0].message.content
            style_data = json.loads(response_text)

            # Create StyleAnalysis object
            return StyleAnalysis(
                tone=style_data.get("tone", "professional"),
                voice=style_data.get("voice", "first-person"),
                sentence_structure=style_data.get("sentence_structure", "varied"),
                vocabulary_level=style_data.get("vocabulary_level", "moderate"),
                opening_style=style_data.get("opening_style", "direct"),
                closing_style=style_data.get("closing_style", "call-to-action"),
                formatting_preferences=style_data.get("formatting_preferences", "standard"),
                use_of_humor=style_data.get("use_of_humor", "minimal"),
                call_to_action_style=style_data.get("call_to_action_style", "direct"),
                personal_touches=style_data.get("personal_touches", "minimal"),
                avg_sentence_length=round(avg_sentence_length, 1),
                avg_paragraph_length=round(avg_paragraph_length, 1),
                key_phrases=key_phrases[:5]  # Top 5 phrases
            )

        except Exception as e:
            # Fallback to basic analysis if LLM fails
            print(f"LLM analysis failed: {e}. Using basic analysis.")
            return StyleAnalysis(
                tone="professional",
                voice="informative",
                sentence_structure="varied lengths",
                vocabulary_level="moderate",
                opening_style="standard",
                closing_style="standard",
                formatting_preferences="standard paragraphs",
                use_of_humor="minimal",
                call_to_action_style="standard",
                personal_touches="minimal",
                avg_sentence_length=round(avg_sentence_length, 1),
                avg_paragraph_length=round(avg_paragraph_length, 1),
                key_phrases=key_phrases[:5]
            )

    async def aggregate_style_profiles(self, style_profiles: list[dict]) -> dict:
        """
        Aggregate multiple style profiles into a single comprehensive profile

        Args:
            style_profiles: List of style_data dictionaries from multiple newsletters

        Returns:
            Aggregated style dictionary
        """
        if not style_profiles:
            return {}

        # Extract common characteristics
        tones = [p.get("tone", "") for p in style_profiles]
        voices = [p.get("voice", "") for p in style_profiles]

        # Most common tone and voice
        most_common_tone = max(set(tones), key=tones.count) if tones else "professional"
        most_common_voice = max(set(voices), key=voices.count) if voices else "informative"

        # Average sentence and paragraph lengths
        avg_sentence_lengths = [p.get("avg_sentence_length", 0) for p in style_profiles if p.get("avg_sentence_length")]
        avg_paragraph_lengths = [p.get("avg_paragraph_length", 0) for p in style_profiles if p.get("avg_paragraph_length")]

        avg_sent = sum(avg_sentence_lengths) / len(avg_sentence_lengths) if avg_sentence_lengths else 15.0
        avg_para = sum(avg_paragraph_lengths) / len(avg_paragraph_lengths) if avg_paragraph_lengths else 50.0

        # Collect all key phrases
        all_phrases = []
        for p in style_profiles:
            all_phrases.extend(p.get("key_phrases", []))
        common_phrases = list(set(all_phrases))[:10]

        # Key characteristics
        characteristics = [
            f"{most_common_tone} tone",
            f"{most_common_voice} voice"
        ]

        # Confidence based on sample count
        confidence = min(len(style_profiles) / 5.0, 1.0)  # Max confidence at 5 samples

        return {
            "tone": most_common_tone,
            "voice": most_common_voice,
            "avg_sentence_length": round(avg_sent, 1),
            "avg_paragraph_length": round(avg_para, 1),
            "key_characteristics": characteristics,
            "common_phrases": common_phrases,
            "style_confidence": round(confidence, 2),
            "sample_count": len(style_profiles)
        }
