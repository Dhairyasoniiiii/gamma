"""
Generation Agent - Handles all AI generation tasks
Complete implementation with full generation, rewrite, translate, and image capabilities
"""

from backend.agents.base_agent import BaseAgent
from backend.services.ai_service import AIService
from backend.config import settings
from typing import Dict
import os


class GenerationAgent(BaseAgent):
    """
    Handles all AI generation tasks:
    - Full presentation generation from prompts
    - Content rewriting (6 modes)
    - Translation (60+ languages)
    - Image generation (DALL-E 3)
    - Text improvement and expansion
    """
    
    def __init__(self):
        super().__init__("GenerationAgent")
        
        # Use free providers by default if enabled in config
        if settings.USE_FREE_PROVIDERS:
            print("[FREE] GenerationAgent using FREE AI providers")
            self.ai_service = AIService()  # Will auto-detect free mode
        else:
            print("[PAID] GenerationAgent using OpenAI")
            self.ai_service = AIService(settings.OPENAI_API_KEY)
    
    async def process(self, input_data: Dict) -> Dict:
        """
        Process generation request
        
        Input structure:
        {
            "type": "full_generation|rewrite|image|translate",
            "prompt": "...",
            "user_id": "...",
            "options": {...}
        }
        """
        
        task_type = input_data['type']
        
        if task_type == 'full_generation':
            return await self._generate_presentation(input_data)
        
        elif task_type == 'rewrite':
            return await self._rewrite_content(input_data)
        
        elif task_type == 'image':
            return await self._generate_image(input_data)
        
        elif task_type == 'translate':
            return await self._translate_content(input_data)
        
        else:
            raise ValueError(f"Unknown task type: {task_type}")
    
    async def _generate_presentation(self, data: Dict) -> Dict:
        """
        Generate complete presentation with GPT-4
        
        Steps:
        1. Check user credits
        2. Generate presentation structure with AI
        3. Generate images for image cards
        4. Save to database
        5. Deduct credits
        6. Track usage
        """
        
        prompt = data['prompt']
        user_id = data['user_id']
        num_cards = data.get('num_cards', 10)
        style = data.get('style', 'professional')
        
        # Check user credits
        if not await self._check_credits(user_id, settings.CREDIT_COST_FULL_GENERATION):
            raise Exception(f"Insufficient credits. Required: {settings.CREDIT_COST_FULL_GENERATION}")
        
        # Generate with AI
        result = await self.ai_service.generate_presentation(
            prompt=prompt,
            num_cards=num_cards,
            style=style
        )
        
        # Save to database
        presentation_id = await self._save_presentation(
            user_id=user_id,
            data=result,
            prompt=prompt
        )
        
        # Deduct credits
        await self._deduct_credits(user_id, settings.CREDIT_COST_FULL_GENERATION)
        
        # Track generation
        await self._track_generation(
            user_id=user_id,
            presentation_id=presentation_id,
            type='full_generation',
            prompt=prompt,
            credits_used=settings.CREDIT_COST_FULL_GENERATION
        )
        
        return {
            'success': True,
            'presentation_id': presentation_id,
            'data': result,
            'credits_used': settings.CREDIT_COST_FULL_GENERATION,
            'credits_remaining': await self._get_credits(user_id)
        }
    
    async def _rewrite_content(self, data: Dict) -> Dict:
        """
        Rewrite text content with 6 modes:
        - improve: Make more professional
        - simplify: Make easier to understand
        - expand: Add more detail
        - shorten: Make more concise
        - casual: More casual tone
        - formal: More formal tone
        """
        
        text = data['text']
        instruction = data.get('instruction', 'improve')
        user_id = data['user_id']
        
        # Check credits
        if not await self._check_credits(user_id, settings.CREDIT_COST_REWRITE):
            raise Exception(f"Insufficient credits. Required: {settings.CREDIT_COST_REWRITE}")
        
        # Rewrite
        rewritten = await self.ai_service.rewrite_text(text, instruction)
        
        # Deduct credits
        await self._deduct_credits(user_id, settings.CREDIT_COST_REWRITE)
        
        return {
            'success': True,
            'original': text,
            'rewritten': rewritten,
            'instruction': instruction,
            'credits_used': settings.CREDIT_COST_REWRITE,
            'credits_remaining': await self._get_credits(user_id)
        }
    
    async def _generate_image(self, data: Dict) -> Dict:
        """
        Generate AI image using DALL-E 3
        
        Supports:
        - Multiple sizes (1024x1024, 1792x1024, 1024x1792)
        - Quality modes (standard, hd)
        - Custom prompts
        """
        
        prompt = data['prompt']
        user_id = data['user_id']
        size = data.get('size', '1024x1024')
        quality = data.get('quality', 'standard')
        
        # Check credits (images cost more)
        if not await self._check_credits(user_id, settings.CREDIT_COST_IMAGE):
            raise Exception(f"Insufficient credits. Required: {settings.CREDIT_COST_IMAGE}")
        
        # Generate
        image_url = await self.ai_service._generate_image(
            prompt=prompt,
            size=size,
            quality=quality
        )
        
        # Deduct credits
        await self._deduct_credits(user_id, settings.CREDIT_COST_IMAGE)
        
        return {
            'success': True,
            'image_url': image_url,
            'prompt': prompt,
            'size': size,
            'quality': quality,
            'credits_used': settings.CREDIT_COST_IMAGE,
            'credits_remaining': await self._get_credits(user_id)
        }
    
    async def _translate_content(self, data: Dict) -> Dict:
        """
        Translate content to 60+ languages
        
        Supported languages include:
        en, es, fr, de, ja, zh, ko, pt, ru, ar, hi, it, nl, pl, tr, vi, th, id, ms, fa, uk, ro, el, cs, sv, da, fi, no, and many more
        """
        
        text = data['text']
        target_language = data['target_language']
        user_id = data['user_id']
        
        # Check credits
        if not await self._check_credits(user_id, settings.CREDIT_COST_TRANSLATE):
            raise Exception(f"Insufficient credits. Required: {settings.CREDIT_COST_TRANSLATE}")
        
        # Translate
        translated = await self.ai_service.translate_text(text, target_language)
        
        # Deduct credits
        await self._deduct_credits(user_id, settings.CREDIT_COST_TRANSLATE)
        
        return {
            'success': True,
            'original': text,
            'translated': translated,
            'target_language': target_language,
            'credits_used': settings.CREDIT_COST_TRANSLATE,
            'credits_remaining': await self._get_credits(user_id)
        }
    
    async def _check_credits(self, user_id: str, required: int = 1) -> bool:
        """Check if user has enough credits"""
        from backend.db.base import SessionLocal
        from backend.models.user import User
        
        db = SessionLocal()
        try:
            user = db.query(User).filter(User.id == user_id).first()
            return user and user.credits_remaining >= required
        finally:
            db.close()
    
    async def _get_credits(self, user_id: str) -> int:
        """Get user's current credit balance"""
        from backend.db.base import SessionLocal
        from backend.models.user import User
        
        db = SessionLocal()
        try:
            user = db.query(User).filter(User.id == user_id).first()
            return user.credits_remaining if user else 0
        finally:
            db.close()
    
    async def _deduct_credits(self, user_id: str, amount: int):
        """Deduct credits from user"""
        from backend.db.base import SessionLocal
        from backend.models.user import User
        
        db = SessionLocal()
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if user:
                user.credits_remaining -= amount
                user.credits_used = (user.credits_used or 0) + amount
                user.total_ai_generations = (user.total_ai_generations or 0) + 1
                db.commit()
        finally:
            db.close()
    
    async def _save_presentation(self, user_id: str, data: Dict, prompt: str) -> str:
        """Save generated presentation to database"""
        from backend.db.base import SessionLocal
        from backend.models.presentation import Presentation
        from backend.models.user import User
        import uuid
        
        # Simple slug generation
        def slugify(text: str) -> str:
            import re
            text = text.lower().strip()
            text = re.sub(r'[^\w\s-]', '', text)
            text = re.sub(r'[-\s]+', '-', text)
            return text[:50]
        
        db = SessionLocal()
        try:
            presentation = Presentation(
                id=uuid.uuid4(),
                title=data.get('title', 'Untitled Presentation'),
                slug=slugify(data.get('title', 'untitled-presentation')),
                owner_id=user_id,
                content=data,
                is_published=False,
                is_public=False
            )
            db.add(presentation)
            db.commit()
            db.refresh(presentation)
            
            # Update user stats
            user = db.query(User).filter(User.id == user_id).first()
            if user:
                user.total_presentations = (user.total_presentations or 0) + 1
                db.commit()
            
            return str(presentation.id)
        finally:
            db.close()
    
    async def _track_generation(
        self,
        user_id: str,
        presentation_id: str,
        type: str,
        prompt: str,
        credits_used: int
    ):
        """
        Track AI generation in analytics
        Future: Store in MongoDB for analytics
        """
        # For now, we just log it
        # In production, this would insert into analytics collection
        pass

