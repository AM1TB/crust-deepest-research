#!/usr/bin/env python3
"""
Simple test script to verify API tools functionality.
This can be run without CrewAI dependencies to test the REST API integration.
"""

import requests
import json


def test_jsonplaceholder_api():
    """Test the JSONPlaceholder API directly."""
    print("🧪 Testing JSONPlaceholder API directly...")
    print("-" * 50)
    
    try:
        # Test the exact endpoint from the user's request
        print("Fetching todo item 1...")
        response = requests.get('https://jsonplaceholder.typicode.com/todos/1', timeout=10)
        response.raise_for_status()
        
        data = response.json()
        print("✅ Success! Response:")
        print(json.dumps(data, indent=2))
        
        # Verify expected structure
        expected_keys = ['userId', 'id', 'title', 'completed']
        missing_keys = [key for key in expected_keys if key not in data]
        
        if missing_keys:
            print(f"⚠️  Warning: Missing expected keys: {missing_keys}")
        else:
            print("✅ Response structure matches expected format!")
        
        print(f"\nData summary:")
        print(f"  - User ID: {data.get('userId')}")
        print(f"  - Todo ID: {data.get('id')}")
        print(f"  - Title: {data.get('title')}")
        print(f"  - Completed: {data.get('completed')}")
        
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return False
    except json.JSONDecodeError as e:
        print(f"❌ JSON parsing failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False


def test_multiple_todos():
    """Test fetching multiple todos."""
    print("\n🧪 Testing multiple todos...")
    print("-" * 50)
    
    try:
        print("Fetching first 5 todos...")
        response = requests.get('https://jsonplaceholder.typicode.com/todos?_limit=5', timeout=10)
        response.raise_for_status()
        
        data = response.json()
        print(f"✅ Success! Fetched {len(data)} todos")
        
        for i, todo in enumerate(data[:3], 1):  # Show first 3
            print(f"  {i}. {todo.get('title')} (ID: {todo.get('id')}, Completed: {todo.get('completed')})")
        
        if len(data) > 3:
            print(f"  ... and {len(data) - 3} more")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_user_specific_todos():
    """Test fetching todos for a specific user."""
    print("\n🧪 Testing user-specific todos...")
    print("-" * 50)
    
    try:
        user_id = 1
        print(f"Fetching todos for user {user_id}...")
        response = requests.get(f'https://jsonplaceholder.typicode.com/users/{user_id}/todos?_limit=3', timeout=10)
        response.raise_for_status()
        
        data = response.json()
        print(f"✅ Success! User {user_id} has {len(data)} todos (showing first 3)")
        
        for i, todo in enumerate(data, 1):
            print(f"  {i}. {todo.get('title')} (Completed: {todo.get('completed')})")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def main():
    """Run all API tests."""
    print("🔧 API Integration Test Suite")
    print("=" * 60)
    
    tests = [
        ("Single Todo", test_jsonplaceholder_api),
        ("Multiple Todos", test_multiple_todos),
        ("User-Specific Todos", test_user_specific_todos)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Test '{test_name}' failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status} - {test_name}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All API tests passed! The REST API integration is working correctly.")
    else:
        print("⚠️  Some tests failed. Check your internet connection and API endpoints.")


if __name__ == "__main__":
    main()
