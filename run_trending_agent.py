"""
Run the Trending Template Generator Agent
Can be run standalone or integrated with Celery
"""
import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.agents.trending_template_agent import TrendingTemplateAgent


def run_agent():
    """Run the trending template agent"""
    print("\n" + "="*80)
    print("🤖 STARTING TRENDING TEMPLATE GENERATOR AGENT")
    print("="*80)
    print("\nThis agent will:")
    print("  • Scrape Google Trends every hour")
    print("  • Generate 8-9 premium templates per hour")
    print("  • Create 200+ templates per day (if running 24/7)")
    print("  • Use 10 advanced design styles")
    print("  • Apply SEO optimization to all templates")
    print("\nPress CTRL+C to stop the agent\n")
    print("="*80 + "\n")
    
    try:
        agent = TrendingTemplateAgent()
        asyncio.run(agent.run_forever())
    except KeyboardInterrupt:
        print("\n\n✅ Agent stopped gracefully")
        print("="*80)
    except Exception as e:
        print(f"\n\n❌ Agent crashed: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    run_agent()
