"""
TRENDING TEMPLATE GENERATOR AGENT
Generates 200+ premium templates daily based on Google Trends
"""

import asyncio
import aiohttp
from typing import List, Dict
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
import json
import random

from backend.services.ai_service import AIService
from backend.db.base import SessionLocal
from backend.models.template import Template
from backend.models.theme import Theme
from backend.config import settings
import os


class TrendingTemplateAgent:
    """
    Advanced Agent that:
    1. Scrapes Google Trends every hour
    2. Generates 200 SEO-optimized prompts daily
    3. Creates 8-9 premium templates per hour
    4. Uses advanced design patterns
    5. Runs continuously 24/7
    """
    
    def __init__(self):
        self.ai_service = AIService()
        self.db = SessionLocal()
        
        # Design quality levels (better than Gamma)
        self.design_levels = [
            "ultra_premium",
            "premium_plus", 
            "premium",
            "professional_plus"
        ]
        
        # Advanced style combinations
        self.style_combinations = [
            "minimalist_modern_luxury",
            "bold_cinematic_3d",
            "swiss_typography_grid",
            "brutalist_neo_modern",
            "glassmorphism_futuristic",
            "retro_wave_premium",
            "organic_flowing_shapes",
            "data_viz_storytelling",
            "editorial_magazine_layout",
            "architectural_minimalism"
        ]
        
        # Template generation count
        self.daily_target = 200
        self.hourly_target = 8  # 8-9 per hour = 192-216 per day
        
        # Try to import pytrends, but provide fallback
        try:
            from pytrends.request import TrendReq
            self.trends_client = TrendReq(hl='en-US', tz=360)
            self.use_trends = True
        except ImportError:
            print("⚠️  pytrends not installed. Using backup trending topics.")
            self.trends_client = None
            self.use_trends = False
        
    async def run_forever(self):
        """Main loop - runs 24/7"""
        print("\n" + "="*80)
        print("🚀 TRENDING TEMPLATE AGENT STARTED")
        print("="*80)
        print(f"📊 Target: {self.daily_target} premium templates per day")
        print(f"⏰ Generating {self.hourly_target}-9 templates every hour")
        print(f"🎨 Design Levels: {len(self.design_levels)} quality tiers")
        print(f"✨ Style Combinations: {len(self.style_combinations)} unique styles")
        print("="*80 + "\n")
        
        while True:
            try:
                # Every hour: get trends and generate templates
                await self.hourly_generation_cycle()
                
                # Wait 1 hour
                print(f"\n💤 Sleeping for 1 hour until next cycle...")
                await asyncio.sleep(3600)
                
            except KeyboardInterrupt:
                print("\n\n⚠️  Agent stopped by user")
                break
            except Exception as e:
                print(f"❌ Error in main loop: {str(e)}")
                await asyncio.sleep(60)  # Wait 1 minute on error
    
    async def hourly_generation_cycle(self):
        """Generate 8-9 templates every hour based on trends"""
        
        print(f"\n{'='*80}")
        print(f"⏰ HOURLY GENERATION CYCLE - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*80}\n")
        
        # Step 1: Get trending topics
        trending_topics = await self.get_trending_topics()
        print(f"📈 Found {len(trending_topics)} trending topics")
        
        # Step 2: Generate SEO-optimized prompts
        seo_prompts = await self.generate_seo_prompts(trending_topics, count=9)
        print(f"✍️  Generated {len(seo_prompts)} SEO-optimized prompts")
        
        # Step 3: Create premium templates
        generated_count = 0
        for i, prompt_data in enumerate(seo_prompts, 1):
            try:
                print(f"\n[{i}/{len(seo_prompts)}] Generating: {prompt_data['title'][:60]}...")
                
                template = await self.create_premium_template(prompt_data)
                
                await self.save_template(template)
                
                print(f"   ✅ Template created: {template['title']}")
                print(f"   📦 Cards: {template['card_count']} | Style: {template['style']}")
                
                generated_count += 1
                
                # Rate limiting (3 seconds between generations)
                await asyncio.sleep(3)
                
            except Exception as e:
                print(f"   ❌ Failed: {str(e)}")
                continue
        
        print(f"\n{'='*80}")
        print(f"✅ Completed hourly cycle: {generated_count}/{len(seo_prompts)} templates generated")
        print(f"📊 Daily progress: ~{generated_count * 24}/{self.daily_target} (if running 24/7)")
        print(f"{'='*80}\n")
    
    async def get_trending_topics(self) -> List[str]:
        """Scrape Google Trends for hot topics"""
        
        trending_topics = []
        
        if self.use_trends and self.trends_client:
            try:
                # Method 1: Real-time trending searches
                trending_searches_df = self.trends_client.trending_searches(pn='united_states')
                trending_topics.extend(trending_searches_df[0].tolist()[:20])
                
                # Method 2: Today's searches
                today_searches_df = self.trends_client.today_searches(pn='US')
                trending_topics.extend(today_searches_df['title'].tolist()[:10])
                
                print("   ✅ Retrieved live Google Trends data")
                
            except Exception as e:
                print(f"   ⚠️  Trends scraping failed: {str(e)}")
                trending_topics = self._get_backup_trending_topics()
        else:
            trending_topics = self._get_backup_trending_topics()
        
        # Remove duplicates
        trending_topics = list(set(trending_topics))
        
        return trending_topics[:30]  # Top 30
    
    def _get_backup_trending_topics(self) -> List[str]:
        """Backup trending topics when API fails"""
        return [
            "AI and Machine Learning",
            "Cryptocurrency trends",
            "Climate change solutions",
            "Remote work strategies",
            "Mental health awareness",
            "Sustainable living",
            "Tech innovation 2025",
            "Startup funding",
            "E-commerce growth",
            "Digital marketing",
            "Personal finance",
            "Health and wellness",
            "Education technology",
            "Social media strategy",
            "Cybersecurity",
            "Cloud computing",
            "Data analytics",
            "Mobile app development",
            "Video content creation",
            "Influencer marketing",
            "Web3 and NFTs",
            "Electric vehicles",
            "Renewable energy",
            "Quantum computing",
            "Biotech innovations",
            "Space exploration",
            "Metaverse platforms",
            "5G technology",
            "Robotics automation",
            "Virtual reality"
        ]
    
    async def generate_seo_prompts(self, trending_topics: List[str], count: int = 9) -> List[Dict]:
        """Generate SEO-optimized prompts from trending topics"""
        
        prompts = []
        
        # Select random topics
        selected_topics = random.sample(
            trending_topics, 
            min(count, len(trending_topics))
        )
        
        for topic in selected_topics:
            # Use AI to create SEO-optimized title and description
            seo_prompt = f"""Create an SEO-optimized presentation template title and description for the trending topic: "{topic}"

Requirements:
- Title should be catchy, professional, and under 60 characters
- Include relevant keywords for SEO
- Make it appealing for business/professional use
- Description should be 150-160 characters

Return JSON:
{{
  "title": "SEO-optimized title",
  "description": "SEO-optimized description",
  "keywords": ["keyword1", "keyword2", "keyword3"],
  "category": "business|technology|marketing|finance|education|creative|health|sales",
  "target_audience": "who will use this"
}}"""
            
            try:
                # Use the free AI service if OpenAI key not available
                if self.ai_service.use_free:
                    # Fallback: Create SEO prompt manually
                    seo_data = self._create_fallback_seo_data(topic)
                else:
                    # Use OpenAI for premium results
                    response = await self.ai_service.client.chat.completions.create(
                        model=settings.DEFAULT_TEXT_MODEL,
                        messages=[
                            {"role": "system", "content": "You are an SEO and marketing expert."},
                            {"role": "user", "content": seo_prompt}
                        ],
                        response_format={"type": "json_object"},
                        temperature=0.8
                    )
                    
                    seo_data = json.loads(response.choices[0].message.content)
                
                seo_data['original_topic'] = topic
                seo_data['design_level'] = random.choice(self.design_levels)
                seo_data['style'] = random.choice(self.style_combinations)
                
                prompts.append(seo_data)
                
            except Exception as e:
                print(f"   ⚠️  SEO generation failed for '{topic}': {str(e)}")
                # Use fallback
                seo_data = self._create_fallback_seo_data(topic)
                seo_data['original_topic'] = topic
                seo_data['design_level'] = random.choice(self.design_levels)
                seo_data['style'] = random.choice(self.style_combinations)
                prompts.append(seo_data)
                continue
        
        return prompts
    
    def _create_fallback_seo_data(self, topic: str) -> Dict:
        """Create SEO data when AI generation fails"""
        
        # Simple SEO optimization
        title = f"Professional {topic} Presentation Template"
        description = f"Create stunning {topic} presentations with our premium template. Perfect for professionals and businesses."
        
        # Extract keywords from topic
        keywords = [word.lower() for word in topic.split() if len(word) > 3]
        keywords.extend(['presentation', 'template', 'professional'])
        
        # Categorize based on keywords
        category_mapping = {
            'business': ['business', 'startup', 'company', 'corporate'],
            'technology': ['tech', 'ai', 'software', 'digital', 'cyber'],
            'marketing': ['marketing', 'social', 'brand', 'advertising'],
            'finance': ['finance', 'investment', 'crypto', 'trading'],
            'education': ['education', 'learning', 'training', 'course'],
            'health': ['health', 'wellness', 'medical', 'fitness'],
            'sales': ['sales', 'revenue', 'growth', 'customer']
        }
        
        category = 'business'  # Default
        for cat, words in category_mapping.items():
            if any(word in topic.lower() for word in words):
                category = cat
                break
        
        return {
            'title': title[:60],
            'description': description[:160],
            'keywords': keywords[:5],
            'category': category,
            'target_audience': 'Business professionals and entrepreneurs'
        }
    
    async def create_premium_template(self, prompt_data: Dict) -> Dict:
        """Create ultra-premium template with advanced design"""
        
        # Build enhanced prompt with design instructions
        enhanced_prompt = f"""Create an ULTRA PREMIUM presentation template about: {prompt_data['title']}

DESIGN REQUIREMENTS:
- Design Level: {prompt_data['design_level']}
- Style: {prompt_data['style']}
- Must be MORE STYLISH than Gamma.app templates
- Use advanced design patterns
- Professional color harmony
- Typography excellence
- Visual hierarchy mastery

TARGET AUDIENCE: {prompt_data.get('target_audience', 'Professionals')}

CONTENT REQUIREMENTS:
- 10-15 cards with varied types
- SEO-optimized content
- Include relevant statistics
- Use power words
- Professional and engaging tone

CARD TYPES TO INCLUDE:
- Hero title card with stunning visual
- Executive summary
- Key statistics with data viz
- Problem/solution cards
- Timeline or process flow
- Comparison cards
- Quote cards with authority
- Call-to-action card
- Contact/closing card

Make every card look like it was designed by a $10,000/day agency."""
        
        try:
            # Generate with premium quality
            result = await self.ai_service.generate_presentation(
                prompt=enhanced_prompt,
                num_cards=12,
                style=prompt_data['style']
            )
            
            # Extract cards from result
            if isinstance(result, dict) and 'slides' in result:
                cards = result['slides']
            elif isinstance(result, str):
                # Parse string result
                import json
                parsed = json.loads(result)
                cards = parsed.get('slides', [])
            else:
                cards = []
            
        except Exception as e:
            print(f"      ⚠️  AI generation failed, using fallback: {str(e)}")
            cards = self._create_fallback_cards(prompt_data)
        
        # Apply advanced theming
        theme = await self._get_premium_theme(prompt_data['style'])
        
        # Enhance card designs
        enhanced_cards = await self._enhance_card_designs(cards, theme)
        
        template_data = {
            'title': prompt_data['title'],
            'description': prompt_data['description'],
            'category': prompt_data['category'],
            'subcategory': prompt_data['original_topic'],
            'content': enhanced_cards,
            'theme': theme,
            'tags': prompt_data['keywords'] + [
                'premium', 
                'seo-optimized', 
                'trending',
                prompt_data['design_level']
            ],
            'card_count': len(enhanced_cards),
            'is_featured': True,  # All trending templates are featured
            'is_premium': True,
            'design_level': prompt_data['design_level'],
            'style': prompt_data['style'],
            'seo_keywords': prompt_data['keywords'],
            'trending_score': 100,  # High score for trending templates
            'generated_from_trends': True,
            'trend_source': prompt_data['original_topic']
        }
        
        return template_data
    
    def _create_fallback_cards(self, prompt_data: Dict) -> List[Dict]:
        """Create basic cards when AI generation fails"""
        return [
            {
                'type': 'title',
                'title': prompt_data['title'],
                'subtitle': 'A professional presentation template'
            },
            {
                'type': 'content',
                'title': 'Overview',
                'content': prompt_data['description']
            },
            {
                'type': 'content',
                'title': 'Key Points',
                'content': f"Explore the latest trends and insights about {prompt_data['original_topic']}"
            },
            {
                'type': 'stats',
                'stats': [
                    {'label': 'Growth', 'value': '100%'},
                    {'label': 'Impact', 'value': 'High'}
                ]
            },
            {
                'type': 'content',
                'title': 'Conclusion',
                'content': 'Professional summary and next steps'
            }
        ]
    
    async def _get_premium_theme(self, style: str) -> Dict:
        """Get or create premium theme based on style"""
        
        # Ultra-premium theme configurations
        premium_themes = {
            "minimalist_modern_luxury": {
                'name': 'Minimalist Luxury',
                'colors': {
                    'primary': '#000000',
                    'secondary': '#FFFFFF',
                    'accent': '#D4AF37',  # Gold
                    'background': '#FAFAFA',
                    'text': '#1A1A1A'
                },
                'fonts': {
                    'heading': 'Playfair Display',
                    'body': 'Inter',
                    'headingWeight': '700'
                },
                'effects': {
                    'shadows': 'premium',
                    'animations': 'subtle',
                    'transitions': 'smooth'
                }
            },
            "bold_cinematic_3d": {
                'name': 'Cinematic 3D',
                'colors': {
                    'primary': '#1A1A2E',
                    'secondary': '#16213E',
                    'accent': '#0F4C75',
                    'background': '#0A0E27',
                    'text': '#EAEAEA'
                },
                'fonts': {
                    'heading': 'Montserrat',
                    'body': 'Open Sans',
                    'headingWeight': '800'
                },
                'effects': {
                    'shadows': '3d-deep',
                    'animations': 'cinematic',
                    'transitions': 'zoom'
                }
            },
            "glassmorphism_futuristic": {
                'name': 'Glass Futuristic',
                'colors': {
                    'primary': 'rgba(255, 255, 255, 0.1)',
                    'secondary': 'rgba(255, 255, 255, 0.05)',
                    'accent': '#00D4FF',
                    'background': 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                    'text': '#FFFFFF'
                },
                'fonts': {
                    'heading': 'Space Grotesk',
                    'body': 'Inter',
                    'headingWeight': '700'
                },
                'effects': {
                    'shadows': 'glass',
                    'animations': 'float',
                    'transitions': 'fade',
                    'blur': '10px'
                }
            },
            "swiss_typography_grid": {
                'name': 'Swiss Grid',
                'colors': {
                    'primary': '#FF0000',
                    'secondary': '#000000',
                    'accent': '#FFFFFF',
                    'background': '#F5F5F5',
                    'text': '#222222'
                },
                'fonts': {
                    'heading': 'Helvetica',
                    'body': 'Helvetica',
                    'headingWeight': '900'
                },
                'effects': {
                    'shadows': 'none',
                    'animations': 'sharp',
                    'transitions': 'instant'
                }
            },
            "brutalist_neo_modern": {
                'name': 'Neo Brutalism',
                'colors': {
                    'primary': '#000000',
                    'secondary': '#FF00FF',
                    'accent': '#00FF00',
                    'background': '#FFFFFF',
                    'text': '#000000'
                },
                'fonts': {
                    'heading': 'Space Mono',
                    'body': 'Courier New',
                    'headingWeight': '700'
                },
                'effects': {
                    'shadows': 'brutal',
                    'animations': 'glitch',
                    'transitions': 'hard'
                }
            }
        }
        
        return premium_themes.get(style, premium_themes['minimalist_modern_luxury'])
    
    async def _enhance_card_designs(self, cards: List[Dict], theme: Dict) -> List[Dict]:
        """Apply premium design enhancements to cards"""
        
        for card in cards:
            # Add advanced design properties
            card['design'] = {
                'theme': theme,
                'animation': self._get_card_animation(card.get('type', 'content')),
                'layout': self._get_advanced_layout(card.get('type', 'content')),
                'effects': {
                    'shadow': 'premium',
                    'hover': 'scale',
                    'transition': 'smooth-300ms'
                }
            }
            
            # Add visual enhancements based on card type
            card_type = card.get('type', 'content')
            
            if card_type == 'title':
                card['design']['effects']['gradient_overlay'] = True
                card['design']['effects']['parallax'] = True
            
            elif card_type == 'stats':
                card['design']['effects']['counter_animation'] = True
                card['design']['effects']['glow'] = True
            
            elif card_type == 'image':
                card['design']['effects']['ken_burns'] = True
                card['design']['effects']['overlay_blend'] = 'multiply'
        
        return cards
    
    def _get_card_animation(self, card_type: str) -> str:
        """Get appropriate animation for card type"""
        animations = {
            'title': 'fade_zoom_in',
            'content': 'slide_up',
            'image': 'scale_in',
            'stats': 'count_up',
            'quote': 'fade_in',
            'timeline': 'reveal_left_to_right',
            'comparison': 'split_reveal'
        }
        return animations.get(card_type, 'fade_in')
    
    def _get_advanced_layout(self, card_type: str) -> str:
        """Get advanced layout configuration"""
        layouts = {
            'title': 'hero_center',
            'content': 'text_focus',
            'image': 'full_bleed',
            'stats': 'grid_showcase',
            'quote': 'centered_emphasis',
            'timeline': 'horizontal_flow',
            'comparison': 'split_screen'
        }
        return layouts.get(card_type, 'standard')
    
    async def save_template(self, template_data: Dict):
        """Save template to database"""
        try:
            template = Template(
                user_id=1,  # System user for trending templates
                title=template_data['title'],
                description=template_data['description'],
                category=template_data['category'],
                subcategory=template_data.get('subcategory', ''),
                content=template_data['content'],
                thumbnail_url=None,  # Will be generated later
                preview_images=[],
                card_count=template_data['card_count'],
                theme_id=None,  # Custom theme stored in content
                tags=template_data.get('tags', []),
                is_featured=template_data.get('is_featured', True),
                is_premium=template_data.get('is_premium', True),
                use_count=0,
                rating=5.0,  # Premium templates start with high rating
                is_public=True
            )
            
            self.db.add(template)
            self.db.commit()
            self.db.refresh(template)
            
            return template
            
        except Exception as e:
            self.db.rollback()
            raise Exception(f"Failed to save template: {str(e)}")


# CLI entry point for running the agent
async def main():
    """Run the trending template agent"""
    agent = TrendingTemplateAgent()
    await agent.run_forever()


if __name__ == "__main__":
    asyncio.run(main())
