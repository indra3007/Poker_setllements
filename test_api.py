#!/usr/bin/env python3
"""
Test script for the Poker Tracker API
"""

import subprocess
import time
import json
import sys

# Give the server a moment to start if needed
time.sleep(1)

# Test 1: GET /api/events
print("\n=== TEST 1: GET /api/events ===")
try:
    result = subprocess.run(
        ['curl', '-s', '-X', 'GET', 'http://localhost:5001/api/events'],
        capture_output=True,
        text=True,
        timeout=5
    )
    print("Status Code: Check response below")
    print("Response:", result.stdout)
    if result.stderr:
        print("Error:", result.stderr)
except Exception as e:
    print(f"ERROR: {e}")

time.sleep(0.5)

# Test 2: POST /api/events - Create Event
print("\n=== TEST 2: POST /api/events (Create Event) ===")
try:
    payload = json.dumps({"event_name": "Test Event - 2025-12-23"})
    result = subprocess.run(
        ['curl', '-s', '-X', 'POST', 
         'http://localhost:5001/api/events',
         '-H', 'Content-Type: application/json',
         '-d', payload],
        capture_output=True,
        text=True,
        timeout=5
    )
    print("Response:", result.stdout)
    if result.stderr:
        print("Error:", result.stderr)
except Exception as e:
    print(f"ERROR: {e}")

time.sleep(0.5)

# Test 3: GET /api/events again
print("\n=== TEST 3: GET /api/events (After Create) ===")
try:
    result = subprocess.run(
        ['curl', '-s', '-X', 'GET', 'http://localhost:5001/api/events'],
        capture_output=True,
        text=True,
        timeout=5
    )
    print("Response:", result.stdout)
    if result.stderr:
        print("Error:", result.stderr)
except Exception as e:
    print(f"ERROR: {e}")

print("\n=== TESTS COMPLETE ===")
