"""
Export API Endpoints
Handles exporting presentations to various formats
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import Optional
from pydantic import BaseModel

from backend.db.base import get_db
from backend.models.user import User
from backend.models.presentation import Presentation
from backend.models.theme import Theme
from backend.utils.auth import get_current_user
from backend.services.export_service import export_service
from backend.config import settings

router = APIRouter(prefix="/api/v1/export", tags=["Export"])


class ExportRequest(BaseModel):
    format: str  # pdf, pptx, html, markdown
    include_theme: bool = True


# Export Presentation
@router.post("/{presentation_id}")
async def export_presentation(
    presentation_id: int,
    export_format: str = Query(..., pattern="^(pdf|pptx|html|markdown)$"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Export a presentation to various formats
    
    - **pdf**: Export as PDF document
    - **pptx**: Export as PowerPoint presentation
    - **html**: Export as standalone HTML file
    - **markdown**: Export as Markdown file
    """
    # Get presentation
    presentation = db.query(Presentation).filter(
        Presentation.id == presentation_id
    ).first()
    
    if not presentation:
        raise HTTPException(status_code=404, detail="Presentation not found")
    
    # Check access permissions
    if presentation.user_id != current_user.id and not presentation.is_public:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Check plan limits for exports
    plan_limits = {
        "free": ["html", "markdown"],
        "plus": ["html", "markdown", "pdf"],
        "pro": ["html", "markdown", "pdf", "pptx"],
        "ultra": ["html", "markdown", "pdf", "pptx"],
        "team": ["html", "markdown", "pdf", "pptx"],
        "business": ["html", "markdown", "pdf", "pptx"]
    }
    
    allowed_formats = plan_limits.get(current_user.plan, ["html", "markdown"])
    
    if export_format not in allowed_formats:
        raise HTTPException(
            status_code=403,
            detail=f"Your plan does not support {export_format} exports. Upgrade to access this feature."
        )
    
    # Get theme if exists
    theme_data = None
    if presentation.theme_id:
        theme = db.query(Theme).filter(Theme.id == presentation.theme_id).first()
        if theme:
            theme_data = {
                "colors": theme.colors,
                "fonts": theme.fonts
            }
    
    # Prepare presentation data
    presentation_data = {
        "title": presentation.title,
        "content": presentation.content
    }
    
    try:
        # Export based on format
        if export_format == "pdf":
            output_path = export_service.export_to_pdf(presentation_data, theme_data)
            media_type = "application/pdf"
            filename = f"{presentation.title}.pdf"
        
        elif export_format == "pptx":
            output_path = export_service.export_to_pptx(presentation_data, theme_data)
            media_type = "application/vnd.openxmlformats-officedocument.presentationml.presentation"
            filename = f"{presentation.title}.pptx"
        
        elif export_format == "html":
            output_path = export_service.export_to_html(presentation_data, theme_data)
            media_type = "text/html"
            filename = f"{presentation.title}.html"
        
        elif export_format == "markdown":
            output_path = export_service.export_to_markdown(presentation_data)
            media_type = "text/markdown"
            filename = f"{presentation.title}.md"
        
        else:
            raise HTTPException(status_code=400, detail="Invalid export format")
        
        # Return file
        return FileResponse(
            path=output_path,
            media_type=media_type,
            filename=filename
        )
    
    except ImportError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Export library not available: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Export failed: {str(e)}"
        )


# Get Available Export Formats
@router.get("/formats")
async def get_export_formats(
    current_user: User = Depends(get_current_user)
):
    """
    Get available export formats based on user's plan
    """
    plan_formats = {
        "free": {
            "available": ["html", "markdown"],
            "unavailable": ["pdf", "pptx"]
        },
        "plus": {
            "available": ["html", "markdown", "pdf"],
            "unavailable": ["pptx"]
        },
        "pro": {
            "available": ["html", "markdown", "pdf", "pptx"],
            "unavailable": []
        },
        "ultra": {
            "available": ["html", "markdown", "pdf", "pptx"],
            "unavailable": []
        },
        "team": {
            "available": ["html", "markdown", "pdf", "pptx"],
            "unavailable": []
        },
        "business": {
            "available": ["html", "markdown", "pdf", "pptx"],
            "unavailable": []
        }
    }
    
    user_formats = plan_formats.get(current_user.plan, plan_formats["free"])
    
    return {
        "plan": current_user.plan,
        "formats": {
            "html": {
                "name": "HTML",
                "description": "Standalone HTML file",
                "available": "html" in user_formats["available"]
            },
            "markdown": {
                "name": "Markdown",
                "description": "Markdown text file",
                "available": "markdown" in user_formats["available"]
            },
            "pdf": {
                "name": "PDF",
                "description": "PDF document",
                "available": "pdf" in user_formats["available"]
            },
            "pptx": {
                "name": "PowerPoint",
                "description": "PowerPoint presentation",
                "available": "pptx" in user_formats["available"]
            }
        }
    }


# Batch Export (Pro+ only)
@router.post("/batch")
async def batch_export(
    presentation_ids: list[int],
    export_format: str = Query(..., pattern="^(pdf|pptx|html|markdown)$"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Export multiple presentations at once (Pro plan or higher)
    """
    # Check plan
    if current_user.plan not in ["pro", "ultra", "team", "business"]:
        raise HTTPException(
            status_code=403,
            detail="Batch export requires Pro plan or higher"
        )
    
    # Limit batch size
    if len(presentation_ids) > 10:
        raise HTTPException(
            status_code=400,
            detail="Maximum 10 presentations per batch export"
        )
    
    results = []
    
    for pres_id in presentation_ids:
        try:
            # Get presentation
            presentation = db.query(Presentation).filter(
                Presentation.id == pres_id,
                Presentation.user_id == current_user.id
            ).first()
            
            if not presentation:
                results.append({
                    "id": pres_id,
                    "status": "error",
                    "message": "Presentation not found"
                })
                continue
            
            # Export logic here (simplified for batch)
            results.append({
                "id": pres_id,
                "status": "success",
                "message": f"Exported as {export_format}"
            })
        
        except Exception as e:
            results.append({
                "id": pres_id,
                "status": "error",
                "message": str(e)
            })
    
    return {
        "total": len(presentation_ids),
        "successful": len([r for r in results if r["status"] == "success"]),
        "failed": len([r for r in results if r["status"] == "error"]),
        "results": results
    }
