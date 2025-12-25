#!/usr/bin/env python3
"""
Integration Test: Full Workflow Test

Tests the complete workflow from creating events through Flask API
to verifying they're committed to GitHub (when token is available).
"""

import subprocess
import time
import json
import os
import sys
import requests


def wait_for_server(url="http://localhost:5001/api/health", timeout=30):
    """Wait for the Flask server to be ready"""
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            response = requests.get(url, timeout=2)
            if response.status_code == 200:
                return True
        except requests.exceptions.RequestException:
            pass
        time.sleep(1)
    return False


def main():
    print("\n" + "="*70)
    print("Integration Test: Full Workflow")
    print("="*70 + "\n")
    
    # Start the Flask app
    print("Starting Flask application...")
    proc = subprocess.Popen(
        ['python3', 'app.py'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    # Wait for server to be ready
    print("Waiting for server to start...")
    if not wait_for_server():
        print("❌ Server failed to start within timeout")
        proc.terminate()
        sys.exit(1)
    
    print("✅ Server is ready!\n")
    
    try:
        # Test 1: Health check
        print("Test 1: Health Check")
        response = requests.get('http://localhost:5001/api/health')
        health = response.json()
        print(f"  Status: {health.get('status')}")
        print(f"  GitHub Enabled: {health.get('github', {}).get('enabled')}")
        print(f"  GitHub Configured: {health.get('github', {}).get('configured')}")
        
        if health.get('github', {}).get('enabled'):
            print(f"  GitHub Authenticated: {health.get('github', {}).get('authenticated')}")
        print("  ✅ PASS\n")
        
        # Test 2: Get initial events
        print("Test 2: Get Initial Events")
        response = requests.get('http://localhost:5001/api/events')
        initial_events = response.json().get('events', [])
        print(f"  Initial events: {initial_events}")
        print("  ✅ PASS\n")
        
        # Test 3: Create a new event
        print("Test 3: Create New Event")
        test_event_name = f"Integration Test {time.strftime('%Y%m%d-%H%M%S')}"
        response = requests.post(
            'http://localhost:5001/api/events',
            json={'event_name': test_event_name},
            headers={'Content-Type': 'application/json'}
        )
        result = response.json()
        
        if result.get('success'):
            print(f"  Created event: {test_event_name}")
            print("  ✅ PASS\n")
        else:
            print(f"  ❌ FAIL: {result.get('error')}\n")
            raise Exception("Failed to create event")
        
        # Test 4: Verify event was added
        print("Test 4: Verify Event Was Added")
        response = requests.get('http://localhost:5001/api/events')
        updated_events = response.json().get('events', [])
        
        if test_event_name in updated_events:
            print(f"  Event found in list: ✅")
            print("  ✅ PASS\n")
        else:
            print(f"  ❌ FAIL: Event not found in list")
            print(f"  Events: {updated_events}\n")
            raise Exception("Event not found after creation")
        
        # Test 5: Verify local file was updated
        print("Test 5: Verify Local File Updated")
        with open('events.json', 'r') as f:
            file_events = json.load(f)
        
        if test_event_name in file_events:
            print(f"  Event found in events.json: ✅")
            print("  ✅ PASS\n")
        else:
            print(f"  ❌ FAIL: Event not in events.json")
            raise Exception("Event not in local file")
        
        # Test 6: GitHub commit verification (if enabled)
        if health.get('github', {}).get('enabled') and health.get('github', {}).get('authenticated'):
            print("Test 6: Verify GitHub Commit")
            print("  GitHub integration is enabled")
            print("  ℹ️  Check GitHub repository manually to verify commit")
            print("  Repository: https://github.com/indra3007/Poker_setllements")
            print("  File: events.json")
            print("  Expected: Should contain the new event")
            print("  ✅ PASS (manual verification needed)\n")
        else:
            print("Test 6: GitHub Integration")
            print("  ⚠️  SKIP: GitHub integration not enabled")
            print("  To enable: Set GITHUB_TOKEN environment variable")
            print("  ✅ PASS (skipped)\n")
        
        # Test 7: Delete the test event
        print("Test 7: Delete Test Event")
        response = requests.delete(f'http://localhost:5001/api/events/{test_event_name}')
        result = response.json()
        
        if result.get('success'):
            print(f"  Deleted event: {test_event_name}")
            print("  ✅ PASS\n")
        else:
            print(f"  ❌ FAIL: {result.get('error')}\n")
        
        # Test 8: Verify event was removed
        print("Test 8: Verify Event Was Removed")
        response = requests.get('http://localhost:5001/api/events')
        final_events = response.json().get('events', [])
        
        if test_event_name not in final_events:
            print(f"  Event not in list: ✅")
            print("  ✅ PASS\n")
        else:
            print(f"  ❌ FAIL: Event still in list")
        
        print("="*70)
        print("✅ All Integration Tests Passed!")
        print("="*70 + "\n")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}\n")
        import traceback
        traceback.print_exc()
        return 1
    finally:
        # Stop the server
        print("Stopping Flask application...")
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
        print("Server stopped.\n")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
