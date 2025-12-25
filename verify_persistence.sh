#!/bin/bash
# Final verification script for event persistence

echo "======================================================================"
echo "FINAL VERIFICATION TEST - Event Persistence"
echo "======================================================================"

# Wait for Flask to be ready
sleep 2

# Test 1: GET events
echo ""
echo "Test 1: GET /api/events"
echo "----------------------------------------------------------------------"
curl -s http://localhost:5001/api/events | python3 -m json.tool

# Test 2: Create new event
echo ""
echo "Test 2: POST /api/events (Create event)"
echo "----------------------------------------------------------------------"
TIMESTAMP=$(date +%s)
EVENT_NAME="Final Verification - $TIMESTAMP"
curl -s -X POST http://localhost:5001/api/events \
  -H "Content-Type: application/json" \
  -d "{\"event_name\":\"$EVENT_NAME\"}" | python3 -m json.tool

# Wait for commit
sleep 8

# Test 3: Verify event in list
echo ""
echo "Test 3: Verify event persisted"
echo "----------------------------------------------------------------------"
curl -s http://localhost:5001/api/events | python3 -m json.tool | grep "$EVENT_NAME" && echo "✓ Event found!" || echo "✗ Event not found!"

# Test 4: Check Git commit
echo ""
echo "Test 4: Verify Git commit"
echo "----------------------------------------------------------------------"
git log --oneline -1 | grep "Update events" && echo "✓ Git commit created!" || echo "✗ No Git commit!"

# Test 5: Delete event
echo ""
echo "Test 5: DELETE /api/events (Clean up)"
echo "----------------------------------------------------------------------"
curl -s -X DELETE "http://localhost:5001/api/events/$EVENT_NAME" | python3 -m json.tool

echo ""
echo "======================================================================"
echo "FINAL VERIFICATION COMPLETE"
echo "======================================================================"
