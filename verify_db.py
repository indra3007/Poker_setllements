#!/usr/bin/env python3
"""
Database Connection Verification Script
Run this to verify your PostgreSQL database setup
"""
import sys
import os
from datetime import datetime

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

def test_imports():
    """Test that all required modules can be imported"""
    print("1️⃣  Testing imports...")
    try:
        from database import engine, DATABASE_URL
        from models import Event, Player, SettlementPayment
        from app import app
        print("   ✅ All imports successful")
        return True
    except ImportError as e:
        print(f"   ❌ Import error: {e}")
        print("   💡 Run: pip install -r requirements.txt")
        return False

def test_environment_variables():
    """Test environment variables are set"""
    print("\n2️⃣  Testing environment variables...")
    required_vars = ['DB_HOST', 'DB_PORT', 'DB_NAME', 'DB_USER', 'DB_PASSWORD']
    missing = []
    
    for var in required_vars:
        value = os.getenv(var)
        if not value:
            missing.append(var)
        else:
            # Mask password
            display_value = value if var != 'DB_PASSWORD' else '*' * len(value)
            print(f"   {var}: {display_value}")
    
    if missing:
        print(f"   ❌ Missing variables: {', '.join(missing)}")
        print("   💡 Create .env file from .env.example")
        return False
    
    print("   ✅ All environment variables set")
    return True

def test_database_connection():
    """Test database connection"""
    print("\n3️⃣  Testing database connection...")
    try:
        from database import engine
        with engine.connect() as conn:
            print("   ✅ Database connection successful")
            return True
    except Exception as e:
        print(f"   ❌ Connection failed: {e}")
        print("   💡 Check database credentials and network connectivity")
        return False

def test_database_tables():
    """Test that required tables exist"""
    print("\n4️⃣  Testing database tables...")
    try:
        from database import engine
        from sqlalchemy import inspect
        
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        required_tables = ['events', 'players', 'settlement_payments']
        missing_tables = [t for t in required_tables if t not in tables]
        
        if missing_tables:
            print(f"   ❌ Missing tables: {', '.join(missing_tables)}")
            print("   💡 Run: python init_db.py")
            return False
        
        print(f"   ✅ All required tables exist: {', '.join(required_tables)}")
        
        # Show table details
        for table in required_tables:
            columns = inspector.get_columns(table)
            print(f"      - {table}: {len(columns)} columns")
        
        return True
    except Exception as e:
        print(f"   ❌ Error checking tables: {e}")
        return False

def test_database_operations():
    """Test basic database operations"""
    print("\n5️⃣  Testing database operations...")
    try:
        from database import get_db, close_db
        from models import Event
        
        db = get_db()
        
        # Count events
        event_count = db.query(Event).count()
        print(f"   ✅ Can query database (found {event_count} events)")
        
        close_db(db)
        return True
    except Exception as e:
        print(f"   ❌ Error testing operations: {e}")
        return False

def test_application_startup():
    """Test that Flask app can start"""
    print("\n6️⃣  Testing Flask application...")
    try:
        from app import app
        
        with app.test_client() as client:
            # Test main route
            response = client.get('/')
            if response.status_code == 200:
                print("   ✅ Main page loads successfully")
            else:
                print(f"   ⚠️  Main page returned status {response.status_code}")
            
            # Test API route
            response = client.get('/api/events')
            if response.status_code == 200:
                data = response.get_json()
                print(f"   ✅ API endpoint working (found {len(data.get('events', []))} events)")
            else:
                print(f"   ⚠️  API returned status {response.status_code}")
        
        return True
    except Exception as e:
        print(f"   ❌ Error testing app: {e}")
        return False

def main():
    """Run all verification tests"""
    print("\n" + "=" * 60)
    print("🎰 Poker Tracker - Database Verification")
    print("=" * 60)
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    results = []
    
    # Run tests
    results.append(('Imports', test_imports()))
    results.append(('Environment Variables', test_environment_variables()))
    results.append(('Database Connection', test_database_connection()))
    results.append(('Database Tables', test_database_tables()))
    results.append(('Database Operations', test_database_operations()))
    results.append(('Application Startup', test_application_startup()))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Summary")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {name}")
    
    print("\n" + "=" * 60)
    print(f"Result: {passed}/{total} tests passed")
    
    if passed == total:
        print("✅ All checks passed! Your database is ready.")
        print("\n🚀 You can now run: python app.py")
        return 0
    else:
        print("❌ Some checks failed. Please fix the issues above.")
        return 1

if __name__ == '__main__':
    sys.exit(main())
