# PostgreSQL Database Setup Guide

This guide explains how to configure and deploy the Poker Tracker application with PostgreSQL.

## 📋 Prerequisites

- PostgreSQL database instance (e.g., Render.com, Heroku, AWS RDS)
- Python 3.9 or higher
- Access to set environment variables in your deployment platform

## 🔧 Database Configuration

### Step 1: Create PostgreSQL Database

If using Render.com:
1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Click "New +" → "PostgreSQL"
3. Configure your database:
   - Name: `poker_settlements`
   - Region: Choose closest to your users
   - Plan: Free tier or higher
4. Click "Create Database"
5. Copy the "External Database URL" (starts with `postgresql://`)

### Step 2: Set Environment Variable

The application reads the database connection from the `DATABASE_URL` environment variable.

#### For Render.com:
1. Go to your web service dashboard
2. Navigate to "Environment" tab
3. Add environment variable:
   - **Key**: `DATABASE_URL`
   - **Value**: Your PostgreSQL connection string (from Step 1)

#### For Local Development:
```bash
export DATABASE_URL="postgresql://user:password@host:port/database"
```

#### Connection String Format:
```
postgresql://username:password@hostname:port/database_name
```

Example:
```
postgresql://poker_user:mypassword123@dpg-xxxxx.oregon-postgres.render.com/poker_settlements
```

### Step 3: Database Initialization

The application automatically creates all required tables on first startup:
- `events` - Stores poker event names and timestamps
- `players` - Stores player data for each event
- `settlement_payments` - Tracks which settlements have been paid

No manual SQL execution is required!

## 🚀 Deployment

### Deploy to Render.com

1. **Fork/Clone the Repository**
   ```bash
   git clone https://github.com/indra3007/Poker_setllements.git
   cd Poker_setllements
   ```

2. **Create Web Service on Render**
   - Go to [Render Dashboard](https://dashboard.render.com/)
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Configure:
     - **Name**: `poker-tracker`
     - **Runtime**: Python
     - **Build Command**: `pip install -r requirements.txt`
     - **Start Command**: `gunicorn --workers 2 --threads 4 --worker-class gthread --bind 0.0.0.0:$PORT app:app`

3. **Set Environment Variables**
   - Add `DATABASE_URL` (your PostgreSQL connection string)
   - `PORT` is automatically set by Render

4. **Deploy**
   - Click "Create Web Service"
   - Render will build and deploy your application
   - Wait for deployment to complete

5. **Verify**
   - Open your app URL (e.g., `https://poker-tracker.onrender.com`)
   - Create a test event to verify database connectivity

## 🔒 Security Best Practices

### ✅ What We've Implemented:
- **SSL/TLS Encryption**: All database connections use `sslmode=require`
- **Parameterized Queries**: All SQL queries use parameter binding (prevents SQL injection)
- **Environment Variables**: Sensitive credentials stored in environment variables
- **Error Handling**: Database errors are caught and handled gracefully
- **Connection Pooling**: Uses psycopg2 connection management

### 🚨 Important Notes:
1. **Never commit database credentials** to version control
2. **Always use environment variables** for sensitive configuration
3. **Use SSL/TLS** for database connections in production
4. **Regular backups** - Configure automated backups in your database provider
5. **Monitor logs** for connection errors or suspicious activity

## 🧪 Testing Database Connection

### Local Testing
```python
python3 test_database.py
```

This will:
- Connect to the database
- Create test event and players
- Verify CRUD operations
- Clean up test data

### Integration Testing
```python
python3 test_integration.py
```

Tests application logic without requiring database connectivity.

## 🔄 Migration from Old System

If you have existing data in JSON/Excel files:

1. The application maintains backward compatibility with Excel exports
2. Old `events.json` file is no longer used (data comes from PostgreSQL)
3. Excel files (`poker_tracker.xlsx`) are still generated for export purposes

### Manual Data Migration (if needed):
```python
# Load existing events from JSON
import json
with open('events.json', 'r') as f:
    old_events = json.load(f)

# Import into database
import db
db.init_database()
for event_name in old_events:
    db.create_event(event_name)
```

## 📊 Database Schema

### Events Table
```sql
CREATE TABLE events (
    id SERIAL PRIMARY KEY,
    event_name VARCHAR(255) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Players Table
```sql
CREATE TABLE players (
    id SERIAL PRIMARY KEY,
    event_name VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL,
    phone VARCHAR(50),
    start_chips DECIMAL(10, 2) DEFAULT 20.00,
    buyins INTEGER DEFAULT 0,
    day1 DECIMAL(10, 2),
    day2 DECIMAL(10, 2),
    day3 DECIMAL(10, 2),
    day4 DECIMAL(10, 2),
    day5 DECIMAL(10, 2),
    day6 DECIMAL(10, 2),
    day7 DECIMAL(10, 2),
    pl DECIMAL(10, 2) DEFAULT 0.00,
    days_played INTEGER DEFAULT 0,
    FOREIGN KEY (event_name) REFERENCES events(event_name) ON DELETE CASCADE,
    UNIQUE(event_name, name)
);
```

### Settlement Payments Table
```sql
CREATE TABLE settlement_payments (
    id SERIAL PRIMARY KEY,
    event_name VARCHAR(255) NOT NULL,
    from_player VARCHAR(255) NOT NULL,
    to_player VARCHAR(255) NOT NULL,
    paid BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (event_name) REFERENCES events(event_name) ON DELETE CASCADE,
    UNIQUE(event_name, from_player, to_player)
);
```

## 🐛 Troubleshooting

### "Unable to connect to the database"
- Verify DATABASE_URL is set correctly
- Check database server is running
- Verify network connectivity
- Ensure SSL is enabled if required by provider

### "relation does not exist"
- Tables are created automatically on first run
- Check application logs for database initialization errors
- Manually run: `python3 -c "import db; db.init_database()"`

### Connection timeouts
- Check database instance is not suspended (free tier limits)
- Verify firewall rules allow connections
- Consider upgrading database plan for better performance

## 📞 Support

For issues or questions:
- Check the [README.md](README.md) for general application information
- Review application logs for error messages
- Ensure all environment variables are set correctly

---

**Ready to deploy?** Follow the steps above and your Poker Tracker will be running with PostgreSQL! 🎰
