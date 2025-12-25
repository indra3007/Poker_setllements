# 🎰 Poker Tracker Web App

A mobile-friendly web application for tracking poker game chip counts and calculating settlements.

## 🌐 Live Demo

**Deployed on Render**: `https://poker-tracker-xxxx.onrender.com` (update after deployment)

## ✨ Features

- 📊 **Table View**: Spreadsheet-like interface for easy data entry
- 💰 **Automatic P/L Calculation**: Real-time profit/loss tracking
- 🔄 **Smart Settlements**: Minimizes number of transactions needed
- 📱 **Mobile-Responsive**: Works perfectly on iPhone/Android
- 💾 **Data Persistence**: Excel-based storage
- ⚡ **Live Totals**: See totals update as you type
- 🎨 **Modern UI**: Clean, professional design
- 🔗 **GitHub Integration**: Automatically commits events to repository (optional)

## 🚀 Quick Start

### Option 1: Use the Deployed Version
Visit the live URL (update after Render deployment)

### Option 2: Run Locally

1. **Clone the repo**:
```bash
git clone git@github.com:indra3007/Poker_setllements.git
cd poker_web
```

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Run the app**:
```bash
python app.py
```

4. **Access it**:
   - On your Mac: http://localhost:5001
   - On your phone (same WiFi): http://YOUR_IP:5001

### Calculating Settlements
1. Tap "💰 Settlements" tab
2. Click "🔄 Calculate"
3. See who pays whom to settle up!

## How It Works

- **Starting Chips**: $20 per player per day
- **P/L Calculation**: (Final Chips) - (Starting Chips + Additional Buy-ins)
- **Settlement Algorithm**: Greedy matching - pairs biggest winners with biggest losers
- **Storage**: All data saved to `poker_tracker.xlsx`

## File Structure

```
poker_web/
├── app.py                 # Flask backend
├── templates/
│   └── index.html        # HTML template
├── static/
│   ├── style.css         # Mobile-responsive CSS
│   └── script.js         # Frontend JavaScript
├── requirements.txt      # Python dependencies
└── poker_tracker.xlsx    # Data storage (created automatically)
```

## API Endpoints

- `GET /api/health` - Health check with GitHub integration status
- `GET /api/events` - Get list of all events
- `POST /api/events` - Create new event (automatically commits to GitHub if configured)
- `DELETE /api/events/<event_name>` - Delete an event
- `GET /api/data/<event_name>` - Get all player data for an event
- `POST /api/save/<event_name>` - Save player data for an event
- `GET /api/settlements/<event_name>` - Calculate settlements for an event
- `POST /api/clear/<event_name>` - Clear all data for an event

## GitHub Integration (Optional)

The application can automatically commit event changes to GitHub. This ensures data persists across deployments and provides version control.

**Setup**: See [GITHUB_INTEGRATION.md](GITHUB_INTEGRATION.md) for detailed setup instructions.

**Quick Setup**:
1. Create a GitHub Personal Access Token with `repo` scope
2. Set environment variable: `export GITHUB_TOKEN='your_token_here'`
3. Restart the application

The app works perfectly without GitHub integration - it's completely optional!

## Tips

💡 **Add to Home Screen**: For best mobile experience, add to iPhone home screen  
💡 **Auto-Calculate**: P/L updates automatically as you enter chip values  
💡 **Offline Mode**: Data is saved on server, accessible by all players  
💡 **Share Link**: Everyone at the table can access the same tracker!  

## Deployment Options

### Local Network (Current Setup)
- Works on Wi-Fi only
- Perfect for home games
- No internet required

### Cloud Deployment
Deploy to Heroku, PythonAnywhere, or DigitalOcean for worldwide access!

## Troubleshooting

**Can't connect from phone?**
- Make sure both devices are on same Wi-Fi
- Check firewall settings
- Try using computer's IP address instead of localhost

**Data not saving?**
- Check console for errors (F12 in browser)
- Make sure `poker_tracker.xlsx` is not open in Excel
- Check file permissions

## Made With

- Flask (Python web framework)
- Vanilla JavaScript (no frameworks!)
- CSS3 (mobile-first responsive design)
- OpenPyXL (Excel file handling)

---

Enjoy your poker nights! 🎲🃏
