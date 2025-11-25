'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { Sparkles, Zap, Users, TrendingUp, Check, ChevronDown, Play } from 'lucide-react';

export default function LandingPage() {
  const router = useRouter();
  const [prompt, setPrompt] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleGenerate = async () => {
    if (!prompt.trim()) {
      setError('Please enter a topic');
      return;
    }

    setLoading(true);
    setError('');

    try {
      let token = localStorage.getItem('access_token');
      
      if (!token) {
        const authRes = await fetch('https://gamma-0od0.onrender.com/api/v1/auth/register', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            name: 'Guest User',
            email: `guest${Date.now()}@temp.com`,
            password: 'guestpass123'
          })
        });
        const authData = await authRes.json();
        token = authData.access_token || '';
        if (token) {
          localStorage.setItem('access_token', token);
        }
      }

      const res = await fetch('https://gamma-0od0.onrender.com/api/v1/ai/generate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          prompt: prompt,
          num_cards: 8
        })
      });

      const data = await res.json();
      router.push(`/editor/${data.presentation_id}`);
      
    } catch (err: any) {
      setError('Generation failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-white">
      {/* Navigation - Exact Gamma Style */}
      <nav className="sticky top-0 z-50 bg-white/95 backdrop-blur-md border-b border-gray-200/50">
        <div className="max-w-[1400px] mx-auto px-8 py-3">
          <div className="flex items-center justify-between">
            <Link href="/" className="flex items-center">
              <span className="text-[28px] font-bold gradient-text tracking-tight">γ</span>
            </Link>

            <div className="hidden lg:flex items-center gap-1">
              <button className="flex items-center gap-1.5 px-4 py-2 text-[15px] font-medium text-gray-700 hover:text-gray-900 hover:bg-gray-50 rounded-lg transition-colors">
                Product <ChevronDown className="w-4 h-4" />
              </button>
              <Link href="#" className="px-4 py-2 text-[15px] font-medium text-gray-700 hover:text-gray-900 hover:bg-gray-50 rounded-lg transition-colors">
                Templates
              </Link>
              <Link href="#" className="px-4 py-2 text-[15px] font-medium text-gray-700 hover:text-gray-900 hover:bg-gray-50 rounded-lg transition-colors">
                Pricing
              </Link>
              <Link href="#" className="px-4 py-2 text-[15px] font-medium text-gray-700 hover:text-gray-900 hover:bg-gray-50 rounded-lg transition-colors">
                Resources
              </Link>
            </div>

            <div className="flex items-center gap-3">
              <Link href="/login" className="px-4 py-2 text-[15px] font-medium text-gray-700 hover:text-gray-900 transition-colors">
                Sign in
              </Link>
              <Link href="/signup" className="px-5 py-2.5 text-[15px] font-semibold bg-gradient-to-r from-purple-600 to-pink-600 text-white rounded-full hover:shadow-lg hover:scale-[1.02] active:scale-[0.98] transition-all duration-200">
                Sign up free
              </Link>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section - Gamma Style */}
      <section className="relative pt-20 pb-16 px-6 overflow-hidden">
        {/* Subtle gradient background */}
        <div className="absolute inset-0 bg-gradient-to-b from-purple-50/30 via-white to-white -z-10" />
        
        <div className="max-w-[1100px] mx-auto text-center">
          {/* Main Headline */}
          <h1 className="text-[52px] lg:text-[68px] font-bold leading-[1.1] tracking-tight mb-6 px-4">
            A new medium for
            <br />
            <span className="gradient-text">presenting ideas</span>
          </h1>

          {/* Subheadline */}
          <p className="text-[20px] lg:text-[24px] text-gray-600 mb-10 max-w-[700px] mx-auto leading-relaxed">
            Beautiful, engaging content with none of the formatting and design work
          </p>

          {/* AI Prompt Input */}
          <div className="max-w-[680px] mx-auto mb-8">
            <div className="relative group">
              <input
                type="text"
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleGenerate()}
                placeholder="Enter a topic, paste text, or drop a file..."
                disabled={loading}
                className="w-full h-[62px] px-6 pr-36 text-[16px] rounded-[16px] border-2 border-gray-200 hover:border-gray-300 focus:border-purple-500 focus:outline-none shadow-sm hover:shadow-md focus:shadow-lg transition-all bg-white"
              />
              <button 
                onClick={handleGenerate}
                disabled={loading}
                className="absolute right-2 top-1/2 -translate-y-1/2 h-[48px] px-6 bg-gradient-to-r from-purple-600 to-pink-600 text-white text-[15px] font-semibold rounded-xl hover:shadow-lg hover:scale-[1.02] active:scale-[0.98] transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {loading ? 'Generating...' : 'Generate →'}
              </button>
            </div>
            {error && (
              <p className="text-[14px] text-red-500 mt-3">{error}</p>
            )}
            <p className="text-[14px] text-gray-500 mt-3">
              Try: "Create a pitch deck for a sustainable fashion startup"
            </p>
          </div>

          {/* Quick Actions */}
          <div className="flex items-center justify-center gap-3 flex-wrap">
            <Link href="/signup" className="flex items-center gap-2 px-5 py-3 bg-white border border-gray-300 rounded-xl text-[15px] font-medium hover:border-gray-400 hover:shadow-sm transition-all">
              <Sparkles className="w-4 h-4" />
              Start from scratch
            </Link>
            <Link href="/templates" className="flex items-center gap-2 px-5 py-3 bg-white border border-gray-300 rounded-xl text-[15px] font-medium hover:border-gray-400 hover:shadow-sm transition-all">
              Browse templates
            </Link>
          </div>
        </div>
      </section>

      {/* Demo Video Section */}
      <section className="py-16 px-6">
        <div className="max-w-[1200px] mx-auto">
          <div className="relative aspect-video rounded-[24px] overflow-hidden shadow-2xl bg-gradient-to-br from-purple-500 via-purple-600 to-pink-600 group cursor-pointer">
            <div className="absolute inset-0 bg-black/10" />
            <div className="absolute inset-0 flex items-center justify-center">
              <div className="w-20 h-20 rounded-full bg-white/20 backdrop-blur-sm flex items-center justify-center group-hover:bg-white/30 group-hover:scale-110 transition-all duration-300">
                <Play className="w-8 h-8 text-white fill-white ml-1" />
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-24 px-6 bg-gradient-to-b from-white to-gray-50/50">
        <div className="max-w-[1200px] mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-[42px] lg:text-[52px] font-bold mb-4 tracking-tight">
              Why teams choose Gamma
            </h2>
            <p className="text-[18px] lg:text-[20px] text-gray-600">
              Create better content in a fraction of the time
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {/* Feature Cards */}
            {[
              {
                icon: <Sparkles className="w-6 h-6 text-purple-600" />,
                title: "AI-powered",
                description: "Generate beautiful presentations, documents, and webpages in seconds with AI",
                color: "bg-purple-100"
              },
              {
                icon: <Zap className="w-6 h-6 text-pink-600" />,
                title: "No design skills",
                description: "Built-in templates and smart themes do the formatting for you",
                color: "bg-pink-100"
              },
              {
                icon: <Users className="w-6 h-6 text-purple-600" />,
                title: "Collaborate live",
                description: "Work together in real-time with comments, reactions, and edits",
                color: "bg-purple-100"
              },
              {
                icon: <TrendingUp className="w-6 h-6 text-pink-600" />,
                title: "Built-in analytics",
                description: "Track views, engagement, and performance with detailed analytics",
                color: "bg-pink-100"
              },
              {
                icon: <Check className="w-6 h-6 text-purple-600" />,
                title: "Quick to create",
                description: "Go from idea to polished content in minutes, not hours",
                color: "bg-purple-100"
              },
              {
                icon: <Sparkles className="w-6 h-6 text-pink-600" />,
                title: "Flexible export",
                description: "Export to PDF, PowerPoint, or share as an interactive webpage",
                color: "bg-pink-100"
              },
            ].map((feature, i) => (
              <div key={i} className="bg-white p-8 rounded-[20px] border border-gray-200 hover:border-gray-300 hover:shadow-lg transition-all duration-300 group">
                <div className={`w-12 h-12 ${feature.color} rounded-[14px] flex items-center justify-center mb-5 group-hover:scale-110 transition-transform`}>
                  {feature.icon}
                </div>
                <h3 className="text-[22px] font-bold mb-3">{feature.title}</h3>
                <p className="text-[16px] text-gray-600 leading-relaxed">{feature.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section className="py-24 px-6 bg-white">
        <div className="max-w-[900px] mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-[42px] lg:text-[52px] font-bold mb-4 tracking-tight">How it works</h2>
          </div>

          <div className="space-y-10">
            {[
              {
                number: "1",
                title: "Describe your idea",
                description: "Type a prompt, paste text, or upload a document. Our AI understands your content."
              },
              {
                number: "2",
                title: "AI generates your content",
                description: "Gamma creates beautiful slides with professional design in seconds."
              },
              {
                number: "3",
                title: "Edit and share",
                description: "Refine with our editor, then share or export anywhere."
              }
            ].map((step, i) => (
              <div key={i} className="flex items-start gap-6">
                <div className="flex-shrink-0 w-14 h-14 bg-gradient-to-br from-purple-600 to-pink-600 rounded-[16px] flex items-center justify-center text-white text-[24px] font-bold shadow-lg">
                  {step.number}
                </div>
                <div className="pt-1">
                  <h3 className="text-[24px] font-bold mb-2">{step.title}</h3>
                  <p className="text-[17px] text-gray-600 leading-relaxed">{step.description}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Social Proof */}
      <section className="py-20 px-6 bg-gray-50">
        <div className="max-w-[1200px] mx-auto">
          <p className="text-center text-[15px] text-gray-500 mb-8 font-medium">Trusted by teams at</p>
          <div className="flex items-center justify-center gap-12 flex-wrap opacity-40">
            {['Google', 'Meta', 'Amazon', 'Microsoft', 'Apple'].map((company) => (
              <div key={company} className="text-[26px] font-bold text-gray-900">{company}</div>
            ))}
          </div>

          <div className="grid md:grid-cols-3 gap-8 max-w-[900px] mx-auto mt-20">
            {[
              { stat: "10M+", label: "Presentations created" },
              { stat: "500K+", label: "Active users" },
              { stat: "4.9/5", label: "Average rating" }
            ].map((item, i) => (
              <div key={i} className="text-center">
                <div className="text-[52px] font-bold gradient-text mb-2">{item.stat}</div>
                <p className="text-[16px] text-gray-600">{item.label}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Pricing */}
      <section className="py-24 px-6 bg-white">
        <div className="max-w-[1300px] mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-[42px] lg:text-[52px] font-bold mb-4 tracking-tight">Choose your plan</h2>
            <p className="text-[18px] lg:text-[20px] text-gray-600">Start free, upgrade as you grow</p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-5 max-w-[1200px] mx-auto">
            {/* Pricing Cards */}
            {[
              {
                name: "Free",
                price: "$0",
                features: ["400 AI credits", "Generate up to 10 cards", "Basic templates"],
                featured: false
              },
              {
                name: "Plus",
                price: "$8",
                period: "/mo",
                features: ["Unlimited AI", "1,000 monthly credits", "Remove branding"],
                featured: false
              },
              {
                name: "Pro",
                price: "$18",
                period: "/mo",
                features: ["4,000 monthly credits", "Premium AI models", "Advanced analytics"],
                featured: true
              },
              {
                name: "Ultra",
                price: "$100",
                period: "/mo",
                features: ["20,000 monthly credits", "Studio mode", "Priority support"],
                featured: false
              }
            ].map((plan, i) => (
              <div
                key={i}
                className={`relative rounded-[20px] p-7 ${
                  plan.featured
                    ? 'bg-gradient-to-br from-purple-600 to-pink-600 text-white scale-105 shadow-2xl'
                    : 'bg-white border-2 border-gray-200 hover:border-gray-300 hover:shadow-lg'
                } transition-all duration-300`}
              >
                {plan.featured && (
                  <div className="absolute -top-3 left-1/2 -translate-x-1/2 px-4 py-1 bg-white text-purple-600 text-[13px] font-bold rounded-full">
                    Popular
                  </div>
                )}
                <h3 className="text-[24px] font-bold mb-3">{plan.name}</h3>
                <div className="mb-6">
                  <span className="text-[42px] font-bold">{plan.price}</span>
                  {plan.period && <span className={`text-[18px] ${plan.featured ? 'opacity-80' : 'text-gray-600'}`}>{plan.period}</span>}
                </div>
                <ul className="space-y-3 mb-8">
                  {plan.features.map((feature, j) => (
                    <li key={j} className="flex items-start gap-2 text-[15px]">
                      <Check className={`w-5 h-5 flex-shrink-0 mt-0.5 ${plan.featured ? 'text-white' : 'text-purple-600'}`} />
                      <span className={plan.featured ? 'text-white' : 'text-gray-600'}>{feature}</span>
                    </li>
                  ))}
                </ul>
                <Link
                  href="/signup"
                  className={`block w-full py-3 text-center text-[15px] font-semibold rounded-xl transition-all ${
                    plan.featured
                      ? 'bg-white text-purple-600 hover:bg-gray-50'
                      : 'bg-gray-900 text-white hover:bg-gray-800'
                  }`}
                >
                  {plan.price === "$0" ? 'Get started' : 'Start free trial'}
                </Link>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-900 text-white py-16 px-6">
        <div className="max-w-[1200px] mx-auto">
          <div className="grid md:grid-cols-4 gap-10 mb-12">
            {[
              {
                title: "Product",
                links: ["Features", "Templates", "Pricing", "Roadmap"]
              },
              {
                title: "Resources",
                links: ["Help Center", "Tutorials", "API Docs", "Blog"]
              },
              {
                title: "Company",
                links: ["About", "Careers", "Contact", "Press"]
              },
              {
                title: "Social",
                links: ["Twitter", "LinkedIn", "Instagram", "YouTube"]
              }
            ].map((column, i) => (
              <div key={i}>
                <h4 className="text-[15px] font-bold mb-4">{column.title}</h4>
                <ul className="space-y-2.5">
                  {column.links.map((link, j) => (
                    <li key={j}>
                      <Link href="#" className="text-[14px] text-gray-400 hover:text-white transition-colors">
                        {link}
                      </Link>
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>

          <div className="border-t border-gray-800 pt-8">
            <p className="text-center text-[14px] text-gray-400">© 2025 Gamma. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </div>
  );
}
