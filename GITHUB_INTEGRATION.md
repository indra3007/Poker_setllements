# GitHub Write-Back Feature

## Overview

This feature enables the Poker Tracker application to automatically commit changes to the `events.json` file back to the GitHub repository. This ensures that event data persists across deployments and can be version controlled.

## Features

✅ **Automatic Commits**: New events are automatically committed to GitHub  
✅ **Retry Logic**: Handles temporary failures with exponential backoff  
✅ **Error Handling**: Gracefully handles authentication and permission errors  
✅ **Optional**: Application works without GitHub integration (local-only mode)  
✅ **Secure**: Uses GitHub Personal Access Token (PAT) for authentication  

## Setup Instructions

### 1. Create a GitHub Personal Access Token

1. Go to GitHub Settings → Developer settings → Personal access tokens → [Tokens (classic)](https://github.com/settings/tokens)
2. Click "Generate new token (classic)"
3. Give it a descriptive name: `Poker Tracker Write Access`
4. Set expiration (recommended: 90 days or 1 year)
5. Select the following scopes:
   - ✅ `repo` (Full control of private repositories)
     - This includes: `repo:status`, `repo_deployment`, `public_repo`, `repo:invite`
6. Click "Generate token"
7. **Copy the token immediately** (you won't be able to see it again!)

### 2. Configure Environment Variables

#### For Local Development:

```bash
# Linux/Mac
export GITHUB_TOKEN='your_github_token_here'
export GITHUB_OWNER='indra3007'
export GITHUB_REPO='Poker_setllements'
export GITHUB_BRANCH='main'

# Windows (PowerShell)
$env:GITHUB_TOKEN='your_github_token_here'
$env:GITHUB_OWNER='indra3007'
$env:GITHUB_REPO='Poker_setllements'
$env:GITHUB_BRANCH='main'
```

#### For Render Deployment:

1. Go to your Render dashboard
2. Select your web service
3. Go to "Environment" tab
4. Add environment variable:
   - Key: `GITHUB_TOKEN`
   - Value: Your GitHub token
5. The other variables (`GITHUB_OWNER`, `GITHUB_REPO`, `GITHUB_BRANCH`) are already configured in `render.yaml`

### 3. Verify Setup

Run the health check endpoint to verify GitHub integration:

```bash
curl http://localhost:5001/api/health
```

Expected response when configured:
```json
{
  "status": "ok",
  "github": {
    "enabled": true,
    "configured": true,
    "authenticated": true,
    "owner": "indra3007",
    "repo": "Poker_setllements",
    "branch": "main"
  }
}
```

## Testing

### Run the GitHub Integration Tests

```bash
# Set your GitHub token
export GITHUB_TOKEN='your_token_here'

# Run tests
python3 test_github_integration.py
```

### Manual Testing

1. Start the application:
   ```bash
   python3 app.py
   ```

2. Create a new event:
   ```bash
   curl -X POST http://localhost:5001/api/events \
     -H "Content-Type: application/json" \
     -d '{"event_name": "Test Event 123"}'
   ```

3. Verify on GitHub:
   - Go to https://github.com/indra3007/Poker_setllements
   - Check the latest commit to `events.json`
   - Should see: "Update events via Poker Tracker app"

## How It Works

### Architecture

```
User Creates Event
       ↓
   Flask API
       ↓
Save to Local events.json
       ↓
GitHub Integration Module
       ↓
Commit to GitHub (with retry)
       ↓
Success or Log Error
```

### Key Components

1. **`github_integration.py`**: Core GitHub API integration
   - Authentication with GitHub
   - File content encoding/decoding
   - Commit creation with SHA handling
   - Retry logic for temporary failures

2. **`app.py`**: Flask application integration
   - Initializes GitHub integration on startup
   - Calls GitHub commit after local save
   - Logs success/failure

3. **Environment Variables**:
   - `GITHUB_TOKEN`: Personal Access Token (required)
   - `GITHUB_OWNER`: Repository owner (default: indra3007)
   - `GITHUB_REPO`: Repository name (default: Poker_setllements)
   - `GITHUB_BRANCH`: Target branch (default: main)

## Error Handling

### Authentication Errors

**Error**: `Invalid GitHub token`  
**Solution**: Verify your token is correct and hasn't expired

**Error**: `GitHub token lacks required permissions`  
**Solution**: Regenerate token with `repo` scope

### Network Errors

**Error**: `GitHub API timeout`  
**Solution**: Application will retry automatically (3 attempts with exponential backoff)

**Error**: `Network error: ...`  
**Solution**: Check internet connection; application will retry

### Repository Errors

**Error**: `Repository not found`  
**Solution**: Verify `GITHUB_OWNER` and `GITHUB_REPO` are correct

**Error**: `File was modified by another process`  
**Solution**: Application will retry with updated SHA automatically

## Graceful Degradation

The application works in three modes:

1. **Full Mode** (with GitHub integration):
   - Events saved locally
   - Events committed to GitHub
   - Best for production

2. **Local-Only Mode** (no token configured):
   - Events saved locally only
   - No GitHub commits
   - Good for development/testing

3. **Fallback Mode** (GitHub errors):
   - Events always saved locally
   - GitHub errors are logged but don't block operations
   - Application continues working

## Security Best Practices

1. **Never commit tokens**: The `.gitignore` excludes `.env` files
2. **Use environment variables**: Never hardcode tokens in source code
3. **Rotate tokens regularly**: Generate new tokens every 90 days
4. **Use minimal permissions**: Only grant `repo` scope
5. **Monitor access**: Check GitHub settings → Personal access tokens → Active tokens

## Troubleshooting

### "GitHub integration disabled: GITHUB_TOKEN not configured"

This is a warning, not an error. The app will work in local-only mode.

To enable GitHub integration:
```bash
export GITHUB_TOKEN='your_token_here'
```

### "Failed to commit events to GitHub"

Check the logs for specific error message. Common causes:
- Invalid token
- Expired token
- Network connectivity
- Repository permissions

The application will continue working; events are still saved locally.

### Testing Authentication

```python
from github_integration import GitHubIntegration

github = GitHubIntegration()
success, error = github.test_authentication()
print(f"Success: {success}")
if not success:
    print(f"Error: {error}")
```

## API Reference

### Health Check Endpoint

**GET** `/api/health`

Returns application health and GitHub integration status.

**Response**:
```json
{
  "status": "ok",
  "github": {
    "enabled": true,
    "configured": true,
    "authenticated": true,
    "owner": "indra3007",
    "repo": "Poker_setllements",
    "branch": "main"
  }
}
```

## Future Enhancements

Possible improvements for future versions:

- [ ] Support for multiple branches
- [ ] Conflict resolution UI
- [ ] Commit history viewer
- [ ] Rollback functionality
- [ ] Webhook integration for real-time sync
- [ ] Support for GitHub Apps (vs Personal Access Tokens)

## Support

For issues or questions:
1. Check the logs: Look for messages from `github_integration` module
2. Run the test suite: `python3 test_github_integration.py`
3. Verify health endpoint: `curl http://localhost:5001/api/health`
4. Check GitHub token permissions
