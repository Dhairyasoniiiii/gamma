"""
Template Management API Endpoints
Handles template listing, searching, and management
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel

from backend.db.base import get_db
from backend.models.user import User
from backend.models.template import Template
from backend.utils.auth import get_current_user
from backend.config import settings, TEMPLATE_CATEGORIES

router = APIRouter(prefix="/api/v1/templates", tags=["Templates"])


# Pydantic Schemas
class TemplateResponse(BaseModel):
    id: int
    name: str
    description: str
    category: str
    subcategory: Optional[str]
    preview_url: Optional[str]
    content: dict
    tags: List[str]
    is_featured: bool
    is_premium: bool
    usage_count: int
    rating: Optional[float]
    created_at: datetime
    
    class Config:
        from_attributes = True


class TemplateListResponse(BaseModel):
    id: int
    name: str
    description: str
    category: str
    subcategory: Optional[str]
    preview_url: Optional[str]
    tags: List[str]
    is_featured: bool
    is_premium: bool
    usage_count: int
    rating: Optional[float]
    
    class Config:
        from_attributes = True


class TemplateCreate(BaseModel):
    name: str
    description: str
    category: str
    subcategory: Optional[str] = None
    preview_url: Optional[str] = None
    content: dict
    tags: List[str] = []
    is_featured: bool = False
    is_premium: bool = False


# List All Templates
@router.get("/", response_model=List[TemplateListResponse])
async def list_templates(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    category: Optional[str] = None,
    subcategory: Optional[str] = None,
    search: Optional[str] = None,
    featured: Optional[bool] = None,
    premium: Optional[bool] = None,
    sort_by: str = Query("popular", pattern="^(popular|recent|rating)$"),
    db: Session = Depends(get_db)
):
    """
    List templates with filters and pagination
    
    - **category**: Filter by category (pitch, marketing, portfolio, etc.)
    - **subcategory**: Filter by subcategory
    - **search**: Search in name, description, and tags
    - **featured**: Show only featured templates
    - **premium**: Filter by premium status
    - **sort_by**: Sort by 'popular', 'recent', or 'rating'
    """
    query = db.query(Template)
    
    # Filter by category
    if category:
        query = query.filter(Template.category == category)
    
    # Filter by subcategory
    if subcategory:
        query = query.filter(Template.subcategory == subcategory)
    
    # Search functionality
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                Template.name.ilike(search_term),
                Template.description.ilike(search_term),
                Template.tags.contains([search.lower()])
            )
        )
    
    # Filter by featured
    if featured is not None:
        query = query.filter(Template.is_featured == featured)
    
    # Filter by premium
    if premium is not None:
        query = query.filter(Template.is_premium == premium)
    
    # Sorting
    if sort_by == "popular":
        query = query.order_by(Template.usage_count.desc())
    elif sort_by == "recent":
        query = query.order_by(Template.created_at.desc())
    elif sort_by == "rating":
        query = query.order_by(Template.rating.desc().nullslast())
    
    templates = query.offset(skip).limit(limit).all()
    return templates


# Get Single Template
@router.get("/{template_id}", response_model=TemplateResponse)
async def get_template(
    template_id: int,
    db: Session = Depends(get_db)
):
    """
    Get a specific template by ID
    """
    template = db.query(Template).filter(Template.id == template_id).first()
    
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    # Increment usage count
    template.usage_count += 1
    db.commit()
    
    return template


# Get Templates by Category
@router.get("/category/{category}", response_model=List[TemplateListResponse])
async def get_templates_by_category(
    category: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Get all templates in a specific category
    """
    templates = db.query(Template).filter(
        Template.category == category
    ).order_by(
        Template.usage_count.desc()
    ).offset(skip).limit(limit).all()
    
    return templates


# Get Featured Templates
@router.get("/featured/all", response_model=List[TemplateListResponse])
async def get_featured_templates(
    limit: int = Query(12, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """
    Get featured templates
    """
    templates = db.query(Template).filter(
        Template.is_featured == True
    ).order_by(
        Template.usage_count.desc()
    ).limit(limit).all()
    
    return templates


# Get Template Categories
@router.get("/categories/list")
async def get_template_categories():
    """
    Get all available template categories
    """
    return {
        "categories": TEMPLATE_CATEGORIES,
        "count": len(TEMPLATE_CATEGORIES)
    }


# Search Templates
@router.get("/search/query", response_model=List[TemplateListResponse])
async def search_templates(
    q: str = Query(..., min_length=2),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Search templates by name, description, or tags
    """
    search_term = f"%{q}%"
    
    templates = db.query(Template).filter(
        or_(
            Template.name.ilike(search_term),
            Template.description.ilike(search_term),
            Template.tags.contains([q.lower()])
        )
    ).order_by(
        Template.usage_count.desc()
    ).offset(skip).limit(limit).all()
    
    return templates


# Get Similar Templates
@router.get("/{template_id}/similar", response_model=List[TemplateListResponse])
async def get_similar_templates(
    template_id: int,
    limit: int = Query(6, ge=1, le=20),
    db: Session = Depends(get_db)
):
    """
    Get similar templates based on category and tags
    """
    # Get the reference template
    reference = db.query(Template).filter(Template.id == template_id).first()
    
    if not reference:
        raise HTTPException(status_code=404, detail="Template not found")
    
    # Find similar templates (same category, excluding the reference)
    similar = db.query(Template).filter(
        Template.category == reference.category,
        Template.id != template_id
    ).order_by(
        Template.usage_count.desc()
    ).limit(limit).all()
    
    return similar


# Create Custom Template (Admin/Pro users only)
@router.post("/", response_model=TemplateResponse)
async def create_template(
    data: TemplateCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a custom template (requires Pro plan or higher)
    """
    # Check if user has permission (Pro plan or higher)
    if current_user.plan not in ["pro", "ultra", "team", "business"]:
        raise HTTPException(
            status_code=403,
            detail="Custom templates require Pro plan or higher"
        )
    
    # Validate category
    if data.category not in TEMPLATE_CATEGORIES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid category. Must be one of: {', '.join(TEMPLATE_CATEGORIES.keys())}"
        )
    
    # Create template
    template = Template(
        name=data.name,
        description=data.description,
        category=data.category,
        subcategory=data.subcategory,
        preview_url=data.preview_url,
        content=data.content,
        tags=data.tags,
        is_featured=data.is_featured,
        is_premium=data.is_premium,
        created_by_user_id=current_user.id
    )
    
    db.add(template)
    db.commit()
    db.refresh(template)
    
    return template


# Get Template Statistics
@router.get("/{template_id}/stats")
async def get_template_stats(
    template_id: int,
    db: Session = Depends(get_db)
):
    """
    Get statistics for a template
    """
    template = db.query(Template).filter(Template.id == template_id).first()
    
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    return {
        "id": template.id,
        "name": template.name,
        "usage_count": template.usage_count,
        "rating": template.rating,
        "is_featured": template.is_featured,
        "is_premium": template.is_premium,
        "created_at": template.created_at
    }


# Get Popular Templates
@router.get("/trending/popular", response_model=List[TemplateListResponse])
async def get_popular_templates(
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """
    Get most popular templates based on usage count
    """
    templates = db.query(Template).order_by(
        Template.usage_count.desc()
    ).limit(limit).all()
    
    return templates


# Get Recently Added Templates
@router.get("/trending/recent", response_model=List[TemplateListResponse])
async def get_recent_templates(
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """
    Get recently added templates
    """
    templates = db.query(Template).order_by(
        Template.created_at.desc()
    ).limit(limit).all()
    
    return templates
