"""
Test all AI generation endpoints
Tests: full generation, rewrite, translate, image generation
"""

import asyncio
from backend.agents.generation_agent import GenerationAgent
from backend.services.ai_service import AIService
from backend.config import settings
from backend.db.base import SessionLocal
from backend.models.user import User
import uuid


async def test_ai_service():
    """Test AI Service directly"""
    print("\n=== Testing AI Service ===")
    
    ai = AIService(settings.OPENAI_API_KEY)
    
    # Test 1: Generate presentation
    print("\n1. Testing presentation generation...")
    try:
        result = await ai.generate_presentation(
            prompt="Create a presentation about Python programming",
            num_cards=5,
            style="professional"
        )
        print(f"✅ Generated presentation with {len(result['cards'])} cards")
        print(f"   Title: {result['title']}")
        print(f"   Theme: {result.get('theme', {}).get('name', 'N/A')}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 2: Rewrite text
    print("\n2. Testing text rewriting...")
    try:
        text = "This is a test. It needs improvement."
        rewritten = await ai.rewrite_text(text, "improve")
        print(f"✅ Original: {text}")
        print(f"   Rewritten: {rewritten}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 3: Translate
    print("\n3. Testing translation...")
    try:
        text = "Hello, how are you?"
        translated = await ai.translate_text(text, "es")
        print(f"✅ English: {text}")
        print(f"   Spanish: {translated}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 4: Image generation
    print("\n4. Testing image generation...")
    try:
        image_url = await ai._generate_image(
            prompt="A beautiful sunset over mountains",
            size="1024x1024",
            quality="standard"
        )
        print(f"✅ Generated image: {image_url[:80]}...")
    except Exception as e:
        print(f"❌ Error: {e}")


async def test_generation_agent():
    """Test Generation Agent with database integration"""
    print("\n\n=== Testing Generation Agent ===")
    
    # Create test user
    db = SessionLocal()
    try:
        # Check if test user exists
        test_user = db.query(User).filter(User.email == "test@example.com").first()
        
        if not test_user:
            print("\n📝 Creating test user...")
            test_user = User(
                id=uuid.uuid4(),
                email="test@example.com",
                full_name="Test User",
                hashed_password="$2b$12$test",  # Not a real password
                plan="Pro",
                credits_remaining=1000,
                is_active=True,
                is_verified=True
            )
            db.add(test_user)
            db.commit()
            db.refresh(test_user)
            print(f"✅ Created test user: {test_user.email} (ID: {test_user.id})")
        else:
            print(f"✅ Using existing test user: {test_user.email} (ID: {test_user.id})")
            # Ensure enough credits
            if test_user.credits_remaining < 100:
                test_user.credits_remaining = 1000
                db.commit()
        
        user_id = str(test_user.id)
        
    finally:
        db.close()
    
    agent = GenerationAgent()
    
    # Test 1: Full generation
    print("\n1. Testing full presentation generation...")
    try:
        result = await agent.process({
            'type': 'full_generation',
            'prompt': 'Create a presentation about artificial intelligence',
            'user_id': user_id,
            'num_cards': 5,
            'style': 'professional'
        })
        print(f"✅ Generated presentation")
        print(f"   Presentation ID: {result['presentation_id']}")
        print(f"   Credits used: {result['credits_used']}")
        print(f"   Credits remaining: {result['credits_remaining']}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 2: Rewrite
    print("\n2. Testing content rewriting...")
    try:
        result = await agent.process({
            'type': 'rewrite',
            'text': 'This presentation is good.',
            'instruction': 'improve',
            'user_id': user_id
        })
        print(f"✅ Rewritten text")
        print(f"   Original: {result['original']}")
        print(f"   Rewritten: {result['rewritten']}")
        print(f"   Credits used: {result['credits_used']}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 3: Translate
    print("\n3. Testing translation...")
    try:
        result = await agent.process({
            'type': 'translate',
            'text': 'Welcome to our presentation',
            'target_language': 'fr',
            'user_id': user_id
        })
        print(f"✅ Translated")
        print(f"   Original: {result['original']}")
        print(f"   Translated: {result['translated']}")
        print(f"   Credits used: {result['credits_used']}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 4: Image generation
    print("\n4. Testing image generation...")
    try:
        result = await agent.process({
            'type': 'image',
            'prompt': 'A futuristic AI robot',
            'user_id': user_id,
            'size': '1024x1024',
            'quality': 'standard'
        })
        print(f"✅ Generated image")
        print(f"   URL: {result['image_url'][:80]}...")
        print(f"   Credits used: {result['credits_used']}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Show final credit balance
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        print(f"\n📊 Final credit balance: {user.credits_remaining}")
        print(f"   Total AI generations: {user.total_ai_generations}")
        print(f"   Total presentations: {user.total_presentations}")
    finally:
        db.close()


def test_imports():
    """Test that all imports work"""
    print("\n=== Testing Imports ===")
    
    try:
        from backend.agents.generation_agent import GenerationAgent
        print("✅ GenerationAgent imported")
    except Exception as e:
        print(f"❌ GenerationAgent import failed: {e}")
        return False
    
    try:
        from backend.services.ai_service import AIService
        print("✅ AIService imported")
    except Exception as e:
        print(f"❌ AIService import failed: {e}")
        return False
    
    try:
        from backend.api.ai import router
        print("✅ AI API router imported")
    except Exception as e:
        print(f"❌ AI API router import failed: {e}")
        return False
    
    try:
        from backend.models.user import User
        from backend.models.presentation import Presentation
        print("✅ Models imported")
    except Exception as e:
        print(f"❌ Models import failed: {e}")
        return False
    
    return True


if __name__ == "__main__":
    print("="*60)
    print("  AI GENERATION TESTING SUITE")
    print("="*60)
    
    # Test imports first
    if not test_imports():
        print("\n❌ Import tests failed. Fix imports before continuing.")
        exit(1)
    
    print("\n✅ All imports successful!\n")
    
    # Check if OpenAI API key is set
    if not settings.OPENAI_API_KEY or settings.OPENAI_API_KEY == "your-openai-api-key":
        print("\n⚠️  WARNING: OpenAI API key not set!")
        print("   Set OPENAI_API_KEY in .env file to test actual AI generation")
        print("   Skipping AI service tests...")
    else:
        # Run AI service tests
        asyncio.run(test_ai_service())
    
    # Run agent tests (these include database operations)
    asyncio.run(test_generation_agent())
    
    print("\n" + "="*60)
    print("  TESTING COMPLETE")
    print("="*60)
