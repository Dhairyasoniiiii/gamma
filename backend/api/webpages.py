"""
Webpages API endpoints for Gamma Clone
Handles public-facing webpages with custom domain support
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel

from backend.db.base import get_db
from backend.models.user import User
from backend.models.webpage import Webpage, WebpageType
from backend.models.folder import Folder
from backend.models.custom_domain import CustomDomain, DomainStatus
from backend.utils.auth import get_current_user
from backend.services.ai_service import AIService
from backend.config import settings

router = APIRouter(prefix="/api/v1/webpages", tags=["Webpages"])


# Request/Response Models
class GenerateWebpageRequest(BaseModel):
    prompt: str
    webpage_type: WebpageType
    target_audience: Optional[str] = None
    tone: Optional[str] = "professional"
    include_cta: Optional[bool] = True
    folder_id: Optional[str] = None


class CreateWebpageRequest(BaseModel):
    title: str
    webpage_type: WebpageType
    content: dict
    description: Optional[str] = None
    seo_title: Optional[str] = None
    seo_description: Optional[str] = None
    seo_keywords: Optional[List[str]] = []
    og_image_url: Optional[str] = None
    folder_id: Optional[str] = None


class UpdateWebpageRequest(BaseModel):
    title: Optional[str] = None
    content: Optional[dict] = None
    description: Optional[str] = None
    seo_title: Optional[str] = None
    seo_description: Optional[str] = None
    seo_keywords: Optional[List[str]] = None
    og_image_url: Optional[str] = None
    folder_id: Optional[str] = None


class PublishWebpageRequest(BaseModel):
    subdomain: Optional[str] = None  # Custom subdomain (requires Pro+)
    custom_domain_id: Optional[str] = None  # Use custom domain (requires Ultra)


class WebpageResponse(BaseModel):
    id: str
    title: str
    webpage_type: str
    content: dict
    description: Optional[str]
    subdomain: Optional[str]
    custom_domain_id: Optional[str]
    is_published: bool
    public_url: Optional[str]
    seo_title: Optional[str]
    seo_description: Optional[str]
    seo_keywords: List[str]
    og_image_url: Optional[str]
    view_count: int
    unique_visitors: int
    folder_id: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


@router.post("/generate", response_model=WebpageResponse, status_code=status.HTTP_201_CREATED)
async def generate_webpage(
    request: GenerateWebpageRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    AI-generate a webpage based on prompt and type.
    Cost: 12 credits
    """
    cost = 12
    
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
        
        # Build generation prompt based on webpage type
        type_instructions = {
            WebpageType.LANDING_PAGE: "Create a high-converting landing page with hero section, features, benefits, social proof, and strong CTA.",
            WebpageType.PORTFOLIO: "Design a professional portfolio showcasing work samples, skills, testimonials, and contact information.",
            WebpageType.EVENT_PAGE: "Build an event page with details, agenda, speakers, registration, and venue information.",
            WebpageType.PRODUCT_PAGE: "Develop a product page with features, specifications, pricing, reviews, and purchase options.",
            WebpageType.ABOUT_PAGE: "Compose an about page telling the story, mission, team, and values.",
            WebpageType.CONTACT_PAGE: "Create a contact page with form, location, hours, and multiple contact methods.",
            WebpageType.CUSTOM: "Design a custom webpage based on the specific requirements provided."
        }
        
        full_prompt = f"""Create a {request.webpage_type.value} webpage.

Topic: {request.prompt}
Target Audience: {request.target_audience or 'General audience'}
Tone: {request.tone}
Include Call-to-Action: {request.include_cta}

Instructions: {type_instructions.get(request.webpage_type, '')}

Generate content as structured JSON with:
- title: Page title
- sections: Array of objects with {{"type": str, "heading": str, "content": str, "cta": optional}}
- seo: Object with {{"title": str, "description": str, "keywords": []}}
"""
        
        generated_content = await ai_service.generate_presentation(
            topic=full_prompt,
            user_id=current_user.id,
            options={"output_format": "webpage", "include_cta": request.include_cta}
        )
        
        # Parse generated content
        if isinstance(generated_content, str):
            import json
            try:
                content_dict = json.loads(generated_content)
            except:
                content_dict = {
                    "title": f"{request.webpage_type.value.title()} Page",
                    "sections": [{"type": "text", "heading": "Content", "content": generated_content}],
                    "seo": {"title": "", "description": "", "keywords": []}
                }
        else:
            content_dict = generated_content
        
        # Create webpage
        webpage = Webpage(
            user_id=current_user.id,
            title=content_dict.get("title", request.prompt[:100]),
            webpage_type=request.webpage_type,
            content=content_dict,
            description=content_dict.get("seo", {}).get("description"),
            seo_title=content_dict.get("seo", {}).get("title"),
            seo_description=content_dict.get("seo", {}).get("description"),
            seo_keywords=content_dict.get("seo", {}).get("keywords", []),
            folder_id=request.folder_id
        )
        
        db.add(webpage)
        
        # Deduct credits
        current_user.credits -= cost
        
        db.commit()
        db.refresh(webpage)
        
        return webpage
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Webpage generation failed: {str(e)}"
        )


@router.post("/", response_model=WebpageResponse, status_code=status.HTTP_201_CREATED)
async def create_webpage(
    request: CreateWebpageRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new webpage manually"""
    # Validate folder ownership if provided
    if request.folder_id:
        folder = db.query(Folder).filter(
            Folder.id == request.folder_id,
            Folder.user_id == current_user.id,
            Folder.is_deleted == False
        ).first()
        if not folder:
            raise HTTPException(status_code=404, detail="Folder not found")
    
    webpage = Webpage(
        user_id=current_user.id,
        title=request.title,
        webpage_type=request.webpage_type,
        content=request.content,
        description=request.description,
        seo_title=request.seo_title,
        seo_description=request.seo_description,
        seo_keywords=request.seo_keywords or [],
        og_image_url=request.og_image_url,
        folder_id=request.folder_id
    )
    
    db.add(webpage)
    db.commit()
    db.refresh(webpage)
    
    return webpage


@router.get("/", response_model=List[WebpageResponse])
async def list_webpages(
    webpage_type: Optional[WebpageType] = None,
    folder_id: Optional[str] = None,
    is_published: Optional[bool] = None,
    skip: int = 0,
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all webpages for current user with optional filters"""
    query = db.query(Webpage).filter(
        Webpage.user_id == current_user.id,
        Webpage.is_deleted == False
    )
    
    if webpage_type:
        query = query.filter(Webpage.webpage_type == webpage_type)
    
    if folder_id:
        query = query.filter(Webpage.folder_id == folder_id)
    
    if is_published is not None:
        query = query.filter(Webpage.is_published == is_published)
    
    webpages = query.order_by(Webpage.updated_at.desc()).offset(skip).limit(limit).all()
    return webpages


@router.get("/{webpage_id}", response_model=WebpageResponse)
async def get_webpage(
    webpage_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific webpage by ID"""
    webpage = db.query(Webpage).filter(
        Webpage.id == webpage_id,
        Webpage.user_id == current_user.id,
        Webpage.is_deleted == False
    ).first()
    
    if not webpage:
        raise HTTPException(status_code=404, detail="Webpage not found")
    
    return webpage


@router.patch("/{webpage_id}", response_model=WebpageResponse)
async def update_webpage(
    webpage_id: str,
    request: UpdateWebpageRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update an existing webpage"""
    webpage = db.query(Webpage).filter(
        Webpage.id == webpage_id,
        Webpage.user_id == current_user.id,
        Webpage.is_deleted == False
    ).first()
    
    if not webpage:
        raise HTTPException(status_code=404, detail="Webpage not found")
    
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
    if request.title is not None:
        webpage.title = request.title
    if request.content is not None:
        webpage.content = request.content
    if request.description is not None:
        webpage.description = request.description
    if request.seo_title is not None:
        webpage.seo_title = request.seo_title
    if request.seo_description is not None:
        webpage.seo_description = request.seo_description
    if request.seo_keywords is not None:
        webpage.seo_keywords = request.seo_keywords
    if request.og_image_url is not None:
        webpage.og_image_url = request.og_image_url
    if request.folder_id is not None:
        webpage.folder_id = request.folder_id
    
    webpage.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(webpage)
    
    return webpage


@router.delete("/{webpage_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_webpage(
    webpage_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Soft delete a webpage"""
    webpage = db.query(Webpage).filter(
        Webpage.id == webpage_id,
        Webpage.user_id == current_user.id,
        Webpage.is_deleted == False
    ).first()
    
    if not webpage:
        raise HTTPException(status_code=404, detail="Webpage not found")
    
    webpage.is_deleted = True
    webpage.deleted_at = datetime.utcnow()
    
    db.commit()
    
    return None


@router.post("/{webpage_id}/publish", response_model=WebpageResponse)
async def publish_webpage(
    webpage_id: str,
    request: PublishWebpageRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Publish webpage to public URL.
    Free: Random subdomain
    Pro: Custom subdomain
    Ultra: Custom domain support
    """
    webpage = db.query(Webpage).filter(
        Webpage.id == webpage_id,
        Webpage.user_id == current_user.id,
        Webpage.is_deleted == False
    ).first()
    
    if not webpage:
        raise HTTPException(status_code=404, detail="Webpage not found")
    
    # Handle custom domain (Ultra only)
    if request.custom_domain_id:
        if current_user.plan != "ultra":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Custom domains require Ultra plan"
            )
        
        domain = db.query(CustomDomain).filter(
            CustomDomain.id == request.custom_domain_id,
            CustomDomain.user_id == current_user.id,
            CustomDomain.status == DomainStatus.VERIFIED
        ).first()
        
        if not domain:
            raise HTTPException(status_code=404, detail="Verified custom domain not found")
        
        webpage.custom_domain_id = request.custom_domain_id
        webpage.public_url = f"https://{domain.domain}"
        webpage.subdomain = None
    
    # Handle custom subdomain (Pro/Ultra)
    elif request.subdomain:
        if current_user.plan not in ["pro", "ultra"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Custom subdomains require Pro or Ultra plan"
            )
        
        # Check subdomain availability
        existing = db.query(Webpage).filter(
            Webpage.subdomain == request.subdomain,
            Webpage.id != webpage_id,
            Webpage.is_deleted == False
        ).first()
        
        if existing:
            raise HTTPException(status_code=409, detail="Subdomain already taken")
        
        webpage.subdomain = request.subdomain
        webpage.public_url = f"https://{request.subdomain}.gamma.app"
        webpage.custom_domain_id = None
    
    # Default: Random subdomain (all plans)
    else:
        if not webpage.subdomain:
            import secrets
            webpage.subdomain = f"web-{secrets.token_urlsafe(8)}"
        webpage.public_url = f"https://{webpage.subdomain}.gamma.app"
        webpage.custom_domain_id = None
    
    webpage.is_published = True
    webpage.published_at = datetime.utcnow()
    
    db.commit()
    db.refresh(webpage)
    
    return webpage


@router.post("/{webpage_id}/unpublish", response_model=WebpageResponse)
async def unpublish_webpage(
    webpage_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Unpublish webpage (remove from public access)"""
    webpage = db.query(Webpage).filter(
        Webpage.id == webpage_id,
        Webpage.user_id == current_user.id,
        Webpage.is_deleted == False
    ).first()
    
    if not webpage:
        raise HTTPException(status_code=404, detail="Webpage not found")
    
    webpage.is_published = False
    webpage.public_url = None
    
    db.commit()
    db.refresh(webpage)
    
    return webpage


@router.post("/{webpage_id}/duplicate", response_model=WebpageResponse, status_code=status.HTTP_201_CREATED)
async def duplicate_webpage(
    webpage_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a duplicate copy of an existing webpage"""
    original = db.query(Webpage).filter(
        Webpage.id == webpage_id,
        Webpage.user_id == current_user.id,
        Webpage.is_deleted == False
    ).first()
    
    if not original:
        raise HTTPException(status_code=404, detail="Webpage not found")
    
    # Create duplicate
    duplicate = Webpage(
        user_id=current_user.id,
        title=f"{original.title} (Copy)",
        webpage_type=original.webpage_type,
        content=original.content.copy(),
        description=original.description,
        seo_title=original.seo_title,
        seo_description=original.seo_description,
        seo_keywords=original.seo_keywords.copy() if original.seo_keywords else [],
        og_image_url=original.og_image_url,
        folder_id=original.folder_id
    )
    
    db.add(duplicate)
    db.commit()
    db.refresh(duplicate)
    
    return duplicate
