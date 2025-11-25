# 🆓 FREE ALTERNATIVES FOR TEMPLATE GENERATION

Yes! Several options let you generate templates without cost. Here's what actually works:

---

## ✅ OPTION 1: GOOGLE GEMINI (Best Free Option) 🏆

### Why Gemini?
- **Free tier:** 500 requests/day
- **No credit card required**
- **Fast response times**
- **Good quality output**
- **15 requests per minute**

### How to Use:

```python
# Replace OpenAI with Gemini

import google.generativeai as genai

genai.configure(api_key="your-google-api-key")

def generate_with_gemini(prompt):
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content(prompt)
    return response.text
```

**Get API Key:** https://aistudio.google.com/app/apikey

**Free Tier Limits:**
- ✅ 15 RPM (requests per minute)
- ✅ 1 million tokens per day
- ✅ **Can generate 500+ templates per day for free**

---

## ✅ OPTION 2: GROQ (Fastest Free Inference)

### Llama 3.1 on Groq (Free & Very Fast)

```bash
# Get free key: https://console.groq.com
# Free tier: 30 requests/minute
```

**Modify script:**

```python
from groq import Groq

client = Groq(api_key="gsk-your-key")

def generate_with_groq(prompt):
    completion = client.chat.completions.create(
        model="llama-3.1-70b-versatile",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    return completion.choices[0].message.content
```

**Free Tier:**
- ✅ 30 requests/minute
- ✅ Very fast inference
- ✅ Can generate all 2,000 templates in ~2 hours

---

## ✅ OPTION 3: PERPLEXITY API

### Why Perplexity?
- **Free tier:** Actually usable limits
- **No credit card required** for testing
- **Similar quality** to GPT-4
- **Built-in web search** for better context

### How to Use:

```python
# Replace OpenAI with Perplexity

import requests

PERPLEXITY_API_KEY = "pplx-your-key"  # Get free from perplexity.ai/settings

def generate_with_perplexity(prompt):
    url = "https://api.perplexity.ai/chat/completions"
    
    payload = {
        "model": "llama-3.1-sonar-large-128k-online",  # Free model
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }
    
    headers = {
        "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
        "Content-Type": "application/json"
    }
    
    response = requests.post(url, json=payload, headers=headers)
    return response.json()
```

**Free Tier:**
- ~5 requests per second
- Enough to generate hundreds of templates
- No expiration

---

## ✅ OPTION 4: ANTHROPIC CLAUDE (Free Credit)

### Claude 3 Haiku (Fast & Free)

```bash
# Get free API key: https://console.anthropic.com
# Free tier: $5 credit (generates ~1,000 templates)
```

**Modify script:**

```python
import anthropic

client = anthropic.Anthropic(api_key="sk-ant-your-key")

def generate_with_claude(prompt):
    message = client.messages.create(
        model="claude-3-haiku-20240307",  # Cheapest model
        max_tokens=2000,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    return message.content[0].text
```

**Cost with free $5 credit:**
- Claude Haiku: $0.25 per 1M input tokens
- ~2,000 templates with free credit

---

## ✅ OPTION 5: OLLAMA (100% Free, Local)

### Use Ollama (Run AI Locally)

**No API costs, no limits, runs on your computer:**

```bash
# 1. Install Ollama (Windows)
# Download from: https://ollama.com/download

# 2. Pull a model (one-time, ~4GB download)
ollama pull llama3.1:8b

# 3. Run it
ollama serve
```

**Modify your script:**

```python
# backend/services/ai_service.py

import requests

class AIService:
    def __init__(self, api_key=None):
        self.use_local = True  # Use Ollama instead
    
    async def generate_presentation(self, prompt: str):
        if self.use_local:
            return await self._generate_with_ollama(prompt)
        # ... existing code
    
    async def _generate_with_ollama(self, prompt: str):
        url = "http://localhost:11434/api/generate"
        
        response = requests.post(url, json={
            "model": "llama3.1:8b",
            "prompt": prompt,
            "stream": False
        })
        
        return response.json()
```

**Pros:**
- ✅ 100% free
- ✅ No limits
- ✅ Privacy (runs locally)

**Cons:**
- ⚠️ Slower than cloud APIs
- ⚠️ Needs ~8GB RAM
- ⚠️ Quality slightly lower than GPT-4

---

## 🎯 RECOMMENDED: MULTI-MODEL APPROACH

**Use multiple free tiers together:**

```python
# backend/services/ai_service.py

class AIService:
    def __init__(self):
        self.providers = [
            {'name': 'gemini', 'limit': 500},
            {'name': 'groq', 'limit': 1000},
            {'name': 'perplexity', 'limit': 500},
        ]
        self.current_provider = 0
    
    async def generate_presentation(self, prompt: str):
        provider = self.providers[self.current_provider]
        
        try:
            if provider['name'] == 'gemini':
                return await self._generate_with_gemini(prompt)
            elif provider['name'] == 'groq':
                return await self._generate_with_groq(prompt)
            elif provider['name'] == 'perplexity':
                return await self._generate_with_perplexity(prompt)
        except Exception:
            # Switch to next provider if limit hit
            self.current_provider = (self.current_provider + 1) % len(self.providers)
            return await self.generate_presentation(prompt)
```

**Result:** Generate all 2,000 templates for **$0** using multiple free tiers!

---

## 📊 COMPARISON TABLE

| Provider | Free Tier | Speed | Quality | Setup |
|----------|-----------|-------|---------|-------|
| **Google Gemini** 🏆 | 500/day | Fast | Good | Easy |
| **Groq** | 30/min | Very Fast | Good | Easy |
| **Perplexity** | 5/sec | Medium | Great | Easy |
| **Claude Haiku** | $5 credit | Medium | Great | Easy |
| **Ollama (Local)** | Unlimited | Slow | Good | Medium |
| OpenAI | ❌ Paid only | Fast | Best | Easy |

---

## 🔧 IMPLEMENTATION GUIDE

### Step 1: Get Free API Keys (5 minutes)

```bash
# 1. Google Gemini (Best) 🏆
https://aistudio.google.com/app/apikey

# 2. Groq (Fastest)
https://console.groq.com

# 3. Perplexity
https://www.perplexity.ai/settings/api

# 4. Claude (backup)
https://console.anthropic.com
```

### Step 2: Install Required Packages

```powershell
# Install free provider libraries
pip install google-generativeai groq anthropic
```

### Step 3: Update Your .env

```env
# Add all free providers
GOOGLE_API_KEY=your-gemini-key
GROQ_API_KEY=gsk-your-key
PERPLEXITY_API_KEY=pplx-your-key
ANTHROPIC_API_KEY=sk-ant-your-key
```

### Step 4: Create Free AI Service

Create `backend/services/free_ai_service.py`:

```python
"""
Free AI Service using Gemini and Groq
No cost alternative to OpenAI
"""

import google.generativeai as genai
from groq import Groq
import os
import json
from typing import Dict

class FreeAIService:
    def __init__(self):
        # Configure all free providers
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
        self.groq = Groq(api_key=os.getenv("GROQ_API_KEY"))
        
        self.providers = ['gemini', 'groq']
        self.current = 0
        self.gemini_count = 0
    
    async def generate_presentation(self, prompt: str, num_cards: int = 10, style: str = "professional"):
        """Generate presentation using free providers"""
        
        full_prompt = f"""Create a presentation with {num_cards} cards.
Style: {style}

{prompt}

Return ONLY valid JSON in this exact format:
{{
    "title": "Presentation Title",
    "cards": [
        {{
            "type": "title",
            "content": {{
                "title": "Main Title",
                "subtitle": "Subtitle"
            }}
        }},
        {{
            "type": "content",
            "content": {{
                "title": "Card Title",
                "body": "Card content"
            }}
        }}
    ],
    "theme": {{
        "name": "professional",
        "primary_color": "#1a73e8",
        "secondary_color": "#34a853"
    }}
}}"""
        
        try:
            if self.providers[self.current] == 'gemini' and self.gemini_count < 500:
                result = await self._use_gemini(full_prompt)
                self.gemini_count += 1
                return result
            else:
                return await self._use_groq(full_prompt)
        except Exception as e:
            print(f"Error with {self.providers[self.current]}: {e}")
            # Rotate to next provider
            self.current = (self.current + 1) % len(self.providers)
            return await self.generate_presentation(prompt, num_cards, style)
    
    async def _use_gemini(self, prompt: str):
        """Use Google Gemini"""
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        return self._parse_response(response.text)
    
    async def _use_groq(self, prompt: str):
        """Use Groq"""
        completion = self.groq.chat.completions.create(
            model="llama-3.1-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=2000
        )
        return self._parse_response(completion.choices[0].message.content)
    
    def _parse_response(self, text: str) -> Dict:
        """Parse JSON response from AI"""
        # Remove markdown code blocks if present
        text = text.strip()
        if text.startswith('```json'):
            text = text[7:]
        if text.startswith('```'):
            text = text[3:]
        if text.endswith('```'):
            text = text[:-3]
        
        try:
            return json.loads(text.strip())
        except json.JSONDecodeError:
            # Fallback: return basic structure
            return {
                "title": "Generated Presentation",
                "cards": [{"type": "title", "content": {"title": "Title", "subtitle": "Subtitle"}}],
                "theme": {"name": "professional"}
            }
```

### Step 5: Create Free Template Generator Script

Create `scripts/seed_templates_free.py`:

```python
"""
Generate templates using FREE AI providers (Gemini + Groq)
No cost alternative to OpenAI
"""

import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.services.free_ai_service import FreeAIService
from backend.db.base import SessionLocal
from backend.models.template import Template
import uuid

class FreeTemplateGenerator:
    def __init__(self):
        self.ai_service = FreeAIService()
        self.db = SessionLocal()
        
        self.categories = {
            'Business': ['Pitch Deck', 'Business Plan', 'Quarterly Review', 'Company Overview'],
            'Education': ['Lecture', 'Course Introduction', 'Assignment', 'Student Project'],
            'Marketing': ['Campaign Brief', 'Product Launch', 'Brand Guidelines', 'Social Media'],
            'Sales': ['Sales Pitch', 'Product Demo', 'Customer Case Study', 'Proposal'],
            'Technology': ['Product Roadmap', 'Technical Spec', 'API Documentation', 'Architecture'],
            'Creative': ['Portfolio', 'Design System', 'Mood Board', 'Brand Story'],
            'Research': ['Research Findings', 'Data Analysis', 'Survey Results', 'Literature Review'],
            'HR': ['Onboarding', 'Training', 'Performance Review', 'Company Culture']
        }
    
    async def generate_all_templates(self):
        """Generate all templates using free providers"""
        print("🆓 Generating templates with FREE AI providers (Gemini + Groq)")
        print("="*60)
        
        total = sum(len(subs) * 25 for subs in self.categories.values())  # 25 per subcategory
        print(f"📊 Total templates to generate: {total}")
        print(f"⏱️  Estimated time: {total // 60} minutes")
        print("="*60)
        
        generated = 0
        
        for category, subcategories in self.categories.items():
            print(f"\n📂 Category: {category}")
            
            for subcategory in subcategories:
                print(f"  📄 {subcategory}...")
                
                for i in range(25):
                    try:
                        template = await self._generate_single_template(category, subcategory, i)
                        self.db.add(template)
                        self.db.commit()
                        
                        generated += 1
                        print(f"    ✅ {generated}/{total}", end='\r')
                        
                        # Small delay to respect rate limits
                        await asyncio.sleep(0.1)
                        
                    except Exception as e:
                        print(f"    ❌ Error: {e}")
                        continue
        
        print(f"\n\n✅ Generated {generated} templates for FREE!")
        self.db.close()
    
    async def _generate_single_template(self, category, subcategory, index):
        """Generate a single template"""
        prompt = f"""Create a professional {subcategory} template for {category}.
Make it practical and ready to use."""
        
        result = await self.ai_service.generate_presentation(
            prompt=prompt,
            num_cards=8,
            style="professional"
        )
        
        template = Template(
            id=uuid.uuid4(),
            title=f"{subcategory} - {category} #{index + 1}",
            category=category,
            subcategory=subcategory,
            description=f"Professional {subcategory} template for {category}",
            thumbnail_url=f"https://via.placeholder.com/400x300?text={subcategory}",
            content=result,
            is_premium=False,
            is_featured=(index % 5 == 0)
        )
        
        return template

async def main():
    print("🚀 Starting FREE template generation...")
    print("📌 Using: Google Gemini + Groq")
    print("💰 Cost: $0\n")
    
    generator = FreeTemplateGenerator()
    await generator.generate_all_templates()

if __name__ == "__main__":
    asyncio.run(main())
```

---

## 🎯 FINAL RECOMMENDATION

### Best Solution: **Gemini + Groq Combo**

```bash
# Day 1: Generate 500 templates with Gemini (free)
# Day 2: Generate 1,000 templates with Groq (free)
# Day 3: Generate 500 more with Gemini (free)

Total: 2,000 templates
Cost: $0
Time: 2-3 days
```

### Quick Setup (10 minutes):

```powershell
# 1. Get API keys
# Gemini: https://aistudio.google.com/app/apikey
# Groq: https://console.groq.com

# 2. Install packages
pip install google-generativeai groq

# 3. Add to .env
echo "GOOGLE_API_KEY=your-key" >> .env
echo "GROQ_API_KEY=gsk-your-key" >> .env

# 4. Run generator
python scripts/seed_templates_free.py
```

---

## 🆘 Troubleshooting

### "Rate limit exceeded"
- Wait a few minutes
- Script automatically switches to next provider

### "Invalid API key"
- Check key format
- Regenerate key from provider dashboard

### "No response from API"
- Check internet connection
- Verify API endpoint URLs
- Try different provider

---

## 💡 Pro Tips

1. **Use overnight:** Run the script overnight to generate all templates
2. **Combine providers:** Use Gemini during day, Groq at night
3. **Cache results:** Save generated templates to avoid regeneration
4. **Monitor usage:** Track daily limits in provider dashboards

---

**🎉 You can now generate all 2,000 templates for FREE!**

Questions? Open an issue or check the [QUICKSTART.md](QUICKSTART.md)
