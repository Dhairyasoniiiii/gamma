'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';

declare global {
  interface Window {
    google: any;
  }
}

const BACKEND_URL = 'https://gamma-0od0.onrender.com';
const GOOGLE_CLIENT_ID = '415749045380-vabasi37ntls7qsu5kkusah11uiff1dl.apps.googleusercontent.com';

export default function LoginPage() {
  const router = useRouter();
  
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  useEffect(() => {
    // Load Google Sign-In script
    const script = document.createElement('script');
    script.src = 'https://accounts.google.com/gsi/client';
    script.async = true;
    script.defer = true;
    
    script.onload = () => {
      if (window.google) {
        window.google.accounts.id.initialize({
          client_id: GOOGLE_CLIENT_ID,
          callback: handleGoogleSignIn,
          auto_select: false
        });
        
        // Render the button
        window.google.accounts.id.renderButton(
          document.getElementById('googleSignInButton'),
          { 
            theme: 'outline', 
            size: 'large',
            width: 400,
            text: 'continue_with'
          }
        );
      }
    };
    
    document.body.appendChild(script);

    return () => {
      if (document.body.contains(script)) {
        document.body.removeChild(script);
      }
    };
  }, []);

  const handleGoogleSignIn = async (response: any) => {
    setError('');
    setLoading(true);
    
    try {
      const res = await fetch(`${BACKEND_URL}/api/v1/auth/google`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ credential: response.credential })
      });
      
      const data = await res.json();
      
      if (!res.ok) {
        throw new Error(data.detail || 'Google sign-in failed');
      }
      
      localStorage.setItem('access_token', data.access_token);
      localStorage.setItem('refresh_token', data.refresh_token);
      
      window.location.href = '/home';
      
    } catch (err: any) {
      console.error('Google sign-in error:', err);
      setError(err.message || 'Failed to sign in with Google');
      setLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setSuccess('');
    
    if (!email || !password) {
      setError('Please fill in all fields');
      return;
    }
    
    setLoading(true);
    
    try {
      const formData = new URLSearchParams();
      formData.append('username', email);
      formData.append('password', password);
      
      const res = await fetch(`${BACKEND_URL}/api/v1/auth/login`, {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/x-www-form-urlencoded'
        },
        body: formData.toString()
      });
      
      const data = await res.json();
      
      if (!res.ok) {
        throw new Error(data.detail || 'Invalid email or password');
      }
      
      localStorage.setItem('access_token', data.access_token);
      localStorage.setItem('refresh_token', data.refresh_token);
      
      window.location.href = '/home';
      
    } catch (error: any) {
      console.error('Login error:', error);
      setError(error.message || 'Failed to login');
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-white flex items-center justify-center px-6">
      
      <div className="w-full max-w-md">
        {/* Logo */}
        <div className="text-center mb-8">
          <Link href="/" className="inline-block">
            <h1 className="text-3xl font-bold gradient-text">Gamma</h1>
          </Link>
          <p className="text-gray-600 mt-2">Welcome back</p>
        </div>

        {/* Error Message */}
        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
            {error}
          </div>
        )}

        {/* Success Message */}
        {success && (
          <div className="mb-6 p-4 bg-green-50 border border-green-200 rounded-lg text-green-700 text-sm">
            {success}
          </div>
        )}

        {/* Form */}
        <div className="bg-white border border-gray-200 rounded-2xl p-8 shadow-sm">
          <form onSubmit={handleSubmit} className="space-y-5">
            {/* Email */}
            <div>
              <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-2">
                Email address
              </label>
              <input
                id="email"
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                disabled={loading}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-600 focus:border-transparent transition-all disabled:opacity-50"
                placeholder="you@example.com"
              />
            </div>

            {/* Password */}
            <div>
              <div className="flex items-center justify-between mb-2">
                <label htmlFor="password" className="block text-sm font-medium text-gray-700">
                  Password
                </label>
                <Link href="#" className="text-sm text-purple-600 hover:text-purple-700">
                  Forgot password?
                </Link>
              </div>
              <input
                id="password"
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                disabled={loading}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-600 focus:border-transparent transition-all disabled:opacity-50"
                placeholder="••••••••"
              />
            </div>

            {/* Submit Button */}
            <button
              type="submit"
              disabled={loading}
              className="w-full py-3 bg-gradient-purple-pink text-white rounded-lg font-medium hover:opacity-90 transition-opacity disabled:opacity-50 disabled:cursor-not-allowed shadow-md"
            >
              {loading ? 'Signing in...' : 'Sign in'}
            </button>
          </form>

          {/* OAuth Buttons */}
          <div className="mt-6">
            <div className="relative">
              <div className="absolute inset-0 flex items-center">
                <div className="w-full border-t border-gray-300"></div>
              </div>
              <div className="relative flex justify-center text-sm">
                <span className="px-4 bg-white text-gray-500">Or continue with</span>
              </div>
            </div>

            <div className="mt-6 flex justify-center">
              <div id="googleSignInButton"></div>
            </div>
          </div>

          {/* Sign Up Link */}
          <div className="mt-6 text-center text-sm text-gray-600">
            Don&apos;t have an account?{' '}
            <Link href="/signup" className="text-purple-600 font-medium hover:text-purple-700">
              Sign up
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
