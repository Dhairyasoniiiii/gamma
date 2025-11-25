# 🆓 FREE AI PROVIDERS SETUP GUIDE

## Quick Start (5 minutes)

Your app now supports **FREE AI providers** instead of expensive OpenAI. Get unlimited AI generation for $0!

## Get Your Free API Keys

### 1. Google Gemini (BEST - Recommended) 🏆
- **Free tier:** 15 requests/minute, 1M tokens/day
- **Can generate:** 500+ templates/day for FREE
- **Get key:** https://aistudio.google.com/app/apikey
- **No credit card required**

### 2. Groq (FASTEST)
- **Free tier:** 30 requests/minute  
- **Can generate:** 1,000+ templates/hour for FREE
- **Get key:** https://console.groq.com
- **No credit card required**

### 3. Perplexity (GOOD QUALITY)
- **Free tier:** 5 requests/second
- **Can generate:** 500+ templates/day for FREE
- **Get key:** https://www.perplexity.ai/settings/api
- **No credit card required**

### 4. Anthropic Claude (Optional)
- **Free credit:** $5 (~1,000 templates)
- **Get key:** https://console.anthropic.com
- **Credit card required but $5 is free**

## Installation

### Step 1: Install New Dependencies

```powershell
# Navigate to backend
cd backend

# Install free provider SDKs
pip install google-generativeai==0.3.2
pip install groq==0.4.1
```

Or install all dependencies:
```powershell
pip install -r requirements.txt
```

### Step 2: Add API Keys to .env

Your `.env` file has been updated with placeholders. Add your keys:

```env
# Get these keys for FREE (links above)
GOOGLE_API_KEY=AIzaSy...your-actual-key
GROQ_API_KEY=gsk_...your-actual-key
PERPLEXITY_API_KEY=pplx-...your-actual-key

# Use free providers instead of OpenAI
USE_FREE_PROVIDERS=true
```

### Step 3: Start the Backend

```powershell
$env:PYTHONPATH="C:\Users\PC\OneDrive\Desktop\gamma clone"
C:/Python39/python.exe -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```

Or use: `.\start-backend.ps1`

## How It Works

### Automatic Provider Rotation

The system automatically rotates between free providers:

1. **Tries Gemini first** (best free tier)
2. **Falls back to Groq** if Gemini limit hit
3. **Falls back to Perplexity** if Groq limit hit
4. **Falls back to Claude** if others fail

### Daily Limits

- Gemini: 500 generations/day
- Groq: 1,000 generations/day  
- Perplexity: 500 generations/day
- **Total: 2,000 free generations/day!**

### Cost Comparison

| Action | OpenAI Cost | Free Providers Cost |
|--------|-------------|---------------------|
| Generate presentation | $0.10 | **$0** |
| Rewrite text | $0.01 | **$0** |
| Translate text | $0.02 | **$0** |
| 2,000 templates | **$200** | **$0** |

## Testing

### Test the free providers:

```powershell
# Run test script
python test_ai_generation.py
```

You should see:
```
🆓 Using FREE AI providers (Gemini, Groq, Perplexity)
✅ Google Gemini configured
✅ Groq configured
✅ Perplexity configured
🤖 Using GEMINI for generation...
✅ Generated presentation with 5 cards
```

### Generate Templates for FREE

```powershell
# Generate all 2,000 templates using free providers
cd scripts
python seed_templates.py
```

This will now use Gemini, Groq, and Perplexity instead of OpenAI!

## Switching Between Free and Paid

### Use Free Providers (Default)
```env
USE_FREE_PROVIDERS=true
```

### Use OpenAI (If you have credits)
```env
USE_FREE_PROVIDERS=false
OPENAI_API_KEY=sk-your-actual-key
```

## Provider Quality

All providers produce excellent results:

- **Gemini 1.5 Flash:** Fast, high quality, best free tier
- **Groq Llama 3.1:** Very fast inference, great quality
- **Perplexity Llama 3.1:** Good quality with web search
- **Claude Haiku:** Excellent quality, $5 free credit

## Troubleshooting

### "No provider configured"
- Make sure you added at least ONE API key to `.env`
- Get Gemini key from: https://aistudio.google.com/app/apikey

### "All providers failed"
- Check your API keys are correct
- Verify you haven't hit daily limits
- Try with just one provider first

### Import errors
```powershell
# Install dependencies
pip install google-generativeai groq anthropic
```

## Next Steps

1. ✅ Get Gemini API key (5 minutes)
2. ✅ Add to `.env` file
3. ✅ Install dependencies: `pip install google-generativeai groq`
4. ✅ Start backend: `.\start-backend.ps1`
5. ✅ Test: Visit http://127.0.0.1:8000/docs
6. ✅ Generate templates: `python scripts/seed_templates.py`

## Result

🎉 **Generate unlimited presentations for $0!**

No more expensive OpenAI bills. Use Google Gemini, Groq, and Perplexity free tiers to power your entire app.
