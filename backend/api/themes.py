"""
Theme Management API Endpoints
Handles theme listing, searching, and custom theme creation
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel

from backend.db.base import get_db
from backend.models.user import User
from backend.models.theme import Theme
from backend.utils.auth import get_current_user
from backend.config import settings

router = APIRouter(prefix="/api/v1/themes", tags=["Themes"])


# Pydantic Schemas
class ThemeResponse(BaseModel):
    id: int
    name: str
    description: str
    category: str
    colors: dict
    fonts: dict
    preview_url: Optional[str]
    is_featured: bool
    is_premium: bool
    usage_count: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class ThemeListResponse(BaseModel):
    id: int
    name: str
    description: str
    category: str
    colors: dict
    preview_url: Optional[str]
    is_featured: bool
    is_premium: bool
    usage_count: int
    
    class Config:
        from_attributes = True


class ThemeCreate(BaseModel):
    name: str
    description: str
    category: str
    colors: dict
    fonts: dict
    preview_url: Optional[str] = None
    is_featured: bool = False
    is_premium: bool = False


# List All Themes
@router.get("/", response_model=List[ThemeListResponse])
async def list_themes(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    category: Optional[str] = None,
    search: Optional[str] = None,
    featured: Optional[bool] = None,
    premium: Optional[bool] = None,
    sort_by: str = Query("popular", pattern="^(popular|recent)$"),
    db: Session = Depends(get_db)
):
    """
    List themes with filters and pagination
    
    - **category**: Filter by category (professional, creative, minimal, bold, dark)
    - **search**: Search in name and description
    - **featured**: Show only featured themes
    - **premium**: Filter by premium status
    - **sort_by**: Sort by 'popular' or 'recent'
    """
    query = db.query(Theme)
    
    # Filter by category
    if category:
        query = query.filter(Theme.category == category)
    
    # Search functionality
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                Theme.name.ilike(search_term),
                Theme.description.ilike(search_term)
            )
        )
    
    # Filter by featured
    if featured is not None:
        query = query.filter(Theme.is_featured == featured)
    
    # Filter by premium
    if premium is not None:
        query = query.filter(Theme.is_premium == premium)
    
    # Sorting
    if sort_by == "popular":
        query = query.order_by(Theme.usage_count.desc())
    elif sort_by == "recent":
        query = query.order_by(Theme.created_at.desc())
    
    themes = query.offset(skip).limit(limit).all()
    return themes


# Get Single Theme
@router.get("/{theme_id}", response_model=ThemeResponse)
async def get_theme(
    theme_id: int,
    db: Session = Depends(get_db)
):
    """
    Get a specific theme by ID
    """
    theme = db.query(Theme).filter(Theme.id == theme_id).first()
    
    if not theme:
        raise HTTPException(status_code=404, detail="Theme not found")
    
    # Increment usage count
    theme.usage_count += 1
    db.commit()
    
    return theme


# Get Themes by Category
@router.get("/category/{category}", response_model=List[ThemeListResponse])
async def get_themes_by_category(
    category: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Get all themes in a specific category
    """
    # Validate category
    valid_categories = ["professional", "creative", "minimal", "bold", "dark"]
    if category not in valid_categories:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid category. Must be one of: {', '.join(valid_categories)}"
        )
    
    themes = db.query(Theme).filter(
        Theme.category == category
    ).order_by(
        Theme.usage_count.desc()
    ).offset(skip).limit(limit).all()
    
    return themes


# Get Featured Themes
@router.get("/featured/all", response_model=List[ThemeListResponse])
async def get_featured_themes(
    limit: int = Query(12, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """
    Get featured themes
    """
    themes = db.query(Theme).filter(
        Theme.is_featured == True
    ).order_by(
        Theme.usage_count.desc()
    ).limit(limit).all()
    
    return themes


# Get Theme Categories
@router.get("/categories/list")
async def get_theme_categories():
    """
    Get all available theme categories
    """
    categories = {
        "professional": "Clean, business-appropriate themes",
        "creative": "Bold, artistic themes for creative work",
        "minimal": "Simple, elegant themes with minimal styling",
        "bold": "High-contrast, impactful themes",
        "dark": "Dark mode themes for presentations"
    }
    
    return {
        "categories": categories,
        "count": len(categories)
    }


# Search Themes
@router.get("/search/query", response_model=List[ThemeListResponse])
async def search_themes(
    q: str = Query(..., min_length=2),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Search themes by name or description
    """
    search_term = f"%{q}%"
    
    themes = db.query(Theme).filter(
        or_(
            Theme.name.ilike(search_term),
            Theme.description.ilike(search_term)
        )
    ).order_by(
        Theme.usage_count.desc()
    ).offset(skip).limit(limit).all()
    
    return themes


# Create Custom Theme (Pro users only)
@router.post("/", response_model=ThemeResponse)
async def create_theme(
    data: ThemeCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a custom theme (requires Pro plan or higher)
    """
    # Check if user has permission (Pro plan or higher)
    if current_user.plan not in ["pro", "ultra", "team", "business"]:
        raise HTTPException(
            status_code=403,
            detail="Custom themes require Pro plan or higher"
        )
    
    # Validate category
    valid_categories = ["professional", "creative", "minimal", "bold", "dark"]
    if data.category not in valid_categories:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid category. Must be one of: {', '.join(valid_categories)}"
        )
    
    # Validate colors structure
    required_color_keys = ["primary", "secondary", "background", "text"]
    if not all(key in data.colors for key in required_color_keys):
        raise HTTPException(
            status_code=400,
            detail=f"Colors must include: {', '.join(required_color_keys)}"
        )
    
    # Validate fonts structure
    required_font_keys = ["heading", "body"]
    if not all(key in data.fonts for key in required_font_keys):
        raise HTTPException(
            status_code=400,
            detail=f"Fonts must include: {', '.join(required_font_keys)}"
        )
    
    # Create theme
    theme = Theme(
        name=data.name,
        description=data.description,
        category=data.category,
        colors=data.colors,
        fonts=data.fonts,
        preview_url=data.preview_url,
        is_featured=data.is_featured,
        is_premium=data.is_premium,
        created_by_user_id=current_user.id
    )
    
    db.add(theme)
    db.commit()
    db.refresh(theme)
    
    return theme


# Get User's Custom Themes
@router.get("/user/custom", response_model=List[ThemeListResponse])
async def get_user_themes(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all custom themes created by the current user
    """
    themes = db.query(Theme).filter(
        Theme.created_by_user_id == current_user.id
    ).order_by(
        Theme.created_at.desc()
    ).all()
    
    return themes


# Update Custom Theme
@router.patch("/{theme_id}", response_model=ThemeResponse)
async def update_theme(
    theme_id: int,
    data: ThemeCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update a custom theme (only owner can update)
    """
    theme = db.query(Theme).filter(
        Theme.id == theme_id,
        Theme.created_by_user_id == current_user.id
    ).first()
    
    if not theme:
        raise HTTPException(
            status_code=404,
            detail="Theme not found or you don't have permission to edit it"
        )
    
    # Update fields
    theme.name = data.name
    theme.description = data.description
    theme.category = data.category
    theme.colors = data.colors
    theme.fonts = data.fonts
    if data.preview_url:
        theme.preview_url = data.preview_url
    
    db.commit()
    db.refresh(theme)
    
    return theme


# Delete Custom Theme
@router.delete("/{theme_id}")
async def delete_theme(
    theme_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a custom theme (only owner can delete)
    """
    theme = db.query(Theme).filter(
        Theme.id == theme_id,
        Theme.created_by_user_id == current_user.id
    ).first()
    
    if not theme:
        raise HTTPException(
            status_code=404,
            detail="Theme not found or you don't have permission to delete it"
        )
    
    db.delete(theme)
    db.commit()
    
    return {"message": "Theme deleted successfully"}


# Get Theme Statistics
@router.get("/{theme_id}/stats")
async def get_theme_stats(
    theme_id: int,
    db: Session = Depends(get_db)
):
    """
    Get statistics for a theme
    """
    theme = db.query(Theme).filter(Theme.id == theme_id).first()
    
    if not theme:
        raise HTTPException(status_code=404, detail="Theme not found")
    
    return {
        "id": theme.id,
        "name": theme.name,
        "usage_count": theme.usage_count,
        "is_featured": theme.is_featured,
        "is_premium": theme.is_premium,
        "created_at": theme.created_at
    }


# Get Popular Themes
@router.get("/trending/popular", response_model=List[ThemeListResponse])
async def get_popular_themes(
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """
    Get most popular themes based on usage count
    """
    themes = db.query(Theme).order_by(
        Theme.usage_count.desc()
    ).limit(limit).all()
    
    return themes
