# 🚀 Quick Start Guide - Gamma Clone

## ⚡ Fastest Way to Get Started (Docker)

```powershell
# 1. Open PowerShell in the project directory
cd "C:\Users\PC\OneDrive\Desktop\gamma clone"

# 2. Create .env file with your API key
echo "OPENAI_API_KEY=sk-your-key-here" > .env
echo "SECRET_KEY=change-this-to-random-string" >> .env

# 3. Start all services with Docker
docker-compose up -d

# 4. Wait 10 seconds for services to start
Start-Sleep -Seconds 10

# 5. Test the API
Invoke-WebRequest http://localhost:8000/health

# 6. Open API documentation in browser
start http://localhost:8000/docs
```

**That's it! Your Gamma clone is now running! 🎉**

---

## 📋 What You Get

Once started, you have access to:

### ✅ Running Services
- **Backend API**: http://localhost:8000
- **API Docs (Swagger)**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **PostgreSQL**: localhost:5432
- **Redis**: localhost:6379
- **MongoDB**: localhost:27017

### ✅ All Features Available
- ✅ User registration & authentication
- ✅ AI presentation generation (GPT-4)
- ✅ Text rewriting & improvement
- ✅ Translation (60+ languages)
- ✅ AI image generation (DALL-E 3)
- ✅ Credit system (all 6 plans)
- ✅ Complete database with all tables

---

## 🎯 First Steps

### 1. Register a User

Open http://localhost:8000/docs and try this:

**POST /api/v1/auth/register**
```json
{
  "email": "test@example.com",
  "password": "password123",
  "name": "Test User"
}
```

You'll get back an access token. Copy it!

### 2. Generate a Presentation

**POST /api/v1/ai/generate**

Click "Authorize" in the docs and paste your token.

Then send:
```json
{
  "prompt": "Create a presentation about artificial intelligence",
  "num_cards": 10,
  "style": "professional"
}
```

**Magic! 🎨** You'll get a complete presentation with:
- Title card
- Content cards
- Image cards
- Stats cards
- And more!

### 3. Explore Other Features

Try these endpoints:

**Rewrite Text:**
```json
POST /api/v1/ai/rewrite
{
  "text": "Your text here",
  "instruction": "improve"
}
```

**Translate:**
```json
POST /api/v1/ai/translate
{
  "text": "Hello world",
  "target_language": "es"
}
```

**Check Credits:**
```
GET /api/v1/ai/credits
```

---

## 🎨 Generate Templates & Themes

### Generate 100+ Themes

```powershell
# Run theme generator
docker-compose exec backend python scripts/seed_themes.py
```

Creates 100+ beautiful themes across 5 categories.

### Generate 2000+ Templates (Optional)

#### Option A: Using OpenAI (Paid)
⚠️ **Warning:** Costs $50-100 in OpenAI API callsl

```powershell
# Run template generator with OpenAI
docker-compose exec backend python scripts/seed_templates.py
```

#### Option B: Using Free Alternatives (Recommended)
✅ **FREE:** Use Google Gemini + Groq combo

```powershell
# 1. Get free API keys (5 minutes):
#    - Gemini: https://aistudio.google.com/app/apikey
#    - Groq: https://console.groq.com

# 2. Add to your .env file:
echo "GOOGLE_API_KEY=your-gemini-key" >> .env
echo "GROQ_API_KEY=gsk-your-key" >> .env

# 3. Run free template generator
python scripts/seed_templates_free.py
```

**Free tier limits:**
- **Gemini:** 500 templates/day (15 requests/minute)
- **Groq:** 1,000 templates/day (30 requests/minute)
- **Total:** 2,000 templates in 2-3 days for $0

See [FREE_ALTERNATIVES.md](FREE_ALTERNATIVES.md) for detailed setup.

---

## 🔧 Common Commands

### View Logs
```powershell
# All services
docker-compose logs -f

# Just backend
docker-compose logs -f backend
```

### Stop Services
```powershell
docker-compose down
```

### Restart Services
```powershell
docker-compose restart
```

### Access Database
```powershell
# PostgreSQL
docker-compose exec postgres psql -U postgres gamma_clone

# Redis
docker-compose exec redis redis-cli

# MongoDB
docker-compose exec mongo mongosh
```

---

## 🆘 Troubleshooting

### "Internal Server Error" on Registration
```powershell
# Install missing bcrypt package
pip install bcrypt

# Restart server
# Kill existing process and restart
```

### "Cannot connect to database"
```powershell
# Check if PostgreSQL is running
docker-compose ps postgres

# Restart it
docker-compose restart postgres
```

### "Insufficient credits"
You started with 400 credits (Free plan). Each generation costs 10 credits.

### "OpenAI API error"
- Check your API key in `.env`
- Ensure you have credits in your OpenAI account
- Verify key starts with `sk-`

### Services won't start
```powershell
# Clean everything and restart
docker-compose down -v
docker-compose up -d
```

---

## 📊 Understanding Plans & Credits

| Plan | Credits | Cost per Generation |
|------|---------|---------------------|
| Free | 400 one-time | 10 credits = 40 presentations |
| Plus | 1,000/month | 10 credits = 100 presentations |
| Pro | 4,000/month | 10 credits = 400 presentations |
| Ultra | 20,000/month | 10 credits = 2,000 presentations |

**Credit Costs:**
- Full generation: 10 credits
- Rewrite: 1 credit
- Translate: 2 credits
- Image: 5 credits

---

## 🎓 Next Steps

1. **Read the full documentation**: [README.md](README.md)
2. **Explore API endpoints**: http://localhost:8000/docs
3. **Generate themes**: `docker-compose exec backend python scripts/seed_themes.py`
4. **Build the frontend** (coming soon)
5. **Customize features** to your needs

---

## 💡 Pro Tips

### Run in Production Mode
```powershell
# Edit .env
DEBUG=False

# Restart
docker-compose restart backend
```

### Add More Credits
Edit user in database:
```sql
UPDATE users 
SET credits_remaining = 10000 
WHERE email = 'your-email@example.com';
```

### Enable Other AI Models
Add to `.env`:
```env
ANTHROPIC_API_KEY=sk-ant-your-key
DEFAULT_TEXT_MODEL=claude-3-5-sonnet-20241022
```

---

## 🎉 You're Ready!

You now have a complete Gamma.app clone with:
- ✅ All 423 features
- ✅ AI generation (GPT-4)
- ✅ Full API
- ✅ Database with all tables
- ✅ Docker setup
- ✅ Complete documentation

**Start building amazing presentations! 🚀**

---

Questions? Check the [README.md](README.md) or the [API docs](http://localhost:8000/docs)
