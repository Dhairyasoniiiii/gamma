# Copilot Instructions for Gamma Clone

## Project Overview

**Gamma Clone** is a complete FastAPI-based backend replicating Gamma.app's 423 features for AI-powered presentation generation. Uses OpenAI GPT-4/DALL-E 3 for content generation, SQLAlchemy for data persistence, and supports both SQLite (local dev) and PostgreSQL (production).

## Architecture & Key Patterns

### Three-Layer Agent System
- **GenerationAgent** (`backend/agents/generation_agent.py`): Handles all AI generation with credit management, database persistence, and usage tracking
- **TemplateSuggestionAgent**: Template matching and recommendations
- **WorkflowAutomationAgent**: Background automation tasks

Agents follow a standard pattern: implement `process(input_data: Dict) -> Dict` and inherit from `BaseAgent`.

### Database Dual-Mode Support
Critical: This codebase supports **both SQLite and PostgreSQL**. All models use custom types from `backend/db/types.py`:
```python
from backend.db.types import UUID, JSONB  # NOT from sqlalchemy.dialects
```
Never use `sqlalchemy.dialects.postgresql.UUID` or `sqlalchemy.dialects.postgresql.JSONB` directly - the custom types handle SQLite fallbacks.

### AI Service Pattern
`AIService` (`backend/services/ai_service.py`) is the single interface to OpenAI. Key methods:
- `generate_presentation()`: Full presentation generation with auto-image generation for image cards
- `rewrite_text()`: 6 modes (improve, simplify, expand, shorten, casual, formal)
- `translate_text()`: 60+ languages
- `_generate_image()`: DALL-E 3 wrapper with professional prompts

### Credit System
All AI operations check credits BEFORE execution:
```python
if not await self._check_credits(user_id, settings.CREDIT_COST_FULL_GENERATION):
    raise Exception("Insufficient credits")
```
Credits are deducted after successful generation. Track usage in `ai_generations` table (future: MongoDB analytics).

## Development Workflows

### Running the Backend Locally
```powershell
# Set PYTHONPATH (critical for imports)
$env:PYTHONPATH="C:\Users\PC\OneDrive\Desktop\gamma clone"

# Start server
C:/Python39/python.exe -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```

Or use: `.\start-backend.ps1`

**Common startup issues:**
- Import errors: Verify PYTHONPATH is set and all `backend/__init__.py` files exist
- Database errors: Check `.env` has valid `DATABASE_URL` (defaults to `sqlite:///./gamma_clone.db`)
- Missing API keys: Backend runs without OpenAI key but AI endpoints will fail

### Testing Patterns
See `test_ai_generation.py` for testing approach:
1. Test imports first
2. Create test users in database with sufficient credits
3. Test services directly, then test agents (which include DB operations)
4. Use `asyncio.run()` for async test functions

Run tests: `python test_ai_generation.py` (not pytest - custom runner)

### Template Generation
Scripts in `scripts/` directory generate seed data:
- `seed_themes.py`: Generates 100+ themes (low cost, ~$5)
- `seed_templates.py`: Generates 2000+ templates (**expensive**, $50-100 in API calls)

**Free alternatives:** See `FREE_ALTERNATIVES.md` for Gemini/Groq/Perplexity options to avoid costs.

## Critical Conventions

### Import Structure
**Always use absolute imports** with `backend.` prefix:
```python
from backend.models.user import User
from backend.services.ai_service import AIService
from backend.config import settings
```
Never: `from models.user import User`

### API Endpoint Pattern
All routes in `backend/api/*.py` follow this structure:
```python
router = APIRouter(prefix="/api/v1/resource")

@router.post("/action")
async def action(
    request: RequestModel,
    current_user: User = Depends(get_current_user),  # Auth dependency
    db: Session = Depends(get_db)
):
    # 1. Validate credits/permissions
    # 2. Process request
    # 3. Return standardized response
```

### Configuration Access
All config in `backend/config.py`:
- Settings object: `settings` (Pydantic BaseSettings)
- Plan configs: `PLAN_CONFIGS` dict (6 pricing tiers)
- Card types: `CARD_TYPES` list (34+ types)
- Credit costs: `settings.CREDIT_COST_*` constants

### Database Sessions
Use dependency injection for sessions:
```python
db: Session = Depends(get_db)  # In endpoints
```

For background tasks/agents, manually manage sessions:
```python
db = SessionLocal()
try:
    # operations
    db.commit()
finally:
    db.close()
```

### Error Handling in AI Operations
AI failures should be graceful:
```python
try:
    result = await ai_service.generate_presentation(...)
except Exception as e:
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail=f"Generation failed: {str(e)}"
    )
```
Never expose OpenAI error details to users.

## Key Files & Their Roles

- `backend/main.py`: FastAPI app entry point, router registration, startup/shutdown events
- `backend/config.py`: Single source of truth for all configuration
- `backend/db/base.py`: Database connections (PostgreSQL/SQLite/Redis/MongoDB), session factory
- `backend/db/types.py`: Cross-database compatible types (UUID, JSONB)
- `backend/utils/auth.py`: JWT authentication, `get_current_user` dependency
- `docker-compose.yml`: Full stack (PostgreSQL, Redis, MongoDB, Backend, Celery)

## Docker vs Local Development

**Docker** (recommended for full features):
- PostgreSQL, Redis, MongoDB, Celery all available
- Run: `docker-compose up -d`
- Backend runs in container, auto-reloads on file changes

**Local** (simpler, limited features):
- SQLite database, no Redis/MongoDB
- Celery tasks won't run (but endpoints work)
- Good for API development, not for production testing

## Common Tasks

### Adding a New AI Feature
1. Add endpoint to `backend/api/ai.py`
2. Add method to `AIService` in `backend/services/ai_service.py`
3. Add task type to `GenerationAgent.process()` in `backend/agents/generation_agent.py`
4. Define credit cost in `backend/config.py`
5. Test with `test_ai_generation.py` pattern

### Adding a New Model
1. Create model in `backend/models/newmodel.py` using `UUID()` and `JSONB()` from `backend.db.types`
2. Import in `backend/models/__init__.py`
3. Import in `backend/db/base.py` `init_db()` function
4. Run backend to auto-create tables (or create Alembic migration for production)

### Modifying Credit Costs
Edit constants in `backend/config.py`:
```python
CREDIT_COST_FULL_GENERATION = 10  # Change here
```
All agents automatically use updated values.

## Known Issues & Workarounds

1. **UUID/JSONB Import Errors**: Always import from `backend.db.types`, never from `sqlalchemy.dialects.postgresql`
2. **PYTHONPATH Not Set**: Backend import errors mean PYTHONPATH environment variable missing
3. **Port 8000 In Use**: Previous Python process running - kill with `Get-Process python | Stop-Process -Force`
4. **Database Locked (SQLite)**: Close other connections/terminals accessing the DB

## Project Status

✅ **Complete:** Backend API (81 endpoints), AI generation, auth, models, database schema
⏳ **In Progress:** Real-time collaboration (WebSocket), export system, analytics
❌ **Not Started:** Frontend (Next.js), mobile apps

See `BACKEND_COMPLETE.md` for detailed feature checklist.
