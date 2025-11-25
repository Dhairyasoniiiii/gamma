"""
Workspace model
"""

from sqlalchemy import Column, String, Integer, Boolean, TIMESTAMP, ForeignKey
from sqlalchemy.sql import func
from backend.db.base import Base
from backend.db.types import UUID, JSONB
import uuid


class Workspace(Base):
    __tablename__ = "workspaces"
    
    id = Column(UUID(), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    slug = Column(String(255), unique=True)
    owner_id = Column(UUID(), ForeignKey('users.id', ondelete='CASCADE'))
    
    # Settings
    description = Column(String(500))
    logo_url = Column(String(500))
    is_personal = Column(Boolean, default=True)
    plan = Column(String(20), default='free')
    
    # Branding
    brand_colors = Column(JSONB())
    brand_fonts = Column(JSONB())
    default_theme_id = Column(UUID())
    
    # Features
    allow_guest_access = Column(Boolean, default=False)
    require_2fa = Column(Boolean, default=False)
    
    # Stats
    member_count = Column(Integer, default=1)
    presentation_count = Column(Integer, default=0)
    storage_used = Column(Integer, default=0)  # in bytes
    
    # Timestamps
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<Workspace(name='{self.name}', plan='{self.plan}')>"


class WorkspaceMember(Base):
    """Workspace members and their roles"""
    __tablename__ = "workspace_members"
    
    id = Column(UUID(), primary_key=True, default=uuid.uuid4)
    workspace_id = Column(UUID(), ForeignKey('workspaces.id', ondelete='CASCADE'), nullable=False, index=True)
    user_id = Column(UUID(), ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    
    # Role
    role = Column(String(20), default='member')  # owner, admin, member, viewer
    
    # Permissions
    can_create = Column(Boolean, default=True)
    can_edit = Column(Boolean, default=True)
    can_delete = Column(Boolean, default=False)
    can_invite = Column(Boolean, default=False)
    
    # Status
    is_active = Column(Boolean, default=True)
    invitation_accepted = Column(Boolean, default=True)
    
    # Timestamps
    joined_at = Column(TIMESTAMP, server_default=func.now())
    last_active = Column(TIMESTAMP, nullable=True)
    
    def __repr__(self):
        return f"<WorkspaceMember(workspace_id='{self.workspace_id}', user_id='{self.user_id}', role='{self.role}')>"
