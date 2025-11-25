"""
Folder Model - For organizing all content types
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from backend.db.base import Base

class Folder(Base):
    __tablename__ = "folders"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False, index=True)
    description = Column(Text, nullable=True)
    color = Column(String(7), nullable=True)  # Hex color for UI
    icon = Column(String(50), nullable=True)  # Icon name
    
    # Hierarchy (nested folders)
    parent_id = Column(Integer, ForeignKey("folders.id"), nullable=True)
    
    # Owner
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Workspace (optional - for team folders)
    workspace_id = Column(Integer, ForeignKey("workspaces.id"), nullable=True)
    
    # Metadata
    item_count = Column(Integer, default=0)  # Count of items in folder
    
    # Soft delete
    is_deleted = Column(Boolean, default=False)
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
