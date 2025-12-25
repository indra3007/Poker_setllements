# Event Persistence Implementation

## Overview
This document describes the Git-based event persistence implementation that ensures events are not lost when the application goes to sleep on Render's free tier.

## Problem Statement
On Render's free tier, applications go to sleep after periods of inactivity. When this happens, any changes to the filesystem are lost, causing newly created events to disappear.

## Solution
The solution implements Git-based persistence where every event change is automatically committed to the Git repository. This ensures that:
1. Events are persisted to `event_storage.json`
2. Changes are committed to Git locally
3. Attempts are made to push to remote (with graceful handling of failures)
4. Events are loaded from persistent storage on app startup

## Architecture

### Components

#### 1. `git_persistence.py`
The core persistence module that handles:
- File-based storage with `event_storage.json`
- Automatic Git commits for every change
- Retry logic with exponential backoff (3 retries: 1s, 2s, 4s delays)
- File corruption detection and recovery
- Comprehensive error handling and logging

#### 2. Updated `app.py`
Modified to use the Git persistence module:
- Loads events from persistent storage on startup
- Saves events with automatic Git commits
- Uses the renamed `event_storage.json` file

#### 3. Updated `.gitignore`
Ensures `event_storage.json` is tracked by Git (not ignored)

## Key Features

### 1. Automatic Git Commits
Every event creation or deletion triggers:
```python
# In git_persistence.py
def commit_changes(self, message: str) -> bool:
    - Add file to git staging
    - Check for changes
    - Commit with descriptive message
    - Attempt to push to remote
    - Return success status
```

### 2. Retry Logic with Exponential Backoff
Failed Git operations are retried up to 3 times:
```python
Retry 1: Wait 1 second
Retry 2: Wait 2 seconds
Retry 3: Wait 4 seconds
```

### 3. File Corruption Detection
On initialization, the module checks if the storage file is valid JSON:
```python
- If corrupted: Backup to .corrupted.{timestamp} file
- Reinitialize with empty event list
- Log error for debugging
```

### 4. Graceful Push Failures
If push to remote fails (common on platforms without Git credentials):
- Logs warning
- Continues operation (file is still saved and committed locally)
- Returns success (local persistence is sufficient)

## Usage

### Basic Usage
```python
from git_persistence import GitPersistence

# Initialize
gp = GitPersistence('event_storage.json')

# Load events
events = gp.load_events()

# Add event (with auto-commit)
gp.add_event("New Event", auto_commit=True)

# Remove event (with auto-commit)
gp.remove_event("Old Event", auto_commit=True)

# Save events (with auto-commit)
gp.save_events(["Event 1", "Event 2"], auto_commit=True)
```

### Flask Integration
```python
from flask import Flask, jsonify
from git_persistence import GitPersistence

app = Flask(__name__)
git_persistence = GitPersistence('event_storage.json')

@app.route('/api/events', methods=['GET'])
def get_events():
    events = git_persistence.load_events()
    return jsonify({'events': events})

@app.route('/api/events', methods=['POST'])
def create_event():
    event_name = request.json.get('event_name')
    success = git_persistence.add_event(event_name, auto_commit=True)
    return jsonify({'success': success})
```

## Configuration

### Environment Variables (Optional)
Currently, the module uses default Git configuration. For production deployments on Render, you may want to add:

```yaml
# render.yaml
envVars:
  - key: GIT_USER_EMAIL
    value: app@pokertracker.local
  - key: GIT_USER_NAME
    value: Poker Tracker App
```

### Tunable Parameters
```python
GitPersistence(
    storage_file='event_storage.json',  # Name of storage file
    max_retries=3                       # Number of retry attempts
)
```

## Error Handling

### Scenario 1: File Not Found
- Creates new file with empty event list
- Logs initialization message

### Scenario 2: Corrupted File
- Backs up corrupted file with timestamp
- Reinitializes with empty event list
- Logs error with details

### Scenario 3: Git Commit Failure
- Retries with exponential backoff
- Logs warning if all retries fail
- Returns False to indicate failure

### Scenario 4: Git Push Failure
- Retries with exponential backoff
- Logs warning (this is expected without credentials)
- Returns True (local commit is sufficient)

## Logging

The module uses Python's logging framework with INFO level:

```
2025-12-25 19:52:19,354 - git_persistence - INFO - Storage file loaded successfully
2025-12-25 19:52:19,354 - git_persistence - INFO - Loaded 7 events from storage
2025-12-25 19:52:19,361 - git_persistence - INFO - Adding event_storage.json to git
2025-12-25 19:52:19,365 - git_persistence - INFO - Committing changes: Update events: 9 event(s) stored
2025-12-25 19:52:19,370 - git_persistence - INFO - Successfully committed changes
2025-12-25 19:52:19,530 - git_persistence - WARNING - Failed to push to remote (expected)
```

## Testing

### Unit Tests
Run `test_persistence.py` for basic persistence module tests:
```bash
python3 test_persistence.py
```

### Comprehensive Tests
Run `test_comprehensive.py` for full test suite:
```bash
python3 test_comprehensive.py
```

### Manual API Tests
```bash
# Start Flask app
python3 app.py

# Test GET events
curl http://localhost:5001/api/events

# Test POST event
curl -X POST http://localhost:5001/api/events \
  -H "Content-Type: application/json" \
  -d '{"event_name":"Test Event"}'

# Test DELETE event
curl -X DELETE http://localhost:5001/api/events/Test%20Event
```

## Deployment on Render

### Prerequisites
1. Git repository connected to Render
2. `render.yaml` configured with build and start commands
3. Python dependencies in `requirements.txt`

### Deployment Steps
1. Push changes to GitHub
2. Render automatically detects changes
3. Builds and deploys application
4. Application loads events from `event_storage.json` on startup

### Post-Deployment Verification
1. Create an event via the UI
2. Check Render logs for Git commit messages
3. Wait for app to sleep (or manually restart)
4. Wake app and verify event persists

## Troubleshooting

### Events Not Persisting
**Check:** Are Git commits being created?
```bash
git log --oneline | head
```

**Check:** Is event_storage.json being tracked?
```bash
git ls-files | grep event_storage.json
```

### Git Push Failures
**Expected:** On Render without Git credentials configured
**Impact:** None - local commits are sufficient
**Solution:** If push is desired, configure Git credentials via environment variables

### File Corruption
**Symptoms:** Empty events list after app restart
**Check:** Look for `.corrupted.{timestamp}` backup files
**Recovery:** Restore from backup or reinitialize

### Performance Issues
**Symptoms:** Slow event creation
**Cause:** Git push retries taking too long
**Solution:** Reduce `max_retries` or implement async commits

## Future Enhancements

1. **Async Commits**: Move Git operations to background thread
2. **Batch Commits**: Commit multiple changes together
3. **Remote Push**: Configure GitHub credentials for Render
4. **Backup Strategy**: Periodic backups to external storage
5. **Conflict Resolution**: Handle concurrent modifications

## Security Considerations

1. **Git Credentials**: Never commit credentials to repository
2. **File Permissions**: Ensure storage file is not world-readable
3. **Logging**: Avoid logging sensitive event data
4. **Access Control**: Implement authentication for API endpoints

## Conclusion

This implementation provides robust event persistence for the Poker Tracker application on Render's free tier. By using Git as the persistence layer, events survive app sleep/wake cycles and are safely stored in the repository.
