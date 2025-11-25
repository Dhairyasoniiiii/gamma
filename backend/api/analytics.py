"""
Analytics API Endpoints
Provides analytics and statistics for presentations, users, and workspaces
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional

from backend.db.base import get_db
from backend.models.user import User
from backend.models.presentation import Presentation
from backend.utils.auth import get_current_user
from backend.services.analytics_service import analytics_service

router = APIRouter(prefix="/api/v1/analytics", tags=["Analytics"])


# Get Presentation Analytics
@router.get("/presentation/{presentation_id}")
async def get_presentation_analytics(
    presentation_id: int,
    days: int = Query(30, ge=1, le=365),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get detailed analytics for a presentation
    
    - **days**: Number of days to analyze (1-365)
    """
    # Check if presentation exists and user has access
    presentation = db.query(Presentation).filter(
        Presentation.id == presentation_id
    ).first()
    
    if not presentation:
        raise HTTPException(status_code=404, detail="Presentation not found")
    
    # Check access
    if presentation.user_id != current_user.id and not presentation.is_public:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Get analytics
    analytics = analytics_service.get_presentation_analytics(
        presentation_id, days, db
    )
    
    if not analytics:
        raise HTTPException(status_code=404, detail="Analytics not found")
    
    return analytics


# Get User Analytics
@router.get("/user/dashboard")
async def get_user_dashboard(
    days: int = Query(30, ge=1, le=365),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get analytics dashboard for current user
    """
    analytics = analytics_service.get_user_analytics(
        current_user.id, days, db
    )
    
    if not analytics:
        raise HTTPException(status_code=404, detail="Analytics not found")
    
    return analytics


# Get Quick Dashboard Stats
@router.get("/dashboard/quick")
async def get_quick_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get quick stats for dashboard overview
    """
    stats = analytics_service.get_dashboard_stats(current_user.id, db)
    
    if not stats:
        raise HTTPException(status_code=404, detail="Stats not found")
    
    return stats


# Get Workspace Analytics (Team plans only)
@router.get("/workspace/{workspace_id}")
async def get_workspace_analytics(
    workspace_id: int,
    days: int = Query(30, ge=1, le=365),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get analytics for a team workspace (Team/Business plans only)
    """
    # Check if user has access to workspace features
    if current_user.plan not in ["team", "business"]:
        raise HTTPException(
            status_code=403,
            detail="Workspace analytics require Team or Business plan"
        )
    
    analytics = analytics_service.get_workspace_analytics(
        workspace_id, days, db
    )
    
    return analytics


# Track Event
@router.post("/track")
async def track_event(
    event_type: str,
    presentation_id: Optional[int] = None,
    metadata: Optional[dict] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Track an analytics event
    
    Event types:
    - view: Presentation viewed
    - edit: Presentation edited
    - share: Presentation shared
    - export: Presentation exported
    - comment: Comment added
    - like: Presentation liked
    """
    event = await analytics_service.track_event(
        event_type=event_type,
        presentation_id=presentation_id,
        user_id=current_user.id,
        metadata=metadata,
        db=db
    )
    
    return {"status": "tracked", "event": event}


# Get Views Trend
@router.get("/presentation/{presentation_id}/trend")
async def get_views_trend(
    presentation_id: int,
    days: int = Query(30, ge=1, le=365),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get views trend for a presentation
    """
    # Check access
    presentation = db.query(Presentation).filter(
        Presentation.id == presentation_id,
        Presentation.user_id == current_user.id
    ).first()
    
    if not presentation:
        raise HTTPException(
            status_code=404,
            detail="Presentation not found"
        )
    
    analytics = analytics_service.get_presentation_analytics(
        presentation_id, days, db
    )
    
    return {
        "presentation_id": presentation_id,
        "period": f"Last {days} days",
        "trend": analytics.get("views_by_day", [])
    }


# Get Engagement Metrics
@router.get("/presentation/{presentation_id}/engagement")
async def get_engagement_metrics(
    presentation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get engagement metrics for a presentation
    """
    presentation = db.query(Presentation).filter(
        Presentation.id == presentation_id,
        Presentation.user_id == current_user.id
    ).first()
    
    if not presentation:
        raise HTTPException(status_code=404, detail="Presentation not found")
    
    # Mock engagement data
    return {
        "presentation_id": presentation_id,
        "metrics": {
            "avg_time_spent": "2m 34s",
            "completion_rate": 0.75,
            "bounce_rate": 0.15,
            "engagement_score": 8.5,
            "shares": 12,
            "comments": 5,
            "likes": 28
        }
    }


# Get Comparison Analytics (Pro+ only)
@router.get("/compare")
async def compare_presentations(
    presentation_ids: str = Query(..., description="Comma-separated presentation IDs"),
    days: int = Query(30, ge=1, le=365),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Compare analytics for multiple presentations (Pro plan or higher)
    """
    # Check plan
    if current_user.plan not in ["pro", "ultra", "team", "business"]:
        raise HTTPException(
            status_code=403,
            detail="Comparison analytics require Pro plan or higher"
        )
    
    # Parse IDs
    try:
        ids = [int(id.strip()) for id in presentation_ids.split(",")]
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid presentation IDs")
    
    if len(ids) > 5:
        raise HTTPException(
            status_code=400,
            detail="Maximum 5 presentations can be compared"
        )
    
    # Get analytics for each
    comparisons = []
    for pres_id in ids:
        presentation = db.query(Presentation).filter(
            Presentation.id == pres_id,
            Presentation.user_id == current_user.id
        ).first()
        
        if presentation:
            analytics = analytics_service.get_presentation_analytics(
                pres_id, days, db
            )
            comparisons.append({
                "id": pres_id,
                "title": presentation.title,
                "views": analytics["metrics"]["total_views"],
                "unique_visitors": analytics["metrics"]["unique_visitors"],
                "engagement_score": analytics["metrics"]["engagement_score"]
            })
    
    return {
        "period": f"Last {days} days",
        "presentations": comparisons
    }
