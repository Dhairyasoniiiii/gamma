# Gamma Clone

Full-stack Gamma.app clone with AI-powered presentation generation.

## Stack
- **Frontend**: Next.js 16, TypeScript, TailwindCSS
- **Backend**: FastAPI, SQLAlchemy, SQLite/PostgreSQL
- **AI**: OpenAI GPT-4, DALL-E 3 (or free alternatives: Groq, Perplexity, Gemini)

## Quick Deploy

### Frontend (Vercel)
1. Push to GitHub
2. Import on Vercel: https://vercel.com/new
3. Set root directory: `frontend`
4. Deploy

### Backend (Railway/Render)
1. Push to GitHub
2. Import on Railway: https://railway.app/new
3. Set root directory: `backend`
4. Add environment variables:
   - `DATABASE_URL` (Railway provides PostgreSQL)
   - `SECRET_KEY`
   - `OPENAI_API_KEY` (optional)
5. Deploy

## Local Development

### Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn backend.main:app --reload
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

## Environment Variables

### Backend (.env)
```
DATABASE_URL=sqlite:///./gamma_clone.db
SECRET_KEY=your-secret-key-min-32-chars
OPENAI_API_KEY=sk-...
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your@email.com
SMTP_PASSWORD=your-app-password
```

### Frontend (.env.local)
```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Features
- ✅ 480+ API endpoints
- ✅ AI presentation generation
- ✅ User authentication & JWT
- ✅ Credit system & billing
- ✅ Template & theme management
- ✅ Real-time collaboration (WebSocket)
- ✅ Export (PDF, PPT, HTML)
- ✅ Analytics & tracking

## Documentation
See individual README files in `backend/` and `frontend/` directories.
