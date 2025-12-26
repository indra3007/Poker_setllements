"""
Database models for Poker Tracker application
"""
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

class Event(Base):
    """Event model - represents a poker event/session"""
    __tablename__ = 'events'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    players = relationship('Player', back_populates='event', cascade='all, delete-orphan')
    settlements = relationship('SettlementPayment', back_populates='event', cascade='all, delete-orphan')
    
    def to_dict(self):
        """Convert event to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Player(Base):
    """Player model - represents a player in an event"""
    __tablename__ = 'players'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    event_id = Column(Integer, ForeignKey('events.id', ondelete='CASCADE'), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    phone = Column(String(50), nullable=True)
    start = Column(Float, default=20.0, nullable=False)
    buyins = Column(Integer, default=0, nullable=False)
    day1 = Column(Float, nullable=True)
    day2 = Column(Float, nullable=True)
    day3 = Column(Float, nullable=True)
    day4 = Column(Float, nullable=True)
    day5 = Column(Float, nullable=True)
    day6 = Column(Float, nullable=True)
    day7 = Column(Float, nullable=True)
    pl = Column(Float, default=0.0, nullable=False)
    days_played = Column(Integer, default=0, nullable=False)
    row_order = Column(Integer, default=0, nullable=False)  # For maintaining order
    
    # Relationships
    event = relationship('Event', back_populates='players')
    
    def to_dict(self):
        """Convert player to dictionary"""
        result = {
            'id': self.id,
            'event_id': self.event_id,
            'name': self.name,
            'phone': self.phone,
            'start': self.start,
            'buyins': self.buyins,
            'pl': self.pl,
            'days_played': self.days_played,
            'row': self.row_order
        }
        # Add day fields dynamically
        for day_num in range(1, 8):
            day_attr = f'day{day_num}'
            day_value = getattr(self, day_attr)
            result[day_attr] = day_value if day_value is not None else ''
        return result

class SettlementPayment(Base):
    """SettlementPayment model - tracks payment status for settlements"""
    __tablename__ = 'settlement_payments'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    event_id = Column(Integer, ForeignKey('events.id', ondelete='CASCADE'), nullable=False, index=True)
    from_player = Column(String(255), nullable=False)
    to_player = Column(String(255), nullable=False)
    amount = Column(Float, nullable=False)
    paid = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    event = relationship('Event', back_populates='settlements')
    
    def to_dict(self):
        """Convert settlement payment to dictionary"""
        return {
            'id': self.id,
            'event_id': self.event_id,
            'from': self.from_player,
            'to': self.to_player,
            'amount': self.amount,
            'paid': self.paid,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
