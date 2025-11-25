"""
AI Generation API endpoints
Handles: Full generation, Rewrite, Translate, Images
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, validator
from typing import List, Optional

from backend.db.base import get_db
from backend.models.user import User
from backend.utils.auth import get_current_user
from backend.utils.credits import check_and_deduct_credits, get_operation_cost
from backend.agents.generation_agent import GenerationAgent
from backend.config import settings

router = APIRouter(prefix="/api/v1/ai", tags=["AI"])

# Initialize agent
generation_agent = GenerationAgent()


# Pydantic models
class GeneratePresentationRequest(BaseModel):
    prompt: str
    num_cards: int = 10
    style: str = "professional"  # professional, creative, minimal, bold
    
    @validator('prompt')
    def validate_prompt(cls, v):
        """Validate and sanitize prompt"""
        if len(v) > 5000:
            raise ValueError('Prompt must be less than 5000 characters')
        if len(v) < 10:
            raise ValueError('Prompt must be at least 10 characters')
        return v.strip()
    
    @validator('num_cards')
    def validate_num_cards(cls, v):
        """Validate number of cards"""
        if v < 1 or v > 100:
            raise ValueError('Number of cards must be between 1 and 100')
        return v
    
    @validator('style')
    def validate_style(cls, v):
        """Validate style"""
        allowed_styles = ['professional', 'creative', 'minimal', 'bold', 'modern', 'elegant']
        if v not in allowed_styles:
            raise ValueError(f'Style must be one of: {", ".join(allowed_styles)}')
        return v


class RewriteTextRequest(BaseModel):
    text: str
    instruction: str = "improve"  # improve, simplify, expand, shorten, casual, formal
    
    @validator('text')
    def validate_text(cls, v):
        """Validate text length"""
        if len(v) > 10000:
            raise ValueError('Text must be less than 10000 characters')
        if len(v) < 1:
            raise ValueError('Text cannot be empty')
        return v.strip()
    
    @validator('instruction')
    def validate_instruction(cls, v):
        """Validate instruction"""
        allowed = ['improve', 'simplify', 'expand', 'shorten', 'casual', 'formal']
        if v not in allowed:
            raise ValueError(f'Instruction must be one of: {", ".join(allowed)}')
        return v


class TranslateTextRequest(BaseModel):
    text: str
    target_language: str  # en, es, fr, de, ja, zh, etc. (60+ languages)
    
    @validator('text')
    def validate_text(cls, v):
        """Validate text length"""
        if len(v) > 10000:
            raise ValueError('Text must be less than 10000 characters')
        if len(v) < 1:
            raise ValueError('Text cannot be empty')
        return v.strip()
    
    @validator('target_language')
    def validate_language(cls, v):
        """Validate language code"""
        if len(v) > 10:
            raise ValueError('Invalid language code')
        return v.lower().strip()


class GenerateImageRequest(BaseModel):
    prompt: str
    size: str = "1024x1024"
    quality: str = "standard"
    
    @validator('prompt')
    def validate_prompt(cls, v):
        """Validate prompt"""
        if len(v) > 1000:
            raise ValueError('Prompt must be less than 1000 characters')
        if len(v) < 10:
            raise ValueError('Prompt must be at least 10 characters')
        return v.strip()
    
    @validator('size')
    def validate_size(cls, v):
        """Validate size"""
        allowed_sizes = ['1024x1024', '1792x1024', '1024x1792']
        if v not in allowed_sizes:
            raise ValueError(f'Size must be one of: {", ".join(allowed_sizes)}')
        return v
    
    @validator('quality')
    def validate_quality(cls, v):
        """Validate quality"""
        if v not in ['standard', 'hd']:
            raise ValueError('Quality must be "standard" or "hd"')
        return v


@router.post("/generate")
async def generate_presentation(
    request: GeneratePresentationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Generate complete presentation from prompt
    
    **Credits required:** 10
    
    **Plans:**
    - Free: Up to 10 cards
    - Plus: Up to 30 cards
    - Pro: Up to 60 cards
    - Ultra: Up to 75 cards
    
    **Returns:**
    - presentation_id
    - title
    - cards (array of card objects)
    - theme (suggested theme)
    """
    
    # Check and deduct credits
    await check_and_deduct_credits(
        user=current_user,
        cost=settings.COST_GENERATE_PRESENTATION,
        db=db,
        operation="generate_presentation",
        metadata={"num_cards": request.num_cards, "style": request.style}
    )
    
    # Check plan limits
    max_cards = current_user.get_max_cards()
    
    if request.num_cards > max_cards:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Your {current_user.plan} plan allows up to {max_cards} cards per generation. Upgrade to generate more."
        )
    
    # Generate
    try:
        result = await generation_agent.process({
            'type': 'full_generation',
            'prompt': request.prompt,
            'user_id': str(current_user.id),
            'num_cards': request.num_cards,
            'style': request.style
        })
        
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Generation failed: {str(e)}"
        )


@router.post("/rewrite")
async def rewrite_text(
    request: RewriteTextRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Rewrite/improve text content
    
    **Credits required:** 1
    
    **Instructions:**
    - improve: Make more professional
    - simplify: Make easier to understand
    - expand: Add more detail
    - shorten: Make more concise
    - casual: More casual tone
    - formal: More formal tone
    """
    
    # Check and deduct credits
    await check_and_deduct_credits(
        user=current_user,
        cost=settings.COST_REWRITE_TEXT,
        db=db,
        operation="rewrite_text",
        metadata={"instruction": request.instruction}
    )
    
    try:
        result = await generation_agent.process({
            'type': 'rewrite',
            'text': request.text,
            'instruction': request.instruction,
            'user_id': str(current_user.id)
        })
        
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Rewrite failed: {str(e)}"
        )


@router.post("/translate")
async def translate_text(
    request: TranslateTextRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Translate text to target language
    
    **Credits required:** 2
    
    **Supported languages:** 60+ including:
    - en (English)
    - es (Spanish)
    - fr (French)
    - de (German)
    - ja (Japanese)
    - zh (Chinese)
    - ko (Korean)
    - pt (Portuguese)
    - ru (Russian)
    - ar (Arabic)
    - and many more...
    """
    
    # Check and deduct credits
    await check_and_deduct_credits(
        user=current_user,
        cost=settings.COST_TRANSLATE,
        db=db,
        operation="translate",
        metadata={"target_language": request.target_language}
    )
    
    try:
        result = await generation_agent.process({
            'type': 'translate',
            'text': request.text,
            'target_language': request.target_language,
            'user_id': str(current_user.id)
        })
        
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Translation failed: {str(e)}"
        )


@router.post("/image")
async def generate_image(
    request: GenerateImageRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Generate AI image using DALL-E 3
    
    **Credits required:** 5
    
    **Available on:** Plus, Pro, Ultra plans
    
    **Sizes:**
    - 1024x1024 (square)
    - 1792x1024 (landscape)
    - 1024x1792 (portrait)
    
    **Quality:**
    - standard
    - hd (Pro/Ultra only)
    """
    
    # Check plan
    if current_user.plan == 'free':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="AI image generation requires Plus plan or higher"
        )
    
    # Check and deduct credits
    await check_and_deduct_credits(
        user=current_user,
        cost=settings.COST_GENERATE_IMAGE,
        db=db,
        operation="generate_image",
        metadata={"size": request.size, "quality": request.quality}
    )
    
    # HD quality only for Pro/Ultra
    if request.quality == 'hd' and current_user.plan not in ['pro', 'ultra']:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="HD quality requires Pro or Ultra plan"
        )
    
    try:
        result = await generation_agent.process({
            'type': 'image',
            'prompt': request.prompt,
            'user_id': str(current_user.id)
        })
        
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Image generation failed: {str(e)}"
        )


@router.get("/credits")
async def get_credits(current_user: User = Depends(get_current_user)):
    """
    Get current user's credit balance
    """
    return {
        "credits_remaining": current_user.credits_remaining,
        "plan": current_user.plan,
        "credits_reset_date": current_user.credits_reset_date
    }
