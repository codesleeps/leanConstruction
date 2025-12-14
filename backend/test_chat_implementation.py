#!/usr/bin/env python3
"""
Test script to verify the chat implementation.
This script tests the basic functionality of the chat API endpoints.
"""

import requests
import json
import time
import uuid
from typing import Optional

class ChatTester:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.token: Optional[str] = None
        self.session_id: Optional[str] = None
        
    def authenticate(self, email: str, password: str) -> bool:
        """Authenticate user and get JWT token."""
        print("🔐 Authenticating user...")
        
        auth_data = {
            "username": email,
            "password": password
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/token",
                data=auth_data,
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            
            if response.status_code == 200:
                token_data = response.json()
                self.token = token_data["access_token"]
                print(f"✅ Authentication successful")
                return True
            else:
                print(f"❌ Authentication failed: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"❌ Authentication error: {e}")
            return False
    
    def test_create_conversation(self) -> bool:
        """Test creating a new conversation."""
        print("📝 Testing conversation creation...")
        
        if not self.token:
            print("❌ No token available. Please authenticate first.")
            return False
            
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            response = requests.post(
                f"{self.base_url}/api/v1/chat/conversations",
                headers=headers,
                json={}
            )
            
            if response.status_code == 200:
                data = response.json()
                self.session_id = data["session_id"]
                print(f"✅ Conversation created with session_id: {self.session_id}")
                return True
            else:
                print(f"❌ Conversation creation failed: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"❌ Conversation creation error: {e}")
            return False
    
    def test_get_conversations(self) -> bool:
        """Test retrieving conversations."""
        print("📋 Testing conversation retrieval...")
        
        if not self.token:
            print("❌ No token available. Please authenticate first.")
            return False
            
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            response = requests.get(
                f"{self.base_url}/api/v1/chat/conversations",
                headers=headers
            )
            
            if response.status_code == 200:
                conversations = response.json()
                print(f"✅ Retrieved {len(conversations)} conversations")
                if conversations:
                    self.session_id = conversations[0]["session_id"]
                    print(f"   Latest session_id: {self.session_id}")
                return True
            else:
                print(f"❌ Conversation retrieval failed: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"❌ Conversation retrieval error: {e}")
            return False
    
    def test_send_message(self, message: str) -> bool:
        """Test sending a message."""
        print(f"💬 Testing message sending: '{message}'")
        
        if not self.token:
            print("❌ No token available. Please authenticate first.")
            return False
            
        try:
            headers = {
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json"
            }
            
            message_data = {
                "content": message,
                "role": "user"
            }
            
            # Add session_id if we have one
            if self.session_id:
                message_data["session_id"] = self.session_id
            
            response = requests.post(
                f"{self.base_url}/api/v1/chat/messages",
                headers=headers,
                json=message_data
            )
            
            if response.status_code == 200:
                data = response.json()
                self.session_id = data["user_message"]["conversation_id"]
                print(f"✅ Message sent successfully")
                print(f"   User message: {data['user_message']['content']}")
                print(f"   Bot response: {data['bot_message']['content']}")
                return True
            else:
                print(f"❌ Message sending failed: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"❌ Message sending error: {e}")
            return False
    
    def test_get_messages(self) -> bool:
        """Test retrieving messages for a conversation."""
        print("📨 Testing message retrieval...")
        
        if not self.token:
            print("❌ No token available. Please authenticate first.")
            return False
            
        if not self.session_id:
            print("❌ No session_id available. Please create or get a conversation first.")
            return False
            
        try:
            headers = {"Authorization": f"Bearer {self.token}"}
            response = requests.get(
                f"{self.base_url}/api/v1/chat/conversations/{self.session_id}/messages",
                headers=headers
            )
            
            if response.status_code == 200:
                messages = response.json()
                print(f"✅ Retrieved {len(messages)} messages")
                for i, msg in enumerate(messages):
                    print(f"   [{i+1}] {msg['role']}: {msg['content']}")
                return True
            else:
                print(f"❌ Message retrieval failed: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"❌ Message retrieval error: {e}")
            return False
    
    def run_full_test(self, email: str, password: str):
        """Run a complete test of the chat functionality."""
        print("🚀 Starting Chat Implementation Test\n")
        
        # Test 1: Authentication
        if not self.authenticate(email, password):
            print("\n❌ Test failed at authentication step")
            return False
        
        print()
        
        # Test 2: Create conversation
        if not self.test_create_conversation():
            print("\n❌ Test failed at conversation creation step")
            return False
        
        print()
        
        # Test 3: Send first message
        if not self.test_send_message("Hello! Can you help me with lean construction principles?"):
            print("\n❌ Test failed at message sending step")
            return False
        
        print()
        
        # Test 4: Retrieve messages
        if not self.test_get_messages():
            print("\n❌ Test failed at message retrieval step")
            return False
        
        print()
        
        # Test 5: Send follow-up message
        if not self.test_send_message("What about waste management?"):
            print("\n❌ Test failed at follow-up message step")
            return False
        
        print()
        
        # Test 6: Get conversations list
        if not self.test_get_conversations():
            print("\n❌ Test failed at conversations list step")
            return False
        
        print("\n🎉 All tests passed! Chat implementation is working correctly.")
        return True

def main():
    """Main test function."""
    import sys
    
    if len(sys.argv) < 3:
        print("Usage: python test_chat_implementation.py <email> <password>")
        print("Example: python test_chat_implementation.py test@example.com password123")
        sys.exit(1)
    
    email = sys.argv[1]
    password = sys.argv[2]
    
    tester = ChatTester()
    success = tester.run_full_test(email, password)
    
    if not success:
        print("\n❌ Test suite failed")
        sys.exit(1)
    else:
        print("\n✅ Test suite completed successfully")

if __name__ == "__main__":
    main()