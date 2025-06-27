import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "http://localhost:8000/api"

def test_gemini_chat():
    """Test the Gemini LangChain/LangGraph integration"""
    
    # Login first (assuming you have a test user)
    login_data = {
        "username": "testuser",
        "password": "testpass123"
    }
    response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    print("Login response:", response.status_code, response.text)
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Get domains
    response = requests.get(f"{BASE_URL}/domains", headers=headers)
    domains = response.json()
    
    # Test each domain with Gemini
    test_messages = {
        "stock": "What's your analysis of Apple's recent quarterly earnings?",
        "law": "What should I know about tenant rights in rental agreements?",
        "entertainment": "What are the most anticipated movies coming out this year?",
        "psychology": "How can I improve my focus and concentration at work?",
        "technical": "Can you explain how to implement a REST API with FastAPI?"
    }
    
    for domain in domains:
        domain_name = domain["name"]
        if domain_name in test_messages:
            print(f"\n--- Testing {domain_name.upper()} domain with Gemini ---")
            
            # Create conversation
            conv_data = {
                "domain_id": domain["id"],
                "title": f"Test {domain_name} conversation"
            }
            response = requests.post(f"{BASE_URL}/conversations", json=conv_data, headers=headers)
            conversation = response.json()
            
            # Send test message
            message_data = {
                "message": test_messages[domain_name]
            }
            response = requests.post(
                f"{BASE_URL}/chat/{conversation['id']}", 
                json=message_data, 
                headers=headers
            )
            
            if response.status_code == 200:
                chat_response = response.json()
                print(f"User: {chat_response['user_message']['content']}")
                print(f"Gemini AI: {chat_response['ai_response']['content'][:300]}...")
            else:
                print(f"Error: {response.status_code} - {response.text}")

if __name__ == "__main__":
    if not os.getenv("GOOGLE_API_KEY"):
        print("Please set GOOGLE_API_KEY in your .env file")
    else:
        test_gemini_chat()