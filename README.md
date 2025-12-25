# 🎰 Poker Tracker Web App

A mobile-friendly web application for tracking poker game chip counts and calculating settlements.

## 🌐 Live Demo

**Deployed on Render**: `https://poker-tracker-xxxx.onrender.com` (update after deployment)

## ✨ Features

- 📊 **Table View**: Spreadsheet-like interface for easy data entry
- 💰 **Automatic P/L Calculation**: Real-time profit/loss tracking
- 🔄 **Smart Settlements**: Minimizes number of transactions needed
- 📱 **Mobile-Responsive**: Works perfectly on iPhone/Android
- 💾 **Data Persistence**: PostgreSQL database storage with automatic Excel export
- ⚡ **Live Totals**: See totals update as you type
- 🎨 **Modern UI**: Clean, professional design

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
- **Storage**: All data saved to PostgreSQL database (with optional Excel export for backup)

## File Structure

```
poker_web/
├── app.py                 # Flask backend
├── db.py                  # PostgreSQL database module
├── templates/
│   └── index.html        # HTML template
├── static/
│   ├── style.css         # Mobile-responsive CSS
│   └── script.js         # Frontend JavaScript
├── requirements.txt      # Python dependencies
└── poker_tracker.xlsx    # Optional Excel export (created automatically)
```

## API Endpoints

- `GET /api/data` - Get all player data
- `POST /api/save` - Save player data
- `GET /api/settlements` - Calculate settlements
- `POST /api/clear` - Clear all data

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
- Verify database connection is working
- Check that the DATABASE_URL environment variable is set correctly

## Database Configuration

The application uses PostgreSQL for data persistence. The database connection can be configured using:

1. **Environment Variable** (recommended for production):
   ```bash
   export DATABASE_URL="postgresql://user:password@host/database"
   ```

2. **Default Connection String** (fallback):
   The application includes a default connection string in `db.py` that can be updated for your environment.

### Database Tables

The application automatically creates the following tables on startup:

- **events**: Stores event names and creation timestamps
- **players**: Stores player data for each event (chips, buy-ins, P/L)
- **settlement_payments**: Tracks which settlements have been paid

### Security Features

- ✅ All SQL queries use parameterized queries (prevents SQL injection)
- ✅ SSL/TLS encryption required for database connections
- ✅ Graceful error handling for connection failures

## Made With

- Flask (Python web framework)
- PostgreSQL (Database)
- psycopg2 (PostgreSQL adapter)
- Vanilla JavaScript (no frameworks!)
- CSS3 (mobile-first responsive design)
- OpenPyXL (Excel file handling)

---

Enjoy your poker nights! 🎲🃏
