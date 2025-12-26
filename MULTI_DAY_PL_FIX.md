# Multi-Day P/L Calculation Fix - Examples

## Bug Description
The old implementation only considered the last day's chip value when calculating P/L, ignoring profits/losses from previous days.

## Example Scenario
A player plays poker for 3 days with these results:

```
Starting chips per day: $20
Buy-ins: 0

Day 1: Ends with $35 chips
Day 2: Ends with $42 chips  
Day 3: Ends with $50 chips
```

## Old Calculation (WRONG)
```
P/L = last_day_value - (start + buyins * 20)
P/L = 50 - (20 + 0 * 20)
P/L = 50 - 20
P/L = +$30
```
**Problem**: Ignores the profit from Day 1 and Day 2!

## New Calculation (CORRECT)
```
Each day is independent:
Day 1 P/L: 35 - 20 = +$15
Day 2 P/L: 42 - 20 = +$22
Day 3 P/L: 50 - 20 = +$30

Total P/L = 15 + 22 + 30 = +$67
Total P/L = +$67 - (buyins * 20)
Total P/L = +$67 - 0
Total P/L = +$67
```
**Benefit**: Correctly accounts for all days played!

## Zero-Sum Validation
In a closed poker game (no rake), the sum of all P/Ls should equal 0:

### Test Data
```
Player A: Day 1 = $30, Day 2 = $25
Player B: Day 1 = $15, Day 2 = $20
Player C: Day 1 = $15, Day 2 = $15
```

### Calculations
```
Player A: (30-20) + (25-20) = +10 + 5 = +$15
Player B: (15-20) + (20-20) = -5 + 0  = -$5
Player C: (15-20) + (15-20) = -5 + -5 = -$10

Total: +15 - 5 - 10 = $0 ✓
```

## Settlements
The settlement calculation automatically works with the new P/L values:
```
Player C pays $10 to Player A
Player B pays $5 to Player A
Result: Player A receives $15, others pay $15 total ✓
```

## Edge Cases Handled
1. **Zero values**: When a player loses all chips (value = 0), it's correctly calculated as -$20 P/L
2. **Empty strings**: Skipped days are properly ignored
3. **Invalid values**: Non-numeric values are gracefully handled
4. **Sparse days**: Non-consecutive days (e.g., Day 1, Day 3, Day 7) work correctly
5. **Buy-ins**: Additional investments are properly subtracted from total P/L

## Testing
All 14 comprehensive unit tests pass, covering:
- Single and multi-day scenarios
- Profit and loss cases
- Buy-ins integration
- Edge cases and error handling
- Float precision
