import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "http://localhost:8000/api"

def test_backend():
    """Complete backend testing script"""
    
    print("🚀 Starting Backend Test...")
    print("=" * 50)
    
    # Test 1: Health Check
    print("\n1. Testing Health Check...")
    try:
        response = requests.get("http://localhost:8000/")
        print(f"✅ Health check: {response.status_code}")
        if response.status_code != 200:
            print("❌ Server not running or health check failed")
            return False
    except Exception as e:
        print(f"❌ Server connection failed: {e}")
        return False
    
    # Test 2: User Registration
    print("\n2. Testing User Registration...")
    signup_data = {
        "email": "test@example.com",
        "username": "testuser",
        "password": "testpass123",
        "full_name": "Test User"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/signup", json=signup_data)
        print(f"✅ Signup: {response.status_code}")
        if response.status_code not in [200, 201]:
            print(f"❌ Signup failed: {response.text}")
            # Continue anyway, user might already exist
    except Exception as e:
        print(f"❌ Signup error: {e}")
        return False
    
    # Test 3: User Login
    print("\n3. Testing User Login...")
    login_data = {
        "email": "test@example.com",
        "username": "testuser",
        "password": "testpass123",
         "full_name": "Test User"

    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
        if response.status_code != 200:
            print(f"❌ Login failed: {response.status_code} - {response.text}")
            return False
        
        token_data = response.json()
        token = token_data["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        print("✅ Login successful, token received")
    except Exception as e:
        print(f"❌ Login error: {e}")
        return False
    
    # Test 4: Get Domains
    print("\n4. Testing Domain Endpoints...")
    try:
        response = requests.get(f"{BASE_URL}/domains", headers=headers)
        if response.status_code != 200:
            print(f"❌ Domains fetch failed: {response.status_code}")
            return False
        
        domains = response.json()
        print(f"✅ Found {len(domains)} domains")
        if len(domains) == 0:
            print("❌ No domains found. Did you run the seed script?")
            return False
        
        for domain in domains:
            print(f"   - {domain['name']}: {domain['description']}")
    except Exception as e:
        print(f"❌ Domains error: {e}")
        return False
    
    # Test 5: Create Conversation
    print("\n5. Testing Conversation Creation...")
    try:
        conv_data = {
            "domain_id": domains[0]["id"],
            "title": "Test Conversation"
        }
        response = requests.post(f"{BASE_URL}/conversations", json=conv_data, headers=headers)
        if response.status_code not in [200, 201]:
            print(f"❌ Conversation creation failed: {response.status_code} - {response.text}")
            return False
        
        conversation = response.json()
        conversation_id = conversation["id"]
        print(f"✅ Conversation created: ID {conversation_id}")
    except Exception as e:
        print(f"❌ Conversation creation error: {e}")
        return False
    
    # Test 6: Get Conversations
    print("\n6. Testing Conversation Listing...")
    try:
        response = requests.get(f"{BASE_URL}/conversations", headers=headers)
        if response.status_code != 200:
            print(f"❌ Conversations fetch failed: {response.status_code}")
            return False
        
        conversations = response.json()
        print(f"✅ Found {len(conversations)} conversations")
    except Exception as e:
        print(f"❌ Conversations fetch error: {e}")
        return False
    
    # Test 7: Send Chat Message (Basic AI Test)
    print("\n7. Testing Chat/AI Integration...")
    test_messages = {
        "stock": "What's your analysis of Apple stock?",
        "law": "What should I know about rental agreements?",
        "entertainment": "Recommend some good movies from 2024",
        "psychology": "How can I manage work stress better?",
        "technical": "Explain how REST APIs work"
    }
    
    domain_name = domains[0]["name"]
    test_message = test_messages.get(domain_name, "Hello, this is a test message!")
    
    try:
        message_data = {"message": test_message}
        response = requests.post(
            f"{BASE_URL}/chat/{conversation_id}", 
            json=message_data, 
            headers=headers
        )
        
        if response.status_code != 200:
            print(f"❌ Chat failed: {response.status_code} - {response.text}")
            return False
        
        chat_response = response.json()
        print("✅ Chat successful!")
        print(f"   User: {chat_response['user_message']['content'][:50]}...")
        print(f"   AI: {chat_response['ai_response']['content'][:100]}...")
        
        # Test if it's using LangChain/Gemini (not just template)
        ai_content = chat_response['ai_response']['content']
        if "template" in ai_content.lower():
            print("⚠️  Warning: Seems to be using template response, not actual AI")
        
    except Exception as e:
        print(f"❌ Chat error: {e}")
        return False
    
    # Test 8: Get Chat History
    print("\n8. Testing Chat History...")
    try:
        response = requests.get(f"{BASE_URL}/chat/{conversation_id}/history", headers=headers)
        if response.status_code != 200:
            print(f"❌ Chat history failed: {response.status_code}")
            return False
        
        history = response.json()
        print(f"✅ Chat history: {len(history)} messages")
    except Exception as e:
        print(f"❌ Chat history error: {e}")
        return False
    
    # Test 9: API Documentation
    print("\n9. Testing API Documentation...")
    try:
        response = requests.get("http://localhost:8000/docs")
        if response.status_code == 200:
            print("✅ API docs available at http://localhost:8000/docs")
        else:
            print("⚠️  API docs might not be available")
    except Exception as e:
        print(f"⚠️  API docs check failed: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 Backend Test Complete!")
    print("✅ All core functionality working")
    print(f"🌐 API Documentation: http://localhost:8000/docs")
    print(f"💾 Database: Connected and working")
    print(f"🤖 AI Integration: {'LangChain + Gemini' if os.getenv('GOOGLE_API_KEY') else 'Template responses'}")
    
    return True

def test_ai_specifically():
    """Test AI integration specifically"""
    print("\n🤖 Testing AI Integration Specifically...")
    
    if not os.getenv("GOOGLE_API_KEY"):
        print("❌ GOOGLE_API_KEY not found in environment")
        return False
    
    # Test Gemini connection directly
    try:
        import google.generativeai as genai
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
        
        # Test if we can import LangChain components
        from app.ai.domain_router import domain_router
        from app.ai.chat_engine import chat_engine
        
        print("✅ LangChain and Gemini components imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Missing dependencies: {e}")
        return False
    except Exception as e:
        print(f"❌ AI setup error: {e}")
        return False

if __name__ == "__main__":
    print("Backend Testing Script")
    print("Make sure your server is running: uvicorn app.main:app --reload")
    print("\nPress Enter to start testing...")
    input()
    
    # Test AI setup first
    ai_ready = test_ai_specifically()
    
    # Test full backend
    
    backend_ready = test_backend()
    
    if backend_ready and ai_ready:
        print("\n🎉 BACKEND IS READY FOR FRONTEND DEVELOPMENT!")
    elif backend_ready:
        print("\n⚠️  Backend works but AI might need configuration")
    else:
        print("\n❌ Backend needs fixes before proceeding")