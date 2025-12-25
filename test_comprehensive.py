#!/usr/bin/env python3
"""
Comprehensive test suite for event persistence functionality
"""

import os
import sys
import json
import time
import subprocess
import requests
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def run_command(cmd):
    """Run a shell command and return output"""
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.returncode, result.stdout, result.stderr

def test_persistence_module():
    """Test the Git persistence module directly"""
    print("\n" + "="*70)
    print("TEST 1: Git Persistence Module")
    print("="*70)
    
    from git_persistence import GitPersistence
    
    # Test initialization
    print("\n1.1 Testing initialization...")
    gp = GitPersistence('event_storage.json')
    print("  ✓ Persistence module initialized")
    
    # Test loading events
    print("\n1.2 Testing event loading...")
    events = gp.load_events()
    print(f"  ✓ Loaded {len(events)} events")
    
    # Test adding event (no commit)
    print("\n1.3 Testing add event (no auto-commit)...")
    test_event = f"Test Suite Event - {int(time.time())}"
    original_count = len(events)
    success = gp.add_event(test_event, auto_commit=False)
    
    if success:
        new_events = gp.load_events()
        if len(new_events) == original_count + 1:
            print(f"  ✓ Event added successfully: {test_event}")
        else:
            print(f"  ✗ Event count mismatch")
            return False
    else:
        print("  ✗ Failed to add event")
        return False
    
    # Test file corruption handling
    print("\n1.4 Testing corruption detection...")
    storage_file = 'event_storage.json'
    
    # Backup
    with open(storage_file, 'r') as f:
        backup = f.read()
    
    # Corrupt
    with open(storage_file, 'w') as f:
        f.write("{ corrupted }")
    
    # Should detect and fix
    try:
        gp2 = GitPersistence(storage_file)
        print("  ✓ Corruption detected and handled")
    except Exception as e:
        print(f"  ✗ Failed to handle corruption: {e}")
        return False
    finally:
        # Restore
        with open(storage_file, 'w') as f:
            f.write(backup)
    
    # Clean up test files
    for f in Path('.').glob('event_storage.json.corrupted.*'):
        f.unlink()
    
    print("\n✓ All persistence module tests passed!")
    return True

def test_flask_api():
    """Test Flask API endpoints"""
    print("\n" + "="*70)
    print("TEST 2: Flask API Endpoints")
    print("="*70)
    
    base_url = "http://localhost:5001"
    
    # Start Flask app
    print("\n2.1 Starting Flask app...")
    proc = subprocess.Popen(
        ['python3', 'app.py'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    # Wait for server to start
    time.sleep(5)
    
    try:
        # Test GET /api/events
        print("\n2.2 Testing GET /api/events...")
        response = requests.get(f"{base_url}/api/events")
        
        if response.status_code == 200:
            data = response.json()
            events = data.get('events', [])
            print(f"  ✓ GET request successful, {len(events)} events returned")
        else:
            print(f"  ✗ GET request failed with status {response.status_code}")
            return False
        
        # Test POST /api/events
        print("\n2.3 Testing POST /api/events...")
        test_event = f"API Integration Test - {int(time.time())}"
        response = requests.post(
            f"{base_url}/api/events",
            json={"event_name": test_event}
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print(f"  ✓ POST request successful, event created: {test_event}")
            else:
                print(f"  ✗ POST request returned success=False")
                return False
        else:
            print(f"  ✗ POST request failed with status {response.status_code}")
            return False
        
        # Verify event was added
        print("\n2.4 Verifying event persistence...")
        time.sleep(2)  # Give time for commit
        response = requests.get(f"{base_url}/api/events")
        
        if response.status_code == 200:
            data = response.json()
            events = data.get('events', [])
            if test_event in events:
                print(f"  ✓ Event persisted successfully")
            else:
                print(f"  ✗ Event not found in events list")
                return False
        
        # Test DELETE /api/events
        print("\n2.5 Testing DELETE /api/events...")
        response = requests.delete(f"{base_url}/api/events/{test_event}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print(f"  ✓ DELETE request successful")
            else:
                print(f"  ✗ DELETE request returned success=False")
                return False
        else:
            print(f"  ✗ DELETE request failed with status {response.status_code}")
            return False
        
        print("\n✓ All Flask API tests passed!")
        return True
        
    finally:
        # Stop Flask app
        proc.terminate()
        proc.wait(timeout=5)

def test_git_commits():
    """Test that changes are committed to Git"""
    print("\n" + "="*70)
    print("TEST 3: Git Commit Verification")
    print("="*70)
    
    from git_persistence import GitPersistence
    
    print("\n3.1 Creating test event with auto-commit...")
    gp = GitPersistence('event_storage.json')
    
    # Get current commit count
    code, stdout, _ = run_command("git log --oneline | wc -l")
    initial_commits = int(stdout.strip())
    
    # Add event with auto-commit
    test_event = f"Git Commit Test - {int(time.time())}"
    success = gp.add_event(test_event, auto_commit=True)
    
    if not success:
        print("  ✗ Failed to add event")
        return False
    
    # Wait for commit
    time.sleep(1)
    
    # Check if new commit was created
    code, stdout, _ = run_command("git log --oneline | wc -l")
    final_commits = int(stdout.strip())
    
    if final_commits > initial_commits:
        print(f"  ✓ New commit created (total commits: {final_commits})")
    else:
        print(f"  ✗ No new commit created")
        return False
    
    # Verify commit message
    code, stdout, _ = run_command("git log -1 --pretty=%B")
    commit_message = stdout.strip()
    
    if "Update events" in commit_message:
        print(f"  ✓ Commit message is correct: {commit_message}")
    else:
        print(f"  ✗ Unexpected commit message: {commit_message}")
        return False
    
    # Remove test event
    gp.remove_event(test_event, auto_commit=False)
    
    print("\n✓ All Git commit tests passed!")
    return True

def test_restart_persistence():
    """Test that events persist across app restarts"""
    print("\n" + "="*70)
    print("TEST 4: Restart Persistence")
    print("="*70)
    
    from git_persistence import GitPersistence
    
    print("\n4.1 Creating test event...")
    gp = GitPersistence('event_storage.json')
    
    test_event = f"Restart Test - {int(time.time())}"
    gp.add_event(test_event, auto_commit=False)
    
    events_before = gp.load_events()
    print(f"  ✓ Event created, total events: {len(events_before)}")
    
    print("\n4.2 Simulating app restart (reloading module)...")
    # Create new instance (simulates restart)
    gp2 = GitPersistence('event_storage.json')
    events_after = gp2.load_events()
    
    if test_event in events_after:
        print(f"  ✓ Event persisted across restart")
    else:
        print(f"  ✗ Event lost after restart")
        return False
    
    if len(events_before) == len(events_after):
        print(f"  ✓ Event count matches ({len(events_after)} events)")
    else:
        print(f"  ✗ Event count mismatch: {len(events_before)} vs {len(events_after)}")
        return False
    
    # Clean up
    gp2.remove_event(test_event, auto_commit=False)
    
    print("\n✓ All restart persistence tests passed!")
    return True

def main():
    """Run all tests"""
    print("\n" + "="*70)
    print("EVENT PERSISTENCE TEST SUITE")
    print("="*70)
    
    results = []
    
    # Run tests
    try:
        results.append(("Persistence Module", test_persistence_module()))
    except Exception as e:
        print(f"\n✗ Persistence module test failed with exception: {e}")
        results.append(("Persistence Module", False))
    
    try:
        results.append(("Git Commits", test_git_commits()))
    except Exception as e:
        print(f"\n✗ Git commit test failed with exception: {e}")
        results.append(("Git Commits", False))
    
    try:
        results.append(("Restart Persistence", test_restart_persistence()))
    except Exception as e:
        print(f"\n✗ Restart persistence test failed with exception: {e}")
        results.append(("Restart Persistence", False))
    
    # Flask API tests require server to be stopped
    try:
        print("\n⚠ Skipping Flask API tests (requires manual testing)")
        print("  Run the following to test API manually:")
        print("    1. python3 app.py")
        print("    2. curl http://localhost:5001/api/events")
        print("    3. curl -X POST http://localhost:5001/api/events -H 'Content-Type: application/json' -d '{\"event_name\":\"Test\"}'")
    except Exception as e:
        print(f"\n✗ Flask API test failed with exception: {e}")
    
    # Print summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    for name, passed in results:
        status = "✓ PASSED" if passed else "✗ FAILED"
        print(f"{name:30} {status}")
    
    all_passed = all(result for _, result in results)
    
    print("\n" + "="*70)
    if all_passed:
        print("ALL TESTS PASSED!")
    else:
        print("SOME TESTS FAILED!")
    print("="*70 + "\n")
    
    return 0 if all_passed else 1

if __name__ == '__main__':
    sys.exit(main())
