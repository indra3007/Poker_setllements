#!/usr/bin/env python3
"""
Unit tests for calculate_pl function to verify multi-day P/L calculations
"""

import unittest
from app import calculate_pl


class TestCalculatePL(unittest.TestCase):
    """Test cases for multi-day P/L calculation"""
    
    def test_single_day_profit(self):
        """Test P/L for a single day with profit"""
        player_data = {
            'start': 20,
            'buyins': 0,
            'day1': 35
        }
        result = calculate_pl(player_data)
        # Day 1: 35 - 20 = +15
        # Total: +15
        self.assertEqual(result, 15.0)
    
    def test_single_day_loss(self):
        """Test P/L for a single day with loss"""
        player_data = {
            'start': 20,
            'buyins': 0,
            'day1': 10
        }
        result = calculate_pl(player_data)
        # Day 1: 10 - 20 = -10
        # Total: -10
        self.assertEqual(result, -10.0)
    
    def test_multi_day_all_profit(self):
        """Test P/L for multiple days with all profits"""
        player_data = {
            'start': 20,
            'buyins': 0,
            'day1': 35,
            'day2': 42,
            'day3': 50
        }
        result = calculate_pl(player_data)
        # Day 1: 35 - 20 = +15
        # Day 2: 42 - 20 = +22
        # Day 3: 50 - 20 = +30
        # Total: 15 + 22 + 30 = +67
        self.assertEqual(result, 67.0)
    
    def test_multi_day_mixed(self):
        """Test P/L for multiple days with mixed results"""
        player_data = {
            'start': 20,
            'buyins': 0,
            'day1': 35,   # +15
            'day2': 15,   # -5
            'day3': 50,   # +30
            'day4': 10    # -10
        }
        result = calculate_pl(player_data)
        # Day 1: 35 - 20 = +15
        # Day 2: 15 - 20 = -5
        # Day 3: 50 - 20 = +30
        # Day 4: 10 - 20 = -10
        # Total: 15 - 5 + 30 - 10 = +30
        self.assertEqual(result, 30.0)
    
    def test_with_buyins(self):
        """Test P/L with buy-ins"""
        player_data = {
            'start': 20,
            'buyins': 2,
            'day1': 35,
            'day2': 42
        }
        result = calculate_pl(player_data)
        # Day 1: 35 - 20 = +15
        # Day 2: 42 - 20 = +22
        # Subtotal: 15 + 22 = +37
        # Buy-ins cost: 2 * 20 = 40
        # Total: 37 - 40 = -3
        self.assertEqual(result, -3.0)
    
    def test_all_seven_days(self):
        """Test P/L for all seven days"""
        player_data = {
            'start': 20,
            'buyins': 1,
            'day1': 30,
            'day2': 25,
            'day3': 40,
            'day4': 15,
            'day5': 35,
            'day6': 20,
            'day7': 50
        }
        result = calculate_pl(player_data)
        # Day 1: 30 - 20 = +10
        # Day 2: 25 - 20 = +5
        # Day 3: 40 - 20 = +20
        # Day 4: 15 - 20 = -5
        # Day 5: 35 - 20 = +15
        # Day 6: 20 - 20 = 0
        # Day 7: 50 - 20 = +30
        # Subtotal: 10 + 5 + 20 - 5 + 15 + 0 + 30 = +75
        # Buy-ins cost: 1 * 20 = 20
        # Total: 75 - 20 = +55
        self.assertEqual(result, 55.0)
    
    def test_no_days_played(self):
        """Test P/L when no days are filled"""
        player_data = {
            'start': 20,
            'buyins': 0
        }
        result = calculate_pl(player_data)
        self.assertEqual(result, 0)
    
    def test_sparse_days(self):
        """Test P/L with non-consecutive days"""
        player_data = {
            'start': 20,
            'buyins': 0,
            'day1': 35,
            'day3': 42,  # Skip day 2
            'day7': 28   # Skip days 4-6
        }
        result = calculate_pl(player_data)
        # Day 1: 35 - 20 = +15
        # Day 3: 42 - 20 = +22
        # Day 7: 28 - 20 = +8
        # Total: 15 + 22 + 8 = +45
        self.assertEqual(result, 45.0)
    
    def test_custom_start_value(self):
        """Test P/L with custom starting value"""
        player_data = {
            'start': 50,
            'buyins': 0,
            'day1': 75,
            'day2': 60
        }
        result = calculate_pl(player_data)
        # Day 1: 75 - 50 = +25
        # Day 2: 60 - 50 = +10
        # Total: 25 + 10 = +35
        self.assertEqual(result, 35.0)
    
    def test_empty_string_values(self):
        """Test P/L with empty string values (should be ignored)"""
        player_data = {
            'start': 20,
            'buyins': 0,
            'day1': 35,
            'day2': '',
            'day3': 42
        }
        result = calculate_pl(player_data)
        # Day 1: 35 - 20 = +15
        # Day 2: ignored (empty string)
        # Day 3: 42 - 20 = +22
        # Total: 15 + 22 = +37
        self.assertEqual(result, 37.0)
    
    def test_invalid_day_values(self):
        """Test P/L with invalid day values (should be skipped)"""
        player_data = {
            'start': 20,
            'buyins': 0,
            'day1': 35,
            'day2': 'invalid',
            'day3': 42
        }
        result = calculate_pl(player_data)
        # Day 1: 35 - 20 = +15
        # Day 2: skipped (invalid value)
        # Day 3: 42 - 20 = +22
        # Total: 15 + 22 = +37
        self.assertEqual(result, 37.0)
    
    def test_zero_day_value(self):
        """Test P/L with zero day value (player lost all chips)"""
        player_data = {
            'start': 20,
            'buyins': 0,
            'day1': 0
        }
        result = calculate_pl(player_data)
        # Day 1: 0 - 20 = -20
        # Total: -20
        self.assertEqual(result, -20.0)
    
    def test_float_precision(self):
        """Test P/L calculation with float precision"""
        player_data = {
            'start': 20,
            'buyins': 0,
            'day1': 23.50,
            'day2': 18.25
        }
        result = calculate_pl(player_data)
        # Day 1: 23.50 - 20 = +3.50
        # Day 2: 18.25 - 20 = -1.75
        # Total: 3.50 - 1.75 = +1.75
        self.assertEqual(result, 1.75)


class TestOldVsNewLogic(unittest.TestCase):
    """Test cases demonstrating the difference between old and new logic"""
    
    def test_old_logic_bug_example(self):
        """
        Demonstrate the bug in the old logic.
        
        Old logic would calculate: last_day_value - (start + buyins*20)
        New logic calculates: sum(each_day - start) - (buyins*20)
        """
        player_data = {
            'start': 20,
            'buyins': 0,
            'day1': 35,   # +15 profit
            'day2': 42,   # +22 profit
            'day3': 50    # +30 profit
        }
        
        # New logic (correct)
        new_result = calculate_pl(player_data)
        # Day 1: +15, Day 2: +22, Day 3: +30 → Total: +67
        self.assertEqual(new_result, 67.0)
        
        # Old logic would have been: 50 - 20 = +30 (WRONG!)
        # This demonstrates that the old logic ignored the profit from day 1 and day 2


if __name__ == '__main__':
    unittest.main()
