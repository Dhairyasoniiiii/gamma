"""
AI Service - OpenAI GPT-4 & DALL-E 3 Integration
Handles all AI generation: presentations, text, images

Can use FREE providers (Gemini, Groq, Perplexity) or OpenAI
"""

from openai import AsyncOpenAI
from typing import Dict, List, Optional
import json
import asyncio
from functools import lru_cache
import hashlib
from backend.config import settings
from backend.db.base import get_redis


class AIService:
    """
    Complete AI service for Gamma Clone
    - Full presentation generation from prompts
    - Text rewriting and improvement
    - Translation (60+ languages)
    - Image generation (DALL-E 3)
    - Smart diagram creation
    - Response caching for performance
    - Timeout handling
    
    Can use FREE providers if USE_FREE_PROVIDERS=True in config
    """
    
    # Cache timeouts (in seconds)
    CACHE_TTL_PRESENTATION = 3600  # 1 hour
    CACHE_TTL_TEXT = 1800  # 30 minutes
    CACHE_TTL_IMAGE = 7200  # 2 hours
    
    def __init__(self, api_key: Optional[str] = None):
        # Check if we should use free providers
        if settings.USE_FREE_PROVIDERS:
            print("[FREE] Using FREE AI providers (Gemini, Groq, Perplexity)")
            from backend.services.free_ai_service import FreeAIService
            self.free_service = FreeAIService()
            self.use_free = True
        else:
            self.api_key = api_key or settings.OPENAI_API_KEY
            if not self.api_key:
                raise ValueError("OpenAI API key is required when USE_FREE_PROVIDERS=False")
            
            self.client = AsyncOpenAI(
                api_key=self.api_key,
                timeout=60.0,  # 60 second timeout
                max_retries=2  # Retry failed requests
            )
            self.text_model = settings.DEFAULT_TEXT_MODEL
            self.image_model = settings.DEFAULT_IMAGE_MODEL
            self.use_free = False
            print("[PAID] Using OpenAI (paid)")
        
        # Get Redis client for caching
        self.redis_client = get_redis()
    
    async def generate_presentation(
        self,
        prompt: str,
        num_cards: int = 10,
        style: str = "professional"
    ) -> Dict:
        """
        Generate complete presentation from prompt with caching
        
        Args:
            prompt: User's description of presentation
            num_cards: Number of cards to generate (10-75 based on plan)
            style: Presentation style (professional, creative, minimal, etc.)
        
        Returns:
            {
                'title': str,
                'cards': [...],
                'theme': {...},
                'metadata': {...}
            }
        """
        
        # Check cache first
        cache_key = self._get_cache_key("presentation", prompt, num_cards, style)
        if self.redis_client:
            try:
                cached = self.redis_client.get(cache_key)
                if cached:
                    return json.loads(cached)
            except Exception:
                pass  # Cache miss or error, continue
        
        # Use free providers if enabled
        if self.use_free:
            result = await self.free_service.generate_presentation(
                prompt=prompt,
                num_cards=num_cards,
                style=style
            )
        else:
            # OpenAI generation with timeout
            result = await self._generate_with_openai(prompt, num_cards, style)
        
        # Cache the result
        if self.redis_client and result:
            try:
                self.redis_client.setex(
                    cache_key,
                    self.CACHE_TTL_PRESENTATION,
                    json.dumps(result)
                )
            except Exception:
                pass  # Cache write failed, not critical
        
        return result
    
    def _get_cache_key(self, prefix: str, *args) -> str:
        """Generate cache key from arguments"""
        key_data = ":".join(str(arg) for arg in args)
        key_hash = hashlib.md5(key_data.encode()).hexdigest()
        return f"ai_service:{prefix}:{key_hash}"
    
    async def _generate_with_openai(
        self,
        prompt: str,
        num_cards: int,
        style: str
    ) -> Dict:
        """Generate presentation using OpenAI with timeout handling"""
        system_prompt = f"""You are an expert presentation designer. Create a {style} presentation with {num_cards} cards.

CARD TYPES AVAILABLE:
- title: Opening title card with title and subtitle
- content: Text content with bullet points
- image: Full-width image card
- split: Two-column layout (text + image)
- quote: Highlighted quote
- stats: Key metrics/statistics (2-4 numbers)
- timeline: Sequential events with dates
- comparison: Side-by-side comparison
- cta: Call-to-action with button
- chart: Data visualization (bar, line, pie)

RULES:
1. First card MUST be "title" type
2. Vary card types for visual interest
3. Include 2-3 image cards (we'll generate these)
4. Use stats/charts for data
5. End with CTA or summary
6. Keep text concise (3-5 bullets max per card)
7. Use professional, engaging language

OUTPUT FORMAT (JSON):
{{
    "title": "Presentation Title",
    "cards": [
        {{
            "id": "card_1",
            "type": "title",
            "title": "Main Title",
            "subtitle": "Subtitle text"
        }},
        {{
            "id": "card_2",
            "type": "content",
            "title": "Section Title",
            "content": {{
                "bullets": ["Point 1", "Point 2", "Point 3"]
            }}
        }},
        {{
            "id": "card_3",
            "type": "stats",
            "title": "Key Metrics",
            "content": {{
                "stats": [
                    {{"label": "Users", "value": "10M+", "trend": "up"}},
                    {{"label": "Growth", "value": "250%", "trend": "up"}}
                ]
            }}
        }},
        {{
            "id": "card_4",
            "type": "image",
            "title": "Visual Section",
            "content": {{
                "image_prompt": "Describe the image to generate",
                "alt": "Image description"
            }}
        }}
    ]
}}"""
        
        try:
            response = await self.client.chat.completions.create(
                model=self.text_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Create a presentation about: {prompt}"}
                ],
                temperature=0.7,
                max_tokens=4000,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            
            # Generate images for image cards
            for card in result['cards']:
                if card['type'] == 'image' and 'image_prompt' in card.get('content', {}):
                    image_url = await self._generate_image(card['content']['image_prompt'])
                    card['content']['image_url'] = image_url
            
            # Add theme suggestion
            result['theme'] = await self._suggest_theme(prompt, style)
            
            # Add metadata
            result['metadata'] = {
                'prompt': prompt,
                'style': style,
                'model': self.text_model,
                'total_cards': len(result['cards'])
            }
            
            return result
            
        except Exception as e:
            raise Exception(f"AI generation failed: {str(e)}")
    
    async def rewrite_text(
        self,
        text: str,
        instruction: str = "improve"
    ) -> str:
        """
        Rewrite/improve text content
        
        Instructions:
        - "improve": Make more professional
        - "simplify": Make easier to understand
        - "expand": Add more detail
        - "shorten": Make more concise
        - "casual": More casual tone
        - "formal": More formal tone
        """
        
        # Use free providers if enabled
        if self.use_free:
            return await self.free_service.rewrite_text(text, instruction)
        
        # Otherwise use OpenAI
        instruction_prompts = {
            "improve": "Make this text more professional and engaging while keeping the same meaning:",
            "simplify": "Simplify this text to make it easier to understand:",
            "expand": "Expand this text with more detail and examples:",
            "shorten": "Make this text more concise while keeping key points:",
            "casual": "Rewrite this in a more casual, conversational tone:",
            "formal": "Rewrite this in a more formal, professional tone:"
        }
        
        prompt = instruction_prompts.get(instruction, instruction)
        
        try:
            response = await self.client.chat.completions.create(
                model=self.text_model,
                messages=[
                    {"role": "system", "content": "You are an expert copywriter. Rewrite the text according to instructions."},
                    {"role": "user", "content": f"{prompt}\n\n{text}"}
                ],
                temperature=0.7,
                max_tokens=1000
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            raise Exception(f"Text rewrite failed: {str(e)}")
    
    async def translate_text(
        self,
        text: str,
        target_language: str
    ) -> str:
        """
        Translate text to target language
        Supports 60+ languages
        """
        
        # Use free providers if enabled
        if self.use_free:
            return await self.free_service.translate_text(text, target_language)
        
        # Otherwise use OpenAI
        try:
            response = await self.client.chat.completions.create(
                model=self.text_model,
                messages=[
                    {"role": "system", "content": f"Translate the following text to {target_language}. Maintain the tone and style."},
                    {"role": "user", "content": text}
                ],
                temperature=0.3,
                max_tokens=2000
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            raise Exception(f"Translation failed: {str(e)}")
    
    async def _generate_image(
        self,
        prompt: str,
        size: str = "1024x1024",
        quality: str = "standard"
    ) -> str:
        """
        Generate image using DALL-E 3
        
        Returns: URL to generated image
        """
        
        try:
            response = await self.client.images.generate(
                model=self.image_model,
                prompt=f"{prompt}. Professional, high-quality, modern design.",
                size=size,
                quality=quality,
                n=1
            )
            
            return response.data[0].url
            
        except Exception as e:
            raise Exception(f"Image generation failed: {str(e)}")
    
    async def _suggest_theme(
        self,
        prompt: str,
        style: str
    ) -> Dict:
        """
        Suggest appropriate theme based on content
        """
        
        # Default themes by style
        theme_suggestions = {
            'professional': {
                'colors': {
                    'primary': '#1E3A8A',
                    'secondary': '#3B82F6',
                    'accent': '#60A5FA',
                    'background': '#FFFFFF',
                    'text': '#1F2937'
                },
                'fonts': {
                    'heading': 'Inter',
                    'body': 'Inter',
                    'headingWeight': '700'
                }
            },
            'creative': {
                'colors': {
                    'primary': '#EC4899',
                    'secondary': '#F59E0B',
                    'accent': '#8B5CF6',
                    'background': '#FFFFFF',
                    'text': '#1F2937'
                },
                'fonts': {
                    'heading': 'Poppins',
                    'body': 'Inter',
                    'headingWeight': '700'
                }
            },
            'minimal': {
                'colors': {
                    'primary': '#000000',
                    'secondary': '#6B7280',
                    'accent': '#3B82F6',
                    'background': '#FFFFFF',
                    'text': '#111827'
                },
                'fonts': {
                    'heading': 'Inter',
                    'body': 'Inter',
                    'headingWeight': '600'
                }
            }
        }
        
        return theme_suggestions.get(style, theme_suggestions['professional'])
    
    async def generate_chart_data(
        self,
        description: str
    ) -> Dict:
        """
        Generate sample chart data based on description
        """
        
        system_prompt = """Generate realistic chart data in JSON format.
        
OUTPUT FORMAT:
{
    "type": "bar|line|pie|scatter",
    "data": {
        "labels": [...],
        "datasets": [
            {
                "label": "Dataset 1",
                "data": [...]
            }
        ]
    },
    "options": {
        "title": "Chart Title"
    }
}"""
        
        try:
            response = await self.client.chat.completions.create(
                model=self.text_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Generate chart data for: {description}"}
                ],
                temperature=0.7,
                max_tokens=1000,
                response_format={"type": "json_object"}
            )
            
            return json.loads(response.choices[0].message.content)
            
        except Exception as e:
            raise Exception(f"Chart generation failed: {str(e)}")
    
    async def extract_key_points(
        self,
        text: str,
        num_points: int = 5
    ) -> List[str]:
        """
        Extract key points from long text
        Useful for converting documents to presentations
        """
        
        try:
            response = await self.client.chat.completions.create(
                model=self.text_model,
                messages=[
                    {"role": "system", "content": f"Extract the {num_points} most important key points from this text. Return as JSON array."},
                    {"role": "user", "content": text}
                ],
                temperature=0.5,
                max_tokens=500,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            return result.get('key_points', [])
            
        except Exception as e:
            raise Exception(f"Key point extraction failed: {str(e)}")
