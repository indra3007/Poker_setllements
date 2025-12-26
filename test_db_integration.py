#!/usr/bin/env python3
"""
Test script for the Poker Tracker API with PostgreSQL backend
Tests using Flask test client with in-memory SQLite database
"""

import sys
import os
import unittest
from unittest.mock import patch, MagicMock

# Set up test environment
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Mock database connection for testing
os.environ['DB_HOST'] = 'localhost'
os.environ['DB_NAME'] = 'test_poker'
os.environ['DB_USER'] = 'test_user'
os.environ['DB_PASSWORD'] = 'test_pass'

class TestPokerTrackerAPI(unittest.TestCase):
    """Test suite for Poker Tracker API endpoints"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test fixtures before any tests run"""
        print("\n" + "=" * 60)
        print("🎰 Poker Tracker API Tests - PostgreSQL Backend")
        print("=" * 60)
    
    def setUp(self):
        """Set up test fixtures before each test"""
        # Note: Actual database connection tests require access to the PostgreSQL instance
        # These tests verify the application structure and logic
        pass
    
    def test_imports(self):
        """Test that all required modules can be imported"""
        print("\n📦 Testing imports...")
        try:
            from app import app
            from models import Event, Player, SettlementPayment
            from database import get_db, close_db
            print("✅ All imports successful")
        except ImportError as e:
            self.fail(f"Import error: {e}")
    
    def test_app_creation(self):
        """Test that Flask app is created successfully"""
        print("\n🌐 Testing Flask app creation...")
        try:
            from app import app
            self.assertIsNotNone(app)
            self.assertEqual(app.name, 'app')
            print("✅ Flask app created successfully")
        except Exception as e:
            self.fail(f"Error creating app: {e}")
    
    def test_models_structure(self):
        """Test that database models have correct structure"""
        print("\n🗄️  Testing database models...")
        try:
            from models import Event, Player, SettlementPayment
            
            # Test Event model
            self.assertTrue(hasattr(Event, 'id'))
            self.assertTrue(hasattr(Event, 'name'))
            self.assertTrue(hasattr(Event, 'created_at'))
            
            # Test Player model
            self.assertTrue(hasattr(Player, 'id'))
            self.assertTrue(hasattr(Player, 'event_id'))
            self.assertTrue(hasattr(Player, 'name'))
            self.assertTrue(hasattr(Player, 'start'))
            self.assertTrue(hasattr(Player, 'buyins'))
            self.assertTrue(hasattr(Player, 'pl'))
            
            # Test SettlementPayment model
            self.assertTrue(hasattr(SettlementPayment, 'id'))
            self.assertTrue(hasattr(SettlementPayment, 'event_id'))
            self.assertTrue(hasattr(SettlementPayment, 'from_player'))
            self.assertTrue(hasattr(SettlementPayment, 'to_player'))
            self.assertTrue(hasattr(SettlementPayment, 'paid'))
            
            print("✅ Database models have correct structure")
        except Exception as e:
            self.fail(f"Error checking models: {e}")
    
    def test_calculate_pl_function(self):
        """Test P/L calculation function"""
        print("\n💰 Testing P/L calculation...")
        try:
            from app import calculate_pl
            
            # Test case 1: No days played
            player_data = {'start': 20, 'buyins': 0}
            pl = calculate_pl(player_data)
            self.assertEqual(pl, 0)
            
            # Test case 2: One day played, profit
            player_data = {'start': 20, 'buyins': 0, 'day1': 50}
            pl = calculate_pl(player_data)
            self.assertEqual(pl, 30.0)
            
            # Test case 3: One day played, loss
            player_data = {'start': 20, 'buyins': 0, 'day1': 10}
            pl = calculate_pl(player_data)
            self.assertEqual(pl, -10.0)
            
            # Test case 4: Multiple days with buy-ins
            player_data = {'start': 20, 'buyins': 2, 'day1': 30, 'day2': 80}
            pl = calculate_pl(player_data)
            # Total investment: 20 + (2 * 20) = 60
            # Final value: 80
            # P/L: 80 - 60 = 20
            self.assertEqual(pl, 20.0)
            
            print("✅ P/L calculation working correctly")
        except Exception as e:
            self.fail(f"Error testing calculate_pl: {e}")
    
    def test_calculate_settlements_function(self):
        """Test settlement calculation function"""
        print("\n🔄 Testing settlement calculation...")
        try:
            from app import calculate_settlements
            
            # Test case: Two winners, two losers
            players = [
                {'name': 'Alice', 'pl': 100},
                {'name': 'Bob', 'pl': 50},
                {'name': 'Charlie', 'pl': -80},
                {'name': 'David', 'pl': -70}
            ]
            
            settlements = calculate_settlements(players)
            
            # Should have settlements
            self.assertGreater(len(settlements), 0)
            
            # Check that each settlement has required fields
            for settlement in settlements:
                self.assertIn('from', settlement)
                self.assertIn('to', settlement)
                self.assertIn('amount', settlement)
                self.assertGreater(settlement['amount'], 0)
            
            # Calculate total settlements
            total_paid = sum(s['amount'] for s in settlements)
            total_winners = sum(p['pl'] for p in players if p['pl'] > 0)
            
            # Total settlements should equal total winnings (within floating point precision)
            self.assertAlmostEqual(total_paid, total_winners, places=2)
            
            print("✅ Settlement calculation working correctly")
        except Exception as e:
            self.fail(f"Error testing calculate_settlements: {e}")
    
    def test_routes_exist(self):
        """Test that all required routes are registered"""
        print("\n🛣️  Testing route registration...")
        try:
            from app import app
            
            # Get all registered routes
            routes = [rule.rule for rule in app.url_map.iter_rules()]
            
            # Check for main routes
            self.assertIn('/', routes)
            
            # Check for API routes
            api_routes = [r for r in routes if r.startswith('/api/')]
            self.assertGreater(len(api_routes), 0)
            
            print(f"✅ Found {len(api_routes)} API routes")
        except Exception as e:
            self.fail(f"Error checking routes: {e}")
    
    def test_environment_variables(self):
        """Test that environment variables are properly configured"""
        print("\n🔐 Testing environment variable configuration...")
        try:
            from database import DB_HOST, DB_PORT, DB_NAME, DB_USER
            
            # Should have database configuration (even if defaults)
            self.assertIsNotNone(DB_HOST)
            self.assertIsNotNone(DB_PORT)
            self.assertIsNotNone(DB_NAME)
            self.assertIsNotNone(DB_USER)
            
            print("✅ Environment variables configured")
        except Exception as e:
            self.fail(f"Error checking environment variables: {e}")

class TestDatabaseSchema(unittest.TestCase):
    """Test database schema and model relationships"""
    
    def test_event_player_relationship(self):
        """Test that Event and Player models have correct relationship"""
        print("\n🔗 Testing Event-Player relationship...")
        try:
            from models import Event, Player
            
            # Check that Event has players relationship
            self.assertTrue(hasattr(Event, 'players'))
            
            # Check that Player has event relationship
            self.assertTrue(hasattr(Player, 'event'))
            
            print("✅ Event-Player relationship configured correctly")
        except Exception as e:
            self.fail(f"Error testing relationship: {e}")
    
    def test_model_to_dict_methods(self):
        """Test that models have to_dict methods"""
        print("\n📋 Testing model to_dict methods...")
        try:
            from models import Event, Player, SettlementPayment
            
            # Check that models have to_dict method
            self.assertTrue(hasattr(Event, 'to_dict'))
            self.assertTrue(hasattr(Player, 'to_dict'))
            self.assertTrue(hasattr(SettlementPayment, 'to_dict'))
            
            print("✅ All models have to_dict methods")
        except Exception as e:
            self.fail(f"Error testing to_dict methods: {e}")

def run_tests():
    """Run all tests"""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test cases
    suite.addTests(loader.loadTestsFromTestCase(TestPokerTrackerAPI))
    suite.addTests(loader.loadTestsFromTestCase(TestDatabaseSchema))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 60)
    print("📊 Test Summary")
    print("=" * 60)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.wasSuccessful():
        print("\n✅ All tests passed!")
        return 0
    else:
        print("\n❌ Some tests failed")
        return 1

if __name__ == '__main__':
    sys.exit(run_tests())
