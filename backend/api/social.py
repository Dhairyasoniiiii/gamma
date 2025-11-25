"""
Social Posts API endpoints for Gamma Clone
Handles social media content generation for Instagram, LinkedIn, Twitter, Facebook, TikTok
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel

from backend.db.base import get_db
from backend.models.user import User
from backend.models.social_post import SocialPost, SocialPlatform
from backend.models.folder import Folder
from backend.utils.auth import get_current_user
from backend.services.ai_service import AIService
from backend.config import settings

router = APIRouter(prefix="/api/v1/social", tags=["Social Posts"])


# Request/Response Models
class GenerateSocialPostRequest(BaseModel):
    prompt: str
    SocialPlatform: SocialPlatform
    tone: Optional[str] = "professional"
    include_hashtags: Optional[bool] = True
    include_emojis: Optional[bool] = True
    folder_id: Optional[str] = None


class CreateSocialPostRequest(BaseModel):
    SocialPlatform: SocialPlatform
    caption: str
    media_url: Optional[str] = None
    media_type: Optional[str] = None  # image, video, carousel
    hashtags: Optional[List[str]] = []
    mentions: Optional[List[str]] = []
    scheduled_for: Optional[datetime] = None
    folder_id: Optional[str] = None


class UpdateSocialPostRequest(BaseModel):
    caption: Optional[str] = None
    media_url: Optional[str] = None
    media_type: Optional[str] = None
    hashtags: Optional[List[str]] = None
    mentions: Optional[List[str]] = None
    scheduled_for: Optional[datetime] = None
    folder_id: Optional[str] = None


class SchedulePostRequest(BaseModel):
    scheduled_for: datetime


class SocialPostResponse(BaseModel):
    id: str
    SocialPlatform: str
    caption: str
    media_url: Optional[str]
    media_type: Optional[str]
    hashtags: List[str]
    mentions: List[str]
    is_published: bool
    scheduled_for: Optional[datetime]
    published_at: Optional[datetime]
    likes_count: int
    comments_count: int
    shares_count: int
    views_count: int
    folder_id: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


@router.post("/generate", response_model=SocialPostResponse, status_code=status.HTTP_201_CREATED)
async def generate_social_post(
    request: GenerateSocialPostRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    AI-generate a social media post optimized for specific SocialPlatform.
    Cost: 5 credits
    """
    cost = 5
    
    if current_user.credits < cost:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail=f"Insufficient credits. Need {cost}, have {current_user.credits}"
        )
    
    # Validate folder ownership if provided
    if request.folder_id:
        folder = db.query(Folder).filter(
            Folder.id == request.folder_id,
            Folder.user_id == current_user.id,
            Folder.is_deleted == False
        ).first()
        if not folder:
            raise HTTPException(status_code=404, detail="Folder not found")
    
    try:
        ai_service = AIService()
        
        # SocialPlatform-specific constraints and best practices
        platform_specs = {
            SocialPlatform.INSTAGRAM: {
                "max_caption": 2200,
                "max_hashtags": 30,
                "recommended_hashtags": "5-10",
                "tips": "Use line breaks, emojis, and story-telling approach"
            },
            SocialPlatform.LINKEDIN: {
                "max_caption": 3000,
                "max_hashtags": 5,
                "recommended_hashtags": "3-5",
                "tips": "Professional tone, industry insights, thought leadership"
            },
            SocialPlatform.TWITTER: {
                "max_caption": 280,
                "max_hashtags": 2,
                "recommended_hashtags": "1-2",
                "tips": "Concise, engaging, use threads for longer content"
            },
            SocialPlatform.FACEBOOK: {
                "max_caption": 63206,
                "max_hashtags": 3,
                "recommended_hashtags": "1-3",
                "tips": "Conversational, encourage engagement, ask questions"
            },
            SocialPlatform.TIKTOK: {
                "max_caption": 2200,
                "max_hashtags": 5,
                "recommended_hashtags": "3-5",
                "tips": "Trendy, hook viewers in first 3 seconds, use trending sounds"
            }
        }
        
        specs = platform_specs.get(request.SocialPlatform, {})
        
        full_prompt = f"""Create a {request.SocialPlatform.value} social media post.

Topic: {request.prompt}
Tone: {request.tone}
Include Hashtags: {request.include_hashtags} (recommended: {specs.get('recommended_hashtags', '3-5')})
Include Emojis: {request.include_emojis}

SocialPlatform Constraints:
- Max caption length: {specs.get('max_caption', 2000)} characters
- Max hashtags: {specs.get('max_hashtags', 5)}
- Best practices: {specs.get('tips', 'Engage your audience')}

Generate content as JSON with:
- caption: Main post text (respecting character limit)
- hashtags: Array of relevant hashtags (without # symbol)
- hook: First sentence designed to stop scrolling
- cta: Call-to-action if applicable
"""
        
        generated_content = await ai_service.generate_presentation(
            topic=full_prompt,
            user_id=current_user.id,
            options={"output_format": "social_post", "SocialPlatform": request.SocialPlatform.value}
        )
        
        # Parse generated content
        if isinstance(generated_content, str):
            import json
            try:
                content_dict = json.loads(generated_content)
            except:
                content_dict = {
                    "caption": generated_content[:specs.get('max_caption', 2000)],
                    "hashtags": [],
                    "hook": "",
                    "cta": ""
                }
        else:
            content_dict = generated_content
        
        caption = content_dict.get("caption", "")
        hashtags = content_dict.get("hashtags", [])[:specs.get('max_hashtags', 5)]
        
        # Create social post
        social_post = SocialPost(
            user_id=current_user.id,
            SocialPlatform=request.SocialPlatform,
            caption=caption,
            hashtags=hashtags,
            folder_id=request.folder_id
        )
        
        db.add(social_post)
        
        # Deduct credits
        current_user.credits -= cost
        
        db.commit()
        db.refresh(social_post)
        
        return social_post
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Social post generation failed: {str(e)}"
        )


@router.post("/", response_model=SocialPostResponse, status_code=status.HTTP_201_CREATED)
async def create_social_post(
    request: CreateSocialPostRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new social post manually"""
    # Validate folder ownership if provided
    if request.folder_id:
        folder = db.query(Folder).filter(
            Folder.id == request.folder_id,
            Folder.user_id == current_user.id,
            Folder.is_deleted == False
        ).first()
        if not folder:
            raise HTTPException(status_code=404, detail="Folder not found")
    
    social_post = SocialPost(
        user_id=current_user.id,
        SocialPlatform=request.SocialPlatform,
        caption=request.caption,
        media_url=request.media_url,
        media_type=request.media_type,
        hashtags=request.hashtags or [],
        mentions=request.mentions or [],
        scheduled_for=request.scheduled_for,
        folder_id=request.folder_id
    )
    
    db.add(social_post)
    db.commit()
    db.refresh(social_post)
    
    return social_post


@router.get("/", response_model=List[SocialPostResponse])
async def list_social_posts(
    SocialPlatform: Optional[SocialPlatform] = None,
    folder_id: Optional[str] = None,
    is_published: Optional[bool] = None,
    scheduled_only: Optional[bool] = False,
    skip: int = 0,
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all social posts for current user with optional filters"""
    query = db.query(SocialPost).filter(
        SocialPost.user_id == current_user.id,
        SocialPost.is_deleted == False
    )
    
    if SocialPlatform:
        query = query.filter(SocialPost.SocialPlatform == SocialPlatform)
    
    if folder_id:
        query = query.filter(SocialPost.folder_id == folder_id)
    
    if is_published is not None:
        query = query.filter(SocialPost.is_published == is_published)
    
    if scheduled_only:
        query = query.filter(
            SocialPost.scheduled_for.isnot(None),
            SocialPost.is_published == False
        )
    
    posts = query.order_by(SocialPost.created_at.desc()).offset(skip).limit(limit).all()
    return posts


@router.get("/{post_id}", response_model=SocialPostResponse)
async def get_social_post(
    post_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific social post by ID"""
    post = db.query(SocialPost).filter(
        SocialPost.id == post_id,
        SocialPost.user_id == current_user.id,
        SocialPost.is_deleted == False
    ).first()
    
    if not post:
        raise HTTPException(status_code=404, detail="Social post not found")
    
    return post


@router.patch("/{post_id}", response_model=SocialPostResponse)
async def update_social_post(
    post_id: str,
    request: UpdateSocialPostRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update an existing social post"""
    post = db.query(SocialPost).filter(
        SocialPost.id == post_id,
        SocialPost.user_id == current_user.id,
        SocialPost.is_deleted == False
    ).first()
    
    if not post:
        raise HTTPException(status_code=404, detail="Social post not found")
    
    # Cannot edit published posts
    if post.is_published:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot edit published posts"
        )
    
    # Validate folder ownership if provided
    if request.folder_id:
        folder = db.query(Folder).filter(
            Folder.id == request.folder_id,
            Folder.user_id == current_user.id,
            Folder.is_deleted == False
        ).first()
        if not folder:
            raise HTTPException(status_code=404, detail="Folder not found")
    
    # Update fields
    if request.caption is not None:
        post.caption = request.caption
    if request.media_url is not None:
        post.media_url = request.media_url
    if request.media_type is not None:
        post.media_type = request.media_type
    if request.hashtags is not None:
        post.hashtags = request.hashtags
    if request.mentions is not None:
        post.mentions = request.mentions
    if request.scheduled_for is not None:
        post.scheduled_for = request.scheduled_for
    if request.folder_id is not None:
        post.folder_id = request.folder_id
    
    post.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(post)
    
    return post


@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_social_post(
    post_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Soft delete a social post"""
    post = db.query(SocialPost).filter(
        SocialPost.id == post_id,
        SocialPost.user_id == current_user.id,
        SocialPost.is_deleted == False
    ).first()
    
    if not post:
        raise HTTPException(status_code=404, detail="Social post not found")
    
    post.is_deleted = True
    post.deleted_at = datetime.utcnow()
    
    db.commit()
    
    return None


@router.post("/{post_id}/schedule", response_model=SocialPostResponse)
async def schedule_social_post(
    post_id: str,
    request: SchedulePostRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Schedule a post for future publishing.
    Requires Pro or Ultra plan.
    """
    # Check plan permissions
    if current_user.plan not in ["pro", "ultra"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Post scheduling requires Pro or Ultra plan"
        )
    
    post = db.query(SocialPost).filter(
        SocialPost.id == post_id,
        SocialPost.user_id == current_user.id,
        SocialPost.is_deleted == False
    ).first()
    
    if not post:
        raise HTTPException(status_code=404, detail="Social post not found")
    
    # Validate schedule time is in future
    if request.scheduled_for <= datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Scheduled time must be in the future"
        )
    
    post.scheduled_for = request.scheduled_for
    
    db.commit()
    db.refresh(post)
    
    return post


@router.post("/{post_id}/publish", response_model=SocialPostResponse)
async def publish_social_post(
    post_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Publish a social post immediately.
    Note: This marks as published in the system. Actual posting to social SocialPlatform
    would require OAuth integration (not implemented).
    """
    post = db.query(SocialPost).filter(
        SocialPost.id == post_id,
        SocialPost.user_id == current_user.id,
        SocialPost.is_deleted == False
    ).first()
    
    if not post:
        raise HTTPException(status_code=404, detail="Social post not found")
    
    if post.is_published:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Post is already published"
        )
    
    post.is_published = True
    post.published_at = datetime.utcnow()
    
    db.commit()
    db.refresh(post)
    
    return post


@router.post("/{post_id}/duplicate", response_model=SocialPostResponse, status_code=status.HTTP_201_CREATED)
async def duplicate_social_post(
    post_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a duplicate copy of an existing social post"""
    original = db.query(SocialPost).filter(
        SocialPost.id == post_id,
        SocialPost.user_id == current_user.id,
        SocialPost.is_deleted == False
    ).first()
    
    if not original:
        raise HTTPException(status_code=404, detail="Social post not found")
    
    # Create duplicate
    duplicate = SocialPost(
        user_id=current_user.id,
        SocialPlatform=original.SocialPlatform,
        caption=original.caption,
        media_url=original.media_url,
        media_type=original.media_type,
        hashtags=original.hashtags.copy() if original.hashtags else [],
        mentions=original.mentions.copy() if original.mentions else [],
        folder_id=original.folder_id
    )
    
    db.add(duplicate)
    db.commit()
    db.refresh(duplicate)
    
    return duplicate
