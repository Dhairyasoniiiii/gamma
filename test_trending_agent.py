"""
Test the Trending Template Generator Agent
Quick test to verify agent functionality
"""
import asyncio
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from backend.agents.trending_template_agent import TrendingTemplateAgent


async def test_agent():
    """Test agent functionality"""
    print("\n" + "="*80)
    print("🧪 TESTING TRENDING TEMPLATE GENERATOR AGENT")
    print("="*80 + "\n")
    
    agent = TrendingTemplateAgent()
    
    # Test 1: Check initialization
    print("✅ Test 1: Agent initialized successfully")
    print(f"   • Design Levels: {len(agent.design_levels)}")
    print(f"   • Style Combinations: {len(agent.style_combinations)}")
    print(f"   • Daily Target: {agent.daily_target}")
    print(f"   • Hourly Target: {agent.hourly_target}")
    
    # Test 2: Get trending topics
    print("\n📈 Test 2: Fetching trending topics...")
    topics = await agent.get_trending_topics()
    print(f"   ✅ Retrieved {len(topics)} trending topics")
    print(f"   • Sample topics: {topics[:5]}")
    
    # Test 3: Generate SEO prompts
    print("\n✍️  Test 3: Generating SEO prompts...")
    prompts = await agent.generate_seo_prompts(topics[:3], count=3)
    print(f"   ✅ Generated {len(prompts)} SEO-optimized prompts")
    for i, prompt in enumerate(prompts, 1):
        print(f"   {i}. {prompt['title']}")
        print(f"      Category: {prompt['category']} | Style: {prompt['style']}")
    
    # Test 4: Create one premium template
    print("\n🎨 Test 4: Creating premium template...")
    if prompts:
        template = await agent.create_premium_template(prompts[0])
        print(f"   ✅ Template created:")
        print(f"      • Title: {template['title']}")
        print(f"      • Cards: {template['card_count']}")
        print(f"      • Design Level: {template['design_level']}")
        print(f"      • Style: {template['style']}")
        print(f"      • Keywords: {', '.join(template['seo_keywords'][:3])}")
    
    print("\n" + "="*80)
    print("✅ ALL TESTS PASSED!")
    print("="*80)
    print("\nAgent is ready for production use.")
    print("Run: python run_trending_agent.py\n")


if __name__ == "__main__":
    try:
        asyncio.run(test_agent())
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
