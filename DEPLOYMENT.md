# 🚀 Poker Tracker Deployment Guide

## Deploy to Render (Free Hosting)

### Step 1: Push to GitHub

```bash
cd /Users/indraneel/Desktop/Python/phonebill/poker_web

# Initialize git (if not already done)
git init

# Add your remote
git remote add origin git@github.com:indra3007/Poker_setllements.git

# Add all files
git add .

# Commit
git commit -m "Initial commit - Poker Tracker Web App"

# Push to GitHub
git push -u origin main
```

If you get an error about `main` vs `master`, try:
```bash
git branch -M main
git push -u origin main
```

### Step 2: Deploy on Render

1. **Go to Render**: https://render.com
2. **Sign in** with your GitHub account
3. **Click "New +"** → Select **"Web Service"**
4. **Connect your repository**: `indra3007/Poker_setllements`
5. **Configure settings**:
   - **Name**: `poker-tracker` (or any name you like)
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python app.py`
   - **Plan**: Free
6. **Click "Create Web Service"**

### Step 3: Wait for Deployment (2-3 minutes)

Render will:
- Clone your repo
- Install dependencies
- Start your app
- Give you a URL like: `https://poker-tracker-xxxx.onrender.com`

### Step 4: Share with Friends! 🎉

Send them the Render URL. They can:
- Add it to iPhone home screen (looks like native app)
- Access from any device with a browser
- All data is shared automatically

## Important Notes

⚠️ **Free Tier Limitations**:
- App sleeps after 15 minutes of inactivity
- Takes 30 seconds to wake up on first visit
- 750 hours/month free (enough for casual use)

✅ **Data Persistence**:
- All data is saved in `poker_tracker.xlsx`
- Data persists even when app sleeps
- Everyone shares the same data

## Updating Your App

When you make changes:

```bash
git add .
git commit -m "Your update message"
git push
```

Render will automatically redeploy (takes 2-3 minutes).

## Troubleshooting

**App not starting?**
- Check Render logs in the dashboard
- Make sure all files are committed to GitHub

**Port errors?**
- The app automatically uses Render's PORT environment variable

**Can't push to GitHub?**
- Make sure you have SSH keys set up: https://docs.github.com/en/authentication
- Or use HTTPS: `git remote set-url origin https://github.com/indra3007/Poker_setllements.git`

## Alternative: Local Network Only

If you want to keep it local (not public):
1. Keep running on your Mac
2. Share your Mac's IP address
3. Friends on same WiFi can access it

Your current setup: http://192.168.68.93:5001
