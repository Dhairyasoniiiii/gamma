# 🧪 TESTING GUIDE - Gamma Clone Backend

Quick guide to test all your backend features!

---

## 🚀 Quick Start

### 1. Start the Backend
```powershell
cd "c:\Users\PC\OneDrive\Desktop\gamma clone"

# Add your OpenAI API key
echo "OPENAI_API_KEY=sk-your-actual-key-here" > .env
echo "STRIPE_SECRET_KEY=sk_test_your-key" >> .env

# Start all services
docker-compose up -d

# Check logs
docker-compose logs -f backend
```

### 2. Access API Documentation
Open browser: **http://localhost:8000/docs**

---

## 📋 Test Checklist

### ✅ Health Check
```bash
GET http://localhost:8000/health
```
Expected: `{"status": "healthy"}`

---

### 🔐 Authentication Tests

#### 1. Register User
```json
POST http://localhost:8000/api/v1/auth/register

{
  "email": "test@example.com",
  "password": "TestPassword123!",
  "full_name": "Test User"
}
```

#### 2. Login
```json
POST http://localhost:8000/api/v1/auth/login

{
  "email": "test@example.com",
  "password": "TestPassword123!"
}
```
**Save the `access_token` for next requests!**

#### 3. Get Current User
```bash
GET http://localhost:8000/api/v1/auth/me
Authorization: Bearer YOUR_ACCESS_TOKEN
```

---

### 🤖 AI Generation Tests

#### 1. Generate Presentation
```json
POST http://localhost:8000/api/v1/ai/generate
Authorization: Bearer YOUR_TOKEN

{
  "prompt": "Create a presentation about sustainable energy",
  "num_cards": 8,
  "style": "professional"
}
```

#### 2. Rewrite Text
```json
POST http://localhost:8000/api/v1/ai/rewrite
Authorization: Bearer YOUR_TOKEN

{
  "text": "This is some text",
  "instruction": "improve"
}
```

#### 3. Translate Text
```json
POST http://localhost:8000/api/v1/ai/translate
Authorization: Bearer YOUR_TOKEN

{
  "text": "Hello, how are you?",
  "target_language": "Spanish"
}
```

#### 4. Generate Image (Plus+ plans)
```json
POST http://localhost:8000/api/v1/ai/image
Authorization: Bearer YOUR_TOKEN

{
  "prompt": "A modern office workspace"
}
```

#### 5. Check Credits
```bash
GET http://localhost:8000/api/v1/ai/credits
Authorization: Bearer YOUR_TOKEN
```

---

### 📄 Presentation Tests

#### 1. Create Presentation
```json
POST http://localhost:8000/api/v1/presentations/
Authorization: Bearer YOUR_TOKEN

{
  "title": "My First Presentation",
  "content": {
    "cards": [
      {
        "type": "title",
        "title": "Welcome",
        "subtitle": "To my presentation"
      },
      {
        "type": "text",
        "title": "Introduction",
        "content": "This is the introduction."
      }
    ]
  },
  "is_public": false
}
```

#### 2. List Presentations
```bash
GET http://localhost:8000/api/v1/presentations/
Authorization: Bearer YOUR_TOKEN
```

#### 3. Get Single Presentation
```bash
GET http://localhost:8000/api/v1/presentations/1
Authorization: Bearer YOUR_TOKEN
```

#### 4. Update Presentation
```json
PATCH http://localhost:8000/api/v1/presentations/1
Authorization: Bearer YOUR_TOKEN

{
  "title": "Updated Title",
  "is_public": true
}
```

#### 5. Duplicate Presentation
```bash
POST http://localhost:8000/api/v1/presentations/1/duplicate
Authorization: Bearer YOUR_TOKEN
```

#### 6. Archive Presentation
```bash
DELETE http://localhost:8000/api/v1/presentations/1
Authorization: Bearer YOUR_TOKEN
```

#### 7. Restore Archived
```bash
POST http://localhost:8000/api/v1/presentations/1/restore
Authorization: Bearer YOUR_TOKEN
```

#### 8. Get Statistics
```bash
GET http://localhost:8000/api/v1/presentations/1/stats
Authorization: Bearer YOUR_TOKEN
```

---

### 📋 Template Tests

#### 1. List All Templates
```bash
GET http://localhost:8000/api/v1/templates/
```

#### 2. Filter by Category
```bash
GET http://localhost:8000/api/v1/templates/?category=pitch&limit=10
```

#### 3. Search Templates
```bash
GET http://localhost:8000/api/v1/templates/search/query?q=business
```

#### 4. Get Featured Templates
```bash
GET http://localhost:8000/api/v1/templates/featured/all?limit=12
```

#### 5. Get Template by ID
```bash
GET http://localhost:8000/api/v1/templates/1
```

#### 6. Get Templates by Category
```bash
GET http://localhost:8000/api/v1/templates/category/pitch
```

#### 7. Create Custom Template (Pro+ only)
```json
POST http://localhost:8000/api/v1/templates/
Authorization: Bearer YOUR_TOKEN

{
  "name": "My Custom Template",
  "description": "A custom template",
  "category": "business",
  "content": {"cards": []},
  "tags": ["custom", "business"]
}
```

---

### 🎨 Theme Tests

#### 1. List All Themes
```bash
GET http://localhost:8000/api/v1/themes/
```

#### 2. Filter by Category
```bash
GET http://localhost:8000/api/v1/themes/?category=professional
```

#### 3. Get Featured Themes
```bash
GET http://localhost:8000/api/v1/themes/featured/all
```

#### 4. Get Theme by ID
```bash
GET http://localhost:8000/api/v1/themes/1
```

#### 5. Create Custom Theme (Pro+ only)
```json
POST http://localhost:8000/api/v1/themes/
Authorization: Bearer YOUR_TOKEN

{
  "name": "My Custom Theme",
  "description": "A custom theme",
  "category": "professional",
  "colors": {
    "primary": "#2563eb",
    "secondary": "#7c3aed",
    "background": "#ffffff",
    "text": "#1f2937"
  },
  "fonts": {
    "heading": "Inter",
    "body": "Inter"
  }
}
```

---

### 📤 Export Tests

#### 1. Export to PDF (Plus+)
```bash
POST http://localhost:8000/api/v1/export/1?export_format=pdf
Authorization: Bearer YOUR_TOKEN
```

#### 2. Export to PowerPoint (Pro+)
```bash
POST http://localhost:8000/api/v1/export/1?export_format=pptx
Authorization: Bearer YOUR_TOKEN
```

#### 3. Export to HTML (All plans)
```bash
POST http://localhost:8000/api/v1/export/1?export_format=html
Authorization: Bearer YOUR_TOKEN
```

#### 4. Export to Markdown (All plans)
```bash
POST http://localhost:8000/api/v1/export/1?export_format=markdown
Authorization: Bearer YOUR_TOKEN
```

#### 5. Get Available Formats
```bash
GET http://localhost:8000/api/v1/export/formats
Authorization: Bearer YOUR_TOKEN
```

---

### 📊 Analytics Tests

#### 1. Get Presentation Analytics
```bash
GET http://localhost:8000/api/v1/analytics/presentation/1?days=30
Authorization: Bearer YOUR_TOKEN
```

#### 2. Get User Dashboard
```bash
GET http://localhost:8000/api/v1/analytics/user/dashboard?days=30
Authorization: Bearer YOUR_TOKEN
```

#### 3. Get Quick Stats
```bash
GET http://localhost:8000/api/v1/analytics/dashboard/quick
Authorization: Bearer YOUR_TOKEN
```

#### 4. Track Event
```json
POST http://localhost:8000/api/v1/analytics/track
Authorization: Bearer YOUR_TOKEN

{
  "event_type": "view",
  "presentation_id": 1,
  "metadata": {"source": "direct"}
}
```

#### 5. Get Views Trend
```bash
GET http://localhost:8000/api/v1/analytics/presentation/1/trend?days=30
Authorization: Bearer YOUR_TOKEN
```

---

### 🤝 Collaboration Tests

#### 1. Share Presentation
```json
POST http://localhost:8000/api/v1/collaboration/1/share
Authorization: Bearer YOUR_TOKEN

{
  "email": "colleague@example.com",
  "permission": "edit",
  "message": "Check out my presentation!"
}
```

#### 2. Get Shares
```bash
GET http://localhost:8000/api/v1/collaboration/1/shares
Authorization: Bearer YOUR_TOKEN
```

#### 3. Add Comment
```json
POST http://localhost:8000/api/v1/collaboration/1/comments
Authorization: Bearer YOUR_TOKEN

{
  "card_id": "card_1",
  "content": "Great slide!",
  "position": {"x": 100, "y": 200}
}
```

#### 4. Get Comments
```bash
GET http://localhost:8000/api/v1/collaboration/1/comments
Authorization: Bearer YOUR_TOKEN
```

#### 5. Get Version History
```bash
GET http://localhost:8000/api/v1/collaboration/1/versions
Authorization: Bearer YOUR_TOKEN
```

#### 6. Create Public Link
```bash
POST http://localhost:8000/api/v1/collaboration/1/public-link
Authorization: Bearer YOUR_TOKEN
```

---

### 💳 Billing Tests

#### 1. Get All Plans
```bash
GET http://localhost:8000/api/v1/billing/plans
```

#### 2. Subscribe to Plan
```json
POST http://localhost:8000/api/v1/billing/subscribe
Authorization: Bearer YOUR_TOKEN

{
  "plan": "plus",
  "billing_period": "monthly",
  "payment_method_id": "pm_test_123"
}
```

#### 3. Get Current Subscription
```bash
GET http://localhost:8000/api/v1/billing/subscription
Authorization: Bearer YOUR_TOKEN
```

#### 4. Change Plan
```json
POST http://localhost:8000/api/v1/billing/change-plan
Authorization: Bearer YOUR_TOKEN

{
  "plan": "pro",
  "billing_period": "monthly"
}
```

#### 5. Get Invoices
```bash
GET http://localhost:8000/api/v1/billing/invoices?limit=10
Authorization: Bearer YOUR_TOKEN
```

---

## 🔧 Generate Test Data

### 1. Generate Themes
```powershell
docker-compose exec backend python scripts/seed_themes.py
```

### 2. Generate Templates
```powershell
docker-compose exec backend python scripts/seed_templates.py
```

---

## 📱 Using Postman

### 1. Import Collection
Create a Postman collection with:
- Base URL: `http://localhost:8000`
- Authorization: Bearer Token
- Content-Type: application/json

### 2. Set Environment Variables
```
BASE_URL = http://localhost:8000
ACCESS_TOKEN = (paste your token here after login)
```

### 3. Test All Endpoints
Use the examples above in Postman!

---

## 🐛 Troubleshooting

### Backend Not Starting?
```powershell
# Check logs
docker-compose logs backend

# Restart services
docker-compose restart

# Rebuild if needed
docker-compose up -d --build
```

### Database Issues?
```powershell
# Check PostgreSQL
docker-compose logs postgres

# Reset database
docker-compose down -v
docker-compose up -d
```

### Import Errors?
The backend dependencies aren't installed yet (this is normal).
When you run `docker-compose up`, all dependencies will be installed automatically.

---

## ✅ Success Criteria

You should be able to:
- ✅ Register and login users
- ✅ Generate presentations with AI
- ✅ Create, read, update, delete presentations
- ✅ Browse templates and themes
- ✅ Export to multiple formats
- ✅ Track analytics
- ✅ Share and collaborate
- ✅ Manage subscriptions

---

## 📊 Expected Results

### After Testing:
- User created with 400 credits (Free plan)
- Presentations generated using AI
- Templates and themes available
- Exports working (HTML, Markdown for free users)
- Analytics tracking views
- Credits deducted after AI operations

---

## 🎯 Next Steps

1. ✅ Test all endpoints
2. ✅ Verify credit system works
3. ✅ Check export formats
4. ✅ Test plan upgrades
5. ✅ Verify analytics tracking

Then: **BUILD THE FRONTEND!** 🚀

---

**Happy Testing!** 🎉
