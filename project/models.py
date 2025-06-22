from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum, Text, Index
from decimal import Decimal
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base
import bcrypt
from datetime import datetime
from sqlalchemy.types import Numeric

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(80), unique=True, nullable=False, index=True)
    password_hash = Column(String(128), nullable=False)
    balance = Column(Numeric(10, 2), default=0.00, nullable=False)
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    sent_transactions = relationship('Transaction', foreign_keys='Transaction.from_user_id', back_populates='sender')
    received_transactions = relationship('Transaction', foreign_keys='Transaction.to_user_id', back_populates='receiver')
    purchases = relationship('Purchase', back_populates='buyer')
    
    def set_password(self, password: str):
        """Hash and set the user's password"""
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    def check_password(self, password: str) -> bool:
        """Check if the provided password matches the stored hash"""
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'balance': float(self.balance),
            'created_at': self.created_at.isoformat()
        }

class Transaction(Base):
    __tablename__ = 'transactions'
    
    id = Column(Integer, primary_key=True, index=True)
    from_user_id = Column(Integer, ForeignKey('users.id'), nullable=True)  # Null for deposits
    to_user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)
    kind = Column(Enum('credit', 'debit', name='transaction_kind'), nullable=False)
    updated_balance = Column(Numeric(10, 2), nullable=False)
    description = Column(String(255), nullable=True)
    timestamp = Column(DateTime, default=func.now(), index=True)
    
    # Relationships
    sender = relationship('User', foreign_keys=[from_user_id], back_populates='sent_transactions')
    receiver = relationship('User', foreign_keys=[to_user_id], back_populates='received_transactions')
    purchase = relationship('Purchase', back_populates='transaction', uselist=False)
    
    def to_dict(self):
        return {
            'id': self.id,
            'kind': self.kind,
            'amt': float(self.amount),
            'updated_bal': float(self.updated_balance),
            'description': self.description,
            'timestamp': self.timestamp.isoformat() + 'Z'
        }

class Product(Base):
    __tablename__ = 'products'
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    price = Column(Numeric(10, 2), nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    purchases = relationship('Purchase', back_populates='product')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'price': float(self.price),
            'description': self.description
        }

class Purchase(Base):
    __tablename__ = 'purchases'
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    amount_paid = Column(Numeric(10, 2), nullable=False)
    transaction_id = Column(Integer, ForeignKey('transactions.id'), nullable=False)
    timestamp = Column(DateTime, default=func.now())
    
    # Relationships
    buyer = relationship('User', back_populates='purchases')
    product = relationship('Product', back_populates='purchases')
    transaction = relationship('Transaction', back_populates='purchase')
    
    def to_dict(self):
        return {
            'id': self.id,
            'product_name': self.product.name,
            'amount_paid': float(self.amount_paid),
            'timestamp': self.timestamp.isoformat() + 'Z'
        }
