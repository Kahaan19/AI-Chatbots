import requests
import json

BASE_URL = "http://localhost:8000/api"

def test_api():
    # Test user registration
    signup_data = {
        "email": "test@example.com",
        "username": "testuser",
        "password": "testpass123",
        "full_name": "Test User"
    }
    
    # Register user
    response = requests.post(f"{BASE_URL}/auth/signup", json=signup_data)
    print("Signup:", response.status_code, response.json())
    
    # Login
    login_data = {
        "username": "testuser",
        "password": "testpass123"
    }
    response = requests.post(f"{BASE_URL}/auth/login", data=login_data)
    token_data = response.json()
    token = token_data["access_token"]
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Get domains
    response = requests.get(f"{BASE_URL}/domains", headers=headers)
    domains = response.json()
    print("Domains:", domains)
    
    # Create conversation
    conv_data = {
        "domain_id": domains[0]["id"],
        "title": "Test Conversation"
    }
    response = requests.post(f"{BASE_URL}/conversations", json=conv_data, headers=headers)
    conversation = response.json()
    print("Created conversation:", conversation)
    
    # Send message
    message_data = {
        "message": "Hello, this is a test message!"
    }
    response = requests.post(
        f"{BASE_URL}/chat/{conversation['id']}", 
        json=message_data, 
        headers=headers
    )
    chat_response = response.json()
    print("Chat response:", chat_response)

if __name__ == "__main__":
    test_api()