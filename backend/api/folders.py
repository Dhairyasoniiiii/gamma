"""
Folders API endpoints for Gamma Clone
Handles hierarchical organization of all content types
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel

from backend.db.base import get_db
from backend.models.user import User
from backend.models.folder import Folder
from backend.models.presentation import Presentation
from backend.models.document import Document
from backend.models.webpage import Webpage
from backend.models.social_post import SocialPost
from backend.utils.auth import get_current_user

router = APIRouter(prefix="/api/v1/folders", tags=["Folders"])


# Request/Response Models
class CreateFolderRequest(BaseModel):
    name: str
    description: Optional[str] = None
    parent_id: Optional[str] = None
    workspace_id: Optional[str] = None


class UpdateFolderRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    parent_id: Optional[str] = None


class MoveItemRequest(BaseModel):
    item_type: str  # presentation, document, webpage, social_post
    item_id: str


class FolderResponse(BaseModel):
    id: str
    name: str
    description: Optional[str]
    parent_id: Optional[str]
    workspace_id: Optional[str]
    item_count: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class FolderContentsResponse(BaseModel):
    folder: FolderResponse
    subfolders: List[FolderResponse]
    presentations: List[dict]
    documents: List[dict]
    webpages: List[dict]
    social_posts: List[dict]


@router.post("/", response_model=FolderResponse, status_code=status.HTTP_201_CREATED)
async def create_folder(
    request: CreateFolderRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new folder"""
    # Validate parent folder ownership if provided
    if request.parent_id:
        parent = db.query(Folder).filter(
            Folder.id == request.parent_id,
            Folder.user_id == current_user.id,
            Folder.is_deleted == False
        ).first()
        if not parent:
            raise HTTPException(status_code=404, detail="Parent folder not found")
    
    folder = Folder(
        user_id=current_user.id,
        name=request.name,
        description=request.description,
        parent_id=request.parent_id,
        workspace_id=request.workspace_id
    )
    
    db.add(folder)
    db.commit()
    db.refresh(folder)
    
    return folder


@router.get("/", response_model=List[FolderResponse])
async def list_folders(
    parent_id: Optional[str] = None,
    workspace_id: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List folders for current user.
    If parent_id is None, returns root-level folders.
    """
    query = db.query(Folder).filter(
        Folder.user_id == current_user.id,
        Folder.is_deleted == False
    )
    
    if parent_id is not None:
        query = query.filter(Folder.parent_id == parent_id)
    elif parent_id is None and "parent_id" not in locals():
        # Only root folders
        query = query.filter(Folder.parent_id.is_(None))
    
    if workspace_id:
        query = query.filter(Folder.workspace_id == workspace_id)
    
    folders = query.order_by(Folder.name).offset(skip).limit(limit).all()
    
    # Update item counts
    for folder in folders:
        count = 0
        count += db.query(Presentation).filter(
            Presentation.folder_id == folder.id,
            Presentation.is_deleted == False
        ).count()
        count += db.query(Document).filter(
            Document.folder_id == folder.id,
            Document.is_deleted == False
        ).count()
        count += db.query(Webpage).filter(
            Webpage.folder_id == folder.id,
            Webpage.is_deleted == False
        ).count()
        count += db.query(SocialPost).filter(
            SocialPost.folder_id == folder.id,
            SocialPost.is_deleted == False
        ).count()
        count += db.query(Folder).filter(
            Folder.parent_id == folder.id,
            Folder.is_deleted == False
        ).count()
        
        folder.item_count = count
    
    return folders


@router.get("/{folder_id}", response_model=FolderResponse)
async def get_folder(
    folder_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific folder by ID"""
    folder = db.query(Folder).filter(
        Folder.id == folder_id,
        Folder.user_id == current_user.id,
        Folder.is_deleted == False
    ).first()
    
    if not folder:
        raise HTTPException(status_code=404, detail="Folder not found")
    
    # Update item count
    count = 0
    count += db.query(Presentation).filter(
        Presentation.folder_id == folder.id,
        Presentation.is_deleted == False
    ).count()
    count += db.query(Document).filter(
        Document.folder_id == folder.id,
        Document.is_deleted == False
    ).count()
    count += db.query(Webpage).filter(
        Webpage.folder_id == folder.id,
        Webpage.is_deleted == False
    ).count()
    count += db.query(SocialPost).filter(
        SocialPost.folder_id == folder.id,
        SocialPost.is_deleted == False
    ).count()
    count += db.query(Folder).filter(
        Folder.parent_id == folder.id,
        Folder.is_deleted == False
    ).count()
    
    folder.item_count = count
    
    return folder


@router.patch("/{folder_id}", response_model=FolderResponse)
async def update_folder(
    folder_id: str,
    request: UpdateFolderRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update an existing folder"""
    folder = db.query(Folder).filter(
        Folder.id == folder_id,
        Folder.user_id == current_user.id,
        Folder.is_deleted == False
    ).first()
    
    if not folder:
        raise HTTPException(status_code=404, detail="Folder not found")
    
    # Validate parent folder if changing
    if request.parent_id is not None:
        # Prevent circular references
        if request.parent_id == folder_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Folder cannot be its own parent"
            )
        
        # Check if new parent exists and is owned by user
        parent = db.query(Folder).filter(
            Folder.id == request.parent_id,
            Folder.user_id == current_user.id,
            Folder.is_deleted == False
        ).first()
        if not parent:
            raise HTTPException(status_code=404, detail="Parent folder not found")
        
        # Check for circular reference in ancestry
        current_parent = parent
        while current_parent.parent_id:
            if current_parent.parent_id == folder_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Cannot create circular folder reference"
                )
            current_parent = db.query(Folder).filter(
                Folder.id == current_parent.parent_id
            ).first()
            if not current_parent:
                break
    
    # Update fields
    if request.name is not None:
        folder.name = request.name
    if request.description is not None:
        folder.description = request.description
    if request.parent_id is not None:
        folder.parent_id = request.parent_id
    
    folder.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(folder)
    
    return folder


@router.delete("/{folder_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_folder(
    folder_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Soft delete a folder.
    All contents are moved to parent folder (or root if no parent).
    """
    folder = db.query(Folder).filter(
        Folder.id == folder_id,
        Folder.user_id == current_user.id,
        Folder.is_deleted == False
    ).first()
    
    if not folder:
        raise HTTPException(status_code=404, detail="Folder not found")
    
    # Move all contents to parent folder
    new_parent_id = folder.parent_id
    
    # Move presentations
    db.query(Presentation).filter(
        Presentation.folder_id == folder_id
    ).update({"folder_id": new_parent_id})
    
    # Move documents
    db.query(Document).filter(
        Document.folder_id == folder_id
    ).update({"folder_id": new_parent_id})
    
    # Move webpages
    db.query(Webpage).filter(
        Webpage.folder_id == folder_id
    ).update({"folder_id": new_parent_id})
    
    # Move social posts
    db.query(SocialPost).filter(
        SocialPost.folder_id == folder_id
    ).update({"folder_id": new_parent_id})
    
    # Move subfolders
    db.query(Folder).filter(
        Folder.parent_id == folder_id
    ).update({"parent_id": new_parent_id})
    
    # Soft delete folder
    folder.is_deleted = True
    folder.deleted_at = datetime.utcnow()
    
    db.commit()
    
    return None


@router.post("/{folder_id}/move", response_model=dict)
async def move_item_to_folder(
    folder_id: str,
    request: MoveItemRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Move an item (presentation, document, webpage, social post) to a folder"""
    # Validate folder ownership
    folder = db.query(Folder).filter(
        Folder.id == folder_id,
        Folder.user_id == current_user.id,
        Folder.is_deleted == False
    ).first()
    
    if not folder:
        raise HTTPException(status_code=404, detail="Folder not found")
    
    # Move item based on type
    item_type = request.item_type.lower()
    item = None
    
    if item_type == "presentation":
        item = db.query(Presentation).filter(
            Presentation.id == request.item_id,
            Presentation.user_id == current_user.id,
            Presentation.is_deleted == False
        ).first()
    elif item_type == "document":
        item = db.query(Document).filter(
            Document.id == request.item_id,
            Document.user_id == current_user.id,
            Document.is_deleted == False
        ).first()
    elif item_type == "webpage":
        item = db.query(Webpage).filter(
            Webpage.id == request.item_id,
            Webpage.user_id == current_user.id,
            Webpage.is_deleted == False
        ).first()
    elif item_type == "social_post":
        item = db.query(SocialPost).filter(
            SocialPost.id == request.item_id,
            SocialPost.user_id == current_user.id,
            SocialPost.is_deleted == False
        ).first()
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid item type. Must be: presentation, document, webpage, or social_post"
        )
    
    if not item:
        raise HTTPException(status_code=404, detail=f"{item_type.title()} not found")
    
    # Move item to folder
    item.folder_id = folder_id
    
    db.commit()
    
    return {
        "message": f"{item_type.title()} moved successfully",
        "item_id": request.item_id,
        "folder_id": folder_id
    }


@router.get("/{folder_id}/contents", response_model=FolderContentsResponse)
async def get_folder_contents(
    folder_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all contents of a folder (subfolders and items)"""
    folder = db.query(Folder).filter(
        Folder.id == folder_id,
        Folder.user_id == current_user.id,
        Folder.is_deleted == False
    ).first()
    
    if not folder:
        raise HTTPException(status_code=404, detail="Folder not found")
    
    # Get subfolders
    subfolders = db.query(Folder).filter(
        Folder.parent_id == folder_id,
        Folder.user_id == current_user.id,
        Folder.is_deleted == False
    ).order_by(Folder.name).all()
    
    # Get presentations
    presentations = db.query(Presentation).filter(
        Presentation.folder_id == folder_id,
        Presentation.user_id == current_user.id,
        Presentation.is_deleted == False
    ).order_by(Presentation.updated_at.desc()).all()
    
    # Get documents
    documents = db.query(Document).filter(
        Document.folder_id == folder_id,
        Document.user_id == current_user.id,
        Document.is_deleted == False
    ).order_by(Document.updated_at.desc()).all()
    
    # Get webpages
    webpages = db.query(Webpage).filter(
        Webpage.folder_id == folder_id,
        Webpage.user_id == current_user.id,
        Webpage.is_deleted == False
    ).order_by(Webpage.updated_at.desc()).all()
    
    # Get social posts
    social_posts = db.query(SocialPost).filter(
        SocialPost.folder_id == folder_id,
        SocialPost.user_id == current_user.id,
        SocialPost.is_deleted == False
    ).order_by(SocialPost.created_at.desc()).all()
    
    # Update folder item count
    folder.item_count = (
        len(subfolders) + len(presentations) + 
        len(documents) + len(webpages) + len(social_posts)
    )
    
    return {
        "folder": folder,
        "subfolders": subfolders,
        "presentations": [{"id": str(p.id), "title": p.title, "updated_at": p.updated_at} for p in presentations],
        "documents": [{"id": str(d.id), "title": d.title, "type": d.document_type.value, "updated_at": d.updated_at} for d in documents],
        "webpages": [{"id": str(w.id), "title": w.title, "type": w.webpage_type.value, "updated_at": w.updated_at} for w in webpages],
        "social_posts": [{"id": str(s.id), "platform": s.platform.value, "caption": s.caption[:50] + "...", "created_at": s.created_at} for s in social_posts]
    }
