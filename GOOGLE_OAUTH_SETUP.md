# Google OAuth Setup Guide

## Quick Setup (5 minutes)

### 1. Create Google OAuth Credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable "Google+ API"
4. Go to **Credentials** → **Create Credentials** → **OAuth client ID**
5. Configure OAuth consent screen:
   - User Type: **External**
   - App name: **Gamma Clone**
   - User support email: Your email
   - Authorized domains: Add your domain (e.g., `vercel.app`)
6. Create OAuth Client ID:
   - Application type: **Web application**
   - Name: **Gamma Clone Web**
   - Authorized JavaScript origins:
     - `http://localhost:3000`
     - `https://frontend-266208fds-dhairyasoniiiiis-projects.vercel.app`
     - `https://your-custom-domain.com` (if you have one)
   - Authorized redirect URIs:
     - `http://localhost:3000`
     - `https://frontend-266208fds-dhairyasoniiiiis-projects.vercel.app`
7. Copy your **Client ID** and **Client Secret**

### 2. Add to Backend Environment Variables

**On Render.com:**
1. Go to your backend service: https://dashboard.render.com/
2. Go to **Environment** tab
3. Add these variables:
   ```
   GOOGLE_CLIENT_ID=your-client-id-here.apps.googleusercontent.com
   GOOGLE_CLIENT_SECRET=your-client-secret-here
   ```
4. Click **Save Changes** (auto-redeploys)

**Local Development (.env file):**
```bash
GOOGLE_CLIENT_ID=your-client-id-here.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-client-secret-here
```

### 3. Add to Frontend Environment Variables

**On Vercel:**
1. Go to your project: https://vercel.com/dhairyasoniiiiis-projects/frontend
2. Go to **Settings** → **Environment Variables**
3. Add:
   ```
   NEXT_PUBLIC_GOOGLE_CLIENT_ID=your-client-id-here.apps.googleusercontent.com
   ```
4. Redeploy: `vercel --prod`

**Local Development (.env.local file):**
```bash
NEXT_PUBLIC_GOOGLE_CLIENT_ID=your-client-id-here.apps.googleusercontent.com
```

### 4. Test Google Sign-In

1. Go to https://frontend-266208fds-dhairyasoniiiiis-projects.vercel.app/signup
2. Click **"Continue with Google"**
3. Select your Google account
4. Should redirect to /home with JWT tokens saved

## Troubleshooting

### "Google Sign-In not loaded"
- Check if NEXT_PUBLIC_GOOGLE_CLIENT_ID is set
- Refresh page to reload Google script

### "Invalid Google token"
- Verify GOOGLE_CLIENT_ID matches between frontend and backend
- Check authorized JavaScript origins in Google Console
- Ensure backend has google-auth package installed

### "OAuth failed"
- Check backend logs on Render
- Verify GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET are set
- Ensure backend requirements.txt has google-auth==2.27.0

## Alternative: Skip Google OAuth

If you want to skip Google OAuth setup temporarily:

1. Just use email/password registration (works without OAuth)
2. Or click "Generate" on homepage (auto-creates guest account)

Google OAuth is optional - the app works without it!
