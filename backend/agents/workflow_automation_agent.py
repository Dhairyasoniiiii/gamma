"""
Workflow Automation Agent
Automates repetitive tasks and provides smart suggestions
"""
import asyncio
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from backend.agents.base_agent import BaseAgent
from backend.models.presentation import Presentation
from backend.models.user import User
from backend.services.ai_service import ai_service


class WorkflowAutomationAgent(BaseAgent):
    """Agent for automating workflows and tasks"""
    
    def __init__(self):
        super().__init__(
            agent_name="workflow_automation_agent",
            max_concurrent_tasks=10
        )
    
    async def process_task(self, task_data: Dict) -> Dict:
        """
        Process workflow automation task
        
        Task types:
        - auto_format: Automatically format presentation
        - batch_update: Update multiple presentations
        - smart_suggestions: Provide smart editing suggestions
        - schedule_export: Schedule automated exports
        - duplicate_and_modify: Create variations
        """
        task_type = task_data.get("type")
        
        if task_type == "auto_format":
            return await self._auto_format(task_data)
        elif task_type == "batch_update":
            return await self._batch_update(task_data)
        elif task_type == "smart_suggestions":
            return await self._smart_suggestions(task_data)
        elif task_type == "schedule_export":
            return await self._schedule_export(task_data)
        elif task_type == "duplicate_and_modify":
            return await self._duplicate_and_modify(task_data)
        else:
            raise ValueError(f"Unknown task type: {task_type}")
    
    async def _auto_format(self, task_data: Dict) -> Dict:
        """
        Automatically format a presentation for consistency
        
        - Fixes typography
        - Ensures consistent spacing
        - Applies design rules
        - Optimizes readability
        """
        presentation_id = task_data.get("presentation_id")
        db: Session = task_data.get("db")
        
        if not db:
            return {"error": "No database session"}
        
        presentation = db.query(Presentation).filter(
            Presentation.id == presentation_id
        ).first()
        
        if not presentation:
            return {"error": "Presentation not found"}
        
        # Get current content
        content = presentation.content
        cards = content.get("cards", [])
        
        changes_made = []
        
        # Apply formatting rules
        for i, card in enumerate(cards):
            # Fix title capitalization
            if card.get("title"):
                original = card["title"]
                card["title"] = card["title"].title()
                if original != card["title"]:
                    changes_made.append(f"Card {i+1}: Fixed title capitalization")
            
            # Ensure consistent punctuation
            if card.get("content") and not card["content"].endswith((".", "!", "?")):
                card["content"] += "."
                changes_made.append(f"Card {i+1}: Added punctuation")
            
            # Fix list formatting
            if card.get("type") == "list" and card.get("items"):
                for j, item in enumerate(card["items"]):
                    if not item.endswith((".", "!", "?")):
                        card["items"][j] = item.strip() + "."
        
        # Update presentation
        presentation.content = content
        db.commit()
        
        return {
            "status": "formatted",
            "presentation_id": presentation_id,
            "changes": changes_made,
            "total_changes": len(changes_made)
        }
    
    async def _batch_update(self, task_data: Dict) -> Dict:
        """
        Update multiple presentations at once
        
        Examples:
        - Apply new theme to all presentations
        - Update branding across presentations
        - Fix common typos
        """
        presentation_ids = task_data.get("presentation_ids", [])
        update_type = task_data.get("update_type")
        update_value = task_data.get("update_value")
        db: Session = task_data.get("db")
        
        if not db:
            return {"error": "No database session"}
        
        results = []
        
        for pres_id in presentation_ids:
            try:
                presentation = db.query(Presentation).filter(
                    Presentation.id == pres_id
                ).first()
                
                if not presentation:
                    results.append({"id": pres_id, "status": "not_found"})
                    continue
                
                # Apply update based on type
                if update_type == "theme":
                    presentation.theme_id = update_value
                elif update_type == "template":
                    presentation.template_id = update_value
                
                db.commit()
                results.append({"id": pres_id, "status": "updated"})
            
            except Exception as e:
                results.append({"id": pres_id, "status": "error", "error": str(e)})
        
        return {
            "total": len(presentation_ids),
            "successful": len([r for r in results if r["status"] == "updated"]),
            "failed": len([r for r in results if r["status"] == "error"]),
            "results": results
        }
    
    async def _smart_suggestions(self, task_data: Dict) -> Dict:
        """
        Provide smart suggestions for improvement
        
        Analyzes:
        - Content quality
        - Design consistency
        - Readability
        - Accessibility
        """
        presentation_id = task_data.get("presentation_id")
        db: Session = task_data.get("db")
        
        if not db:
            return {"error": "No database session"}
        
        presentation = db.query(Presentation).filter(
            Presentation.id == presentation_id
        ).first()
        
        if not presentation:
            return {"error": "Presentation not found"}
        
        suggestions = []
        
        # Analyze content
        content = presentation.content
        cards = content.get("cards", [])
        
        # Check card count
        if len(cards) < 5:
            suggestions.append({
                "type": "content",
                "priority": "medium",
                "suggestion": "Consider adding more cards for better storytelling",
                "action": "add_cards"
            })
        
        # Check for missing images
        has_images = any(card.get("type") == "image" for card in cards)
        if not has_images:
            suggestions.append({
                "type": "design",
                "priority": "medium",
                "suggestion": "Add images to make your presentation more engaging",
                "action": "add_images"
            })
        
        # Check text length
        for i, card in enumerate(cards):
            if card.get("type") == "text" and card.get("content"):
                word_count = len(card["content"].split())
                if word_count > 100:
                    suggestions.append({
                        "type": "readability",
                        "priority": "high",
                        "suggestion": f"Card {i+1} has too much text ({word_count} words). Consider splitting.",
                        "action": "split_card",
                        "card_index": i
                    })
        
        # Check theme
        if not presentation.theme_id:
            suggestions.append({
                "type": "design",
                "priority": "high",
                "suggestion": "Apply a theme for better visual consistency",
                "action": "apply_theme"
            })
        
        return {
            "presentation_id": presentation_id,
            "suggestions": suggestions,
            "total_suggestions": len(suggestions)
        }
    
    async def _schedule_export(self, task_data: Dict) -> Dict:
        """
        Schedule automated exports
        """
        presentation_id = task_data.get("presentation_id")
        export_format = task_data.get("format", "pdf")
        schedule = task_data.get("schedule", "daily")
        
        # In production: Create scheduled task in Celery
        return {
            "status": "scheduled",
            "presentation_id": presentation_id,
            "format": export_format,
            "schedule": schedule,
            "next_run": (datetime.utcnow() + timedelta(days=1)).isoformat()
        }
    
    async def _duplicate_and_modify(self, task_data: Dict) -> Dict:
        """
        Create variations of a presentation
        
        Example: Create versions with different themes, languages, or content
        """
        presentation_id = task_data.get("presentation_id")
        modifications = task_data.get("modifications", [])
        db: Session = task_data.get("db")
        
        if not db:
            return {"error": "No database session"}
        
        original = db.query(Presentation).filter(
            Presentation.id == presentation_id
        ).first()
        
        if not original:
            return {"error": "Presentation not found"}
        
        variations = []
        
        for mod in modifications:
            # Create duplicate
            duplicate = Presentation(
                title=f"{original.title} ({mod.get('name', 'Copy')})",
                content=original.content.copy(),
                template_id=mod.get("template_id", original.template_id),
                theme_id=mod.get("theme_id", original.theme_id),
                user_id=original.user_id,
                is_public=False
            )
            
            db.add(duplicate)
            db.flush()
            
            variations.append({
                "id": duplicate.id,
                "title": duplicate.title,
                "modification": mod.get("name")
            })
        
        db.commit()
        
        return {
            "original_id": presentation_id,
            "variations": variations,
            "total_created": len(variations)
        }


# Singleton instance
workflow_automation_agent = WorkflowAutomationAgent()
