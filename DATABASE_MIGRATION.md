# Database Migration Guide

This guide explains the migration from file-based storage (Excel + JSON) to PostgreSQL database.

## Overview

The Poker Tracker application has been migrated from:
- **Old**: Excel files (`poker_tracker.xlsx`) and JSON files (`events.json`, `settlements_tracking.json`)
- **New**: PostgreSQL database with SQLAlchemy ORM

## Database Schema

### Tables

#### 1. events
Stores poker event/session information.

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| name | VARCHAR(255) | Unique event name |
| created_at | TIMESTAMP | When event was created |

#### 2. players
Stores player data for each event.

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| event_id | INTEGER | Foreign key to events.id |
| name | VARCHAR(255) | Player name |
| phone | VARCHAR(50) | Player phone (optional) |
| start | FLOAT | Starting chip amount |
| buyins | INTEGER | Number of buy-ins |
| day1-day7 | FLOAT | Chip values for each day (nullable) |
| pl | FLOAT | Calculated profit/loss |
| days_played | INTEGER | Number of days played |
| row_order | INTEGER | Display order |

#### 3. settlement_payments
Tracks payment status for settlements.

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| event_id | INTEGER | Foreign key to events.id |
| from_player | VARCHAR(255) | Player making payment |
| to_player | VARCHAR(255) | Player receiving payment |
| amount | FLOAT | Payment amount |
| paid | BOOLEAN | Whether payment is complete |
| created_at | TIMESTAMP | When record was created |
| updated_at | TIMESTAMP | Last update time |

## Setting Up the Database

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

This will install:
- SQLAlchemy (ORM)
- psycopg2-binary (PostgreSQL adapter)
- python-dotenv (environment variables)

### 2. Configure Environment Variables

Create a `.env` file in the project root:

```bash
# Copy the example file
cp .env.example .env

# Edit with your database credentials
nano .env
```

Required variables:
```
DB_HOST=your-postgres-host
DB_PORT=5432
DB_NAME=poker_settlements
DB_USER=your-username
DB_PASSWORD=your-password
SECRET_KEY=your-secret-key
```

### 3. Initialize Database

Run the initialization script:

```bash
python init_db.py
```

This will:
- Test the database connection
- Create all required tables
- Verify the schema

## Code Changes

### Application Structure

New files added:
- `database.py` - Database connection and session management
- `models.py` - SQLAlchemy ORM models
- `init_db.py` - Database initialization script

Modified files:
- `app.py` - Refactored to use database instead of files
- `requirements.txt` - Added database dependencies
- `.gitignore` - Excludes `.env` and data files

### API Changes

All API endpoints remain the same, but implementation changed:

**Before** (File-based):
```python
def load_events():
    with open(EVENTS_FILE, 'r') as f:
        return json.load(f)
```

**After** (Database):
```python
def get_events():
    db = get_db()
    events = db.query(Event).all()
    return [event.name for event in events]
```

### Data Flow

**Old Flow:**
1. Request → Flask Route
2. Read/Write Excel/JSON files
3. Response

**New Flow:**
1. Request → Flask Route
2. Database Session → SQL Query
3. ORM Models → Python Objects
4. Response

## Migrating Existing Data

If you have existing data in Excel/JSON files:

### Option 1: Manual Re-entry
1. Deploy the new version
2. Create events through the UI
3. Re-enter player data

### Option 2: Write a Migration Script

```python
#!/usr/bin/env python3
"""
Data migration script - Excel/JSON to PostgreSQL
"""
import json
import openpyxl
from database import get_db
from models import Event, Player, SettlementPayment

def migrate_data():
    db = get_db()
    
    # Migrate events
    with open('events.json', 'r') as f:
        event_names = json.load(f)
    
    for event_name in event_names:
        event = Event(name=event_name)
        db.add(event)
    db.commit()
    
    # Migrate player data from Excel
    wb = openpyxl.load_workbook('poker_tracker.xlsx')
    for event_name in event_names:
        if event_name not in wb.sheetnames:
            continue
            
        event = db.query(Event).filter(Event.name == event_name).first()
        ws = wb[event_name]
        
        for row_idx in range(2, ws.max_row + 1):
            row = ws[row_idx]
            if not row[0].value:
                continue
                
            player = Player(
                event_id=event.id,
                name=row[0].value,
                phone=row[1].value,
                start=row[2].value or 20,
                buyins=row[3].value or 0,
                day1=row[4].value,
                day2=row[5].value,
                day3=row[6].value,
                day4=row[7].value,
                day5=row[8].value,
                day6=row[9].value,
                day7=row[10].value,
                pl=row[11].value or 0,
                days_played=row[12].value or 0,
                row_order=row_idx - 2
            )
            db.add(player)
    
    db.commit()
    print("✅ Migration complete!")

if __name__ == '__main__':
    migrate_data()
```

## Deployment Considerations

### Environment Variables on Render

In your Render dashboard, set these environment variables:
- `DB_HOST` - Your PostgreSQL host
- `DB_PORT` - Usually 5432
- `DB_NAME` - Database name
- `DB_USER` - Database username
- `DB_PASSWORD` - Database password
- `SECRET_KEY` - Flask secret key
- `FLASK_ENV` - Set to `production`

### Database Backups

Set up regular backups:
```bash
# Manual backup
pg_dump -h $DB_HOST -U $DB_USER -d $DB_NAME > backup.sql

# Restore from backup
psql -h $DB_HOST -U $DB_USER -d $DB_NAME < backup.sql
```

### Connection Pooling

The application uses SQLAlchemy's connection pooling:
- Pool size: 10 connections
- Max overflow: 20 connections
- Pre-ping: Enabled (verifies connections before use)

## Testing

Run tests to verify the migration:

```bash
python test_db_integration.py
```

Tests include:
- Database model structure
- ORM relationships
- P/L calculation logic
- Settlement algorithm
- API route registration

## Rollback Plan

If you need to rollback to the file-based version:

1. Restore `app_old.py` to `app.py`:
   ```bash
   cp app_old.py app.py
   ```

2. Restore old `requirements.txt`:
   ```bash
   git checkout HEAD~1 requirements.txt
   ```

3. Reinstall dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Performance Considerations

### Database Indexes

The following columns are indexed for better performance:
- `events.name` - For fast event lookup
- `players.event_id` - For fast player queries by event
- `settlement_payments.event_id` - For fast settlement queries

### Query Optimization

- Uses `order_by` for sorted results
- Uses `filter` instead of loading all records
- Implements cascade deletes for related records
- Uses connection pooling to reduce overhead

## Security Improvements

1. **Environment Variables**: Database credentials no longer in code
2. **Connection Pooling**: Better resource management
3. **ORM Protection**: SQLAlchemy helps prevent SQL injection
4. **Prepared Statements**: All queries use parameterized queries

## Troubleshooting

### "Could not translate host name"
- Check `DB_HOST` in `.env` file
- Verify network connectivity to database
- Try using IP address instead of hostname

### "Database does not exist"
- Create the database: `createdb poker_settlements`
- Or ask your DBA to create it
- Verify `DB_NAME` matches actual database name

### "Permission denied"
- Check database user has required permissions
- Grant permissions: `GRANT ALL ON DATABASE poker_settlements TO user;`

### Import errors
- Ensure all dependencies installed: `pip install -r requirements.txt`
- Check Python version (3.8+ required)

## Support

For questions or issues:
1. Check the troubleshooting section in README.md
2. Review application logs for error details
3. Verify database connectivity with `python init_db.py`

---

*Last updated: December 2025*
