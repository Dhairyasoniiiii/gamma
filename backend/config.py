"""
Gamma Clone Configuration
Central configuration for all backend services
"""

from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    APP_NAME: str = "Gamma Clone"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    API_V1_STR: str = "/api/v1"
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./gamma_clone.db")
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    MONGODB_URL: str = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-this-in-production-min-32-chars")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 43200  # 30 days
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Warn if using default SECRET_KEY
        if self.SECRET_KEY == "your-secret-key-change-this-in-production":
            import warnings
            warnings.warn(
                "WARNING: Using default SECRET_KEY! "
                "Set SECRET_KEY environment variable in production.",
                UserWarning,
                stacklevel=2
            )
    
    # CORS
    BACKEND_CORS_ORIGINS: list = [
        "http://localhost:3000",
        "http://localhost:8000",
        "http://127.0.0.1:3000",
    ]
    
    # AI Services - OpenAI (Paid)
    OPENAI_API_KEY: Optional[str] = None
    
    # Free AI Providers
    GOOGLE_API_KEY: Optional[str] = None  # Gemini - Best free tier
    GROQ_API_KEY: Optional[str] = None  # Groq - Fastest free inference
    PERPLEXITY_API_KEY: Optional[str] = None  # Perplexity - Good quality
    ANTHROPIC_API_KEY: Optional[str] = None  # Claude - $5 free credit
    
    # Other AI Services
    STABILITY_API_KEY: Optional[str] = None
    
    # OAuth Configuration
    GOOGLE_CLIENT_ID: Optional[str] = os.getenv("GOOGLE_CLIENT_ID")
    GOOGLE_CLIENT_SECRET: Optional[str] = os.getenv("GOOGLE_CLIENT_SECRET")
    
    # AI Provider Selection
    USE_FREE_PROVIDERS: bool = True  # Use free providers instead of OpenAI
    
    # AI Model Configuration
    DEFAULT_TEXT_MODEL: str = "gpt-4-turbo-preview"
    DEFAULT_IMAGE_MODEL: str = "dall-e-3"
    
    # Credits Configuration
    FREE_PLAN_CREDITS: int = 400
    PLUS_PLAN_CREDITS: int = -1  # unlimited
    PRO_PLAN_CREDITS: int = -1   # unlimited
    ULTRA_PLAN_CREDITS: int = -1 # unlimited
    
    # AI Credits Cost (per operation)
    COST_GENERATE_PRESENTATION: int = 40
    COST_REWRITE_TEXT: int = 5
    COST_TRANSLATE: int = 5
    COST_GENERATE_IMAGE: int = 10
    COST_MAGIC_DESIGN: int = 15
    COST_SMART_RESIZE: int = 3
    COST_AI_SUGGESTIONS: int = 2
    
    # Export Limits (per month)
    FREE_EXPORT_LIMIT: int = 0  # no exports
    PLUS_EXPORT_LIMIT: int = -1  # unlimited
    PRO_EXPORT_LIMIT: int = -1   # unlimited
    
    # Features Access
    FREE_FEATURES: list = [
        "basic_generation",
        "limited_templates",
        "basic_themes",
        "web_sharing"
    ]
    
    PLUS_FEATURES: list = [
        "unlimited_generation",
        "all_templates",
        "all_themes",
        "pdf_export",
        "pptx_export",
        "custom_branding",
        "analytics",
        "team_collaboration"
    ]
    
    PRO_FEATURES: list = [
        "unlimited_generation",
        "all_templates",
        "all_themes",
        "all_exports",
        "custom_branding",
        "advanced_analytics",
        "priority_support",
        "api_access",
        "white_label",
        "unlimited_team_members"
    ]
    
    # Credits Configuration (legacy compatibility)
    CREDITS_FREE_PLAN: int = 400
    CREDITS_PLUS_PLAN: int = 1000
    CREDITS_PRO_PLAN: int = 4000
    CREDITS_ULTRA_PLAN: int = 20000
    
    # Credit Costs (legacy compatibility)
    CREDIT_COST_FULL_GENERATION: int = 10
    CREDIT_COST_REWRITE: int = 1
    CREDIT_COST_TRANSLATE: int = 2
    CREDIT_COST_IMAGE: int = 5
    CREDIT_COST_DIAGRAM: int = 3
    
    # Storage
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    AWS_S3_BUCKET: str = "gamma-clone-storage"
    AWS_REGION: str = "us-east-1"
    USE_LOCAL_STORAGE: bool = True
    LOCAL_STORAGE_PATH: str = "./storage"
    
    # Email
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    SMTP_FROM: str = "noreply@gamma-clone.com"
    SMTP_FROM_NAME: str = "Gamma"
    EMAILS_FROM_EMAIL: str = "noreply@gamma-clone.com"
    EMAILS_FROM_NAME: str = "Gamma Clone"
    
    # Stripe
    STRIPE_SECRET_KEY: Optional[str] = None
    STRIPE_WEBHOOK_SECRET: Optional[str] = None
    STRIPE_PRICE_ID_PLUS: Optional[str] = None
    STRIPE_PRICE_ID_PRO: Optional[str] = None
    STRIPE_PRICE_ID_ULTRA: Optional[str] = None
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    RATE_LIMIT_AI_PER_HOUR: int = 100
    
    # WebSocket
    WS_MESSAGE_QUEUE_SIZE: int = 100
    WS_HEARTBEAT_INTERVAL: int = 30
    
    # Celery
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"
    
    # File Upload
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS: set = {
        "png", "jpg", "jpeg", "gif", "webp",
        "pdf", "pptx", "docx", "txt", "md"
    }
    
    # Export
    EXPORT_QUALITY_HIGH: str = "high"
    EXPORT_QUALITY_MEDIUM: str = "medium"
    EXPORT_QUALITY_LOW: str = "low"
    
    # Frontend URLs
    FRONTEND_URL: str = "http://localhost:3000"
    
    # Monitoring
    SENTRY_DSN: Optional[str] = None
    LOG_LEVEL: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Initialize settings
settings = Settings()


# Plan configurations
PLAN_CONFIGS = {
    "free": {
        "name": "Free",
        "price": 0,
        "monthly_credits": 0,  # One-time 400 credits
        "max_cards_per_generation": 10,
        "features": [
            "400 AI credits (one-time)",
            "Generate up to 10 cards",
            "Basic AI models",
            "PDF/PPT export",
            "Web publishing",
            "Basic templates",
            "Gamma branding"
        ]
    },
    "plus": {
        "name": "Plus",
        "price": 8,
        "monthly_credits": 1000,
        "max_cards_per_generation": 30,
        "features": [
            "Everything in Free",
            "Unlimited AI creations",
            "1,000 monthly credits",
            "Remove branding",
            "Advanced AI image models",
            "Custom fonts",
            "Basic analytics",
            "Priority support"
        ]
    },
    "pro": {
        "name": "Pro",
        "price": 18,
        "monthly_credits": 4000,
        "max_cards_per_generation": 60,
        "features": [
            "Everything in Plus",
            "4,000 monthly credits",
            "Premium AI models (GPT-4, DALL-E 3)",
            "Custom branding",
            "Advanced analytics",
            "Password protection",
            "API access",
            "10 custom domains"
        ]
    },
    "ultra": {
        "name": "Ultra",
        "price": 100,
        "monthly_credits": 20000,
        "max_cards_per_generation": 75,
        "features": [
            "Everything in Pro",
            "20,000 monthly credits",
            "Most advanced AI models",
            "100 custom domains",
            "Early access to features",
            "Studio Mode (cinematic images)",
            "Extended generation"
        ]
    },
    "team": {
        "name": "Team",
        "price": 20,  # per user
        "monthly_credits": 2000,
        "max_cards_per_generation": 50,
        "features": [
            "Team workspaces",
            "Real-time collaboration",
            "Brand kits",
            "Admin controls",
            "Team analytics"
        ]
    },
    "business": {
        "name": "Business",
        "price": 40,  # per user
        "monthly_credits": 5000,
        "max_cards_per_generation": 75,
        "features": [
            "Everything in Team",
            "SSO",
            "Advanced security",
            "Dedicated support",
            "Custom contracts"
        ]
    }
}


# Card type definitions (34+ types)
CARD_TYPES = [
    "title", "content", "image", "split", "quote", "stats",
    "timeline", "comparison", "cta", "video", "audio", "code",
    "table", "chart", "diagram", "flowchart", "orgchart", "mindmap",
    "gantt", "kanban", "form", "button", "divider", "spacer",
    "gallery", "carousel", "accordion", "tabs", "hero", "feature-grid",
    "testimonial", "pricing", "faq", "contact"
]


# Template categories
TEMPLATE_CATEGORIES = {
    'business': ['Pitch Decks', 'Business Plans', 'Quarterly Reviews', 
                 'Sales Presentations', 'Marketing Plans', 'Annual Reports'],
    'education': ['Lectures', 'Course Materials', 'Student Projects',
                  'Research Presentations', 'Thesis Defense', 'Workshops'],
    'technology': ['Product Launches', 'Tech Demos', 'API Documentation',
                   'Software Architecture', 'Development Roadmaps', 'Sprint Reviews'],
    'marketing': ['Campaign Briefs', 'Brand Guidelines', 'Social Media Strategy',
                  'Content Calendars', 'Influencer Decks', 'Product Marketing'],
    'sales': ['Sales Decks', 'Product Demos', 'ROI Calculators',
              'Territory Plans', 'Win/Loss Analysis', 'Pricing Proposals'],
    'creative': ['Portfolios', 'Design Presentations', 'Creative Briefs',
                 'Mood Boards', 'Style Guides', 'Photography Portfolios'],
    'healthcare': ['Medical Presentations', 'Patient Education', 'Research Posters',
                   'Clinical Trials', 'Health Reports', 'Wellness Programs'],
    'finance': ['Financial Reports', 'Investment Pitches', 'Budget Presentations',
                'Audit Reports', 'Risk Assessments', 'Portfolio Reviews']
}


# Theme categories
THEME_CATEGORIES = [
    'professional', 'creative', 'minimal', 'bold', 'dark'
]
