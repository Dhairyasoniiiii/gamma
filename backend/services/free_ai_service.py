"""
Free AI Service - Multi-Provider AI Generation
Supports: Google Gemini, Groq, Perplexity, Anthropic Claude
Automatically rotates between providers to maximize free tier usage
"""

import requests
import json
import asyncio
from typing import Dict, List, Optional
from backend.config import settings


class FreeAIService:
    """
    Free AI service with automatic provider rotation
    
    Providers:
    - Google Gemini: 15 RPM, 1M tokens/day (BEST FREE TIER)
    - Groq: 30 RPM (FASTEST)
    - Perplexity: 5 RPS
    - Claude Haiku: $5 free credit
    
    Automatically rotates when limits hit
    """
    
    def __init__(self):
        # Track usage per provider
        self.usage = {
            'gemini': {'count': 0, 'daily_limit': 500},
            'groq': {'count': 0, 'daily_limit': 1000},
            'perplexity': {'count': 0, 'daily_limit': 500},
            'claude': {'count': 0, 'daily_limit': 1000}
        }
        
        # Initialize providers
        self._init_providers()
        
        # Provider priority order
        self.providers = []
        self.available_providers = []  # Actually available
        self.current_provider_index = 0
    
    def _init_providers(self):
        """Initialize all available providers"""
        self.available_providers = []
        
        # Google Gemini
        if settings.GOOGLE_API_KEY:
            try:
                import google.generativeai as genai
                genai.configure(api_key=settings.GOOGLE_API_KEY)
                self.gemini_model = genai.GenerativeModel('gemini-pro')
                self.available_providers.append('gemini')
                print("[OK] Google Gemini configured")
            except (ImportError, AttributeError, KeyboardInterrupt, Exception) as e:
                print(f"[SKIP] Google Gemini not available: {type(e).__name__}")
        
        # Groq
        if settings.GROQ_API_KEY:
            try:
                from groq import Groq
                self.groq_client = Groq(api_key=settings.GROQ_API_KEY)
                self.available_providers.append('groq')
                print("[OK] Groq configured")
            except Exception as e:
                print(f"[SKIP] Groq not available: {type(e).__name__}")
        
        # Perplexity (REST API)
        if settings.PERPLEXITY_API_KEY:
            self.perplexity_key = settings.PERPLEXITY_API_KEY
            self.available_providers.append('perplexity')
            print("[OK] Perplexity configured")
        
        # Anthropic Claude
        if settings.ANTHROPIC_API_KEY:
            try:
                import anthropic
                self.claude_client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
                self.available_providers.append('claude')
                print("[OK] Anthropic Claude configured")
            except Exception as e:
                print(f"[SKIP] Anthropic not available: {type(e).__name__}")
        
        if not self.available_providers:
            print("[ERROR] No AI providers configured! Set API keys in .env file")
        
        self.providers = self.available_providers
    
    async def generate_presentation(
        self,
        prompt: str,
        num_cards: int = 10,
        style: str = "professional"
    ) -> Dict:
        """
        Generate complete presentation using free providers
        Automatically rotates between providers
        """
        
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
        }}
    ]
}}

IMPORTANT: Return ONLY valid JSON, no markdown formatting or code blocks."""
        
        user_prompt = f"Create a presentation about: {prompt}"
        
        # Try providers in order until one succeeds
        for attempt in range(len(self.providers)):
            provider = self._get_next_provider()
            
            try:
                print(f"[AI] Using {provider.upper()} for generation...")
                
                if provider == 'gemini':
                    result = await self._generate_with_gemini(system_prompt, user_prompt)
                elif provider == 'groq':
                    result = await self._generate_with_groq(system_prompt, user_prompt)
                elif provider == 'perplexity':
                    result = await self._generate_with_perplexity(system_prompt, user_prompt)
                elif provider == 'claude':
                    result = await self._generate_with_claude(system_prompt, user_prompt)
                else:
                    continue
                
                # Track successful usage
                self.usage[provider]['count'] += 1
                
                # Add theme and metadata
                result['theme'] = self._suggest_theme(style)
                result['metadata'] = {
                    'prompt': prompt,
                    'style': style,
                    'provider': provider,
                    'total_cards': len(result.get('cards', []))
                }
                
                return result
                
            except Exception as e:
                print(f"[WARNING] {provider.upper()} failed: {str(e)}")
                # Try next provider
                continue
        
        raise Exception("All AI providers failed. Please check your API keys.")
    
    async def rewrite_text(
        self,
        text: str,
        instruction: str = "improve"
    ) -> str:
        """Rewrite text using free providers"""
        
        instruction_prompts = {
            "improve": "Make this text more professional and engaging while keeping the same meaning:",
            "simplify": "Simplify this text to make it easier to understand:",
            "expand": "Expand this text with more detail and examples:",
            "shorten": "Make this text more concise while keeping key points:",
            "casual": "Rewrite this in a more casual, conversational tone:",
            "formal": "Rewrite this in a more formal, professional tone:"
        }
        
        prompt = f"{instruction_prompts.get(instruction, instruction)}\n\n{text}"
        
        # Try providers
        for attempt in range(len(self.providers)):
            provider = self._get_next_provider()
            
            try:
                if provider == 'gemini':
                    return await self._simple_gemini_call(prompt)
                elif provider == 'groq':
                    return await self._simple_groq_call(prompt)
                elif provider == 'perplexity':
                    return await self._simple_perplexity_call(prompt)
                elif provider == 'claude':
                    return await self._simple_claude_call(prompt)
            except Exception as e:
                print(f"[WARNING] {provider.upper()} failed: {str(e)}")
                continue
        
        raise Exception("All AI providers failed")
    
    async def translate_text(
        self,
        text: str,
        target_language: str
    ) -> str:
        """Translate text using free providers"""
        
        prompt = f"Translate the following text to {target_language}. Maintain the tone and style.\n\n{text}"
        
        # Try providers
        for attempt in range(len(self.providers)):
            provider = self._get_next_provider()
            
            try:
                if provider == 'gemini':
                    return await self._simple_gemini_call(prompt)
                elif provider == 'groq':
                    return await self._simple_groq_call(prompt)
                elif provider == 'perplexity':
                    return await self._simple_perplexity_call(prompt)
                elif provider == 'claude':
                    return await self._simple_claude_call(prompt)
            except Exception as e:
                continue
        
        raise Exception("All AI providers failed")
    
    # Provider-specific implementations
    
    async def _generate_with_gemini(self, system_prompt: str, user_prompt: str) -> Dict:
        """Generate with Google Gemini"""
        model = genai.GenerativeModel('gemini-1.5-flash')
        full_prompt = f"{system_prompt}\n\n{user_prompt}"
        
        response = model.generate_content(full_prompt)
        text = response.text
        
        # Clean markdown code blocks if present
        text = text.strip()
        if text.startswith('```'):
            text = text.split('```')[1]
            if text.startswith('json'):
                text = text[4:]
            text = text.strip()
        
        return json.loads(text)
    
    async def _generate_with_groq(self, system_prompt: str, user_prompt: str) -> Dict:
        """Generate with Groq"""
        completion = self.groq_client.chat.completions.create(
            model="llama-3.1-70b-versatile",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7,
            max_tokens=4000
        )
        
        text = completion.choices[0].message.content.strip()
        
        # Clean markdown code blocks if present
        if text.startswith('```'):
            text = text.split('```')[1]
            if text.startswith('json'):
                text = text[4:]
            text = text.strip()
        
        return json.loads(text)
    
    async def _generate_with_perplexity(self, system_prompt: str, user_prompt: str) -> Dict:
        """Generate with Perplexity"""
        url = "https://api.perplexity.ai/chat/completions"
        
        payload = {
            "model": "llama-3.1-sonar-large-128k-online",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
        }
        
        headers = {
            "Authorization": f"Bearer {self.perplexity_key}",
            "Content-Type": "application/json"
        }
        
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        
        result = response.json()
        text = result['choices'][0]['message']['content'].strip()
        
        # Clean markdown code blocks
        if text.startswith('```'):
            text = text.split('```')[1]
            if text.startswith('json'):
                text = text[4:]
            text = text.strip()
        
        return json.loads(text)
    
    async def _generate_with_claude(self, system_prompt: str, user_prompt: str) -> Dict:
        """Generate with Claude"""
        message = self.claude_client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=4000,
            system=system_prompt,
            messages=[
                {"role": "user", "content": user_prompt}
            ]
        )
        
        text = message.content[0].text.strip()
        
        # Clean markdown code blocks
        if text.startswith('```'):
            text = text.split('```')[1]
            if text.startswith('json'):
                text = text[4:]
            text = text.strip()
        
        return json.loads(text)
    
    # Simple text generation methods
    
    async def _simple_gemini_call(self, prompt: str) -> str:
        """Simple text generation with Gemini"""
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        return response.text.strip()
    
    async def _simple_groq_call(self, prompt: str) -> str:
        """Simple text generation with Groq"""
        completion = self.groq_client.chat.completions.create(
            model="llama-3.1-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        return completion.choices[0].message.content.strip()
    
    async def _simple_perplexity_call(self, prompt: str) -> str:
        """Simple text generation with Perplexity"""
        url = "https://api.perplexity.ai/chat/completions"
        
        payload = {
            "model": "llama-3.1-sonar-large-128k-online",
            "messages": [{"role": "user", "content": prompt}]
        }
        
        headers = {
            "Authorization": f"Bearer {self.perplexity_key}",
            "Content-Type": "application/json"
        }
        
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        
        result = response.json()
        return result['choices'][0]['message']['content'].strip()
    
    async def _simple_claude_call(self, prompt: str) -> str:
        """Simple text generation with Claude"""
        message = self.claude_client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}]
        )
        return message.content[0].text.strip()
    
    # Helper methods
    
    def _get_next_provider(self) -> str:
        """Get next available provider with capacity"""
        # Check current provider first
        for _ in range(len(self.providers)):
            provider = self.providers[self.current_provider_index]
            
            # Check if provider has capacity
            if self.usage[provider]['count'] < self.usage[provider]['daily_limit']:
                return provider
            
            # Move to next provider
            self.current_provider_index = (self.current_provider_index + 1) % len(self.providers)
        
        # If all providers at limit, reset and use first
        print("[WARNING] All providers at daily limit, resetting counts")
        for provider in self.usage:
            self.usage[provider]['count'] = 0
        return self.providers[0]
    
    def _suggest_theme(self, style: str) -> Dict:
        """Suggest theme based on style"""
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
    
    def get_usage_stats(self) -> Dict:
        """Get current usage statistics"""
        return {
            'usage': self.usage,
            'current_provider': self.providers[self.current_provider_index]
        }
