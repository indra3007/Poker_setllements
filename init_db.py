#!/usr/bin/env python3
"""
Database initialization script
Creates all necessary tables for the Poker Tracker application
"""
import sys
import os
from sqlalchemy import inspect

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import engine, Base, DATABASE_URL
from models import Event, Player, SettlementPayment

def init_db():
    """Initialize database - create all tables"""
    print("🎰 Poker Tracker - Database Initialization")
    print("=" * 50)
    print(f"📊 Database URL: {DATABASE_URL.split('@')[1] if '@' in DATABASE_URL else 'N/A'}")
    print()
    
    try:
        # Test connection
        print("🔌 Testing database connection...")
        with engine.connect() as conn:
            print("✅ Database connection successful!")
        
        # Check existing tables
        inspector = inspect(engine)
        existing_tables = inspector.get_table_names()
        print(f"\n📋 Existing tables: {existing_tables if existing_tables else 'None'}")
        
        # Create all tables
        print("\n🏗️  Creating tables...")
        Base.metadata.create_all(bind=engine)
        
        # Verify tables were created
        inspector = inspect(engine)
        new_tables = inspector.get_table_names()
        print(f"✅ Tables created: {new_tables}")
        
        print("\n" + "=" * 50)
        print("✅ Database initialization complete!")
        print("=" * 50)
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error initializing database: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = init_db()
    sys.exit(0 if success else 1)
