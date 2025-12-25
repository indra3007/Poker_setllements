"""
Database module for PostgreSQL operations
Handles all database connections and queries with proper error handling
"""

import psycopg2
from psycopg2.extras import RealDictCursor
import os
from contextlib import contextmanager

# Database connection string
DATABASE_URL = os.environ.get(
    'DATABASE_URL',
    'postgresql://poker_settlements_user:39d1mKqYkt252OAVwEfFFK1vDnPuIEWN@dpg-d56rrvre5dus73cvg310-a.oregon-postgres.render.com/poker_settlements'
)


@contextmanager
def get_db_connection():
    """Context manager for database connections with automatic cleanup"""
    conn = None
    try:
        # Add SSL mode for Render.com PostgreSQL databases
        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
        yield conn
        conn.commit()
    except psycopg2.OperationalError as e:
        if conn:
            conn.rollback()
        print(f"Database connection error: {e}")
        raise Exception("Unable to connect to the database. Please check your connection string and network connectivity.")
    except Exception as e:
        if conn:
            conn.rollback()
        raise e
    finally:
        if conn:
            conn.close()


def init_database():
    """Initialize database tables if they don't exist"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Events table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS events (
                id SERIAL PRIMARY KEY,
                event_name VARCHAR(255) UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Players table - stores player data for each event
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS players (
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
            )
        ''')
        
        # Settlement payments tracking table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS settlement_payments (
                id SERIAL PRIMARY KEY,
                event_name VARCHAR(255) NOT NULL,
                from_player VARCHAR(255) NOT NULL,
                to_player VARCHAR(255) NOT NULL,
                paid BOOLEAN DEFAULT FALSE,
                FOREIGN KEY (event_name) REFERENCES events(event_name) ON DELETE CASCADE,
                UNIQUE(event_name, from_player, to_player)
            )
        ''')
        
        cursor.close()
        print("✅ Database tables initialized successfully")


def get_all_events():
    """Get list of all event names"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT event_name FROM events ORDER BY created_at DESC')
        events = [row[0] for row in cursor.fetchall()]
        cursor.close()
        return events


def create_event(event_name):
    """Create a new event"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO events (event_name) VALUES (%s)',
            (event_name,)
        )
        cursor.close()


def delete_event(event_name):
    """Delete an event and all associated data"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM events WHERE event_name = %s', (event_name,))
        cursor.close()


def event_exists(event_name):
    """Check if event exists"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT 1 FROM events WHERE event_name = %s', (event_name,))
        exists = cursor.fetchone() is not None
        cursor.close()
        return exists


def get_event_players(event_name):
    """Get all players for a specific event"""
    with get_db_connection() as conn:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute('''
            SELECT name, phone, start_chips as start, buyins, 
                   day1, day2, day3, day4, day5, day6, day7, 
                   pl, days_played
            FROM players 
            WHERE event_name = %s
            ORDER BY id
        ''', (event_name,))
        players = cursor.fetchall()
        cursor.close()
        
        # Convert to regular dict and handle None values
        result = []
        for player in players:
            player_dict = dict(player)
            # Convert None to empty string for day fields
            for day in ['day1', 'day2', 'day3', 'day4', 'day5', 'day6', 'day7']:
                if player_dict[day] is None:
                    player_dict[day] = ''
                else:
                    player_dict[day] = float(player_dict[day])
            # Convert decimal to float
            player_dict['start'] = float(player_dict['start'])
            player_dict['pl'] = float(player_dict['pl'])
            player_dict['phone'] = player_dict['phone'] or ''
            result.append(player_dict)
        
        return result


def save_event_players(event_name, players):
    """Save/update all players for a specific event"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Delete existing players for this event
        cursor.execute('DELETE FROM players WHERE event_name = %s', (event_name,))
        
        # Insert new player data
        for player in players:
            # Handle empty string values for day fields
            day_values = []
            for day in ['day1', 'day2', 'day3', 'day4', 'day5', 'day6', 'day7']:
                val = player.get(f'{day}', '')
                day_values.append(float(val) if val and val != '' else None)
            
            cursor.execute('''
                INSERT INTO players 
                (event_name, name, phone, start_chips, buyins, 
                 day1, day2, day3, day4, day5, day6, day7, pl, days_played)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ''', (
                event_name,
                player.get('name', ''),
                player.get('phone', ''),
                player.get('start', 20),
                player.get('buyins', 0),
                *day_values,
                player.get('pl', 0),
                player.get('days_played', 0)
            ))
        
        cursor.close()


def get_settlement_payments(event_name):
    """Get settlement payment tracking for an event"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT from_player, to_player, paid 
            FROM settlement_payments 
            WHERE event_name = %s
        ''', (event_name,))
        
        payments = {}
        for row in cursor.fetchall():
            settlement_key = f"{row[0]}→{row[1]}"
            payments[settlement_key] = row[2]
        
        cursor.close()
        return payments


def mark_settlement_paid(event_name, from_player, to_player, paid):
    """Mark a settlement as paid or unpaid"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Use INSERT ... ON CONFLICT to handle updates
        cursor.execute('''
            INSERT INTO settlement_payments (event_name, from_player, to_player, paid)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (event_name, from_player, to_player) 
            DO UPDATE SET paid = EXCLUDED.paid
        ''', (event_name, from_player, to_player, paid))
        
        cursor.close()
