# Email Setup Guide

## ✅ What's Implemented

1. **Backend Email Service** (`backend/services/email_service.py`)
   - Welcome email with beautiful HTML template
   - Password reset email (ready for future use)
   - Graceful fallback if SMTP not configured

2. **Updated Auth API** (`backend/api/auth.py`)
   - Sends welcome email on registration
   - Non-blocking (won't fail registration if email fails)

3. **Updated Frontend** (`frontend/src/app/(auth)/signup/page.tsx`)
   - Success/error message display
   - Loading states
   - Form validation
   - Redirects to /home after successful signup

4. **Dependencies**
   - `aiosmtplib==3.0.1` added and installed

## 🔧 Configuration (Optional)

### For Gmail SMTP

1. Create app password: https://myaccount.google.com/apppasswords

2. Add to `.env` file (create if doesn't exist):
```env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

### Current Behavior (No SMTP)

Without SMTP configuration, emails will:
- ✅ Not block registration
- ✅ Log to console: "⚠️ SMTP not configured. Email would be sent to..."
- ✅ Show email subject in logs

## 🧪 Testing

### Test Registration (Frontend + Backend)

1. **Start Backend:**
   ```powershell
   $env:PYTHONPATH="C:\Users\PC\OneDrive\Desktop\gamma clone"
   C:/Python39/python.exe -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
   ```

2. **Frontend already running at:** http://localhost:3000

3. **Test signup:**
   - Go to http://localhost:3000/signup
   - Fill in form (name, email, password 8+ chars)
   - Check "I agree" checkbox
   - Click "Create account"
   - Should see green success message
   - Backend logs will show: "⚠️ SMTP not configured. Email would be sent to..."

### Test API Directly

```powershell
# Test registration
Invoke-RestMethod -Uri "http://localhost:8000/api/v1/auth/register" -Method POST -Headers @{"Content-Type"="application/json"} -Body '{"name":"Test User","email":"test@example.com","password":"Password123"}'
```

## 📧 Welcome Email Template

The email includes:
- Gamma gradient logo
- Personalized greeting with user's name
- Feature highlights (bullet list)
- "Get Started" button linking to /home
- Professional footer
- Responsive design (looks good on all devices)

## 🎯 What's Next

You can now:

1. **Test the signup flow** - Create account and see success message
2. **Add SMTP credentials** - To actually send emails (optional)
3. **Build the dashboard** - Create `/home` page for after signup
4. **Add login page** - Similar clean design for /login
5. **Add password reset** - Email service already has reset template ready

## 🔍 Troubleshooting

**"Registration failed"**
- Check backend is running on port 8000
- Check browser console for errors
- Verify backend logs for details

**"Email already registered"**
- User already exists in database
- Use different email or delete from DB

**No email received (with SMTP configured)**
- Check spam folder
- Verify SMTP credentials
- Check backend logs for error details
- Test with `telnet smtp.gmail.com 587`
