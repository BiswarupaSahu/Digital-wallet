from fastapi import FastAPI, Depends, HTTPException, status, Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import desc
from decimal import Decimal
from typing import List, Optional

from database import get_db, engine
from models import Base, User, Transaction, Product, Purchase
from schemas import (
    UserRegister, FundAccount, PayUser, ProductCreate, BuyProduct,
    BalanceResponse, TransactionResponse, ProductResponse, MessageResponse,
    ProductAddedResponse, PurchaseResponse, HealthResponse, ErrorResponse
)
from auth import get_current_user
from currency_service import currency_service

# Create database tables
Base.metadata.create_all(bind=engine)

# Create FastAPI app
app = FastAPI(
    title="Digital Wallet API",
    description="A comprehensive backend service for a digital wallet system with user authentication, fund transfers, transaction history, and product purchases.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Exception handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error"}
    )

# Routes

@app.post("/register", response_model=MessageResponse, status_code=201)
async def register_user(user_data: UserRegister, db: Session = Depends(get_db)):
    """Register a new user"""
    try:
        # Check if username already exists
        existing_user = db.query(User).filter(User.username == user_data.username).first()
        if existing_user:
            raise HTTPException(
                status_code=400,
                detail="Username already exists"
            )
        
        # Create new user
        user = User(username=user_data.username)
        user.set_password(user_data.password)
        
        db.add(user)
        db.commit()
        
        return MessageResponse(message="User registered successfully")
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Registration failed")

@app.post("/fund", response_model=BalanceResponse)
async def fund_account(
    fund_data: FundAccount,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Fund the user's account"""
    try:
        amount = Decimal(str(fund_data.amt))
        
        # Update user balance
        current_user.balance += amount
        new_balance = current_user.balance
        
        # Create transaction record
        transaction = Transaction(
            to_user_id=current_user.id,
            amount=amount,
            kind='credit',
            updated_balance=new_balance,
            description='Account funding'
        )
        
        db.add(transaction)
        db.commit()
        
        return BalanceResponse(balance=float(new_balance), currency="INR")
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to fund account")

@app.post("/pay", response_model=BalanceResponse)
async def pay_user(
    payment_data: PayUser,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Pay another user"""
    try:
        amount = Decimal(str(payment_data.amt))
        recipient_username = payment_data.to.strip()
        
        # Find recipient
        recipient = db.query(User).filter(User.username == recipient_username).first()
        if not recipient:
            raise HTTPException(status_code=400, detail="Recipient not found")
        
        if recipient.id == current_user.id:
            raise HTTPException(status_code=400, detail="Cannot pay yourself")
        
        # Check sufficient balance
        if current_user.balance < amount:
            raise HTTPException(status_code=400, detail="Insufficient funds")
        
        # Update balances
        current_user.balance -= amount
        recipient.balance += amount
        
        # Create transaction records
        debit_transaction = Transaction(
            from_user_id=current_user.id,
            to_user_id=current_user.id,
            amount=amount,
            kind='debit',
            updated_balance=current_user.balance,
            description=f'Payment to {recipient_username}'
        )
        
        credit_transaction = Transaction(
            from_user_id=current_user.id,
            to_user_id=recipient.id,
            amount=amount,
            kind='credit',
            updated_balance=recipient.balance,
            description=f'Payment from {current_user.username}'
        )
        
        db.add(debit_transaction)
        db.add(credit_transaction)
        db.commit()
        
        return BalanceResponse(balance=float(current_user.balance), currency="INR")
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Payment failed")

@app.get("/bal", response_model=BalanceResponse)
async def get_balance(
    currency: str = Query("INR", description="Currency code (INR, USD, EUR, GBP)"),
    current_user: User = Depends(get_current_user)
):
    """Get user balance, optionally in different currency"""
    try:
        currency = currency.upper()
        balance = float(current_user.balance)
        
        if currency == 'INR':
            return BalanceResponse(balance=balance, currency='INR')
        
        try:
            converted_balance = currency_service.convert_currency(balance, 'INR', currency)
            return BalanceResponse(balance=converted_balance, currency=currency)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to get balance")

@app.get("/stmt", response_model=List[TransactionResponse])
async def get_statement(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's transaction history"""
    try:
        transactions = db.query(Transaction)\
            .filter(Transaction.to_user_id == current_user.id)\
            .order_by(desc(Transaction.timestamp))\
            .all()
        
        return [TransactionResponse(**transaction.to_dict()) for transaction in transactions]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to get statement")

@app.post("/product", response_model=ProductAddedResponse, status_code=201)
async def add_product(
    product_data: ProductCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add a new product to the catalog"""
    try:
        # Create product
        product = Product(
            name=product_data.name,
            price=Decimal(str(product_data.price)),
            description=product_data.description
        )
        
        db.add(product)
        db.commit()
        db.refresh(product)
        
        return ProductAddedResponse(id=product.id, message="Product added")
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to add product")

@app.get("/product", response_model=List[ProductResponse])
async def list_products(db: Session = Depends(get_db)):
    """List all products in the catalog"""
    try:
        products = db.query(Product).all()
        return [ProductResponse(**product.to_dict()) for product in products]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to list products")

@app.post("/buy", response_model=PurchaseResponse)
async def buy_product(
    purchase_data: BuyProduct,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Buy a product using wallet balance"""
    try:
        # Find product
        product = db.query(Product).filter(Product.id == purchase_data.product_id).first()
        if not product:
            raise HTTPException(status_code=400, detail="Product not found")
        
        # Check sufficient balance
        if current_user.balance < product.price:
            raise HTTPException(status_code=400, detail="Insufficient balance")
        
        # Update user balance
        current_user.balance -= product.price
        
        # Create transaction record
        transaction = Transaction(
            from_user_id=current_user.id,
            to_user_id=current_user.id,
            amount=product.price,
            kind='debit',
            updated_balance=current_user.balance,
            description=f'Purchase: {product.name}'
        )
        
        # Create purchase record
        purchase = Purchase(
            user_id=current_user.id,
            product_id=product.id,
            amount_paid=product.price,
            transaction=transaction
        )
        
        db.add(transaction)
        db.add(purchase)
        db.commit()
        
        return PurchaseResponse(
            message="Product purchased",
            balance=float(current_user.balance)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Purchase failed")

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(status="healthy", message="Digital Wallet API is running")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=5000, reload=True)