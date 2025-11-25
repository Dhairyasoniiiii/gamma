"""
Celery Worker Tasks
Background jobs for exports, emails, analytics, and scheduled tasks
"""
from celery import Celery
from datetime import datetime
import os

# Initialize Celery
celery_app = Celery(
    'gamma_tasks',
    broker=os.getenv('REDIS_URL', 'redis://localhost:6379/0'),
    backend=os.getenv('REDIS_URL', 'redis://localhost:6379/0')
)

# Celery configuration
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=300,  # 5 minutes max
    task_soft_time_limit=240  # 4 minutes soft limit
)


# ========== Export Tasks ==========

@celery_app.task(name='tasks.export_presentation')
def export_presentation(presentation_id: int, format: str, user_id: int):
    """
    Export a presentation in the background
    
    Args:
        presentation_id: ID of presentation to export
        format: Export format (pdf, pptx, html, markdown)
        user_id: ID of requesting user
    """
    try:
        from backend.db.base import SessionLocal
        from backend.models.presentation import Presentation
        from backend.models.theme import Theme
        from backend.services.export_service import export_service
        
        db = SessionLocal()
        
        # Get presentation
        presentation = db.query(Presentation).filter(
            Presentation.id == presentation_id
        ).first()
        
        if not presentation:
            return {"error": "Presentation not found"}
        
        # Get theme if exists
        theme_data = None
        if presentation.theme_id:
            theme = db.query(Theme).filter(Theme.id == presentation.theme_id).first()
            if theme:
                theme_data = {
                    "colors": theme.colors,
                    "fonts": theme.fonts
                }
        
        # Prepare data
        presentation_data = {
            "title": presentation.title,
            "content": presentation.content
        }
        
        # Export
        if format == "pdf":
            output_path = export_service.export_to_pdf(presentation_data, theme_data)
        elif format == "pptx":
            output_path = export_service.export_to_pptx(presentation_data, theme_data)
        elif format == "html":
            output_path = export_service.export_to_html(presentation_data, theme_data)
        elif format == "markdown":
            output_path = export_service.export_to_markdown(presentation_data)
        else:
            return {"error": "Invalid format"}
        
        db.close()
        
        return {
            "status": "completed",
            "presentation_id": presentation_id,
            "format": format,
            "output_path": output_path,
            "completed_at": datetime.utcnow().isoformat()
        }
    
    except Exception as e:
        return {"error": str(e)}


@celery_app.task(name='tasks.batch_export')
def batch_export(presentation_ids: list, format: str, user_id: int):
    """
    Export multiple presentations
    """
    results = []
    
    for pres_id in presentation_ids:
        try:
            result = export_presentation(pres_id, format, user_id)
            results.append({"id": pres_id, "status": "success", "result": result})
        except Exception as e:
            results.append({"id": pres_id, "status": "error", "error": str(e)})
    
    return {
        "total": len(presentation_ids),
        "successful": len([r for r in results if r["status"] == "success"]),
        "failed": len([r for r in results if r["status"] == "error"]),
        "results": results
    }


# ========== Email Tasks ==========

@celery_app.task(name='tasks.send_email')
def send_email(to: str, subject: str, body: str, html: bool = False):
    """
    Send email notification
    """
    try:
        # In production: Use SendGrid, AWS SES, or similar
        print(f"Sending email to {to}: {subject}")
        
        return {
            "status": "sent",
            "to": to,
            "subject": subject,
            "sent_at": datetime.utcnow().isoformat()
        }
    
    except Exception as e:
        return {"error": str(e)}


@celery_app.task(name='tasks.send_share_invitation')
def send_share_invitation(email: str, presentation_id: int, permission: str, message: str = None):
    """
    Send presentation share invitation
    """
    subject = "You've been invited to collaborate"
    body = f"""
    You've been invited to collaborate on a presentation.
    
    Permission: {permission}
    
    {message if message else ''}
    
    Click here to view: https://gamma.app/share/{presentation_id}
    """
    
    return send_email(email, subject, body)


@celery_app.task(name='tasks.send_export_notification')
def send_export_notification(email: str, presentation_id: int, format: str, download_url: str):
    """
    Send export completion notification
    """
    subject = "Your export is ready"
    body = f"""
    Your presentation export is ready!
    
    Format: {format.upper()}
    
    Download: {download_url}
    """
    
    return send_email(email, subject, body)


# ========== Analytics Tasks ==========

@celery_app.task(name='tasks.process_analytics_event')
def process_analytics_event(event_type: str, presentation_id: int, user_id: int, metadata: dict):
    """
    Process and store analytics event
    """
    try:
        from backend.db.base import SessionLocal
        
        db = SessionLocal()
        
        # In production: Store in analytics_events table or MongoDB
        event = {
            "event_type": event_type,
            "presentation_id": presentation_id,
            "user_id": user_id,
            "metadata": metadata,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        db.close()
        
        return {"status": "processed", "event": event}
    
    except Exception as e:
        return {"error": str(e)}


@celery_app.task(name='tasks.aggregate_analytics')
def aggregate_analytics(presentation_id: int):
    """
    Aggregate analytics data for a presentation
    """
    try:
        # In production: Query analytics_events and calculate metrics
        return {
            "status": "aggregated",
            "presentation_id": presentation_id,
            "aggregated_at": datetime.utcnow().isoformat()
        }
    
    except Exception as e:
        return {"error": str(e)}


# ========== Template & Theme Generation Tasks ==========

@celery_app.task(name='tasks.generate_templates')
def generate_templates(category: str, count: int = 10):
    """
    Generate templates in the background
    """
    try:
        from backend.db.base import SessionLocal
        from backend.models.template import Template
        from backend.services.ai_service import ai_service
        
        db = SessionLocal()
        templates_created = []
        
        for i in range(count):
            # Generate template using AI
            # (Simplified version)
            template = Template(
                name=f"Generated Template {i+1}",
                description=f"AI-generated {category} template",
                category=category,
                content={"cards": []},
                tags=[category, "ai-generated"]
            )
            
            db.add(template)
            templates_created.append(template.id)
        
        db.commit()
        db.close()
        
        return {
            "status": "completed",
            "category": category,
            "count": len(templates_created),
            "template_ids": templates_created
        }
    
    except Exception as e:
        return {"error": str(e)}


# ========== Cleanup Tasks ==========

@celery_app.task(name='tasks.cleanup_temp_files')
def cleanup_temp_files():
    """
    Clean up temporary export files older than 24 hours
    """
    try:
        import os
        from datetime import timedelta
        
        temp_dir = "/tmp/gamma_exports"
        cutoff = datetime.utcnow() - timedelta(days=1)
        
        deleted = 0
        
        if os.path.exists(temp_dir):
            for filename in os.listdir(temp_dir):
                filepath = os.path.join(temp_dir, filename)
                if os.path.isfile(filepath):
                    file_time = datetime.fromtimestamp(os.path.getmtime(filepath))
                    if file_time < cutoff:
                        os.remove(filepath)
                        deleted += 1
        
        return {
            "status": "completed",
            "deleted": deleted,
            "cleaned_at": datetime.utcnow().isoformat()
        }
    
    except Exception as e:
        return {"error": str(e)}


@celery_app.task(name='tasks.reset_monthly_credits')
def reset_monthly_credits():
    """
    Reset credits for all users at the start of each month
    """
    try:
        from backend.db.base import SessionLocal
        from backend.models.user import User
        from backend.config import PLAN_CONFIGS
        
        db = SessionLocal()
        
        users = db.query(User).all()
        reset_count = 0
        
        for user in users:
            # Reset to plan default
            plan_credits = PLAN_CONFIGS.get(user.plan, {}).get("credits_per_month", 400)
            user.credits = plan_credits
            reset_count += 1
        
        db.commit()
        db.close()
        
        return {
            "status": "completed",
            "users_reset": reset_count,
            "reset_at": datetime.utcnow().isoformat()
        }
    
    except Exception as e:
        return {"error": str(e)}


# ========== Scheduled Tasks ==========

# Schedule periodic tasks
celery_app.conf.beat_schedule = {
    'cleanup-temp-files-daily': {
        'task': 'tasks.cleanup_temp_files',
        'schedule': 86400.0,  # Once per day (24 hours)
    },
    'reset-credits-monthly': {
        'task': 'tasks.reset_monthly_credits',
        'schedule': 2592000.0,  # Once per month (30 days)
    },
}
