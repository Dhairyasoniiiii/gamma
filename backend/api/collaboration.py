"""
Collaboration API Endpoints
Handles sharing, permissions, comments, and version history
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel

from backend.db.base import get_db
from backend.models.user import User
from backend.models.presentation import Presentation
from backend.models.comment import Comment, SharedPresentation
from backend.utils.auth import get_current_user
import uuid

router = APIRouter(prefix="/api/v1/collaboration", tags=["Collaboration"])


# Pydantic Schemas
class ShareRequest(BaseModel):
    email: str
    permission: str  # view, comment, edit
    message: Optional[str] = None


class CommentCreate(BaseModel):
    card_id: str
    content: str
    position: Optional[dict] = None


class SuggestionCreate(BaseModel):
    card_id: str
    type: str  # text, layout, design
    content: str
    suggested_value: Optional[dict] = None


# Share Presentation
@router.post("/{presentation_id}/share")
async def share_presentation(
    presentation_id: int,
    share_data: ShareRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Share a presentation with another user
    
    Permissions:
    - view: Can only view the presentation
    - comment: Can view and add comments
    - edit: Can view, comment, and edit
    """
    # Check if presentation exists and user owns it
    presentation = db.query(Presentation).filter(
        Presentation.id == presentation_id,
        Presentation.user_id == current_user.id
    ).first()
    
    if not presentation:
        raise HTTPException(
            status_code=404,
            detail="Presentation not found or you don't have permission"
        )
    
    # Validate permission level
    if share_data.permission not in ["view", "comment", "edit"]:
        raise HTTPException(status_code=400, detail="Invalid permission level")
    
    # Check plan limits
    plan_limits = {
        "free": {"max_collaborators": 0},
        "plus": {"max_collaborators": 5},
        "pro": {"max_collaborators": 20},
        "ultra": {"max_collaborators": 100},
        "team": {"max_collaborators": -1},  # Unlimited
        "business": {"max_collaborators": -1}
    }
    
    max_collab = plan_limits.get(current_user.plan, {}).get("max_collaborators", 0)
    
    if max_collab == 0:
        raise HTTPException(
            status_code=403,
            detail="Collaboration requires Plus plan or higher"
        )
    
    # Find user by email
    shared_user = db.query(User).filter(User.email == share_data.email).first()
    if not shared_user:
        raise HTTPException(
            status_code=404,
            detail=f"User with email {share_data.email} not found"
        )
    
    # Check if already shared
    existing_share = db.query(SharedPresentation).filter(
        SharedPresentation.presentation_id == presentation_id,
        SharedPresentation.shared_with_id == shared_user.id
    ).first()
    
    if existing_share:
        # Update existing share
        existing_share.permission = share_data.permission
        db.commit()
        db.refresh(existing_share)
        
        return {
            "status": "updated",
            "presentation_id": presentation_id,
            "shared_with": share_data.email,
            "permission": share_data.permission
        }
    
    # Create new share
    new_share = SharedPresentation(
        id=uuid.uuid4(),
        presentation_id=presentation_id,
        owner_id=current_user.id,
        shared_with_id=shared_user.id,
        permission=share_data.permission
    )
    db.add(new_share)
    db.commit()
    db.refresh(new_share)
    
    return {
        "status": "shared",
        "share_id": str(new_share.id),
        "presentation_id": presentation_id,
        "shared_with": share_data.email,
        "permission": share_data.permission,
        "share_link": f"https://gamma.app/share/{presentation_id}"
    }


# Get Share Settings
@router.get("/{presentation_id}/shares")
async def get_shares(
    presentation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all shares for a presentation
    """
    presentation = db.query(Presentation).filter(
        Presentation.id == presentation_id,
        Presentation.user_id == current_user.id
    ).first()
    
    if not presentation:
        raise HTTPException(status_code=404, detail="Presentation not found")
    
    # Get all shares for this presentation
    shares = db.query(SharedPresentation).filter(
        SharedPresentation.presentation_id == presentation_id
    ).all()
    
    # Build collaborators list with user details
    collaborators = []
    for share in shares:
        shared_user = db.query(User).filter(User.id == share.shared_with_id).first()
        if shared_user:
            collaborators.append({
                "share_id": str(share.id),
                "user_id": str(shared_user.id),
                "email": shared_user.email,
                "name": shared_user.name or shared_user.email,
                "permission": share.permission,
                "shared_at": share.created_at.isoformat() if share.created_at else None
            })
    
    return {
        "presentation_id": presentation_id,
        "is_public": presentation.is_public,
        "public_link": f"https://gamma.app/public/{presentation_id}" if presentation.is_public else None,
        "collaborators": collaborators
    }


# Update Share Permission
@router.patch("/{presentation_id}/shares/{share_id}")
async def update_share_permission(
    presentation_id: int,
    share_id: int,
    permission: str = Query(..., pattern="^(view|comment|edit)$"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update permission level for a share
    """
    presentation = db.query(Presentation).filter(
        Presentation.id == presentation_id,
        Presentation.user_id == current_user.id
    ).first()
    
    if not presentation:
        raise HTTPException(status_code=404, detail="Presentation not found")
    
    # Find and update share
    share = db.query(SharedPresentation).filter(
        SharedPresentation.id == share_id,
        SharedPresentation.presentation_id == presentation_id,
        SharedPresentation.owner_id == current_user.id
    ).first()
    
    if not share:
        raise HTTPException(status_code=404, detail="Share not found")
    
    share.permission = permission
    db.commit()
    db.refresh(share)
    
    return {
        "status": "updated",
        "share_id": str(share.id),
        "new_permission": permission
    }


# Revoke Access
@router.delete("/{presentation_id}/shares/{share_id}")
async def revoke_access(
    presentation_id: int,
    share_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Revoke access to a presentation
    """
    presentation = db.query(Presentation).filter(
        Presentation.id == presentation_id,
        Presentation.user_id == current_user.id
    ).first()
    
    if not presentation:
        raise HTTPException(status_code=404, detail="Presentation not found")
    
    # Find and delete share
    share = db.query(SharedPresentation).filter(
        SharedPresentation.id == share_id,
        SharedPresentation.presentation_id == presentation_id,
        SharedPresentation.owner_id == current_user.id
    ).first()
    
    if not share:
        raise HTTPException(status_code=404, detail="Share not found")
    
    db.delete(share)
    db.commit()
    
    return {"status": "revoked", "share_id": str(share_id)}


# Add Comment
@router.post("/{presentation_id}/comments")
async def add_comment(
    presentation_id: int,
    comment_data: CommentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Add a comment to a presentation card
    """
    # Check access
    presentation = db.query(Presentation).filter(
        Presentation.id == presentation_id
    ).first()
    
    if not presentation:
        raise HTTPException(status_code=404, detail="Presentation not found")
    
    # Check if user has access (owner or shared with comment/edit permission)
    if presentation.user_id != current_user.id and not presentation.is_public:
        # Check if user has share access
        share = db.query(SharedPresentation).filter(
            SharedPresentation.presentation_id == presentation_id,
            SharedPresentation.shared_with_id == current_user.id,
            SharedPresentation.permission.in_(["comment", "edit"])
        ).first()
        
        if not share:
            raise HTTPException(status_code=403, detail="Access denied")
    
    # Create comment
    new_comment = Comment(
        id=uuid.uuid4(),
        presentation_id=presentation_id,
        card_id=comment_data.card_id,
        user_id=current_user.id,
        text=comment_data.content
    )
    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)
    
    return {
        "id": str(new_comment.id),
        "presentation_id": str(presentation_id),
        "card_id": comment_data.card_id,
        "user_id": str(current_user.id),
        "user_name": current_user.name or current_user.email,
        "content": comment_data.content,
        "position": comment_data.position,
        "created_at": new_comment.created_at.isoformat() if new_comment.created_at else None,
        "resolved": False
    }


# Get Comments
@router.get("/{presentation_id}/comments")
async def get_comments(
    presentation_id: int,
    card_id: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get comments for a presentation or specific card
    """
    presentation = db.query(Presentation).filter(
        Presentation.id == presentation_id
    ).first()
    
    if not presentation:
        raise HTTPException(status_code=404, detail="Presentation not found")
    
    # Check access
    if presentation.user_id != current_user.id and not presentation.is_public:
        # Check if user has share access
        share = db.query(SharedPresentation).filter(
            SharedPresentation.presentation_id == presentation_id,
            SharedPresentation.shared_with_id == current_user.id
        ).first()
        
        if not share:
            raise HTTPException(status_code=403, detail="Access denied")
    
    # Query comments
    query = db.query(Comment).filter(Comment.presentation_id == presentation_id)
    if card_id:
        query = query.filter(Comment.card_id == card_id)
    
    comments = query.order_by(Comment.created_at.desc()).all()
    
    # Build comment list with user details
    comment_list = []
    for comment in comments:
        user = db.query(User).filter(User.id == comment.user_id).first()
        comment_list.append({
            "id": str(comment.id),
            "card_id": comment.card_id,
            "user_id": str(comment.user_id),
            "user_name": user.name if user else "Unknown",
            "content": comment.text,
            "created_at": comment.created_at.isoformat() if comment.created_at else None,
            "resolved": bool(comment.is_resolved)
        })
    
    return {
        "presentation_id": presentation_id,
        "card_id": card_id,
        "comments": comment_list
    }


# Resolve Comment
@router.patch("/{presentation_id}/comments/{comment_id}/resolve")
async def resolve_comment(
    presentation_id: int,
    comment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Mark a comment as resolved
    """
    # Find comment
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    
    # Check if user has permission (owner or editor)
    presentation = db.query(Presentation).filter(
        Presentation.id == comment.presentation_id
    ).first()
    
    if not presentation:
        raise HTTPException(status_code=404, detail="Presentation not found")
    
    is_owner = presentation.user_id == current_user.id
    is_editor = db.query(SharedPresentation).filter(
        SharedPresentation.presentation_id == presentation.id,
        SharedPresentation.shared_with_id == current_user.id,
        SharedPresentation.permission == "edit"
    ).first() is not None
    
    if not (is_owner or is_editor):
        raise HTTPException(status_code=403, detail="Permission denied")
    
    # Resolve comment
    comment.is_resolved = 1
    comment.resolved_by = current_user.id
    comment.resolved_at = datetime.utcnow()
    db.commit()
    
    return {
        "status": "resolved",
        "comment_id": str(comment_id)
    }


# Add Suggestion
@router.post("/{presentation_id}/suggestions")
async def add_suggestion(
    presentation_id: int,
    suggestion_data: SuggestionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Add a suggestion for improvement
    """
    presentation = db.query(Presentation).filter(
        Presentation.id == presentation_id
    ).first()
    
    if not presentation:
        raise HTTPException(status_code=404, detail="Presentation not found")
    
    # In production: Save to suggestions table
    return {
        "id": 1,
        "presentation_id": presentation_id,
        "card_id": suggestion_data.card_id,
        "type": suggestion_data.type,
        "content": suggestion_data.content,
        "created_by": current_user.id,
        "status": "pending"
    }


# Get Version History
@router.get("/{presentation_id}/versions")
async def get_version_history(
    presentation_id: int,
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get version history for a presentation
    """
    presentation = db.query(Presentation).filter(
        Presentation.id == presentation_id,
        Presentation.user_id == current_user.id
    ).first()
    
    if not presentation:
        raise HTTPException(status_code=404, detail="Presentation not found")
    
    # In production: Query from versions table
    return {
        "presentation_id": presentation_id,
        "versions": [
            {
                "id": 1,
                "version_number": 1,
                "created_at": presentation.updated_at.isoformat(),
                "created_by": current_user.id,
                "changes": "Initial version"
            }
        ]
    }


# Restore Version (Pro+ only)
@router.post("/{presentation_id}/versions/{version_id}/restore")
async def restore_version(
    presentation_id: int,
    version_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Restore a previous version (Pro plan or higher)
    """
    if current_user.plan not in ["pro", "ultra", "team", "business"]:
        raise HTTPException(
            status_code=403,
            detail="Version restore requires Pro plan or higher"
        )
    
    presentation = db.query(Presentation).filter(
        Presentation.id == presentation_id,
        Presentation.user_id == current_user.id
    ).first()
    
    if not presentation:
        raise HTTPException(status_code=404, detail="Presentation not found")
    
    # In production: Restore from versions table
    return {
        "status": "restored",
        "version_id": version_id,
        "presentation_id": presentation_id
    }


# Get Public Share Link
@router.post("/{presentation_id}/public-link")
async def create_public_link(
    presentation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create or get public share link
    """
    presentation = db.query(Presentation).filter(
        Presentation.id == presentation_id,
        Presentation.user_id == current_user.id
    ).first()
    
    if not presentation:
        raise HTTPException(status_code=404, detail="Presentation not found")
    
    # Make presentation public
    presentation.is_public = True
    db.commit()
    
    return {
        "status": "public",
        "public_link": f"https://gamma.app/public/{presentation_id}",
        "embed_code": f'<iframe src="https://gamma.app/embed/{presentation_id}" width="720" height="540"></iframe>'
    }


# Disable Public Access
@router.delete("/{presentation_id}/public-link")
async def disable_public_link(
    presentation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Disable public access to presentation
    """
    presentation = db.query(Presentation).filter(
        Presentation.id == presentation_id,
        Presentation.user_id == current_user.id
    ).first()
    
    if not presentation:
        raise HTTPException(status_code=404, detail="Presentation not found")
    
    presentation.is_public = False
    db.commit()
    
    return {"status": "private"}
