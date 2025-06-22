from pydantic import BaseModel, Field, validator
from typing import Optional
from decimal import Decimal

class UserRegister(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6, max_length=100)
    
    @validator('username')
    def validate_username(cls, v):
        if not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError('Username can only contain letters, numbers, underscores, and hyphens')
        return v.strip()

class FundAccount(BaseModel):
    amt: float = Field(..., gt=0, le=999999.99)

class PayUser(BaseModel):
    to: str = Field(..., min_length=1)
    amt: float = Field(..., gt=0, le=999999.99)

class ProductCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=255)
    price: float = Field(..., gt=0, le=999999.99)
    description: Optional[str] = Field(None, max_length=1000)
    
    @validator('name')
    def validate_name(cls, v):
        return v.strip()
    
    @validator('description')
    def validate_description(cls, v):
        return v.strip() if v else None

class BuyProduct(BaseModel):
    product_id: int = Field(..., gt=0)

class UserResponse(BaseModel):
    id: int
    username: str
    balance: float
    created_at: str

class BalanceResponse(BaseModel):
    balance: float
    currency: str

class TransactionResponse(BaseModel):
    id: int
    kind: str
    amt: float
    updated_bal: float
    description: Optional[str]
    timestamp: str

class ProductResponse(BaseModel):
    id: int
    name: str
    price: float
    description: Optional[str]

class MessageResponse(BaseModel):
    message: str

class ErrorResponse(BaseModel):
    error: str

class ProductAddedResponse(BaseModel):
    id: int
    message: str

class PurchaseResponse(BaseModel):
    message: str
    balance: float

class HealthResponse(BaseModel):
    status: str
    message: str