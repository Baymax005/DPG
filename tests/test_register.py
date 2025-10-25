"""
Test script to register a new user and login
Run this after starting the server with: python backend/main.py
"""
import requests
import json
from datetime import datetime

# API endpoint
BASE_URL = "http://localhost:9000"
REGISTER_URL = f"{BASE_URL}/api/v1/auth/register"
LOGIN_URL = f"{BASE_URL}/api/v1/auth/login"
ME_URL = f"{BASE_URL}/api/v1/auth/me"

# User data - using timestamp to create unique email
timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
user_data = {
    "email": f"user{timestamp}@example.com",
    "password": "Test123456",
    "first_name": "Test",
    "last_name": "User"
}

print("="*60)
print("🚀 Testing DPG Authentication System")
print("="*60)

# 1. Register new user
print(f"\n1️⃣ Registering new user: {user_data['email']}")
response = requests.post(REGISTER_URL, json=user_data)

if response.status_code == 201:
    print("   ✅ User registered successfully!")
    user = response.json()
    print(f"   📧 Email: {user['email']}")
    print(f"   🆔 User ID: {user['id']}")
    print(f"   ✅ Is Active: {user['is_active']}")
else:
    print(f"   ❌ Registration failed with status {response.status_code}")
    print(f"   {response.json()}")
    exit(1)

# 2. Login with credentials
print(f"\n2️⃣ Logging in with email: {user_data['email']}")
login_data = {
    "email": user_data['email'],
    "password": user_data['password']
}
response = requests.post(LOGIN_URL, json=login_data)

if response.status_code == 200:
    print("   ✅ Login successful!")
    token_data = response.json()
    access_token = token_data['access_token']
    print(f"   🔑 Access Token: {access_token[:50]}...")
else:
    print(f"   ❌ Login failed with status {response.status_code}")
    print(f"   {response.json()}")
    exit(1)

# 3. Get current user info (protected endpoint)
print(f"\n3️⃣ Getting user profile (protected endpoint)")
headers = {
    "Authorization": f"Bearer {access_token}"
}
response = requests.get(ME_URL, headers=headers)

if response.status_code == 200:
    print("   ✅ Profile retrieved successfully!")
    profile = response.json()
    print(f"   📧 Email: {profile['email']}")
    print(f"   👤 Name: {profile['first_name']} {profile['last_name']}")
    print(f"   🔐 KYC Status: {profile['kyc_status']}")
    print(f"   ✅ Verified: {profile['is_verified']}")
else:
    print(f"   ❌ Failed to get profile with status {response.status_code}")
    print(f"   {response.json()}")

print("\n" + "="*60)
print("✨ All tests passed! Your authentication system works!")
print("="*60)
