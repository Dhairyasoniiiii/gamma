"""
Documents API endpoints for Gamma Clone
Handles long-form content: reports, articles, proposals, whitepapers, blog posts, memos, case studies
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel

from backend.db.base import get_db
from backend.models.user import User
from backend.models.document import Document, DocumentType
from backend.models.folder import Folder
from backend.utils.auth import get_current_user
from backend.services.ai_service import AIService
from backend.config import settings

router = APIRouter(prefix="/api/v1/documents", tags=["Documents"])


# Request/Response Models
class GenerateDocumentRequest(BaseModel):
    prompt: str
    document_type: DocumentType
    target_audience: Optional[str] = None
    tone: Optional[str] = "professional"
    length: Optional[str] = "medium"  # short, medium, long
    folder_id: Optional[str] = None


class CreateDocumentRequest(BaseModel):
    title: str
    document_type: DocumentType
    content: dict
    description: Optional[str] = None
    tags: Optional[List[str]] = []
    folder_id: Optional[str] = None


class UpdateDocumentRequest(BaseModel):
    title: Optional[str] = None
    content: Optional[dict] = None
    description: Optional[str] = None
    tags: Optional[List[str]] = None
    folder_id: Optional[str] = None


class DocumentResponse(BaseModel):
    id: str
    title: str
    document_type: str
    content: dict
    description: Optional[str]
    tags: List[str]
    word_count: int
    reading_time_minutes: int
    is_published: bool
    published_url: Optional[str]
    folder_id: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


@router.post("/generate", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def generate_document(
    request: GenerateDocumentRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    AI-generate a document based on prompt and type.
    Cost: 15 credits for long documents, 10 for medium, 5 for short
    """
    # Calculate credit cost based on length
    credit_costs = {"short": 5, "medium": 10, "long": 15}
    cost = credit_costs.get(request.length, 10)
    
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
        # Generate document with AI
        ai_service = AIService()
        
        # Build generation prompt based on document type
        type_instructions = {
            DocumentType.REPORT: "Create a professional report with executive summary, findings, analysis, and recommendations.",
            DocumentType.ARTICLE: "Write an engaging article with introduction, body paragraphs, and conclusion.",
            DocumentType.PROPOSAL: "Draft a business proposal with problem statement, solution, benefits, timeline, and budget.",
            DocumentType.WHITEPAPER: "Compose an authoritative whitepaper with research, data, and expert analysis.",
            DocumentType.BLOG: "Write a conversational blog post with personality and reader engagement.",
            DocumentType.MEMO: "Create a concise memo with clear action items and key points.",
            DocumentType.CASE_STUDY: "Document a case study with background, challenges, solution, and results."
        }
        
        full_prompt = f"""Create a {request.document_type.value} document.

Topic: {request.prompt}
Target Audience: {request.target_audience or 'General professional audience'}
Tone: {request.tone}
Length: {request.length} (short=500 words, medium=1500 words, long=3000+ words)

Instructions: {type_instructions.get(request.document_type, '')}

Generate content as structured JSON with these sections:
- title: Document title
- sections: Array of objects with {{"heading": str, "content": str}}
- metadata: Object with {{"keywords": [], "summary": str}}
"""
        
        generated_content = await ai_service.generate_presentation(
            topic=full_prompt,
            user_id=current_user.id,
            options={"output_format": "document", "length": request.length}
        )
        
        # Parse generated content
        if isinstance(generated_content, str):
            import json
            try:
                content_dict = json.loads(generated_content)
            except:
                content_dict = {
                    "title": f"{request.document_type.value.title()} Document",
                    "sections": [{"heading": "Content", "content": generated_content}],
                    "metadata": {"keywords": [], "summary": ""}
                }
        else:
            content_dict = generated_content
        
        # Calculate word count
        word_count = sum(
            len(section.get("content", "").split())
            for section in content_dict.get("sections", [])
        )
        reading_time = max(1, word_count // 200)  # Average reading speed: 200 wpm
        
        # Create document
        document = Document(
            user_id=current_user.id,
            title=content_dict.get("title", request.prompt[:100]),
            document_type=request.document_type,
            content=content_dict,
            description=content_dict.get("metadata", {}).get("summary"),
            tags=content_dict.get("metadata", {}).get("keywords", []),
            word_count=word_count,
            reading_time_minutes=reading_time,
            folder_id=request.folder_id
        )
        
        db.add(document)
        
        # Deduct credits
        current_user.credits -= cost
        
        db.commit()
        db.refresh(document)
        
        return document
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Document generation failed: {str(e)}"
        )


@router.post("/", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def create_document(
    request: CreateDocumentRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new document manually"""
    # Validate folder ownership if provided
    if request.folder_id:
        folder = db.query(Folder).filter(
            Folder.id == request.folder_id,
            Folder.user_id == current_user.id,
            Folder.is_deleted == False
        ).first()
        if not folder:
            raise HTTPException(status_code=404, detail="Folder not found")
    
    # Calculate word count
    word_count = sum(
        len(section.get("content", "").split())
        for section in request.content.get("sections", [])
    )
    reading_time = max(1, word_count // 200)
    
    document = Document(
        user_id=current_user.id,
        title=request.title,
        document_type=request.document_type,
        content=request.content,
        description=request.description,
        tags=request.tags or [],
        word_count=word_count,
        reading_time_minutes=reading_time,
        folder_id=request.folder_id
    )
    
    db.add(document)
    db.commit()
    db.refresh(document)
    
    return document


@router.get("/", response_model=List[DocumentResponse])
async def list_documents(
    document_type: Optional[DocumentType] = None,
    folder_id: Optional[str] = None,
    is_published: Optional[bool] = None,
    skip: int = 0,
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all documents for current user with optional filters"""
    query = db.query(Document).filter(
        Document.user_id == current_user.id,
        Document.is_deleted == False
    )
    
    if document_type:
        query = query.filter(Document.document_type == document_type)
    
    if folder_id:
        query = query.filter(Document.folder_id == folder_id)
    
    if is_published is not None:
        query = query.filter(Document.is_published == is_published)
    
    documents = query.order_by(Document.updated_at.desc()).offset(skip).limit(limit).all()
    return documents


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific document by ID"""
    document = db.query(Document).filter(
        Document.id == document_id,
        Document.user_id == current_user.id,
        Document.is_deleted == False
    ).first()
    
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    return document


@router.patch("/{document_id}", response_model=DocumentResponse)
async def update_document(
    document_id: str,
    request: UpdateDocumentRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update an existing document"""
    document = db.query(Document).filter(
        Document.id == document_id,
        Document.user_id == current_user.id,
        Document.is_deleted == False
    ).first()
    
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
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
        document.title = request.title
    if request.content is not None:
        document.content = request.content
        # Recalculate word count
        document.word_count = sum(
            len(section.get("content", "").split())
            for section in request.content.get("sections", [])
        )
        document.reading_time_minutes = max(1, document.word_count // 200)
    if request.description is not None:
        document.description = request.description
    if request.tags is not None:
        document.tags = request.tags
    if request.folder_id is not None:
        document.folder_id = request.folder_id
    
    document.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(document)
    
    return document


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    document_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Soft delete a document"""
    document = db.query(Document).filter(
        Document.id == document_id,
        Document.user_id == current_user.id,
        Document.is_deleted == False
    ).first()
    
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    document.is_deleted = True
    document.deleted_at = datetime.utcnow()
    
    db.commit()
    
    return None


@router.post("/{document_id}/publish", response_model=DocumentResponse)
async def publish_document(
    document_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Publish document to public URL (Pro/Ultra only)"""
    # Check plan permissions
    if current_user.plan not in ["pro", "ultra"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Document publishing requires Pro or Ultra plan"
        )
    
    document = db.query(Document).filter(
        Document.id == document_id,
        Document.user_id == current_user.id,
        Document.is_deleted == False
    ).first()
    
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Generate public URL
    import secrets
    slug = f"{document.title.lower().replace(' ', '-')[:50]}-{secrets.token_urlsafe(8)}"
    document.published_url = f"https://gamma.app/docs/{slug}"
    document.is_published = True
    document.published_at = datetime.utcnow()
    
    db.commit()
    db.refresh(document)
    
    return document


@router.post("/{document_id}/unpublish", response_model=DocumentResponse)
async def unpublish_document(
    document_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Unpublish document (remove from public access)"""
    document = db.query(Document).filter(
        Document.id == document_id,
        Document.user_id == current_user.id,
        Document.is_deleted == False
    ).first()
    
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    document.is_published = False
    document.published_url = None
    
    db.commit()
    db.refresh(document)
    
    return document


@router.post("/{document_id}/duplicate", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def duplicate_document(
    document_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a duplicate copy of an existing document"""
    original = db.query(Document).filter(
        Document.id == document_id,
        Document.user_id == current_user.id,
        Document.is_deleted == False
    ).first()
    
    if not original:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Create duplicate
    duplicate = Document(
        user_id=current_user.id,
        title=f"{original.title} (Copy)",
        document_type=original.document_type,
        content=original.content.copy(),
        description=original.description,
        tags=original.tags.copy() if original.tags else [],
        word_count=original.word_count,
        reading_time_minutes=original.reading_time_minutes,
        folder_id=original.folder_id
    )
    
    db.add(duplicate)
    db.commit()
    db.refresh(duplicate)
    
    return duplicate
