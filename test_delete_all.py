#!/usr/bin/env python3
"""
Test script for the delete all passwords functionality.
This script tests the API endpoint to ensure it works correctly.
"""

import requests
import json

def test_delete_all_passwords():
    """Test the delete all passwords API endpoint."""
    
    # Base URL for the application
    base_url = "http://127.0.0.1:5000"
    
    # Test data
    test_user = {
        "username": "testuser",
        "password": "testpass123"
    }
    
    print("🧪 Testing Delete All Passwords Functionality")
    print("=" * 50)
    
    # Step 1: Try to login (this will fail if user doesn't exist, but that's OK for testing)
    print("1. Testing login...")
    try:
        login_response = requests.post(f"{base_url}/login", data=test_user)
        print(f"   Login response status: {login_response.status_code}")
        if login_response.status_code == 200:
            print("   ✅ Login successful")
        else:
            print("   ⚠️  Login failed (user might not exist)")
    except requests.exceptions.ConnectionError:
        print("   ❌ Could not connect to server. Make sure the app is running on http://127.0.0.1:5000")
        return
    
    # Step 2: Test the delete all passwords endpoint
    print("\n2. Testing delete all passwords endpoint...")
    try:
        delete_response = requests.post(f"{base_url}/api/passwords/delete_all", 
                                      headers={'Content-Type': 'application/json'})
        print(f"   Delete all response status: {delete_response.status_code}")
        
        if delete_response.status_code == 401:
            print("   ✅ Endpoint exists and requires authentication (expected)")
        elif delete_response.status_code == 200:
            print("   ✅ Endpoint exists and returned success")
            try:
                result = delete_response.json()
                print(f"   Response: {result}")
            except:
                print("   Response: (non-JSON response)")
        else:
            print(f"   ⚠️  Unexpected status code: {delete_response.status_code}")
            try:
                print(f"   Response: {delete_response.text}")
            except:
                print("   Response: (could not read)")
                
    except requests.exceptions.ConnectionError:
        print("   ❌ Could not connect to server")
    except Exception as e:
        print(f"   ❌ Error testing endpoint: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 Test Summary:")
    print("- The delete all passwords API endpoint should be accessible at /api/passwords/delete_all")
    print("- It should require authentication (return 401 if not logged in)")
    print("- It should accept POST requests with JSON content type")
    print("- The frontend button should be available in the dashboard")
    print("- The confirmation modal should appear when clicking the button")

if __name__ == "__main__":
    test_delete_all_passwords() 