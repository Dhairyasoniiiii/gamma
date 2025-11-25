"""
Template Suggestion Agent
Intelligently suggests templates based on content and context
"""
import asyncio
from typing import Dict, List, Optional
from sqlalchemy.orm import Session
import json

from backend.agents.base_agent import BaseAgent
from backend.models.template import Template
from backend.models.user import User
from backend.services.ai_service import ai_service


class TemplateSuggestionAgent(BaseAgent):
    """Agent for suggesting appropriate templates"""
    
    def __init__(self):
        super().__init__(
            agent_name="template_suggestion_agent",
            max_concurrent_tasks=5
        )
    
    async def process_task(self, task_data: Dict) -> Dict:
        """
        Process template suggestion task
        
        Task types:
        - suggest_by_content: Suggest based on text content
        - suggest_by_category: Suggest within a category
        - suggest_similar: Suggest similar to existing presentation
        """
        task_type = task_data.get("type")
        
        if task_type == "suggest_by_content":
            return await self._suggest_by_content(task_data)
        elif task_type == "suggest_by_category":
            return await self._suggest_by_category(task_data)
        elif task_type == "suggest_similar":
            return await self._suggest_similar(task_data)
        else:
            raise ValueError(f"Unknown task type: {task_type}")
    
    async def _suggest_by_content(self, task_data: Dict) -> Dict:
        """
        Suggest templates based on content/topic
        
        Args:
            task_data: {
                "content": str,
                "user_id": int,
                "limit": int (optional)
            }
        """
        content = task_data.get("content", "")
        user_id = task_data.get("user_id")
        limit = task_data.get("limit", 5)
        
        # Analyze content with AI
        prompt = f"""Analyze this presentation topic/content and determine the best category and keywords:

Content: {content}

Return a JSON with:
- category: One of (pitch, marketing, portfolio, education, business, creative, personal, report)
- keywords: List of 3-5 relevant keywords
- tone: professional/creative/minimal
- purpose: What is this presentation for?
"""
        
        try:
            analysis = await ai_service.generate_text(
                prompt=prompt,
                max_tokens=200
            )
            
            # Parse AI response (simplified)
            # In production: Use structured output
            analysis_data = {
                "category": "business",  # Default
                "keywords": ["presentation"],
                "tone": "professional"
            }
            
            # Get database session from task_data
            db: Session = task_data.get("db")
            if not db:
                return {"error": "No database session"}
            
            # Query templates based on analysis
            query = db.query(Template)
            
            if analysis_data.get("category"):
                query = query.filter(Template.category == analysis_data["category"])
            
            # Get templates ordered by usage
            templates = query.order_by(
                Template.usage_count.desc()
            ).limit(limit).all()
            
            return {
                "suggestions": [
                    {
                        "id": t.id,
                        "name": t.name,
                        "description": t.description,
                        "category": t.category,
                        "relevance_score": 0.9,  # Mock score
                        "reason": f"Great for {analysis_data['category']} presentations"
                    }
                    for t in templates
                ],
                "analysis": analysis_data
            }
        
        except Exception as e:
            return {"error": str(e)}
    
    async def _suggest_by_category(self, task_data: Dict) -> Dict:
        """
        Suggest templates within a specific category
        """
        category = task_data.get("category")
        limit = task_data.get("limit", 10)
        db: Session = task_data.get("db")
        
        if not db:
            return {"error": "No database session"}
        
        # Get top templates in category
        templates = db.query(Template).filter(
            Template.category == category
        ).order_by(
            Template.usage_count.desc(),
            Template.rating.desc().nullslast()
        ).limit(limit).all()
        
        return {
            "category": category,
            "suggestions": [
                {
                    "id": t.id,
                    "name": t.name,
                    "description": t.description,
                    "usage_count": t.usage_count,
                    "rating": t.rating
                }
                for t in templates
            ]
        }
    
    async def _suggest_similar(self, task_data: Dict) -> Dict:
        """
        Suggest templates similar to an existing presentation
        """
        presentation_id = task_data.get("presentation_id")
        limit = task_data.get("limit", 5)
        db: Session = task_data.get("db")
        
        if not db:
            return {"error": "No database session"}
        
        # Get the presentation
        from backend.models.presentation import Presentation
        presentation = db.query(Presentation).filter(
            Presentation.id == presentation_id
        ).first()
        
        if not presentation:
            return {"error": "Presentation not found"}
        
        # If presentation has a template, find similar ones
        if presentation.template_id:
            template = db.query(Template).filter(
                Template.id == presentation.template_id
            ).first()
            
            if template:
                # Find templates in same category
                similar = db.query(Template).filter(
                    Template.category == template.category,
                    Template.id != template.id
                ).order_by(
                    Template.usage_count.desc()
                ).limit(limit).all()
                
                return {
                    "original_template": {
                        "id": template.id,
                        "name": template.name
                    },
                    "suggestions": [
                        {
                            "id": t.id,
                            "name": t.name,
                            "description": t.description,
                            "category": t.category
                        }
                        for t in similar
                    ]
                }
        
        # If no template, suggest based on content
        return await self._suggest_by_content({
            "content": presentation.title,
            "user_id": presentation.user_id,
            "limit": limit,
            "db": db
        })


# Singleton instance
template_suggestion_agent = TemplateSuggestionAgent()
