"""
Analytics Service
Tracks and analyzes presentation views, engagement, and user behavior
"""
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
import json

from backend.models.presentation import Presentation
from backend.models.user import User


class AnalyticsService:
    """Service for tracking and analyzing presentation analytics"""
    
    def __init__(self):
        self.mongodb_collection = None  # Initialize MongoDB connection if needed
    
    # ========== Event Tracking ==========
    
    async def track_event(
        self,
        event_type: str,
        presentation_id: Optional[int] = None,
        user_id: Optional[int] = None,
        metadata: Optional[dict] = None,
        db: Optional[Session] = None
    ) -> dict:
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
        event = {
            "event_type": event_type,
            "presentation_id": presentation_id,
            "user_id": user_id,
            "timestamp": datetime.utcnow().isoformat(),
            "metadata": metadata or {}
        }
        
        # Store in MongoDB (if available) or PostgreSQL
        # For now, we'll return the event structure
        return event
    
    # ========== Presentation Analytics ==========
    
    def get_presentation_analytics(
        self,
        presentation_id: int,
        days: int = 30,
        db: Session = None
    ) -> dict:
        """
        Get analytics for a specific presentation
        
        Returns:
        - Total views
        - Unique visitors
        - View trend (last N days)
        - Engagement metrics
        - Top referring sources
        """
        presentation = db.query(Presentation).filter(
            Presentation.id == presentation_id
        ).first()
        
        if not presentation:
            return None
        
        # Calculate date range
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Basic metrics
        total_views = presentation.view_count
        
        # Generate mock trend data (replace with real DB queries)
        views_by_day = self._generate_views_trend(total_views, days)
        
        return {
            "presentation_id": presentation_id,
            "title": presentation.title,
            "period": f"Last {days} days",
            "metrics": {
                "total_views": total_views,
                "unique_visitors": int(total_views * 0.7),  # Estimate
                "avg_time_spent": "2m 34s",  # Mock data
                "completion_rate": 0.75,  # 75% of viewers see all slides
                "engagement_score": 8.5  # Out of 10
            },
            "views_by_day": views_by_day,
            "demographics": {
                "countries": [
                    {"country": "United States", "views": int(total_views * 0.4)},
                    {"country": "United Kingdom", "views": int(total_views * 0.2)},
                    {"country": "Canada", "views": int(total_views * 0.15)},
                    {"country": "Germany", "views": int(total_views * 0.12)},
                    {"country": "Others", "views": int(total_views * 0.13)}
                ],
                "devices": [
                    {"device": "Desktop", "percentage": 65},
                    {"device": "Mobile", "percentage": 25},
                    {"device": "Tablet", "percentage": 10}
                ]
            },
            "referrers": [
                {"source": "Direct", "views": int(total_views * 0.5)},
                {"source": "Social Media", "views": int(total_views * 0.3)},
                {"source": "Email", "views": int(total_views * 0.15)},
                {"source": "Other", "views": int(total_views * 0.05)}
            ]
        }
    
    def _generate_views_trend(self, total_views: int, days: int) -> List[dict]:
        """Generate mock trend data"""
        import random
        
        views_per_day = max(1, total_views // days)
        trend = []
        
        for i in range(days):
            date = datetime.utcnow() - timedelta(days=days - i - 1)
            views = random.randint(
                max(1, views_per_day - 5),
                views_per_day + 5
            )
            trend.append({
                "date": date.strftime("%Y-%m-%d"),
                "views": views
            })
        
        return trend
    
    # ========== User Analytics ==========
    
    def get_user_analytics(
        self,
        user_id: int,
        days: int = 30,
        db: Session = None
    ) -> dict:
        """
        Get analytics for a user's presentations
        
        Returns:
        - Total presentations
        - Total views across all presentations
        - Most viewed presentations
        - Activity timeline
        - Credits usage
        """
        # Get user
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return None
        
        # Get user's presentations
        presentations = db.query(Presentation).filter(
            Presentation.user_id == user_id,
            Presentation.is_archived == False
        ).all()
        
        # Calculate metrics
        total_presentations = len(presentations)
        total_views = sum(p.view_count for p in presentations)
        public_count = sum(1 for p in presentations if p.is_public)
        
        # Sort by views
        top_presentations = sorted(
            presentations,
            key=lambda p: p.view_count,
            reverse=True
        )[:5]
        
        return {
            "user_id": user_id,
            "period": f"Last {days} days",
            "summary": {
                "total_presentations": total_presentations,
                "public_presentations": public_count,
                "total_views": total_views,
                "avg_views_per_presentation": total_views / max(1, total_presentations),
                "credits_remaining": user.credits,
                "current_plan": user.plan
            },
            "top_presentations": [
                {
                    "id": p.id,
                    "title": p.title,
                    "views": p.view_count,
                    "created_at": p.created_at.isoformat()
                }
                for p in top_presentations
            ],
            "activity": {
                "presentations_created": self._get_presentations_created_count(user_id, days, db),
                "exports": 0,  # Mock data
                "shares": 0,  # Mock data
                "ai_generations": self._get_ai_generations_count(user_id, days, db)
            }
        }
    
    def _get_presentations_created_count(
        self,
        user_id: int,
        days: int,
        db: Session
    ) -> int:
        """Get count of presentations created in period"""
        start_date = datetime.utcnow() - timedelta(days=days)
        count = db.query(func.count(Presentation.id)).filter(
            Presentation.user_id == user_id,
            Presentation.created_at >= start_date
        ).scalar()
        return count or 0
    
    def _get_ai_generations_count(
        self,
        user_id: int,
        days: int,
        db: Session
    ) -> int:
        """Get count of AI generations in period (mock)"""
        # In production, query ai_generations table
        return 0
    
    # ========== Workspace Analytics ==========
    
    def get_workspace_analytics(
        self,
        workspace_id: int,
        days: int = 30,
        db: Session = None
    ) -> dict:
        """
        Get analytics for a team workspace
        
        Returns:
        - Team activity
        - Member contributions
        - Total views
        - Collaboration metrics
        """
        return {
            "workspace_id": workspace_id,
            "period": f"Last {days} days",
            "summary": {
                "total_presentations": 0,
                "total_views": 0,
                "active_members": 0,
                "total_collaborations": 0
            },
            "members": [],
            "activity_timeline": []
        }
    
    # ========== Dashboard Stats ==========
    
    def get_dashboard_stats(
        self,
        user_id: int,
        db: Session = None
    ) -> dict:
        """
        Get quick stats for user dashboard
        
        Returns:
        - Recent activity
        - Quick metrics
        - Recommendations
        """
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return None
        
        # Get presentations
        presentations = db.query(Presentation).filter(
            Presentation.user_id == user_id,
            Presentation.is_archived == False
        ).all()
        
        # Calculate quick stats
        total_views = sum(p.view_count for p in presentations)
        recent_presentations = sorted(
            presentations,
            key=lambda p: p.updated_at,
            reverse=True
        )[:3]
        
        return {
            "quick_stats": {
                "total_presentations": len(presentations),
                "total_views": total_views,
                "credits_remaining": user.credits,
                "plan": user.plan
            },
            "recent_presentations": [
                {
                    "id": p.id,
                    "title": p.title,
                    "views": p.view_count,
                    "updated_at": p.updated_at.isoformat()
                }
                for p in recent_presentations
            ],
            "usage_this_month": {
                "presentations_created": len([
                    p for p in presentations
                    if p.created_at >= datetime.utcnow() - timedelta(days=30)
                ]),
                "credits_used": 0,  # Mock data
                "exports": 0  # Mock data
            }
        }
    
    # ========== Engagement Tracking ==========
    
    def track_slide_view(
        self,
        presentation_id: int,
        slide_index: int,
        time_spent: float,
        user_id: Optional[int] = None
    ):
        """Track individual slide view"""
        # Store in analytics database
        pass
    
    def track_interaction(
        self,
        presentation_id: int,
        interaction_type: str,
        metadata: dict,
        user_id: Optional[int] = None
    ):
        """
        Track user interactions
        
        Interaction types:
        - click
        - scroll
        - zoom
        - comment
        - share
        """
        # Store in analytics database
        pass


# Singleton instance
analytics_service = AnalyticsService()
