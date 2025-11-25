"""Models package"""

from backend.models.user import User
from backend.models.presentation import Presentation
from backend.models.template import Template
from backend.models.theme import Theme
from backend.models.workspace import Workspace, WorkspaceMember
from backend.models.comment import Comment, SharedPresentation
from backend.models.analytics import Analytics, PresentationView, AggregatedStats
from backend.models.billing import BillingHistory, Subscription, CreditsPurchase
# NEW MODELS
from backend.models.document import Document, DocumentType, DocumentStatus
from backend.models.webpage import Webpage, WebpageType, WebpageStatus
from backend.models.social_post import SocialPost, SocialPlatform, SocialPostStatus
from backend.models.folder import Folder
from backend.models.custom_domain import CustomDomain, DomainStatus

__all__ = [
    "User",
    "Presentation",
    "Template",
    "Theme",
    "Workspace",
    "WorkspaceMember",
    "Comment",
    "SharedPresentation",
    "Analytics",
    "PresentationView",
    "AggregatedStats",
    "BillingHistory",
    "Subscription",
    "CreditsPurchase",
    # NEW MODELS
    "Document", "DocumentType", "DocumentStatus",
    "Webpage", "WebpageType", "WebpageStatus",
    "SocialPost", "SocialPlatform", "SocialPostStatus",
    "Folder",
    "CustomDomain", "DomainStatus"
]
