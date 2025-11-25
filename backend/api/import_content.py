"""
Import Content API endpoints for Gamma Clone
Handles importing content from PDF, PowerPoint, URLs, and Zoom transcripts
"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import Optional
from pydantic import BaseModel, HttpUrl

from backend.db.base import get_db
from backend.models.user import User
from backend.models.presentation import Presentation
from backend.models.document import Document, DocumentType
from backend.utils.auth import get_current_user
from backend.services.import_service import ImportService

router = APIRouter(prefix="/api/v1/import", tags=["Import"])


# Request/Response Models
class ImportURLRequest(BaseModel):
    url: HttpUrl
    import_as: str = "presentation"  # presentation or document
    folder_id: Optional[str] = None


class ImportZoomRequest(BaseModel):
    transcript_text: str
    meeting_title: Optional[str] = None
    folder_id: Optional[str] = None


class ImportResponse(BaseModel):
    success: bool
    message: str
    item_id: Optional[str] = None
    item_type: str
    title: str
    slides_count: Optional[int] = None
    word_count: Optional[int] = None


@router.post("/pdf", response_model=ImportResponse)
async def import_from_pdf(
    file: UploadFile = File(...),
    import_as: str = "document",
    folder_id: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Import content from PDF file.
    Can import as document (default) or presentation.
    Cost: 8 credits
    """
    cost = 8
    
    if current_user.credits < cost:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail=f"Insufficient credits. Need {cost}, have {current_user.credits}"
        )
    
    # Validate file type
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be a PDF"
        )
    
    # Validate import type
    if import_as not in ["document", "presentation"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="import_as must be 'document' or 'presentation'"
        )
    
    try:
        # Read file content
        content = await file.read()
        
        # Import using service
        import_service = ImportService()
        result = await import_service.import_from_pdf(
            pdf_content=content,
            filename=file.filename,
            user_id=current_user.id,
            import_as=import_as,
            folder_id=folder_id,
            db=db
        )
        
        # Deduct credits
        current_user.credits -= cost
        db.commit()
        
        return ImportResponse(
            success=True,
            message=f"Successfully imported PDF as {import_as}",
            item_id=result["item_id"],
            item_type=import_as,
            title=result["title"],
            slides_count=result.get("slides_count"),
            word_count=result.get("word_count")
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"PDF import failed: {str(e)}"
        )


@router.post("/pptx", response_model=ImportResponse)
async def import_from_pptx(
    file: UploadFile = File(...),
    folder_id: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Import presentation from PowerPoint file (.pptx).
    Always imports as presentation.
    Cost: 10 credits
    """
    cost = 10
    
    if current_user.credits < cost:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail=f"Insufficient credits. Need {cost}, have {current_user.credits}"
        )
    
    # Validate file type
    if not file.filename.lower().endswith('.pptx'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be a PowerPoint file (.pptx)"
        )
    
    try:
        # Read file content
        content = await file.read()
        
        # Import using service
        import_service = ImportService()
        result = await import_service.import_from_pptx(
            pptx_content=content,
            filename=file.filename,
            user_id=current_user.id,
            folder_id=folder_id,
            db=db
        )
        
        # Deduct credits
        current_user.credits -= cost
        db.commit()
        
        return ImportResponse(
            success=True,
            message="Successfully imported PowerPoint presentation",
            item_id=result["item_id"],
            item_type="presentation",
            title=result["title"],
            slides_count=result.get("slides_count")
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"PowerPoint import failed: {str(e)}"
        )


@router.post("/url", response_model=ImportResponse)
async def import_from_url(
    request: ImportURLRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Import content from any URL by scraping webpage content.
    Can import as presentation or document.
    Cost: 6 credits
    """
    cost = 6
    
    if current_user.credits < cost:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail=f"Insufficient credits. Need {cost}, have {current_user.credits}"
        )
    
    # Validate import type
    if request.import_as not in ["document", "presentation"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="import_as must be 'document' or 'presentation'"
        )
    
    try:
        # Import using service
        import_service = ImportService()
        result = await import_service.import_from_url(
            url=str(request.url),
            user_id=current_user.id,
            import_as=request.import_as,
            folder_id=request.folder_id,
            db=db
        )
        
        # Deduct credits
        current_user.credits -= cost
        db.commit()
        
        return ImportResponse(
            success=True,
            message=f"Successfully imported content from URL as {request.import_as}",
            item_id=result["item_id"],
            item_type=request.import_as,
            title=result["title"],
            slides_count=result.get("slides_count"),
            word_count=result.get("word_count")
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"URL import failed: {str(e)}"
        )


@router.post("/zoom-transcript", response_model=ImportResponse)
async def import_zoom_transcript(
    request: ImportZoomRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Import Zoom meeting transcript and convert to presentation or document.
    Extracts key points, action items, and decisions.
    Cost: 7 credits
    """
    cost = 7
    
    if current_user.credits < cost:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail=f"Insufficient credits. Need {cost}, have {current_user.credits}"
        )
    
    try:
        # Import using service
        import_service = ImportService()
        result = await import_service.import_from_zoom_transcript(
            transcript_text=request.transcript_text,
            meeting_title=request.meeting_title,
            user_id=current_user.id,
            folder_id=request.folder_id,
            db=db
        )
        
        # Deduct credits
        current_user.credits -= cost
        db.commit()
        
        return ImportResponse(
            success=True,
            message="Successfully imported Zoom transcript as document",
            item_id=result["item_id"],
            item_type="document",
            title=result["title"],
            word_count=result.get("word_count")
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Zoom transcript import failed: {str(e)}"
        )


@router.get("/supported-formats")
async def get_supported_formats():
    """Get list of supported import formats and their details"""
    return {
        "formats": [
            {
                "type": "pdf",
                "extensions": [".pdf"],
                "import_as": ["document", "presentation"],
                "credit_cost": 8,
                "max_file_size_mb": 50,
                "description": "Import content from PDF files"
            },
            {
                "type": "pptx",
                "extensions": [".pptx"],
                "import_as": ["presentation"],
                "credit_cost": 10,
                "max_file_size_mb": 100,
                "description": "Import PowerPoint presentations"
            },
            {
                "type": "url",
                "extensions": [],
                "import_as": ["document", "presentation"],
                "credit_cost": 6,
                "max_file_size_mb": None,
                "description": "Import content from any webpage URL"
            },
            {
                "type": "zoom_transcript",
                "extensions": [".txt", ".vtt"],
                "import_as": ["document"],
                "credit_cost": 7,
                "max_file_size_mb": 10,
                "description": "Import Zoom meeting transcripts"
            }
        ],
        "notes": [
            "All imports require sufficient credits",
            "File size limits are enforced to prevent abuse",
            "Imported content can be edited after import",
            "PDF and URL imports support both document and presentation output"
        ]
    }
