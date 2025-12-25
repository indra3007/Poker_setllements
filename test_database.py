#!/usr/bin/env python3
"""
Test script for database operations
"""

import db
import sys

print("=" * 60)
print("Testing PostgreSQL Database Operations")
print("=" * 60)

# Test 1: Initialize database
print("\n1. Initializing database...")
try:
    db.init_database()
    print("   ✅ Database initialized successfully")
except Exception as e:
    print(f"   ❌ Error: {e}")
    sys.exit(1)

# Test 2: Create an event
print("\n2. Creating test event...")
try:
    test_event = "Test Event - DB Test"
    db.create_event(test_event)
    print(f"   ✅ Event '{test_event}' created")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test 3: Get all events
print("\n3. Getting all events...")
try:
    events = db.get_all_events()
    print(f"   ✅ Found {len(events)} event(s):")
    for event in events:
        print(f"      - {event}")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test 4: Check if event exists
print("\n4. Checking if event exists...")
try:
    exists = db.event_exists(test_event)
    print(f"   ✅ Event exists: {exists}")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test 5: Save player data
print("\n5. Saving player data...")
try:
    players = [
        {
            'name': 'Player 1',
            'phone': '555-0001',
            'start': 20,
            'buyins': 2,
            'day1': 50,
            'day2': 75,
            'day3': '',
            'day4': '',
            'day5': '',
            'day6': '',
            'day7': '',
            'pl': 15,
            'days_played': 2
        },
        {
            'name': 'Player 2',
            'phone': '555-0002',
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
    db.save_event_players(test_event, players)
    print(f"   ✅ Saved {len(players)} player(s)")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test 6: Get player data
print("\n6. Getting player data...")
try:
    players = db.get_event_players(test_event)
    print(f"   ✅ Retrieved {len(players)} player(s):")
    for player in players:
        print(f"      - {player['name']}: P/L = ${player['pl']}")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test 7: Mark settlement as paid
print("\n7. Marking settlement as paid...")
try:
    db.mark_settlement_paid(test_event, 'Player 2', 'Player 1', True)
    print("   ✅ Settlement marked as paid")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test 8: Get settlement payments
print("\n8. Getting settlement payments...")
try:
    payments = db.get_settlement_payments(test_event)
    print(f"   ✅ Retrieved {len(payments)} settlement(s):")
    for key, paid in payments.items():
        print(f"      - {key}: {'PAID' if paid else 'UNPAID'}")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test 9: Delete event
print("\n9. Deleting test event...")
try:
    db.delete_event(test_event)
    print(f"   ✅ Event '{test_event}' deleted")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test 10: Verify deletion
print("\n10. Verifying event deletion...")
try:
    events = db.get_all_events()
    if test_event not in events:
        print(f"   ✅ Event successfully deleted (total events: {len(events)})")
    else:
        print(f"   ❌ Event still exists!")
except Exception as e:
    print(f"   ❌ Error: {e}")

print("\n" + "=" * 60)
print("All database tests completed!")
print("=" * 60)
