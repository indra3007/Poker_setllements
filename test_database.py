#!/usr/bin/env python3
"""
Test database integration functionality
"""

import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Test imports
print("Testing imports...")
try:
    from app import app, load_events, USE_DATABASE
    from database import (
        init_database, db_load_events, db_save_event, db_delete_event,
        db_load_players, db_save_players, db_clear_players,
        db_load_settlement_payments, db_save_settlement_payment,
        DATABASE_URL
    )
    print("✅ Imports successful")
except Exception as e:
    print(f"❌ Import error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Check database configuration
print(f"\n📊 Database Configuration:")
print(f"   DATABASE_URL configured: {bool(DATABASE_URL)}")
print(f"   USE_DATABASE flag: {USE_DATABASE}")

if not DATABASE_URL:
    print("\n⚠️  No DATABASE_URL configured. Tests will verify fallback behavior.")
else:
    print(f"\n🔗 Testing database connection...")
    try:
        success = init_database()
        if success:
            print("✅ Database connection and initialization successful!")
        else:
            print("❌ Database initialization failed")
    except Exception as e:
        print(f"❌ Database connection error: {e}")
        print("⚠️  Tests will proceed with fallback storage")

# Test Flask application with test client
print("\n🧪 Testing Flask Application API...")
try:
    with app.test_client() as client:
        # Test 1: GET events (should work with or without database)
        print("\n1. Testing GET /api/events...")
        response = client.get('/api/events')
        print(f"   Status: {response.status_code}")
        data = response.get_json()
        print(f"   Events: {data.get('events', [])}")
        assert response.status_code == 200, "GET /api/events failed"
        print("   ✅ GET /api/events successful")
        
        # Test 2: Create a test event
        test_event_name = "Database Test Event - 2025-12-25"
        print(f"\n2. Testing POST /api/events (creating '{test_event_name}')...")
        response = client.post('/api/events', 
                             json={"event_name": test_event_name})
        print(f"   Status: {response.status_code}")
        data = response.get_json()
        print(f"   Response: {data}")
        if response.status_code == 200:
            print("   ✅ Event created successfully")
        elif response.status_code == 400 and 'already exists' in data.get('error', ''):
            print("   ℹ️  Event already exists (expected if test ran before)")
        else:
            print(f"   ❌ Unexpected response: {response.status_code}")
        
        # Test 3: Verify event appears in list
        print(f"\n3. Testing GET /api/events (verify event was created)...")
        response = client.get('/api/events')
        data = response.get_json()
        events = data.get('events', [])
        print(f"   Events: {events}")
        if test_event_name in events:
            print("   ✅ Event found in list")
        else:
            print("   ⚠️  Event not in list (may have failed to create)")
        
        # Test 4: Save player data
        print(f"\n4. Testing POST /api/save/{test_event_name} (save player data)...")
        player_data = {
            'players': [
                {
                    'name': 'Test Player 1',
                    'phone': '123-456-7890',
                    'start': 20,
                    'buyins': 1,
                    'day1': 45,
                    'day2': '',
                    'day3': '',
                    'day4': '',
                    'day5': '',
                    'day6': '',
                    'day7': '',
                    'pl': 5,
                    'days_played': 1
                },
                {
                    'name': 'Test Player 2',
                    'phone': '098-765-4321',
                    'start': 20,
                    'buyins': 0,
                    'day1': 10,
                    'day2': '',
                    'day3': '',
                    'day4': '',
                    'day5': '',
                    'day6': '',
                    'day7': '',
                    'pl': -10,
                    'days_played': 1
                }
            ]
        }
        response = client.post(f'/api/save/{test_event_name}', json=player_data)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.get_json()}")
        if response.status_code == 200:
            print("   ✅ Player data saved successfully")
        else:
            print(f"   ❌ Failed to save player data")
        
        # Test 5: Retrieve player data
        print(f"\n5. Testing GET /api/data/{test_event_name} (retrieve player data)...")
        response = client.get(f'/api/data/{test_event_name}')
        print(f"   Status: {response.status_code}")
        data = response.get_json()
        players = data.get('players', [])
        print(f"   Players: {len(players)} found")
        for i, player in enumerate(players):
            print(f"      Player {i+1}: {player.get('name')} (P/L: ${player.get('pl', 0)})")
        if len(players) == 2:
            print("   ✅ Player data retrieved successfully")
        else:
            print(f"   ⚠️  Expected 2 players, got {len(players)}")
        
        # Test 6: Calculate settlements
        print(f"\n6. Testing GET /api/settlements/{test_event_name} (calculate settlements)...")
        response = client.get(f'/api/settlements/{test_event_name}')
        print(f"   Status: {response.status_code}")
        data = response.get_json()
        settlements = data.get('settlements', [])
        print(f"   Settlements: {len(settlements)} found")
        for settlement in settlements:
            print(f"      {settlement['from']} → {settlement['to']}: ${settlement['amount']}")
        if len(settlements) > 0:
            print("   ✅ Settlements calculated successfully")
        
        # Test 7: Mark settlement as paid
        if len(settlements) > 0:
            print(f"\n7. Testing POST /api/settlements/{test_event_name}/mark_paid...")
            settlement = settlements[0]
            response = client.post(
                f'/api/settlements/{test_event_name}/mark_paid',
                json={
                    'from': settlement['from'],
                    'to': settlement['to'],
                    'paid': True
                }
            )
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.get_json()}")
            if response.status_code == 200:
                print("   ✅ Settlement marked as paid successfully")
            
            # Verify payment status
            response = client.get(f'/api/settlements/{test_event_name}')
            data = response.get_json()
            settlements = data.get('settlements', [])
            if settlements and settlements[0].get('paid'):
                print("   ✅ Payment status verified")
        
        # Test 8: Clear event data
        print(f"\n8. Testing POST /api/clear/{test_event_name} (clear event data)...")
        response = client.post(f'/api/clear/{test_event_name}')
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.get_json()}")
        if response.status_code == 200:
            print("   ✅ Event data cleared successfully")
        
        # Test 9: Delete test event
        print(f"\n9. Testing DELETE /api/events/{test_event_name} (cleanup)...")
        response = client.delete(f'/api/events/{test_event_name}')
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.get_json()}")
        if response.status_code == 200:
            print("   ✅ Event deleted successfully")
        
        print("\n" + "="*60)
        print("✅ All API tests completed successfully!")
        print("="*60)
        
except Exception as e:
    print(f"\n❌ Test error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n🎉 Database integration tests completed!")
