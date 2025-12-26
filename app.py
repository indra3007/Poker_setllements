#!/usr/bin/env python3
"""
Poker Tracker Web App - Version 3 with PostgreSQL
With Event/Session Management and Database Integration
"""

from flask import Flask, render_template, request, jsonify
import os
from datetime import datetime
from dotenv import load_dotenv
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy import desc

# Load environment variables
load_dotenv()

from database import get_db, close_db, engine
from models import Event, Player, SettlementPayment

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'poker-tracker-secret-key-2025')

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

@app.route('/test')
def test():
    """Test page"""
    return render_template('test.html')

@app.route('/api/events', methods=['GET'])
def get_events():
    """Get list of all events"""
    db = None
    try:
        print(f"\n=== GET EVENTS CALLED ===")
        db = get_db()
        
        # Query all events
        events = db.query(Event).order_by(Event.created_at.desc()).all()
        event_names = [event.name for event in events]
        
        print(f"Events loaded from DB: {event_names}")
        result = {'events': event_names}
        print(f"Returning: {result}")
        
        return jsonify(result)
        
    except SQLAlchemyError as e:
        print(f"❌ Database error in get_events: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': 'Database error', 'events': []}), 500
    except Exception as e:
        print(f"❌ Error in get_events: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e), 'events': []}), 500
    finally:
        if db:
            close_db(db)

@app.route('/api/events', methods=['POST'])
def create_event():
    """Create new event"""
    db = None
    try:
        print(f"\n=== CREATE EVENT CALLED ===")
        print(f"Request JSON: {request.json}")
        
        data = request.json
        event_name = data.get('event_name', '').strip()
        print(f"Event name: '{event_name}'")
        
        if not event_name:
            return jsonify({'success': False, 'error': 'Event name required'}), 400
        
        db = get_db()
        
        # Check if event already exists
        existing_event = db.query(Event).filter(Event.name == event_name).first()
        if existing_event:
            return jsonify({'success': False, 'error': 'Event already exists'}), 400
        
        # Create new event
        new_event = Event(name=event_name)
        db.add(new_event)
        db.commit()
        
        print(f"✅ Event created successfully: {event_name}")
        
        return jsonify({'success': True, 'event_name': event_name})
        
    except IntegrityError as e:
        if db:
            db.rollback()
        print(f"❌ Integrity error in create_event: {e}")
        return jsonify({'success': False, 'error': 'Event already exists'}), 400
    except SQLAlchemyError as e:
        if db:
            db.rollback()
        print(f"❌ Database error in create_event: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': 'Database error'}), 500
    except Exception as e:
        if db:
            db.rollback()
        print(f"❌ Error in create_event: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        if db:
            close_db(db)

@app.route('/api/events/<event_name>', methods=['DELETE'])
def delete_event(event_name):
    """Delete an event"""
    db = None
    try:
        db = get_db()
        
        # Find event
        event = db.query(Event).filter(Event.name == event_name).first()
        if not event:
            return jsonify({'success': False, 'error': 'Event not found'}), 404
        
        # Delete event (cascade will delete players and settlements)
        db.delete(event)
        db.commit()
        
        return jsonify({'success': True})
        
    except SQLAlchemyError as e:
        if db:
            db.rollback()
        print(f"❌ Database error in delete_event: {e}")
        return jsonify({'success': False, 'error': 'Database error'}), 500
    except Exception as e:
        if db:
            db.rollback()
        print(f"Error deleting event: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        if db:
            close_db(db)

@app.route('/api/data/<event_name>', methods=['GET'])
def get_event_data(event_name):
    """Get data for specific event"""
    db = None
    try:
        db = get_db()
        
        # Find event
        event = db.query(Event).filter(Event.name == event_name).first()
        if not event:
            return jsonify({'players': []})
        
        # Get all players for this event
        players = db.query(Player).filter(Player.event_id == event.id).order_by(Player.row_order).all()
        
        players_data = [player.to_dict() for player in players]
        
        return jsonify({'players': players_data})
        
    except SQLAlchemyError as e:
        print(f"❌ Database error in get_event_data: {e}")
        return jsonify({'players': []}), 500
    except Exception as e:
        print(f"Error getting event data: {e}")
        return jsonify({'players': []}), 500
    finally:
        if db:
            close_db(db)

@app.route('/api/save/<event_name>', methods=['POST'])
def save_event_data(event_name):
    """Save data for specific event"""
    db = None
    try:
        data = request.json
        players_data = data.get('players', [])
        
        db = get_db()
        
        # Find or create event
        event = db.query(Event).filter(Event.name == event_name).first()
        if not event:
            event = Event(name=event_name)
            db.add(event)
            db.commit()
            db.refresh(event)
        
        # Delete existing players for this event
        db.query(Player).filter(Player.event_id == event.id).delete()
        
        # Add new players
        for idx, player_data in enumerate(players_data):
            if not player_data.get('name'):
                continue
                
            # Calculate P/L and days played
            pl = calculate_pl(player_data)
            days_played = sum(1 for day in range(1, 8) if player_data.get(f'day{day}'))
            
            player = Player(
                event_id=event.id,
                name=player_data.get('name', ''),
                phone=player_data.get('phone', ''),
                start=float(player_data.get('start', 20)),
                buyins=int(player_data.get('buyins', 0)),
                day1=float(player_data.get('day1')) if player_data.get('day1') else None,
                day2=float(player_data.get('day2')) if player_data.get('day2') else None,
                day3=float(player_data.get('day3')) if player_data.get('day3') else None,
                day4=float(player_data.get('day4')) if player_data.get('day4') else None,
                day5=float(player_data.get('day5')) if player_data.get('day5') else None,
                day6=float(player_data.get('day6')) if player_data.get('day6') else None,
                day7=float(player_data.get('day7')) if player_data.get('day7') else None,
                pl=pl,
                days_played=days_played,
                row_order=idx
            )
            db.add(player)
        
        db.commit()
        
        return jsonify({'success': True, 'message': 'Data saved successfully'})
        
    except SQLAlchemyError as e:
        if db:
            db.rollback()
        print(f"❌ Database error in save_event_data: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': 'Database error'}), 500
    except Exception as e:
        if db:
            db.rollback()
        print(f"Error saving event data: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        if db:
            close_db(db)

@app.route('/api/settlements/<event_name>', methods=['GET'])
def get_event_settlements(event_name):
    """Calculate settlements for specific event"""
    db = None
    try:
        db = get_db()
        
        # Find event
        event = db.query(Event).filter(Event.name == event_name).first()
        if not event:
            return jsonify({'settlements': []})
        
        # Get all players with non-zero P/L
        players = db.query(Player).filter(
            Player.event_id == event.id,
            Player.pl != 0
        ).all()
        
        if not players:
            return jsonify({'settlements': [], 'message': 'No player data found'})
        
        players_data = [{'name': p.name, 'pl': float(p.pl)} for p in players]
        settlements = calculate_settlements(players_data)
        
        # Load payment status for this event
        settlement_payments = db.query(SettlementPayment).filter(
            SettlementPayment.event_id == event.id
        ).all()
        
        # Create a lookup dictionary for payment status
        payment_status = {
            f"{sp.from_player}→{sp.to_player}": sp.paid
            for sp in settlement_payments
        }
        
        # Add payment status to each settlement
        for settlement in settlements:
            settlement_key = f"{settlement['from']}→{settlement['to']}"
            settlement['paid'] = payment_status.get(settlement_key, False)
        
        return jsonify({
            'settlements': settlements,
            'total_winners': sum(p['pl'] for p in players_data if p['pl'] > 0),
            'total_losers': abs(sum(p['pl'] for p in players_data if p['pl'] < 0))
        })
        
    except SQLAlchemyError as e:
        print(f"❌ Database error in get_event_settlements: {e}")
        return jsonify({'settlements': []}), 500
    except Exception as e:
        print(f"Error getting settlements: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'settlements': []}), 500
    finally:
        if db:
            close_db(db)

@app.route('/api/settlements/<event_name>/mark_paid', methods=['POST'])
def mark_settlement_paid(event_name):
    """Mark a settlement as paid or unpaid"""
    db = None
    try:
        data = request.json
        from_player = data.get('from')
        to_player = data.get('to')
        paid = data.get('paid', True)
        
        db = get_db()
        
        # Find event
        event = db.query(Event).filter(Event.name == event_name).first()
        if not event:
            return jsonify({'success': False, 'error': 'Event not found'}), 404
        
        # Find or create settlement payment record
        settlement = db.query(SettlementPayment).filter(
            SettlementPayment.event_id == event.id,
            SettlementPayment.from_player == from_player,
            SettlementPayment.to_player == to_player
        ).first()
        
        if settlement:
            # Update existing record
            settlement.paid = paid
            settlement.updated_at = datetime.utcnow()
        else:
            # Create new record
            amount = data.get('amount', 0)
            settlement = SettlementPayment(
                event_id=event.id,
                from_player=from_player,
                to_player=to_player,
                amount=amount,
                paid=paid
            )
            db.add(settlement)
        
        db.commit()
        
        return jsonify({
            'success': True,
            'message': f"Settlement marked as {'paid' if paid else 'unpaid'}"
        })
        
    except SQLAlchemyError as e:
        if db:
            db.rollback()
        print(f"❌ Database error in mark_settlement_paid: {e}")
        return jsonify({'success': False, 'error': 'Database error'}), 500
    except Exception as e:
        if db:
            db.rollback()
        print(f"Error marking settlement: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        if db:
            close_db(db)

@app.route('/api/clear/<event_name>', methods=['POST'])
def clear_event_data(event_name):
    """Clear data for specific event"""
    db = None
    try:
        db = get_db()
        
        # Find event
        event = db.query(Event).filter(Event.name == event_name).first()
        if not event:
            return jsonify({'success': False, 'error': 'Event not found'}), 404
        
        # Delete all players for this event
        db.query(Player).filter(Player.event_id == event.id).delete()
        db.commit()
        
        return jsonify({'success': True, 'message': f'Event "{event_name}" cleared successfully'})
        
    except SQLAlchemyError as e:
        if db:
            db.rollback()
        print(f"❌ Database error in clear_event_data: {e}")
        return jsonify({'success': False, 'error': 'Database error'}), 500
    except Exception as e:
        if db:
            db.rollback()
        print(f"Error clearing event data: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500
    finally:
        if db:
            close_db(db)

if __name__ == '__main__':
    # Test database connection on startup
    try:
        with engine.connect() as conn:
            print("✅ Database connection successful!")
    except Exception as e:
        print(f"⚠️  Warning: Could not connect to database: {e}")
        print("Application will start but database operations will fail.")
    
    # Get port from environment variable (for deployment) or use 5001 for local
    port = int(os.environ.get('PORT', 5001))
    
    # Check if running in production
    is_production = os.environ.get('RENDER', False) or os.environ.get('FLASK_ENV') == 'production'
    
    print("\n🎰 Poker Tracker Web App v3 - PostgreSQL Edition")
    print("=" * 50)
    if is_production:
        print("🌐 Production Mode")
    else:
        print("🌐 Development Mode - Running Locally")
        print("📱 Open on your phone:")
        print(f"   http://YOUR_COMPUTER_IP:{port}")
        print("\n💻 Open on this computer:")
        print(f"   http://localhost:{port}")
    print("\n✅ Ready! Press Ctrl+C to stop")
    print("=" * 50 + "\n")
    
    app.run(host='0.0.0.0', port=port, debug=not is_production)
