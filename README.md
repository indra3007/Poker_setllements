# 🎰 Poker Tracker Web App - PostgreSQL Edition

A mobile-friendly web application for tracking poker game chip counts and calculating settlements, now powered by PostgreSQL database.

## 🌐 Live Demo

**Deployed on Render**: `https://poker-tracker-xxxx.onrender.com` (update after deployment)

## ✨ Features

- 📊 **Table View**: Spreadsheet-like interface for easy data entry
- 💰 **Automatic P/L Calculation**: Real-time profit/loss tracking
- 🔄 **Smart Settlements**: Minimizes number of transactions needed
- 📱 **Mobile-Responsive**: Works perfectly on iPhone/Android
- 💾 **Database Persistence**: PostgreSQL-based storage with SQLAlchemy ORM
- ⚡ **Live Totals**: See totals update as you type
- 🎨 **Modern UI**: Clean, professional design
- 🔐 **Secure**: Environment-based configuration for credentials

## 🚀 Quick Start

### Option 1: Use the Deployed Version
Visit the live URL (update after Render deployment)

### Option 2: Run Locally

1. **Clone the repo**:
```bash
git clone git@github.com:indra3007/Poker_setllements.git
cd Poker_setllements
```

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Configure environment variables**:
```bash
# Copy the example environment file
cp .env.example .env

# Edit .env file with your database credentials
# For local development, you can use a local PostgreSQL instance
nano .env
```

4. **Initialize the database**:
```bash
python init_db.py
```

5. **Run the app**:
```bash
python app.py
```

6. **Access it**:
   - On your computer: http://localhost:5001
   - On your phone (same WiFi): http://YOUR_IP:5001

## 📋 Environment Variables

Create a `.env` file in the root directory with the following variables:

```bash
# Database Configuration
DB_HOST=your-database-host
DB_PORT=5432
DB_NAME=poker_settlements
DB_USER=your-database-user
DB_PASSWORD=your-database-password

# Flask Configuration
SECRET_KEY=your-secret-key-here
FLASK_ENV=development  # or production

# Optional: Override port (default: 5001)
PORT=5001
```

**Note**: Never commit your `.env` file to version control. Use `.env.example` as a template.

## 🗄️ Database Setup

### PostgreSQL Database

This application uses PostgreSQL as the database backend. You need to have access to a PostgreSQL instance with the following tables:

- **events**: Stores poker event/session information
- **players**: Stores player data for each event (chip counts, buy-ins, P/L)
- **settlement_payments**: Tracks payment status for settlements

### Initialize Database Tables

Run the initialization script to create all necessary tables:

```bash
python init_db.py
```

This will:
- Connect to your PostgreSQL database
- Create all required tables
- Verify the schema

## How It Works

- **Starting Chips**: $20 per player per day
- **P/L Calculation**: (Final Chips) - (Starting Chips + Additional Buy-ins)
- **Settlement Algorithm**: Greedy matching - pairs biggest winners with biggest losers
- **Storage**: All data saved to PostgreSQL database

## File Structure

```
Poker_setllements/
├── app.py                 # Flask backend with database integration
├── database.py            # Database connection and configuration
├── models.py              # SQLAlchemy ORM models
├── init_db.py            # Database initialization script
├── templates/
│   ├── index_v2.html     # Main HTML template
│   └── test.html         # Test page
├── static/
│   ├── style.css         # Mobile-responsive CSS
│   └── script_v2.js      # Frontend JavaScript
├── requirements.txt       # Python dependencies
├── .env.example          # Environment variables template
└── .gitignore            # Git ignore rules
```

## 🔧 API Endpoints

### Events Management
- `GET /api/events` - Get all events
- `POST /api/events` - Create new event
- `DELETE /api/events/<event_name>` - Delete an event

### Player Data
- `GET /api/data/<event_name>` - Get player data for event
- `POST /api/save/<event_name>` - Save player data for event
- `POST /api/clear/<event_name>` - Clear all player data for event

### Settlements
- `GET /api/settlements/<event_name>` - Calculate settlements for event
- `POST /api/settlements/<event_name>/mark_paid` - Mark a settlement as paid/unpaid

## 🧪 Testing

Run the test suite to verify the application:

```bash
# Run integration tests
python test_db_integration.py
```

The test suite includes:
- Import and module tests
- Database model structure tests
- P/L calculation tests
- Settlement algorithm tests
- Route registration tests
- Environment configuration tests

## Tips

💡 **Add to Home Screen**: For best mobile experience, add to iPhone home screen  
💡 **Auto-Calculate**: P/L updates automatically as you enter chip values  
💡 **Cloud Storage**: Data is saved in PostgreSQL, accessible by all players  
💡 **Share Link**: Everyone at the table can access the same tracker!  
💡 **Secure**: Database credentials stored in environment variables

## 🚀 Deployment

### Deploy to Render

1. **Create a PostgreSQL database** on Render or another provider
2. **Set environment variables** in your Render dashboard:
   - `DB_HOST`
   - `DB_PORT`
   - `DB_NAME`
   - `DB_USER`
   - `DB_PASSWORD`
   - `SECRET_KEY`
   - `FLASK_ENV=production`
3. **Deploy the application** - it will automatically run `init_db.py` on first deployment

### Other Deployment Options

The application can be deployed to:
- Heroku (with Heroku Postgres)
- DigitalOcean App Platform
- AWS Elastic Beanstalk (with RDS)
- Google Cloud Run (with Cloud SQL)

## Troubleshooting

**Database connection errors?**
- Verify database credentials in `.env` file
- Check that PostgreSQL server is running and accessible
- Verify firewall rules allow connections
- Check database connection URL format

**Can't connect from phone?**
- Make sure both devices are on same Wi-Fi (local mode)
- Check firewall settings
- Try using computer's IP address instead of localhost

**Data not saving?**
- Check console for errors (F12 in browser)
- Verify database connection is working
- Check database permissions

**Import errors?**
- Make sure all dependencies are installed: `pip install -r requirements.txt`
- Verify Python version (3.8 or higher recommended)

## 🔄 Migration from File-Based Storage

If you're migrating from the old Excel/JSON-based version:

1. **Backup your data**: Save copies of `events.json`, `poker_tracker.xlsx`, and `settlements_tracking.json`
2. **Set up the database**: Follow the database setup instructions above
3. **Manual data migration**: You may need to manually re-enter existing events and player data
4. **Old files**: The old files will no longer be used once the database is active

## Made With

- Flask (Python web framework)
- SQLAlchemy (ORM for database operations)
- PostgreSQL (Database)
- psycopg2 (PostgreSQL adapter)
- Vanilla JavaScript (no frameworks!)
- CSS3 (mobile-first responsive design)

## 🔐 Security Notes

- Database credentials should never be committed to version control
- Use strong passwords for database users
- In production, use HTTPS for all connections
- Regularly backup your database
- Keep dependencies up to date

---

Enjoy your poker nights! 🎲🃏
