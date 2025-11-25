'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'

declare global {
  interface Window {
    google: any;
  }
}

const BACKEND_URL = 'https://gamma-0od0.onrender.com';
const GOOGLE_CLIENT_ID = '415749045380-vabasi37ntls7qsu5kkusah11uiff1dl.apps.googleusercontent.com';

export default function SignupPage() {
  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [agreed, setAgreed] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [loading, setLoading] = useState(false)
  const router = useRouter()

  useEffect(() => {
    // Load Google Sign-In script
    const script = document.createElement('script')
    script.src = 'https://accounts.google.com/gsi/client'
    script.async = true
    script.defer = true
    
    script.onload = () => {
      if (window.google) {
        window.google.accounts.id.initialize({
          client_id: GOOGLE_CLIENT_ID,
          callback: handleGoogleSignIn,
          auto_select: false
        })
        
        // Render the button
        window.google.accounts.id.renderButton(
          document.getElementById('googleSignInButton'),
          { 
            theme: 'outline', 
            size: 'large',
            width: 400,
            text: 'signup_with'
          }
        )
      }
    }
    
    document.body.appendChild(script)

    return () => {
      if (document.body.contains(script)) {
        document.body.removeChild(script)
      }
    }
  }, [])

  const handleGoogleSignIn = async (response: any) => {
    setError('')
    setLoading(true)
    
    try {
      const res = await fetch(`${BACKEND_URL}/api/v1/auth/google`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ credential: response.credential })
      })
      
      const data = await res.json()
      
      if (!res.ok) {
        throw new Error(data.detail || 'Google sign-in failed')
      }
      
      localStorage.setItem('access_token', data.access_token)
      localStorage.setItem('refresh_token', data.refresh_token)
      
      window.location.href = '/home'
      
    } catch (err: any) {
      console.error('Google sign-in error:', err)
      setError(err.message || 'Failed to sign in with Google')
      setLoading(false)
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setSuccess('')
    
    if (!agreed) {
      setError('Please agree to the Terms of Service and Privacy Policy')
      return
    }
    
    if (password.length < 8) {
      setError('Password must be at least 8 characters')
      return
    }
    
    setLoading(true)
    
    try {
      const res = await fetch(`${BACKEND_URL}/api/v1/auth/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name, email, password })
      })
      
      const data = await res.json()
      
      if (!res.ok) {
        throw new Error(data.detail || 'Registration failed')
      }
      
      localStorage.setItem('access_token', data.access_token)
      localStorage.setItem('refresh_token', data.refresh_token)
      
      window.location.href = '/home'
      
    } catch (err: any) {
      console.error('Registration error:', err)
      setError(err.message || 'Failed to register')
      setLoading(false)
    }
  }

  return (
    <div style={{
      minHeight: '100vh',
      backgroundColor: '#ffffff',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      padding: '16px'
    }}>
      <div style={{ 
        width: '100%', 
        maxWidth: '400px' 
      }}>
        
        {/* Logo */}
        <h1 style={{
          fontSize: '40px',
          fontWeight: '700',
          background: 'linear-gradient(to right, #8B5CF6, #EC4899)',
          WebkitBackgroundClip: 'text',
          WebkitTextFillColor: 'transparent',
          textAlign: 'center',
          marginBottom: '32px'
        }}>
          Gamma
        </h1>

        {/* Heading */}
        <h2 style={{
          fontSize: '24px',
          fontWeight: '600',
          color: '#111827',
          textAlign: 'center',
          marginBottom: '32px'
        }}>
          Create your free account
        </h2>

        {/* Error Message */}
        {error && (
          <div style={{
            padding: '12px 16px',
            backgroundColor: '#FEE2E2',
            border: '1px solid #EF4444',
            borderRadius: '8px',
            color: '#991B1B',
            marginBottom: '20px',
            fontSize: '14px'
          }}>
            {error}
          </div>
        )}

        {/* Success Message */}
        {success && (
          <div style={{
            padding: '12px 16px',
            backgroundColor: '#D1FAE5',
            border: '1px solid #10B981',
            borderRadius: '8px',
            color: '#065F46',
            marginBottom: '20px',
            fontSize: '14px'
          }}>
            {success}
          </div>
        )}

        {/* Form */}
        <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
          
          {/* Name Input */}
          <div>
            <label style={{
              display: 'block',
              fontSize: '14px',
              fontWeight: '500',
              color: '#374151',
              marginBottom: '8px'
            }}>
              Full name
            </label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="John Doe"
              required
              disabled={loading}
              style={{
                width: '100%',
                height: '48px',
                padding: '0 16px',
                fontSize: '16px',
                border: '1px solid #E5E7EB',
                borderRadius: '8px',
                outline: 'none',
                opacity: loading ? 0.6 : 1,
                cursor: loading ? 'not-allowed' : 'text'
              }}
            />
          </div>

          {/* Email Input */}
          <div>
            <label style={{
              display: 'block',
              fontSize: '14px',
              fontWeight: '500',
              color: '#374151',
              marginBottom: '8px'
            }}>
              Email address
            </label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="you@example.com"
              required
              disabled={loading}
              style={{
                width: '100%',
                height: '48px',
                padding: '0 16px',
                fontSize: '16px',
                border: '1px solid #E5E7EB',
                borderRadius: '8px',
                outline: 'none',
                opacity: loading ? 0.6 : 1,
                cursor: loading ? 'not-allowed' : 'text'
              }}
            />
          </div>

          {/* Password Input */}
          <div>
            <label style={{
              display: 'block',
              fontSize: '14px',
              fontWeight: '500',
              color: '#374151',
              marginBottom: '8px'
            }}>
              Password
            </label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
              required
              disabled={loading}
              style={{
                width: '100%',
                height: '48px',
                padding: '0 16px',
                fontSize: '16px',
                border: '1px solid #E5E7EB',
                borderRadius: '8px',
                outline: 'none',
                opacity: loading ? 0.6 : 1,
                cursor: loading ? 'not-allowed' : 'text'
              }}
            />
            <p style={{
              fontSize: '12px',
              color: '#6B7280',
              marginTop: '4px'
            }}>
              Must be at least 8 characters
            </p>
          </div>

          {/* Checkbox */}
          <div style={{ display: 'flex', alignItems: 'flex-start', gap: '8px' }}>
            <input
              type="checkbox"
              checked={agreed}
              onChange={(e) => setAgreed(e.target.checked)}
              disabled={loading}
              style={{
                width: '16px',
                height: '16px',
                marginTop: '4px',
                cursor: loading ? 'not-allowed' : 'pointer'
              }}
            />
            <label style={{
              fontSize: '14px',
              color: '#4B5563'
            }}>
              I agree to the{' '}
              <a href="#" style={{ color: '#8B5CF6', textDecoration: 'none' }}>
                Terms of Service
              </a>
              {' '}and{' '}
              <a href="#" style={{ color: '#8B5CF6', textDecoration: 'none' }}>
                Privacy Policy
              </a>
            </label>
          </div>

          {/* Submit Button */}
          <button
            type="submit"
            disabled={loading}
            style={{
              width: '100%',
              height: '48px',
              background: loading ? '#D1D5DB' : 'linear-gradient(to right, #8B5CF6, #EC4899)',
              color: 'white',
              fontSize: '16px',
              fontWeight: '600',
              border: 'none',
              borderRadius: '8px',
              cursor: loading ? 'not-allowed' : 'pointer',
              opacity: loading ? 0.7 : 1
            }}
          >
            {loading ? 'Creating account...' : 'Create account'}
          </button>
        </form>

        {/* Divider */}
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '16px',
          margin: '24px 0'
        }}>
          <div style={{ flex: 1, height: '1px', backgroundColor: '#E5E7EB' }} />
          <span style={{ fontSize: '14px', color: '#6B7280' }}>
            Or continue with
          </span>
          <div style={{ flex: 1, height: '1px', backgroundColor: '#E5E7EB' }} />
        </div>

        {/* Google Button */}
        <div style={{ marginTop: '20px', display: 'flex', justifyContent: 'center' }}>
          <div id="googleSignInButton"></div>
        </div>

        {/* Bottom Link */}
        <p style={{
          textAlign: 'center',
          marginTop: '24px',
          fontSize: '14px',
          color: '#6B7280'
        }}>
          Already have an account?{' '}
          <a href="/login" onClick={(e) => { e.preventDefault(); router.push('/login'); }} style={{
            color: '#8B5CF6',
            fontWeight: '500',
            textDecoration: 'none',
            cursor: 'pointer'
          }}>
            Sign in
          </a>
        </p>
      </div>
    </div>
  )
}
