"""
Template Generation Script
Generates 2000+ professional templates using AI
As specified in the blueprint
"""

import asyncio
from typing import List, Dict
import json
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.services.ai_service import AIService
from backend.db.base import SessionLocal
from backend.models.template import Template
from backend.config import settings, TEMPLATE_CATEGORIES


class TemplateGenerator:
    """
    Generates 2000+ professional templates
    Using AI to create diverse, high-quality templates
    """
    
    def __init__(self):
        self.ai_service = AIService(settings.OPENAI_API_KEY)
        self.db = SessionLocal()
    
    async def generate_all_templates(self):
        """Generate all 2000+ templates"""
        
        print("🚀 Starting template generation...")
        print(f"📊 Target: 2000+ templates across {len(TEMPLATE_CATEGORIES)} categories\n")
        
        total_generated = 0
        
        for category, subcategories in TEMPLATE_CATEGORIES.items():
            print(f"\n{'='*60}")
            print(f"📁 Category: {category.upper()}")
            print(f"🎯 Subcategories: {len(subcategories)}")
            print(f"{'='*60}\n")
            
            category_count = 0
            templates_per_subcategory = 30  # 30 templates per subcategory
            
            for subcategory in subcategories:
                print(f"  📂 {subcategory}...")
                
                for i in range(templates_per_subcategory):
                    try:
                        template = await self._generate_single_template(
                            category=category,
                            subcategory=subcategory,
                            index=i
                        )
                        
                        await self._save_template(template)
                        
                        category_count += 1
                        total_generated += 1
                        
                        if category_count % 10 == 0:
                            print(f"    ✓ Generated {category_count} in {category}")
                        
                        # Rate limiting (20 requests per minute for OpenAI)
                        await asyncio.sleep(3)
                        
                    except Exception as e:
                        print(f"    ✗ Error: {str(e)}")
                        continue
            
            print(f"\n✅ Completed {category}: {category_count} templates\n")
        
        print(f"\n{'='*60}")
        print(f"🎉 GENERATION COMPLETE!")
        print(f"📊 Total templates generated: {total_generated}")
        print(f"{'='*60}\n")
    
    async def _generate_single_template(
        self,
        category: str,
        subcategory: str,
        index: int
    ) -> Dict:
        """Generate a single template using AI"""
        
        # Create specific prompt for this template
        prompt = f"""Create a professional {subcategory} template for {category}.

Requirements:
- Create 8-12 cards with varied types
- Include realistic, professional content
- Use appropriate layout for {category} context
- Make it visually appealing and modern
- Include placeholders that users can easily customize

Template should be ready-to-use and production-quality."""
        
        # Generate with AI
        result = await self.ai_service.generate_presentation(
            prompt=prompt,
            num_cards=10,
            style=self._get_style_for_category(category)
        )
        
        # Add metadata
        template_data = {
            'title': self._generate_title(subcategory, index),
            'description': self._generate_description(subcategory, category),
            'category': category,
            'subcategory': subcategory,
            'content': result['cards'],
            'theme': result.get('theme'),
            'tags': self._generate_tags(category, subcategory),
            'card_count': len(result['cards']),
            'estimated_time': 15,  # 15 minutes
            'difficulty': 'intermediate',
            'is_featured': (index < 3),  # First 3 in each subcategory are featured
            'is_premium': False
        }
        
        return template_data
    
    def _get_style_for_category(self, category: str) -> str:
        """Get appropriate style for category"""
        style_map = {
            'business': 'professional',
            'education': 'professional',
            'technology': 'minimal',
            'marketing': 'creative',
            'sales': 'professional',
            'creative': 'creative',
            'healthcare': 'professional',
            'finance': 'professional'
        }
        return style_map.get(category, 'professional')
    
    def _generate_title(self, subcategory: str, index: int) -> str:
        """Generate template title"""
        
        variations = [
            f"Professional {subcategory}",
            f"Modern {subcategory}",
            f"{subcategory} Template",
            f"Complete {subcategory}",
            f"{subcategory} Presentation",
            f"Expert {subcategory}",
            f"Premium {subcategory}",
            f"Ultimate {subcategory}",
            f"Advanced {subcategory}",
            f"Creative {subcategory}"
        ]
        
        return variations[index % len(variations)]
    
    def _generate_description(self, subcategory: str, category: str) -> str:
        """Generate template description"""
        
        return f"A professional, ready-to-use {subcategory} template for {category} professionals. Features modern design, customizable content, and proven structure. Perfect for creating impactful presentations quickly."
    
    def _generate_tags(self, category: str, subcategory: str) -> List[str]:
        """Generate relevant tags"""
        
        base_tags = [category, subcategory.lower()]
        
        additional_tags = {
            'business': ['corporate', 'professional', 'executive', 'strategy'],
            'education': ['academic', 'learning', 'teaching', 'training'],
            'technology': ['tech', 'innovation', 'digital', 'software'],
            'marketing': ['brand', 'campaign', 'strategy', 'social'],
            'sales': ['pitch', 'proposal', 'revenue', 'growth'],
            'creative': ['design', 'portfolio', 'showcase', 'visual'],
            'healthcare': ['medical', 'health', 'clinical', 'patient'],
            'finance': ['financial', 'investment', 'analysis', 'budget']
        }
        
        return base_tags + additional_tags.get(category, [])
    
    async def _save_template(self, template_data: Dict):
        """Save template to database"""
        
        try:
            template = Template(
                title=template_data['title'],
                description=template_data['description'],
                category=template_data['category'],
                subcategory=template_data['subcategory'],
                content=template_data['content'],
                # theme_id will be set later
                tags=template_data['tags'],
                card_count=template_data['card_count'],
                estimated_time=template_data['estimated_time'],
                difficulty=template_data['difficulty'],
                is_featured=template_data['is_featured'],
                is_premium=template_data['is_premium'],
                is_system_template=True
            )
            
            self.db.add(template)
            self.db.commit()
            
        except Exception as e:
            self.db.rollback()
            raise e


# Run the generator
async def main():
    generator = TemplateGenerator()
    await generator.generate_all_templates()


if __name__ == "__main__":
    print("\n" + "="*60)
    print("🎨 GAMMA CLONE - TEMPLATE GENERATOR")
    print("="*60 + "\n")
    
    print("⚠️  WARNING:")
    print("This will generate 2000+ templates using OpenAI API")
    print("Estimated cost: $50-100")
    print("Estimated time: 2-3 hours")
    print("\nMake sure you have:")
    print("1. OPENAI_API_KEY set in environment")
    print("2. Database configured and running")
    print("3. Sufficient API credits\n")
    
    response = input("Continue? (yes/no): ")
    if response.lower() == 'yes':
        asyncio.run(main())
    else:
        print("Cancelled.")
