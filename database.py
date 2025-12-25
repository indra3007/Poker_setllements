#!/usr/bin/env python3
"""
Database module for PostgreSQL integration
Handles all database operations for the Poker Tracker app
"""

import psycopg2
from psycopg2.extras import RealDictCursor
import os
import json
from contextlib import contextmanager

DATABASE_URL = os.environ.get('DATABASE_URL')

@contextmanager
def get_db_connection():
    """Context manager for database connections"""
    if not DATABASE_URL:
        raise ValueError("DATABASE_URL environment variable is not set")
    
    conn = None
    try:
        conn = psycopg2.connect(DATABASE_URL)
        yield conn
        conn.commit()
    except Exception as e:
        if conn:
            conn.rollback()
        print(f"Database error: {e}")
        raise
    finally:
        if conn:
            conn.close()

def init_database():
    """Initialize database schema"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Create events table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS events (
                    id SERIAL PRIMARY KEY,
                    event_name VARCHAR(255) UNIQUE NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create players table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS players (
                    id SERIAL PRIMARY KEY,
                    event_name VARCHAR(255) NOT NULL,
                    name VARCHAR(255) NOT NULL,
                    phone VARCHAR(50),
                    start_chips FLOAT DEFAULT 20,
                    buyins INTEGER DEFAULT 0,
                    day1 FLOAT,
                    day2 FLOAT,
                    day3 FLOAT,
                    day4 FLOAT,
                    day5 FLOAT,
                    day6 FLOAT,
                    day7 FLOAT,
                    pl FLOAT DEFAULT 0,
                    days_played INTEGER DEFAULT 0,
                    FOREIGN KEY (event_name) REFERENCES events(event_name) ON DELETE CASCADE,
                    UNIQUE(event_name, name)
                )
            """)
            
            # Create settlements table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS settlement_payments (
                    id SERIAL PRIMARY KEY,
                    event_name VARCHAR(255) NOT NULL,
                    from_player VARCHAR(255) NOT NULL,
                    to_player VARCHAR(255) NOT NULL,
                    paid BOOLEAN DEFAULT FALSE,
                    FOREIGN KEY (event_name) REFERENCES events(event_name) ON DELETE CASCADE,
                    UNIQUE(event_name, from_player, to_player)
                )
            """)
            
            print("✅ Database schema initialized successfully")
            return True
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        import traceback
        traceback.print_exc()
        return False

def db_load_events():
    """Load all events from database"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT event_name FROM events ORDER BY created_at")
        rows = cursor.fetchall()
        return [row[0] for row in rows]

def db_save_event(event_name):
    """Save a new event to database"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO events (event_name) VALUES (%s) ON CONFLICT DO NOTHING",
            (event_name,)
        )
        return True

def db_delete_event(event_name):
    """Delete an event from database (cascade deletes players and settlements)"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM events WHERE event_name = %s", (event_name,))
        return True

def db_load_players(event_name):
    """Load all players for a specific event"""
    with get_db_connection() as conn:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        cursor.execute("""
            SELECT id as row, name, phone, start_chips as start, buyins,
                   day1, day2, day3, day4, day5, day6, day7, pl, days_played
            FROM players
            WHERE event_name = %s
            ORDER BY id
        """, (event_name,))
        rows = cursor.fetchall()
        # Convert to list of dicts and handle None values
        players = []
        for row in rows:
            player = dict(row)
            # Convert None to empty string for day fields
            for day in range(1, 8):
                day_key = f'day{day}'
                if player.get(day_key) is None:
                    player[day_key] = ''
            players.append(player)
        return players

def db_save_players(event_name, players):
    """Save all players for a specific event"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Delete existing players for this event
        cursor.execute("DELETE FROM players WHERE event_name = %s", (event_name,))
        
        # Insert new player data
        for player in players:
            cursor.execute("""
                INSERT INTO players (
                    event_name, name, phone, start_chips, buyins,
                    day1, day2, day3, day4, day5, day6, day7, pl, days_played
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                event_name,
                player.get('name', ''),
                player.get('phone', ''),
                player.get('start', 20),
                player.get('buyins', 0),
                player.get('day1') or None,
                player.get('day2') or None,
                player.get('day3') or None,
                player.get('day4') or None,
                player.get('day5') or None,
                player.get('day6') or None,
                player.get('day7') or None,
                player.get('pl', 0),
                player.get('days_played', 0)
            ))
        
        return True

def db_clear_players(event_name):
    """Clear all player data for a specific event"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM players WHERE event_name = %s", (event_name,))
        return True

def db_load_settlement_payments(event_name=None):
    """Load settlement payment tracking"""
    with get_db_connection() as conn:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        if event_name:
            cursor.execute("""
                SELECT from_player, to_player, paid
                FROM settlement_payments
                WHERE event_name = %s
            """, (event_name,))
        else:
            cursor.execute("""
                SELECT event_name, from_player, to_player, paid
                FROM settlement_payments
            """)
        
        rows = cursor.fetchall()
        
        if event_name:
            # Return dict of settlement_key -> paid status
            result = {}
            for row in rows:
                settlement_key = f"{row['from_player']}→{row['to_player']}"
                result[settlement_key] = row['paid']
            return result
        else:
            # Return nested dict: event_name -> settlement_key -> paid status
            result = {}
            for row in rows:
                event = row['event_name']
                if event not in result:
                    result[event] = {}
                settlement_key = f"{row['from_player']}→{row['to_player']}"
                result[event][settlement_key] = row['paid']
            return result

def db_save_settlement_payment(event_name, from_player, to_player, paid):
    """Save settlement payment status"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO settlement_payments (event_name, from_player, to_player, paid)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (event_name, from_player, to_player)
            DO UPDATE SET paid = EXCLUDED.paid
        """, (event_name, from_player, to_player, paid))
        return True
