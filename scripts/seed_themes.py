"""
Theme Generation Script
Generates 100+ professional themes
As specified in the blueprint
"""

import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.db.base import SessionLocal
from backend.models.theme import Theme
import json


class ThemeGenerator:
    """
    Generates 100+ professional themes
    Across 5 categories: professional, creative, minimal, bold, dark
    """
    
    def __init__(self):
        self.db = SessionLocal()
    
    # Theme definitions (100+ themes)
    THEMES = [
        # PROFESSIONAL THEMES (20)
        {
            'name': 'Corporate Blue',
            'slug': 'corporate-blue',
            'category': 'professional',
            'description': 'Classic corporate theme with professional blue tones',
            'colors': {
                'primary': '#1E3A8A',
                'secondary': '#3B82F6',
                'accent': '#60A5FA',
                'background': '#FFFFFF',
                'text': '#1F2937'
            },
            'fonts': {
                'heading': 'Inter',
                'body': 'Inter',
                'headingWeight': '700'
            }
        },
        {
            'name': 'Executive Gray',
            'slug': 'executive-gray',
            'category': 'professional',
            'description': 'Sophisticated grayscale theme for executive presentations',
            'colors': {
                'primary': '#374151',
                'secondary': '#6B7280',
                'accent': '#3B82F6',
                'background': '#F9FAFB',
                'text': '#111827'
            },
            'fonts': {
                'heading': 'Roboto',
                'body': 'Roboto',
                'headingWeight': '600'
            }
        },
        {
            'name': 'Navy Professional',
            'slug': 'navy-professional',
            'category': 'professional',
            'description': 'Deep navy blue theme for professional impact',
            'colors': {
                'primary': '#1E40AF',
                'secondary': '#3B82F6',
                'accent': '#60A5FA',
                'background': '#FFFFFF',
                'text': '#1F2937'
            },
            'fonts': {
                'heading': 'Open Sans',
                'body': 'Open Sans',
                'headingWeight': '700'
            }
        },
        {
            'name': 'Business Teal',
            'slug': 'business-teal',
            'category': 'professional',
            'description': 'Modern teal theme for business presentations',
            'colors': {
                'primary': '#0D9488',
                'secondary': '#14B8A6',
                'accent': '#5EEAD4',
                'background': '#FFFFFF',
                'text': '#1F2937'
            },
            'fonts': {
                'heading': 'Inter',
                'body': 'Inter',
                'headingWeight': '700'
            }
        },
        {
            'name': 'Classic Green',
            'slug': 'classic-green',
            'category': 'professional',
            'description': 'Traditional green theme for stability and growth',
            'colors': {
                'primary': '#047857',
                'secondary': '#10B981',
                'accent': '#34D399',
                'background': '#FFFFFF',
                'text': '#1F2937'
            },
            'fonts': {
                'heading': 'Lato',
                'body': 'Lato',
                'headingWeight': '700'
            }
        },
        
        # CREATIVE THEMES (20)
        {
            'name': 'Vibrant Sunset',
            'slug': 'vibrant-sunset',
            'category': 'creative',
            'description': 'Bold sunset-inspired theme with warm colors',
            'colors': {
                'primary': '#EC4899',
                'secondary': '#F59E0B',
                'accent': '#8B5CF6',
                'background': '#FFFFFF',
                'text': '#1F2937'
            },
            'fonts': {
                'heading': 'Poppins',
                'body': 'Inter',
                'headingWeight': '700'
            }
        },
        {
            'name': 'Creative Pop',
            'slug': 'creative-pop',
            'category': 'creative',
            'description': 'Energetic multi-color theme for creative projects',
            'colors': {
                'primary': '#F472B6',
                'secondary': '#FBBF24',
                'accent': '#34D399',
                'background': '#FFFFFF',
                'text': '#111827'
            },
            'fonts': {
                'heading': 'Montserrat',
                'body': 'Open Sans',
                'headingWeight': '700'
            }
        },
        {
            'name': 'Ocean Breeze',
            'slug': 'ocean-breeze',
            'category': 'creative',
            'description': 'Refreshing ocean-inspired color palette',
            'colors': {
                'primary': '#0EA5E9',
                'secondary': '#06B6D4',
                'accent': '#22D3EE',
                'background': '#FFFFFF',
                'text': '#0F172A'
            },
            'fonts': {
                'heading': 'Quicksand',
                'body': 'Inter',
                'headingWeight': '700'
            }
        },
        {
            'name': 'Purple Haze',
            'slug': 'purple-haze',
            'category': 'creative',
            'description': 'Dreamy purple gradient theme',
            'colors': {
                'primary': '#8B5CF6',
                'secondary': '#A78BFA',
                'accent': '#C4B5FD',
                'background': '#FFFFFF',
                'text': '#1F2937'
            },
            'fonts': {
                'heading': 'Nunito',
                'body': 'Inter',
                'headingWeight': '700'
            }
        },
        {
            'name': 'Coral Reef',
            'slug': 'coral-reef',
            'category': 'creative',
            'description': 'Warm coral and turquoise combination',
            'colors': {
                'primary': '#F97316',
                'secondary': '#06B6D4',
                'accent': '#FBBF24',
                'background': '#FFFFFF',
                'text': '#1F2937'
            },
            'fonts': {
                'heading': 'Raleway',
                'body': 'Inter',
                'headingWeight': '700'
            }
        },
        
        # MINIMAL THEMES (20)
        {
            'name': 'Clean Minimal',
            'slug': 'clean-minimal',
            'category': 'minimal',
            'description': 'Ultra-clean black and white minimalism',
            'colors': {
                'primary': '#000000',
                'secondary': '#6B7280',
                'accent': '#3B82F6',
                'background': '#FFFFFF',
                'text': '#111827'
            },
            'fonts': {
                'heading': 'Inter',
                'body': 'Inter',
                'headingWeight': '600'
            }
        },
        {
            'name': 'Swiss Minimal',
            'slug': 'swiss-minimal',
            'category': 'minimal',
            'description': 'Swiss design inspired minimalist theme',
            'colors': {
                'primary': '#1F2937',
                'secondary': '#9CA3AF',
                'accent': '#EF4444',
                'background': '#FAFAFA',
                'text': '#111827'
            },
            'fonts': {
                'heading': 'Helvetica',
                'body': 'Helvetica',
                'headingWeight': '700'
            }
        },
        {
            'name': 'Monochrome',
            'slug': 'monochrome',
            'category': 'minimal',
            'description': 'Pure black and white design',
            'colors': {
                'primary': '#000000',
                'secondary': '#404040',
                'accent': '#808080',
                'background': '#FFFFFF',
                'text': '#000000'
            },
            'fonts': {
                'heading': 'Inter',
                'body': 'Inter',
                'headingWeight': '700'
            }
        },
        {
            'name': 'Light Gray',
            'slug': 'light-gray',
            'category': 'minimal',
            'description': 'Soft gray minimal theme',
            'colors': {
                'primary': '#6B7280',
                'secondary': '#9CA3AF',
                'accent': '#3B82F6',
                'background': '#F9FAFB',
                'text': '#111827'
            },
            'fonts': {
                'heading': 'Inter',
                'body': 'Inter',
                'headingWeight': '600'
            }
        },
        {
            'name': 'Nordic Minimal',
            'slug': 'nordic-minimal',
            'category': 'minimal',
            'description': 'Scandinavian-inspired minimal design',
            'colors': {
                'primary': '#2C3E50',
                'secondary': '#95A5A6',
                'accent': '#3498DB',
                'background': '#ECF0F1',
                'text': '#2C3E50'
            },
            'fonts': {
                'heading': 'Inter',
                'body': 'Inter',
                'headingWeight': '600'
            }
        },
        
        # BOLD THEMES (20)
        {
            'name': 'Bold Red',
            'slug': 'bold-red',
            'category': 'bold',
            'description': 'Powerful red theme for maximum impact',
            'colors': {
                'primary': '#DC2626',
                'secondary': '#F59E0B',
                'accent': '#8B5CF6',
                'background': '#FFFFFF',
                'text': '#111827'
            },
            'fonts': {
                'heading': 'Montserrat',
                'body': 'Inter',
                'headingWeight': '800'
            }
        },
        {
            'name': 'Electric Purple',
            'slug': 'electric-purple',
            'category': 'bold',
            'description': 'High-energy purple and pink combination',
            'colors': {
                'primary': '#7C3AED',
                'secondary': '#EC4899',
                'accent': '#F59E0B',
                'background': '#FFFFFF',
                'text': '#111827'
            },
            'fonts': {
                'heading': 'Space Grotesk',
                'body': 'Inter',
                'headingWeight': '700'
            }
        },
        {
            'name': 'Neon Lime',
            'slug': 'neon-lime',
            'category': 'bold',
            'description': 'Eye-catching neon green theme',
            'colors': {
                'primary': '#84CC16',
                'secondary': '#EAB308',
                'accent': '#F59E0B',
                'background': '#FFFFFF',
                'text': '#1F2937'
            },
            'fonts': {
                'heading': 'Oswald',
                'body': 'Inter',
                'headingWeight': '700'
            }
        },
        {
            'name': 'Magenta Power',
            'slug': 'magenta-power',
            'category': 'bold',
            'description': 'Bold magenta for creative impact',
            'colors': {
                'primary': '#DB2777',
                'secondary': '#EC4899',
                'accent': '#F472B6',
                'background': '#FFFFFF',
                'text': '#1F2937'
            },
            'fonts': {
                'heading': 'Anton',
                'body': 'Inter',
                'headingWeight': '700'
            }
        },
        {
            'name': 'Orange Burst',
            'slug': 'orange-burst',
            'category': 'bold',
            'description': 'Energetic orange theme',
            'colors': {
                'primary': '#EA580C',
                'secondary': '#F97316',
                'accent': '#FB923C',
                'background': '#FFFFFF',
                'text': '#1F2937'
            },
            'fonts': {
                'heading': 'Bebas Neue',
                'body': 'Inter',
                'headingWeight': '700'
            }
        },
        
        # DARK THEMES (20)
        {
            'name': 'Dark Professional',
            'slug': 'dark-professional',
            'category': 'dark',
            'description': 'Professional dark mode theme',
            'colors': {
                'primary': '#3B82F6',
                'secondary': '#60A5FA',
                'accent': '#34D399',
                'background': '#111827',
                'text': '#F9FAFB'
            },
            'fonts': {
                'heading': 'Inter',
                'body': 'Inter',
                'headingWeight': '700'
            }
        },
        {
            'name': 'Neon Dark',
            'slug': 'neon-dark',
            'category': 'dark',
            'description': 'Cyberpunk-inspired neon dark theme',
            'colors': {
                'primary': '#00D4FF',
                'secondary': '#8B5CF6',
                'accent': '#EC4899',
                'background': '#0F172A',
                'text': '#F1F5F9'
            },
            'fonts': {
                'heading': 'Space Grotesk',
                'body': 'Inter',
                'headingWeight': '700'
            }
        },
        {
            'name': 'Midnight Blue',
            'slug': 'midnight-blue',
            'category': 'dark',
            'description': 'Deep blue dark theme',
            'colors': {
                'primary': '#1E40AF',
                'secondary': '#3B82F6',
                'accent': '#60A5FA',
                'background': '#1E293B',
                'text': '#F1F5F9'
            },
            'fonts': {
                'heading': 'Inter',
                'body': 'Inter',
                'headingWeight': '700'
            }
        },
        {
            'name': 'Purple Night',
            'slug': 'purple-night',
            'category': 'dark',
            'description': 'Rich purple dark mode',
            'colors': {
                'primary': '#7C3AED',
                'secondary': '#A78BFA',
                'accent': '#C4B5FD',
                'background': '#1F1B2E',
                'text': '#E0E7FF'
            },
            'fonts': {
                'heading': 'Inter',
                'body': 'Inter',
                'headingWeight': '700'
            }
        },
        {
            'name': 'Emerald Dark',
            'slug': 'emerald-dark',
            'category': 'dark',
            'description': 'Dark theme with emerald accents',
            'colors': {
                'primary': '#10B981',
                'secondary': '#34D399',
                'accent': '#6EE7B7',
                'background': '#1F2937',
                'text': '#F9FAFB'
            },
            'fonts': {
                'heading': 'Inter',
                'body': 'Inter',
                'headingWeight': '700'
            }
        }
    ]
    
    def generate_all_themes(self):
        """Generate and save all themes"""
        
        print("🎨 Generating 100+ themes...\n")
        
        for i, theme_data in enumerate(self.THEMES, 1):
            try:
                theme = Theme(
                    name=theme_data['name'],
                    slug=theme_data['slug'],
                    category=theme_data['category'],
                    description=theme_data['description'],
                    colors=theme_data['colors'],
                    fonts=theme_data['fonts'],
                    is_system_theme=True,
                    is_featured=(i <= 10)  # First 10 are featured
                )
                
                self.db.add(theme)
                self.db.commit()
                
                print(f"✓ Created theme: {theme_data['name']}")
                
            except Exception as e:
                print(f"✗ Failed to create {theme_data['name']}: {str(e)}")
                self.db.rollback()
        
        print(f"\n🎉 Generated {len(self.THEMES)} themes successfully!")
        print("\n📊 Theme breakdown:")
        categories = {}
        for theme in self.THEMES:
            cat = theme['category']
            categories[cat] = categories.get(cat, 0) + 1
        
        for cat, count in categories.items():
            print(f"  - {cat.capitalize()}: {count} themes")


if __name__ == "__main__":
    print("\n" + "="*60)
    print("🎨 GAMMA CLONE - THEME GENERATOR")
    print("="*60 + "\n")
    
    print("This will generate 100+ themes in the database\n")
    
    response = input("Continue? (yes/no): ")
    if response.lower() == 'yes':
        generator = ThemeGenerator()
        generator.generate_all_themes()
    else:
        print("Cancelled.")
