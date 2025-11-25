'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';

const BACKEND_URL = 'https://gamma-0od0.onrender.com';
const GOOGLE_CLIENT_ID = '415749045380-vabasi37ntls7qsu5kkusah11uiff1dl.apps.googleusercontent.com';

declare global {
  interface Window {
    google: any;
  }
}

export default function SignupPage() {
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    const script = document.createElement('script');
    script.src = 'https://accounts.google.com/gsi/client';
    script.async = true;
    script.defer = true;
    
    script.onload = () => {
      if (window.google) {
        window.google.accounts.id.initialize({
          client_id: GOOGLE_CLIENT_ID,
          callback: (response: any) => {
            fetch(`${BACKEND_URL}/api/v1/auth/google`, {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ credential: response.credential })
            })
            .then(res => res.json())
            .then(data => {
              localStorage.setItem('access_token', data.access_token);
              localStorage.setItem('refresh_token', data.refresh_token);
              window.location.href = '/dashboard';
            })
            .catch(() => setError('Google signup failed'));
          }
        });
        
        window.google.accounts.id.renderButton(
          document.getElementById('googleButton'),
          { theme: 'outline', size: 'large', width: 368, text: 'signup_with' }
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

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const res = await fetch(`${BACKEND_URL}/api/v1/auth/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name, email, password })
      });

      const data = await res.json();

      if (res.ok && data.access_token) {
        localStorage.setItem('access_token', data.access_token);
        localStorage.setItem('refresh_token', data.refresh_token);
        window.location.href = '/dashboard';
      } else {
        setError(data.detail || 'Signup failed');
        setLoading(false);
      }
    } catch (err) {
      setError('Connection error');
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#fafafa] flex items-center justify-center p-4">
      <div className="w-full max-w-[400px]">
        <Link href="/" className="block text-center mb-8">
          <svg className="w-8 h-8 mx-auto mb-3" viewBox="0 0 32 32" fill="none">
            <rect width="32" height="32" rx="6" fill="url(#gradient)"/>
            <path d="M8 16L14 10L20 16L14 22L8 16Z" fill="white"/>
            <defs>
              <linearGradient id="gradient" x1="0" y1="0" x2="32" y2="32">
                <stop offset="0%" stopColor="#8B5CF6"/>
                <stop offset="100%" stopColor="#EC4899"/>
              </linearGradient>
            </defs>
          </svg>
        </Link>

        <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-8">
          <h1 className="text-2xl font-semibold text-gray-900 text-center mb-2">
            Create your account
          </h1>
          <p className="text-sm text-gray-600 text-center mb-6">
            Start creating beautiful presentations with AI
          </p>

          {error && (
            <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg text-sm text-red-700">
              {error}
            </div>
          )}

          <div className="mb-6">
            <div id="googleButton" className="flex justify-center"></div>
          </div>

          <div className="relative my-6">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-gray-200"></div>
            </div>
            <div className="relative flex justify-center text-xs">
              <span className="px-2 bg-white text-gray-500 uppercase tracking-wide">
                Or continue with email
              </span>
            </div>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1.5">Full name</label>
              <input
                type="text"
                required
                value={name}
                onChange={(e) => setName(e.target.value)}
                className="w-full h-11 px-3.5 text-[15px] border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
                placeholder="John Doe"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1.5">Email</label>
              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full h-11 px-3.5 text-[15px] border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
                placeholder="name@company.com"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1.5">Password</label>
              <input
                type="password"
                required
                minLength={8}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full h-11 px-3.5 text-[15px] border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
                placeholder="••••••••"
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full h-11 bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white text-[15px] font-medium rounded-lg disabled:opacity-50 shadow-sm mt-6"
            >
              {loading ? 'Creating account...' : 'Create account'}
            </button>
          </form>

          <p className="text-center text-sm text-gray-600 mt-6">
            Already have an account?{' '}
            <Link href="/login" className="text-purple-600 hover:text-purple-700 font-medium">
              Sign in
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}
