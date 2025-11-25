'use client'

import { useEffect, useState } from 'react'
import { useRouter, useParams } from 'next/navigation'

interface Card {
  type: string
  title: string
  content: string
  layout?: string
}

interface Presentation {
  id: string
  title: string
  cards: Card[]
  theme: any
}

export default function EditorPage() {
  const params = useParams()
  const router = useRouter()
  const [presentation, setPresentation] = useState<Presentation | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [editingCard, setEditingCard] = useState<number | null>(null)

  useEffect(() => {
    loadPresentation()
  }, [params.id])

  const loadPresentation = async () => {
    try {
      const token = localStorage.getItem('access_token')
      if (!token) {
        router.push('/signup')
        return
      }

      const res = await fetch(`https://gamma-0od0.onrender.com/api/v1/presentations/${params.id}`, {
        headers: { 'Authorization': `Bearer ${token}` }
      })

      if (!res.ok) throw new Error('Failed to load presentation')
      
      const data = await res.json()
      setPresentation(data)
    } catch (err: any) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const updateCard = async (index: number, field: string, value: string) => {
    if (!presentation) return

    const updatedCards = [...presentation.cards]
    updatedCards[index] = { ...updatedCards[index], [field]: value }
    setPresentation({ ...presentation, cards: updatedCards })

    // Auto-save to backend
    try {
      const token = localStorage.getItem('access_token')
      await fetch(`https://gamma-0od0.onrender.com/api/v1/presentations/${params.id}`, {
        method: 'PATCH',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ cards: updatedCards })
      })
    } catch (err) {
      console.error('Auto-save failed:', err)
    }
  }

  const exportPDF = async () => {
    try {
      const token = localStorage.getItem('access_token')
      const res = await fetch(`https://gamma-0od0.onrender.com/api/v1/export/pdf/${params.id}`, {
        headers: { 'Authorization': `Bearer ${token}` }
      })
      const blob = await res.blob()
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `${presentation?.title || 'presentation'}.pdf`
      a.click()
    } catch (err) {
      alert('Export failed')
    }
  }

  if (loading) return <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100vh', fontSize: '24px' }}>Loading...</div>
  if (error) return <div style={{ padding: '40px', textAlign: 'center', color: '#EF4444' }}>Error: {error}</div>
  if (!presentation) return <div>Presentation not found</div>

  return (
    <div style={{ minHeight: '100vh', backgroundColor: '#FAFAFA' }}>
      {/* Top Bar */}
      <div style={{
        backgroundColor: '#FFFFFF',
        borderBottom: '1px solid #E5E7EB',
        padding: '16px 24px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
          <h1 style={{
            fontSize: '20px',
            fontWeight: '600',
            background: 'linear-gradient(to right, #8B5CF6, #EC4899)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
            margin: 0
          }}>Gamma</h1>
          <input
            type="text"
            value={presentation.title}
            onChange={(e) => setPresentation({ ...presentation, title: e.target.value })}
            style={{
              fontSize: '16px',
              border: 'none',
              outline: 'none',
              fontWeight: '500',
              padding: '4px 8px'
            }}
          />
        </div>
        
        <div style={{ display: 'flex', gap: '12px' }}>
          <button
            onClick={exportPDF}
            style={{
              padding: '10px 20px',
              backgroundColor: '#FFFFFF',
              border: '1px solid #E5E7EB',
              borderRadius: '8px',
              fontSize: '14px',
              fontWeight: '500',
              cursor: 'pointer'
            }}
          >
            Export PDF
          </button>
          <button
            onClick={() => router.push('/')}
            style={{
              padding: '10px 20px',
              background: 'linear-gradient(to right, #8B5CF6, #EC4899)',
              border: 'none',
              borderRadius: '8px',
              color: 'white',
              fontSize: '14px',
              fontWeight: '500',
              cursor: 'pointer'
            }}
          >
            Done
          </button>
        </div>
      </div>

      {/* Cards */}
      <div style={{
        maxWidth: '900px',
        margin: '0 auto',
        padding: '40px 24px'
      }}>
        {presentation.cards.map((card, index) => (
          <div
            key={index}
            onClick={() => setEditingCard(index)}
            style={{
              backgroundColor: '#FFFFFF',
              borderRadius: '12px',
              padding: '32px',
              marginBottom: '24px',
              boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
              cursor: 'pointer',
              border: editingCard === index ? '2px solid #8B5CF6' : '2px solid transparent'
            }}
          >
            {editingCard === index ? (
              <>
                <input
                  type="text"
                  value={card.title}
                  onChange={(e) => updateCard(index, 'title', e.target.value)}
                  style={{
                    width: '100%',
                    fontSize: '28px',
                    fontWeight: '700',
                    border: 'none',
                    outline: 'none',
                    marginBottom: '16px',
                    color: '#111827'
                  }}
                  placeholder="Card title"
                />
                <textarea
                  value={card.content}
                  onChange={(e) => updateCard(index, 'content', e.target.value)}
                  style={{
                    width: '100%',
                    fontSize: '16px',
                    border: 'none',
                    outline: 'none',
                    minHeight: '100px',
                    color: '#4B5563',
                    lineHeight: '1.6',
                    fontFamily: 'inherit',
                    resize: 'vertical'
                  }}
                  placeholder="Card content"
                />
              </>
            ) : (
              <>
                <h2 style={{
                  fontSize: '28px',
                  fontWeight: '700',
                  color: '#111827',
                  marginBottom: '16px'
                }}>
                  {card.title || 'Untitled'}
                </h2>
                <p style={{
                  fontSize: '16px',
                  color: '#4B5563',
                  lineHeight: '1.6',
                  whiteSpace: 'pre-wrap'
                }}>
                  {card.content}
                </p>
              </>
            )}
          </div>
        ))}
      </div>
    </div>
  )
}
