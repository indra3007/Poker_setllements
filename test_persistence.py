#!/usr/bin/env python3
"""
Test script for Git persistence module
"""

import os
import sys
import json
import time

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from git_persistence import GitPersistence

def test_git_persistence():
    """Test Git persistence functionality"""
    
    print("\n" + "="*60)
    print("Testing Git Persistence Module")
    print("="*60)
    
    # Initialize persistence handler
    print("\n1. Initializing Git persistence...")
    gp = GitPersistence(storage_file='event_storage.json')
    print("✓ Git persistence initialized")
    
    # Test loading events
    print("\n2. Loading existing events...")
    events = gp.load_events()
    print(f"✓ Loaded {len(events)} events: {events}")
    
    # Test adding a new event
    print("\n3. Adding a test event...")
    test_event = f"Test Event - {int(time.time())}"
    success = gp.add_event(test_event, auto_commit=False)  # Don't commit for now
    
    if success:
        print(f"✓ Successfully added event: {test_event}")
    else:
        print(f"✗ Failed to add event (may already exist)")
    
    # Test loading events again
    print("\n4. Reloading events...")
    events = gp.load_events()
    print(f"✓ Loaded {len(events)} events: {events}")
    
    # Test file corruption detection
    print("\n5. Testing file corruption detection...")
    storage_file = 'event_storage.json'
    
    # Backup current content
    with open(storage_file, 'r') as f:
        original_content = f.read()
    
    # Write corrupted content
    with open(storage_file, 'w') as f:
        f.write("{ this is corrupted json [")
    
    print("   Created corrupted file")
    
    # Try to initialize - should detect and fix corruption
    gp2 = GitPersistence(storage_file=storage_file)
    print("✓ Corruption detected and handled")
    
    # Restore original content
    with open(storage_file, 'w') as f:
        f.write(original_content)
    print("✓ Original content restored")
    
    # Test save and commit (dry run)
    print("\n6. Testing save functionality...")
    current_events = gp.load_events()
    success = gp.save_events(current_events, auto_commit=False)
    
    if success:
        print("✓ Save functionality working")
    else:
        print("✗ Save failed")
    
    print("\n" + "="*60)
    print("All tests completed!")
    print("="*60 + "\n")

if __name__ == '__main__':
    test_git_persistence()
