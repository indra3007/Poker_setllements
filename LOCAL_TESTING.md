# 🎰 Poker Tracker - Local Testing Guide

## Quick Start - Local Testing

### 1. Install Dependencies
```bash
cd /Users/indraneel/Desktop/Python/phonebill/poker_web
/Users/indraneel/Desktop/Python/venv/bin/pip install -r requirements.txt
```

### 2. Run Flask Development Server
```bash
/Users/indraneel/Desktop/Python/venv/bin/python app.py
```

Output should show:
```
🎰 Poker Tracker Web App v2 - Event Management
==================================================
🌐 Development Mode - Running Locally
💻 Open on this computer:
   http://localhost:5001
✅ Ready! Press Ctrl+C to stop
```

### 3. Open in Browser
- **Local PC**: http://localhost:5001
- **Mobile/Other Device**: http://192.168.68.97:5001 (replace with your actual IP)

### 4. Test Event Creation
1. Click **"+ Create New Event"** button
2. Enter event name (e.g., "Christmas Poker")
3. Select a date
4. Click **"Create"**
5. Event should appear in the grid

### 5. Monitor Debug Output
Check the terminal running Flask for debug messages:
```
=== CREATE EVENT CALLED ===
Request JSON: {'event_name': 'Christmas Poker - 2025-12-25'}
Event name: 'Christmas Poker - 2025-12-25'
Creating workbook...
Getting/creating sheet: 'Christmas Poker - 2025-12-25'
Saving workbook...
✅ Event created successfully!
```

## API Testing with curl

### Test 1: List all events
```bash
curl -s http://localhost:5001/api/events | jq .
```

Expected response:
```json
{
  "events": [
    "Christmas Poker - 2025-12-25",
    "New Year Party - 2026-01-01"
  ]
}
```

### Test 2: Create new event
```bash
curl -X POST http://localhost:5001/api/events \
  -H "Content-Type: application/json" \
  -d '{"event_name":"Test Event - 2025-12-23"}'
```

Expected response:
```json
{
  "success": true,
  "event_name": "Test Event - 2025-12-23"
}
```

### Test 3: Verify event was created
```bash
curl -s http://localhost:5001/api/events | jq .
```

## Browser DevTools Debugging

### Open DevTools
Press **F12** and navigate to:

1. **Console Tab** - Shows JavaScript errors/logs
2. **Network Tab** - Shows HTTP requests
   - Look for `/api/events` POST request
   - Check the Response - should have `"success": true`
   - Check Status - should be 200
3. **Sources Tab** - Debug JavaScript code

### What to look for if event creation fails:
1. Network error (red) on `/api/events` POST request
2. Response is not JSON (malformed response)
3. JavaScript error in Console tab
4. Response status is not 200 (check error message)

## Files Created for This Issue

| File | Purpose |
|------|---------|
| `test_direct.py` | Direct Python test of Flask API |
| `test_api.py` | Curl-based API testing |
| `DEBUG_REPORT.md` | Investigation findings |
| `LOCAL_TESTING.md` | This file |

## Deployment to Render

### Prerequisites
- GitHub repository with the code
- Render.com account

### Steps
1. Commit and push changes to GitHub:
   ```bash
   git add .
   git commit -m "Fix: Event creation and add production WSGI server"
   git push
   ```

2. Go to https://render.com
3. Click "New +" → "Web Service"
4. Connect your GitHub repository
5. Configure:
   - Name: `poker-tracker`
   - Environment: `Python 3`
   - Build command: `pip install -r requirements.txt` (auto-filled)
   - Start command: (should auto-detect from render.yaml)

6. Deploy!

### After Deployment
Test the deployed app:
```bash
curl -s https://poker-tracker-xxxxx.onrender.com/api/events | jq .
```

## Troubleshooting

### Issue: Event creation button does nothing
**Solution:**
1. Check browser console (F12) for errors
2. Check Flask terminal for debug output
3. Test API directly with curl

### Issue: "Event already exists" error
**Solution:**
- This is expected if you create the same event twice
- Try with a different event name or date

### Issue: No events appear after creation
**Possible Causes:**
1. Network request failed - check Network tab in DevTools
2. JavaScript error - check Console tab
3. Backend error - check Flask terminal output
4. Browser cache - try Ctrl+Shift+Delete or hard refresh (Cmd+Shift+R on Mac)

### Issue: Port 5001 already in use
**Solution:**
```bash
# Kill the process using port 5001
lsof -i :5001 | grep LISTEN | awk '{print $2}' | xargs kill -9
```

## File Locations
- **Project Root**: `/Users/indraneel/Desktop/Python/phonebill/poker_web`
- **Main App**: `app.py`
- **Frontend**: `templates/index_v2.html`
- **JavaScript**: `static/script_v2.js`
- **Styles**: `static/style.css`
- **Data Files**:
  - `events.json` - List of events
  - `poker_tracker.xlsx` - Event data
  - `settlements_tracking.json` - Settlement records

## Next Steps

1. ✅ Test locally and verify event creation works
2. ✅ Check browser console and network tab for any errors
3. ✅ Deploy to Render
4. ✅ Test on deployed instance
5. Remove debug logging from `app.py` before final deployment (optional)
