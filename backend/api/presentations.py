"""
Presentation Management API Endpoints
Handles CRUD operations for presentations
"""
from fastapi import APIRouter, Depends, HTTPException, Query, status as http_status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, validator
import json

from backend.db.base import get_db
from backend.models.user import User
from backend.models.presentation import Presentation
from backend.models.template import Template
from backend.models.theme import Theme
from backend.utils.auth import get_current_user
from backend.config import settings

router = APIRouter(prefix="/api/v1/presentations", tags=["Presentations"])


# Pydantic Schemas
class PresentationCreate(BaseModel):
    title: str
    content: dict
    template_id: Optional[int] = None
    theme_id: Optional[int] = None
    is_public: bool = False
    
    @validator('title')
    def validate_title(cls, v):
        """Validate and sanitize title"""
        if len(v) > 500:
            raise ValueError('Title must be less than 500 characters')
        if len(v) < 1:
            raise ValueError('Title cannot be empty')
        return v.strip()
    
    @validator('content')
    def validate_content(cls, v):
        """Validate content structure"""
        if not isinstance(v, dict):
            raise ValueError('Content must be a dictionary')
        # Limit content size to prevent DoS
        import json
        content_size = len(json.dumps(v))
        if content_size > 10 * 1024 * 1024:  # 10MB limit
            raise ValueError('Content size exceeds 10MB limit')
        return v


class PresentationUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[dict] = None
    template_id: Optional[int] = None
    theme_id: Optional[int] = None
    is_public: Optional[bool] = None
    
    @validator('title')
    def validate_title(cls, v):
        """Validate and sanitize title"""
        if v is not None:
            if len(v) > 500:
                raise ValueError('Title must be less than 500 characters')
            if len(v) < 1:
                raise ValueError('Title cannot be empty')
            return v.strip()
        return v
    
    @validator('content')
    def validate_content(cls, v):
        """Validate content structure"""
        if v is not None:
            if not isinstance(v, dict):
                raise ValueError('Content must be a dictionary')
            import json
            content_size = len(json.dumps(v))
            if content_size > 10 * 1024 * 1024:  # 10MB limit
                raise ValueError('Content size exceeds 10MB limit')
        return v


class PresentationResponse(BaseModel):
    id: int
    title: str
    content: dict
    template_id: Optional[int]
    theme_id: Optional[int]
    is_public: bool
    is_archived: bool
    view_count: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class PresentationListResponse(BaseModel):
    id: int
    title: str
    template_id: Optional[int]
    theme_id: Optional[int]
    is_public: bool
    is_archived: bool
    view_count: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Create Presentation
@router.post("/", response_model=PresentationResponse)
async def create_presentation(
    data: PresentationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new presentation
    """
    # Validate template if provided
    if data.template_id:
        template = db.query(Template).filter(Template.id == data.template_id).first()
        if not template:
            raise HTTPException(status_code=404, detail="Template not found")
    
    # Validate theme if provided
    if data.theme_id:
        theme = db.query(Theme).filter(Theme.id == data.theme_id).first()
        if not theme:
            raise HTTPException(status_code=404, detail="Theme not found")
    
    # Create presentation
    presentation = Presentation(
        title=data.title,
        content=data.content,
        template_id=data.template_id,
        theme_id=data.theme_id,
        user_id=current_user.id,
        is_public=data.is_public
    )
    
    db.add(presentation)
    db.commit()
    db.refresh(presentation)
    
    return presentation


# Get Single Presentation
@router.get("/{presentation_id}", response_model=PresentationResponse)
async def get_presentation(
    presentation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get a specific presentation by ID
    """
    presentation = db.query(Presentation).filter(
        Presentation.id == presentation_id
    ).first()
    
    if not presentation:
        raise HTTPException(status_code=404, detail="Presentation not found")
    
    # Check access permissions
    if presentation.user_id != current_user.id and not presentation.is_public:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Increment view count if public
    if presentation.is_public and presentation.user_id != current_user.id:
        presentation.view_count += 1
        db.commit()
    
    return presentation


# List User Presentations
@router.get("/", response_model=List[PresentationListResponse])
async def list_presentations(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    archived: Optional[bool] = None,
    search: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List all presentations for the current user
    """
    query = db.query(Presentation).filter(Presentation.user_id == current_user.id)
    
    # Filter by archived status
    if archived is not None:
        query = query.filter(Presentation.is_archived == archived)
    
    # Search by title (protect against SQL injection)
    if search:
        # Sanitize search input
        search = search.strip()[:255]  # Limit length
        # Use parameterized query to prevent SQL injection
        query = query.filter(Presentation.title.ilike(f"%{search}%"))
    
    # Order by updated_at desc
    query = query.order_by(Presentation.updated_at.desc())
    
    presentations = query.offset(skip).limit(limit).all()
    return presentations


# Update Presentation
@router.patch("/{presentation_id}", response_model=PresentationResponse)
async def update_presentation(
    presentation_id: int,
    data: PresentationUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update a presentation
    """
    presentation = db.query(Presentation).filter(
        Presentation.id == presentation_id,
        Presentation.user_id == current_user.id
    ).first()
    
    if not presentation:
        raise HTTPException(status_code=404, detail="Presentation not found")
    
    # Update fields
    if data.title is not None:
        presentation.title = data.title
    
    if data.content is not None:
        presentation.content = data.content
    
    if data.template_id is not None:
        template = db.query(Template).filter(Template.id == data.template_id).first()
        if not template:
            raise HTTPException(status_code=404, detail="Template not found")
        presentation.template_id = data.template_id
    
    if data.theme_id is not None:
        theme = db.query(Theme).filter(Theme.id == data.theme_id).first()
        if not theme:
            raise HTTPException(status_code=404, detail="Theme not found")
        presentation.theme_id = data.theme_id
    
    if data.is_public is not None:
        presentation.is_public = data.is_public
    
    db.commit()
    db.refresh(presentation)
    
    return presentation


# Delete Presentation
@router.delete("/{presentation_id}")
async def delete_presentation(
    presentation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a presentation (soft delete - archives it)
    """
    presentation = db.query(Presentation).filter(
        Presentation.id == presentation_id,
        Presentation.user_id == current_user.id
    ).first()
    
    if not presentation:
        raise HTTPException(status_code=404, detail="Presentation not found")
    
    # Soft delete
    presentation.is_archived = True
    db.commit()
    
    return {"message": "Presentation archived successfully"}


# Permanently Delete Presentation
@router.delete("/{presentation_id}/permanent")
async def permanently_delete_presentation(
    presentation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Permanently delete a presentation
    """
    presentation = db.query(Presentation).filter(
        Presentation.id == presentation_id,
        Presentation.user_id == current_user.id
    ).first()
    
    if not presentation:
        raise HTTPException(status_code=404, detail="Presentation not found")
    
    # Hard delete
    db.delete(presentation)
    db.commit()
    
    return {"message": "Presentation permanently deleted"}


# Restore Archived Presentation
@router.post("/{presentation_id}/restore")
async def restore_presentation(
    presentation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Restore an archived presentation
    """
    presentation = db.query(Presentation).filter(
        Presentation.id == presentation_id,
        Presentation.user_id == current_user.id,
        Presentation.is_archived == True
    ).first()
    
    if not presentation:
        raise HTTPException(status_code=404, detail="Archived presentation not found")
    
    presentation.is_archived = False
    db.commit()
    
    return {"message": "Presentation restored successfully"}


# Duplicate Presentation
@router.post("/{presentation_id}/duplicate", response_model=PresentationResponse)
async def duplicate_presentation(
    presentation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Duplicate a presentation
    """
    original = db.query(Presentation).filter(
        Presentation.id == presentation_id
    ).first()
    
    if not original:
        raise HTTPException(status_code=404, detail="Presentation not found")
    
    # Check access permissions
    if original.user_id != current_user.id and not original.is_public:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Create duplicate
    duplicate = Presentation(
        title=f"{original.title} (Copy)",
        content=original.content.copy() if isinstance(original.content, dict) else original.content,
        template_id=original.template_id,
        theme_id=original.theme_id,
        user_id=current_user.id,
        is_public=False  # Always private by default
    )
    
    db.add(duplicate)
    db.commit()
    db.refresh(duplicate)
    
    return duplicate


# Get Presentation Statistics
@router.get("/{presentation_id}/stats")
async def get_presentation_stats(
    presentation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get statistics for a presentation
    """
    presentation = db.query(Presentation).filter(
        Presentation.id == presentation_id,
        Presentation.user_id == current_user.id
    ).first()
    
    if not presentation:
        raise HTTPException(status_code=404, detail="Presentation not found")
    
    # Calculate stats
    card_count = 0
    word_count = 0
    
    if presentation.content and isinstance(presentation.content, dict):
        cards = presentation.content.get("cards", [])
        card_count = len(cards)
        
        # Count words in all text content
        for card in cards:
            if card.get("type") == "text" and card.get("content"):
                word_count += len(card["content"].split())
            elif card.get("title"):
                word_count += len(card["title"].split())
            if card.get("subtitle"):
                word_count += len(card["subtitle"].split())
    
    return {
        "id": presentation.id,
        "title": presentation.title,
        "view_count": presentation.view_count,
        "card_count": card_count,
        "word_count": word_count,
        "is_public": presentation.is_public,
        "created_at": presentation.created_at,
        "updated_at": presentation.updated_at
    }
