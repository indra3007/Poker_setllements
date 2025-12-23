#!/usr/bin/env python3
"""
Direct test of Flask app functions
"""

import sys
import os
sys.path.insert(0, '/Users/indraneel/Desktop/Python/phonebill/poker_web')
os.chdir('/Users/indraneel/Desktop/Python/phonebill/poker_web')

# Test imports
print("Testing imports...")
try:
    from app import app, load_events, save_events
    print("✅ App imports successful")
except Exception as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)

# Test load_events function
print("\nTesting load_events()...")
try:
    events = load_events()
    print(f"✅ load_events() returned: {events}")
except Exception as e:
    print(f"❌ Error: {e}")

# Test save_events function
print("\nTesting save_events()...")
try:
    test_events = ["Test Event 1", "Test Event 2"]
    save_events(test_events)
    print(f"✅ save_events() successful")
    
    # Reload and verify
    loaded = load_events()
    print(f"✅ Reloaded events: {loaded}")
except Exception as e:
    print(f"❌ Error: {e}")

# Test Flask test client
print("\nTesting Flask routes...")
try:
    with app.test_client() as client:
        print("\n1. Testing GET /api/events...")
        response = client.get('/api/events')
        print(f"   Status: {response.status_code}")
        print(f"   Data: {response.get_json()}")
        
        print("\n2. Testing POST /api/events...")
        response = client.post('/api/events', 
                              json={"event_name": "Test Event - 2025-12-23"})
        print(f"   Status: {response.status_code}")
        print(f"   Data: {response.get_json()}")
        
        print("\n3. Testing GET /api/events again...")
        response = client.get('/api/events')
        print(f"   Status: {response.status_code}")
        print(f"   Data: {response.get_json()}")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n✅ All tests completed!")
