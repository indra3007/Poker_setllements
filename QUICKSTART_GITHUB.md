# Quick Start: GitHub Integration

## What is this?
The Poker Tracker app can now automatically save event changes to GitHub! This means your event list is backed up and version controlled.

## Do I need it?
**No!** The app works perfectly without GitHub integration. This is an optional feature.

## How to enable it?

### Step 1: Get a GitHub Token
1. Go to: https://github.com/settings/tokens
2. Click "Generate new token (classic)"
3. Give it a name: "Poker Tracker"
4. Check the box: ✅ `repo`
5. Click "Generate token"
6. **Copy the token immediately!**

### Step 2: Set the Token

#### On Mac/Linux:
```bash
export GITHUB_TOKEN='paste_your_token_here'
```

#### On Windows:
```powershell
$env:GITHUB_TOKEN='paste_your_token_here'
```

#### On Render:
1. Go to your Render dashboard
2. Click on your service
3. Go to "Environment" tab
4. Add: `GITHUB_TOKEN` = `your_token_here`

### Step 3: Start the App
```bash
python3 app.py
```

## How to verify it's working?

### Check 1: Health Endpoint
```bash
curl http://localhost:5001/api/health
```

Look for:
```json
{
  "github": {
    "enabled": true,
    "authenticated": true
  }
}
```

### Check 2: Create an Event
1. Create an event in the app
2. Go to: https://github.com/indra3007/Poker_setllements
3. Look at the latest commit to `events.json`
4. You should see: "Update events via Poker Tracker app"

## Troubleshooting

### "GitHub integration disabled"
- This is just a warning, not an error
- The app works fine without GitHub integration
- To enable it, set the `GITHUB_TOKEN` environment variable

### "Invalid GitHub token"
- Your token might be expired
- Create a new token and update the environment variable

### "GitHub token lacks required permissions"
- Your token needs the `repo` scope
- Create a new token with the correct permissions

### Still not working?
- See the full guide: [GITHUB_INTEGRATION.md](GITHUB_INTEGRATION.md)
- Run the test: `python3 test_github_integration.py`
- Check the logs for specific error messages

## What happens without GitHub integration?
Everything works normally! Events are saved locally to `events.json`. The only difference is they're not automatically backed up to GitHub.

## Benefits of GitHub Integration
- ✅ Automatic backups of your event list
- ✅ Version history (see all changes over time)
- ✅ Easy to restore from GitHub if needed
- ✅ Multi-user safe (handles conflicts automatically)

## Security Notes
- Never share your GitHub token
- Never commit your token to source code
- Rotate your token every 90 days
- Only grant the `repo` permission

---

**Need more help?** See [GITHUB_INTEGRATION.md](GITHUB_INTEGRATION.md) for the complete guide.
