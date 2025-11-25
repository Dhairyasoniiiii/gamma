# 🤖 TRENDING TEMPLATE GENERATOR AGENT

## Overview

The **Trending Template Generator Agent** is an autonomous background service that continuously generates premium presentation templates based on real-time Google Trends data. It's designed to compete with and exceed Gamma.app's template quality while providing SEO-optimized, trend-driven content.

---

## 🎯 Key Features

### 1. **Autonomous 24/7 Operation**
- Runs continuously in the background
- Generates templates every hour
- Self-healing error recovery
- Graceful shutdown on interruption

### 2. **Google Trends Integration**
- Scrapes real-time trending searches
- Monitors "Today's Searches" feed
- Fallback to curated trending topics
- 30+ trending topics per cycle

### 3. **SEO Optimization**
- AI-powered title generation (under 60 characters)
- Meta descriptions (150-160 characters)
- Keyword extraction and optimization
- Category-based classification

### 4. **Premium Design Quality**
- **4 Quality Tiers:**
  - Ultra Premium
  - Premium Plus
  - Premium
  - Professional Plus

- **10 Advanced Style Combinations:**
  1. Minimalist Modern Luxury
  2. Bold Cinematic 3D
  3. Swiss Typography Grid
  4. Brutalist Neo Modern
  5. Glassmorphism Futuristic
  6. Retro Wave Premium
  7. Organic Flowing Shapes
  8. Data Viz Storytelling
  9. Editorial Magazine Layout
  10. Architectural Minimalism

### 5. **Production Targets**
- **8-9 templates per hour**
- **192-216 templates per day** (24/7 operation)
- **5,760-6,480 templates per month**
- **69,120-77,760 templates per year**

---

## 📦 Installation

### 1. Install Dependencies

```bash
cd "c:\Users\PC\OneDrive\Desktop\gamma clone"
pip install pytrends aiohttp
```

### 2. Verify Installation

```bash
python -c "from pytrends.request import TrendReq; print('✅ pytrends installed')"
```

---

## 🚀 Usage

### Method 1: Standalone Execution

```bash
# Run the agent directly
python run_trending_agent.py
```

### Method 2: As Background Service (PowerShell)

```powershell
# Start in background
Start-Process python -ArgumentList "run_trending_agent.py" -WindowStyle Hidden

# Or with output visible
Start-Process python -ArgumentList "run_trending_agent.py"
```

### Method 3: Integrated with Celery (Production)

```python
# In celery worker configuration
from backend.agents.trending_template_agent import TrendingTemplateAgent

@celery.task
def run_trending_agent():
    agent = TrendingTemplateAgent()
    asyncio.run(agent.run_forever())
```

---

## 📊 How It Works

### Hourly Generation Cycle

```
┌─────────────────────────────────────────────────────────────┐
│  1. SCRAPE GOOGLE TRENDS (30 trending topics)              │
│     • Real-time trending searches                           │
│     • Today's searches                                       │
│     • Fallback to curated topics if API fails              │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  2. GENERATE SEO PROMPTS (9 optimized prompts)             │
│     • AI-powered title generation                           │
│     • Meta description optimization                         │
│     • Keyword extraction                                    │
│     • Category classification                               │
│     • Design style selection                                │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  3. CREATE PREMIUM TEMPLATES (8-9 templates)               │
│     • Ultra-premium design application                      │
│     • 10-15 cards with varied types                        │
│     • Advanced theming                                      │
│     • Animation & effects                                   │
│     • Card design enhancement                               │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  4. SAVE TO DATABASE                                        │
│     • Mark as featured & premium                            │
│     • Add SEO metadata                                      │
│     • Set trending score to 100                            │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  5. WAIT 1 HOUR → REPEAT                                   │
└─────────────────────────────────────────────────────────────┘
```

---

## 🎨 Premium Themes

### 1. Minimalist Modern Luxury
```json
{
  "colors": {
    "primary": "#000000",
    "secondary": "#FFFFFF",
    "accent": "#D4AF37",
    "background": "#FAFAFA",
    "text": "#1A1A1A"
  },
  "fonts": {
    "heading": "Playfair Display",
    "body": "Inter"
  },
  "effects": {
    "shadows": "premium",
    "animations": "subtle"
  }
}
```

### 2. Bold Cinematic 3D
```json
{
  "colors": {
    "primary": "#1A1A2E",
    "secondary": "#16213E",
    "accent": "#0F4C75",
    "background": "#0A0E27"
  },
  "fonts": {
    "heading": "Montserrat",
    "body": "Open Sans"
  },
  "effects": {
    "shadows": "3d-deep",
    "animations": "cinematic"
  }
}
```

### 3. Glassmorphism Futuristic
```json
{
  "colors": {
    "primary": "rgba(255, 255, 255, 0.1)",
    "accent": "#00D4FF",
    "background": "linear-gradient(135deg, #667eea 0%, #764ba2 100%)"
  },
  "fonts": {
    "heading": "Space Grotesk",
    "body": "Inter"
  },
  "effects": {
    "shadows": "glass",
    "blur": "10px",
    "animations": "float"
  }
}
```

---

## 📈 Performance Metrics

### Expected Output (24/7 Operation)

| Time Period | Templates Generated |
|-------------|-------------------|
| Per Hour    | 8-9               |
| Per Day     | 192-216           |
| Per Week    | 1,344-1,512       |
| Per Month   | 5,760-6,480       |
| Per Year    | 69,120-77,760     |

### API Call Rates

- **Google Trends API:** 1 call/hour
- **OpenAI API:** 9 calls/hour (for SEO optimization)
- **OpenAI API:** 9 calls/hour (for template generation)
- **Total:** ~20 API calls/hour

### Credit Costs (if using paid APIs)

- **SEO Generation:** $0.002 per prompt × 9 = $0.018/hour
- **Template Generation:** $0.02 per template × 9 = $0.18/hour
- **Total:** ~$0.20/hour = **$4.80/day** = **$144/month**

---

## 🔧 Configuration

### Environment Variables

```bash
# Required
OPENAI_API_KEY=your_api_key_here

# Optional (for free alternatives)
GROQ_API_KEY=your_groq_key
PERPLEXITY_API_KEY=your_perplexity_key
```

### Adjusting Generation Rate

Edit `backend/agents/trending_template_agent.py`:

```python
class TrendingTemplateAgent:
    def __init__(self):
        self.daily_target = 200  # Change this
        self.hourly_target = 8   # Change this (8-9 default)
```

### Changing Update Frequency

```python
async def run_forever(self):
    while True:
        await self.hourly_generation_cycle()
        await asyncio.sleep(3600)  # Change from 3600 (1 hour)
```

---

## 📋 Output Format

Each generated template includes:

```json
{
  "title": "SEO-optimized title under 60 chars",
  "description": "SEO-optimized description 150-160 chars",
  "category": "business|technology|marketing|etc",
  "subcategory": "Original trending topic",
  "content": [
    {
      "type": "title",
      "title": "Hero Title",
      "design": {
        "theme": {...},
        "animation": "fade_zoom_in",
        "effects": {
          "gradient_overlay": true,
          "parallax": true
        }
      }
    },
    // ... more cards
  ],
  "tags": ["keyword1", "keyword2", "premium", "trending"],
  "card_count": 12,
  "is_featured": true,
  "is_premium": true,
  "design_level": "ultra_premium",
  "style": "minimalist_modern_luxury",
  "seo_keywords": ["keyword1", "keyword2"],
  "trending_score": 100,
  "generated_from_trends": true,
  "trend_source": "Original Google Trends topic"
}
```

---

## 🛡️ Error Handling

### Google Trends API Failures
- Automatic fallback to curated trending topics
- Continues generation with backup data
- Logs warning but doesn't stop

### OpenAI API Failures
- Falls back to free AI providers (Groq, Perplexity)
- Uses manual SEO generation if all AI fails
- Creates basic templates with predefined cards

### Database Errors
- Transaction rollback
- Continues to next template
- Logs error for monitoring

### Network Issues
- 1-minute wait on errors
- Automatic retry
- Graceful degradation

---

## 📊 Monitoring

### Console Output

```
================================================================================
⏰ HOURLY GENERATION CYCLE - 2025-11-23 04:30:00
================================================================================

📈 Found 30 trending topics
   ✅ Retrieved live Google Trends data
✍️  Generated 9 SEO-optimized prompts

[1/9] Generating: AI and Machine Learning for Business...
   ✅ Template created: AI and Machine Learning for Business
   📦 Cards: 12 | Style: glassmorphism_futuristic

[2/9] Generating: Cryptocurrency Investment Strategies...
   ✅ Template created: Cryptocurrency Investment Strategies
   📦 Cards: 14 | Style: bold_cinematic_3d

...

================================================================================
✅ Completed hourly cycle: 9/9 templates generated
📊 Daily progress: ~216/200 (if running 24/7)
================================================================================
```

---

## 🔄 Integration with Main Backend

### Option 1: Separate Process (Recommended)

Run independently from main backend:

```bash
# Terminal 1: Main backend
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000

# Terminal 2: Trending agent
python run_trending_agent.py
```

### Option 2: Celery Integration

Add to `backend/workers/tasks.py`:

```python
from backend.agents.trending_template_agent import TrendingTemplateAgent

@celery.task(bind=True)
def trending_template_generator(self):
    """Run trending template generator as Celery task"""
    agent = TrendingTemplateAgent()
    asyncio.run(agent.hourly_generation_cycle())
```

Schedule in Celery beat:

```python
app.conf.beat_schedule = {
    'generate-trending-templates': {
        'task': 'backend.workers.tasks.trending_template_generator',
        'schedule': 3600.0,  # Every hour
    },
}
```

---

## ⚡ Performance Tips

### 1. Reduce API Costs
- Use free AI providers (Groq, Perplexity) instead of OpenAI
- Cache trending topics for 1 hour
- Batch API calls when possible

### 2. Optimize Database Writes
- Use bulk inserts for templates
- Index trending_score and is_featured columns
- Clean up old low-performing templates

### 3. Improve Generation Speed
- Reduce sleep time between templates (from 3s to 1s)
- Use concurrent template generation
- Pre-fetch themes and styles

### 4. Scale Horizontally
- Run multiple agents with different categories
- Use message queue for template generation jobs
- Distribute across multiple servers

---

## 🎯 Success Metrics

Track these KPIs:

1. **Generation Rate:** Templates/hour
2. **Success Rate:** Successful generations / Total attempts
3. **API Uptime:** Google Trends availability %
4. **Template Quality:** Average rating
5. **SEO Performance:** Click-through rate from search
6. **Usage Rate:** Templates used by users
7. **Trending Accuracy:** Topics that become popular

---

## 🚀 Deployment

### Production Checklist

- [ ] Install pytrends: `pip install pytrends`
- [ ] Set OPENAI_API_KEY in environment
- [ ] Configure backup AI providers (Groq, Perplexity)
- [ ] Set up monitoring and logging
- [ ] Configure database indexes
- [ ] Set up Celery for scheduled tasks
- [ ] Configure error alerting (Sentry)
- [ ] Test fallback mechanisms
- [ ] Set up health checks
- [ ] Configure auto-restart on failure

### Systemd Service (Linux)

```ini
[Unit]
Description=Trending Template Generator Agent
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/path/to/gamma-clone
ExecStart=/usr/bin/python3 run_trending_agent.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### Windows Service

Use `NSSM` (Non-Sucking Service Manager):

```bash
nssm install TrendingAgent "C:\Python39\python.exe" "run_trending_agent.py"
nssm start TrendingAgent
```

---

## 📞 Support

- **Documentation:** See this file
- **Issues:** Check console output for errors
- **Logs:** Agent prints detailed status to console
- **Testing:** Run manually first before deploying as service

---

## 🎉 Success!

Your Trending Template Generator Agent is now ready to:

✅ Generate 200+ premium templates daily  
✅ Use real Google Trends data  
✅ Apply 10 advanced design styles  
✅ Optimize for SEO automatically  
✅ Run continuously 24/7  
✅ Compete with Gamma.app quality  

**Start the agent:** `python run_trending_agent.py`
