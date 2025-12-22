#!/usr/bin/env python3
"""
Poker Tracker Web App - Version 2
With Event/Session Management and Quick Player Selection
"""

from flask import Flask, render_template, request, jsonify
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment
import os
from datetime import datetime
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = 'poker-tracker-secret-key-2025'

EXCEL_FILE = 'poker_tracker.xlsx'
EVENTS_FILE = 'events.json'
SETTLEMENTS_FILE = 'settlements_tracking.json'

def load_settlement_payments():
    """Load settlement payment tracking from JSON"""
    if os.path.exists(SETTLEMENTS_FILE):
        with open(SETTLEMENTS_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_settlement_payments(payments):
    """Save settlement payment tracking to JSON"""
    with open(SETTLEMENTS_FILE, 'w') as f:
        json.dump(payments, f, indent=2)

def load_events():
    """Load events list from JSON file"""
    if os.path.exists(EVENTS_FILE):
        with open(EVENTS_FILE, 'r') as f:
            return json.load(f)
    return []

def save_events(events):
    """Save events list to JSON file"""
    with open(EVENTS_FILE, 'w') as f:
        json.dump(events, f, indent=2)

def get_or_create_sheet(wb, sheet_name):
    """Get existing sheet or create new one"""
    if sheet_name in wb.sheetnames:
        return wb[sheet_name]
    
    # Create new sheet
    ws = wb.create_sheet(sheet_name)
    
    # Headers
    headers = ['Player Name', 'Phone', 'Start', 'Buy-ins', 'Day 1 End', 'Day 2 End', 'Day 3 End', 
               'Day 4 End', 'Day 5 End', 'Day 6 End', 'Day 7 End', 'P/L ($)', 'Days Played']
    ws.append(headers)
    
    # Style header row
    header_fill = PatternFill(start_color='1DA1F2', end_color='1DA1F2', fill_type='solid')
    header_font = Font(bold=True, color='FFFFFF', size=12)
    
    for cell in ws[1]:
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal='center', vertical='center')
    
    return ws

def create_or_load_workbook():
    """Create new workbook or load existing one"""
    if os.path.exists(EXCEL_FILE):
        return openpyxl.load_workbook(EXCEL_FILE)
    
    # Create new workbook
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Events"
    ws.append(['Event List'])
    wb.save(EXCEL_FILE)
    return wb

def calculate_pl(player_data):
    """Calculate P/L based on last filled day and buy-ins"""
    start = player_data.get('start', 20)
    buyins = player_data.get('buyins', 0)
    days_played = 0
    last_value = start
    
    for day in range(1, 8):
        day_key = f'day{day}'
        if day_key in player_data and player_data[day_key]:
            try:
                days_played += 1
                last_value = float(player_data[day_key])
            except:
                pass
    
    if days_played == 0:
        return 0
    
    total_investment = start + (buyins * 20)
    pl = last_value - total_investment
    return round(pl, 2)

def calculate_settlements(players):
    """Calculate optimal settlements using greedy algorithm"""
    # Separate winners and losers
    winners = [(p['name'], p['pl']) for p in players if p['pl'] > 0]
    losers = [(p['name'], -p['pl']) for p in players if p['pl'] < 0]
    
    # Sort by amount (descending)
    winners.sort(key=lambda x: x[1], reverse=True)
    losers.sort(key=lambda x: x[1], reverse=True)
    
    settlements = []
    i, j = 0, 0
    
    while i < len(winners) and j < len(losers):
        winner_name, win_amount = winners[i]
        loser_name, loss_amount = losers[j]
        
        payment = min(win_amount, loss_amount)
        settlements.append({
            'from': loser_name,
            'to': winner_name,
            'amount': round(payment, 2)
        })
        
        winners[i] = (winner_name, win_amount - payment)
        losers[j] = (loser_name, loss_amount - payment)
        
        if winners[i][1] < 0.01:  # Account for floating point precision
            i += 1
        if losers[j][1] < 0.01:
            j += 1
    
    return settlements

@app.route('/')
def index():
    """Main page"""
    return render_template('index_v2.html')

@app.route('/api/events', methods=['GET'])
def get_events():
    """Get list of all events"""
    events = load_events()
    return jsonify({'events': events})

@app.route('/api/events', methods=['POST'])
def create_event():
    """Create new event"""
    data = request.json
    event_name = data.get('event_name', '').strip()
    
    if not event_name:
        return jsonify({'success': False, 'error': 'Event name required'}), 400
    
    events = load_events()
    
    # Check if event already exists
    if event_name in events:
        return jsonify({'success': False, 'error': 'Event already exists'}), 400
    
    events.append(event_name)
    save_events(events)
    
    # Create sheet in Excel
    wb = create_or_load_workbook()
    get_or_create_sheet(wb, event_name)
    wb.save(EXCEL_FILE)
    wb.close()
    
    return jsonify({'success': True, 'event_name': event_name})

@app.route('/api/events/<event_name>', methods=['DELETE'])
def delete_event(event_name):
    """Delete an event"""
    events = load_events()
    
    if event_name not in events:
        return jsonify({'success': False, 'error': 'Event not found'}), 404
    
    # Remove from events list
    events.remove(event_name)
    save_events(events)
    
    # Remove sheet from Excel
    try:
        wb = create_or_load_workbook()
        if event_name in wb.sheetnames:
            del wb[event_name]
            wb.save(EXCEL_FILE)
        wb.close()
    except Exception as e:
        print(f"Error deleting sheet: {e}")
    
    # Remove settlement tracking for this event
    try:
        settlements = load_settlement_payments()
        if event_name in settlements:
            del settlements[event_name]
            save_settlement_payments(settlements)
    except Exception as e:
        print(f"Error deleting settlement tracking: {e}")
    
    return jsonify({'success': True})

@app.route('/api/data/<event_name>', methods=['GET'])
def get_event_data(event_name):
    """Get data for specific event"""
    wb = create_or_load_workbook()
    
    if event_name not in wb.sheetnames:
        wb.close()
        return jsonify({'players': []})
    
    ws = wb[event_name]
    players = []
    
    # Read data from sheet (skip header row)
    for row_idx in range(2, ws.max_row + 1):
        row = ws[row_idx]
        player_data = {
            'row': row_idx,
            'name': row[0].value or '',
            'phone': row[1].value or '',
            'start': row[2].value or 20,
            'buyins': row[3].value or 0,
            'day1': row[4].value or '',
            'day2': row[5].value or '',
            'day3': row[6].value or '',
            'day4': row[7].value or '',
            'day5': row[8].value or '',
            'day6': row[9].value or '',
            'day7': row[10].value or '',
            'pl': row[11].value or 0,
            'days_played': row[12].value or 0
        }
        
        # Only include rows with names
        if player_data['name']:
            players.append(player_data)
    
    wb.close()
    return jsonify({'players': players})

@app.route('/api/save/<event_name>', methods=['POST'])
def save_event_data(event_name):
    """Save data for specific event"""
    data = request.json
    players = data.get('players', [])
    
    wb = create_or_load_workbook()
    ws = get_or_create_sheet(wb, event_name)
    
    # Clear existing data (keep headers)
    for row_idx in range(2, ws.max_row + 1):
        for col_idx in range(1, 14):
            ws.cell(row=row_idx, column=col_idx, value='')
    
    # Write new data
    for idx, player in enumerate(players):
        row_idx = idx + 2
        
        ws.cell(row=row_idx, column=1, value=player.get('name', ''))
        ws.cell(row=row_idx, column=2, value=player.get('phone', ''))
        ws.cell(row=row_idx, column=3, value=player.get('start', 20))
        ws.cell(row=row_idx, column=4, value=player.get('buyins', 0))  # Save buy-ins!
        
        # Day values
        for day in range(1, 8):
            day_val = player.get(f'day{day}', '')
            if day_val:
                ws.cell(row=row_idx, column=4+day, value=float(day_val))
        
        # Calculate P/L and days played
        pl = calculate_pl(player)
        days_played = sum(1 for day in range(1, 8) if player.get(f'day{day}'))
        
        ws.cell(row=row_idx, column=12, value=pl)
        ws.cell(row=row_idx, column=13, value=days_played)
    
    wb.save(EXCEL_FILE)
    wb.close()
    
    return jsonify({'success': True, 'message': 'Data saved successfully'})

@app.route('/api/settlements/<event_name>', methods=['GET'])
def get_event_settlements(event_name):
    """Calculate settlements for specific event"""
    wb = create_or_load_workbook()
    
    if event_name not in wb.sheetnames:
        wb.close()
        return jsonify({'settlements': []})
    
    ws = wb[event_name]
    players = []
    
    for row_idx in range(2, ws.max_row + 1):
        row = ws[row_idx]
        name = row[0].value
        pl = row[11].value or 0
        
        if name and pl != 0:
            players.append({'name': name, 'pl': float(pl)})
    
    wb.close()
    
    if not players:
        return jsonify({'settlements': [], 'message': 'No player data found'})
    
    settlements = calculate_settlements(players)
    
    # Load payment status for this event
    payment_tracking = load_settlement_payments()
    event_payments = payment_tracking.get(event_name, {})
    
    # Add payment status to each settlement
    for settlement in settlements:
        settlement_key = f"{settlement['from']}→{settlement['to']}"
        settlement['paid'] = event_payments.get(settlement_key, False)
    
    return jsonify({
        'settlements': settlements,
        'total_winners': sum(p['pl'] for p in players if p['pl'] > 0),
        'total_losers': abs(sum(p['pl'] for p in players if p['pl'] < 0))
    })

@app.route('/api/settlements/<event_name>/mark_paid', methods=['POST'])
def mark_settlement_paid(event_name):
    """Mark a settlement as paid or unpaid"""
    data = request.json
    from_player = data.get('from')
    to_player = data.get('to')
    paid = data.get('paid', True)
    
    settlement_key = f"{from_player}→{to_player}"
    
    # Load existing payment tracking
    payment_tracking = load_settlement_payments()
    
    # Initialize event tracking if not exists
    if event_name not in payment_tracking:
        payment_tracking[event_name] = {}
    
    # Update payment status
    payment_tracking[event_name][settlement_key] = paid
    
    # Save back to file
    save_settlement_payments(payment_tracking)
    
    return jsonify({
        'success': True,
        'message': f"Settlement marked as {'paid' if paid else 'unpaid'}"
    })

@app.route('/api/clear/<event_name>', methods=['POST'])
def clear_event_data(event_name):
    """Clear data for specific event"""
    wb = create_or_load_workbook()
    
    if event_name in wb.sheetnames:
        ws = wb[event_name]
        # Keep headers, clear data rows
        for row_idx in range(2, ws.max_row + 1):
            for col_idx in range(1, 14):
                ws.cell(row=row_idx, column=col_idx, value='')
        wb.save(EXCEL_FILE)
    
    wb.close()
    return jsonify({'success': True, 'message': f'Event "{event_name}" cleared successfully'})

if __name__ == '__main__':
    create_or_load_workbook()
    
    # Get port from environment variable (for deployment) or use 5001 for local
    port = int(os.environ.get('PORT', 5001))
    
    # Check if running in production
    is_production = os.environ.get('RENDER', False)
    
    print("\n🎰 Poker Tracker Web App v2 - Event Management")
    print("=" * 50)
    if is_production:
        print("🌐 Production Mode - Deployed on Render")
    else:
        print("🌐 Development Mode - Running Locally")
        print("📱 Open on your phone:")
        print(f"   http://YOUR_COMPUTER_IP:{port}")
        print("\n💻 Open on this computer:")
        print(f"   http://localhost:{port}")
    print("\n✅ Ready! Press Ctrl+C to stop")
    print("=" * 50 + "\n")
    
    app.run(host='0.0.0.0', port=port, debug=not is_production)
