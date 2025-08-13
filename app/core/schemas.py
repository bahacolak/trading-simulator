from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime
from enum import Enum

class TradeSide(str, Enum):
    BUY = "buy"
    SELL = "sell"

class Symbol(str, Enum):
    GOLD = "GOLD"
    SILVER = "SILVER"

class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6)

class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class UserResponse(BaseModel):
    id: int
    username: str
    balance: float
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

class TradeCreate(BaseModel):
    symbol: Symbol
    side: TradeSide
    quantity: float = Field(..., gt=0)

    @field_validator('quantity')
    def validate_quantity(cls, v):
        if v <= 0:
            raise ValueError('Quantity must be positive')
        if v > 1000:
            raise ValueError('Quantity too large')
        return round(v, 4)

class TradeResponse(BaseModel):
    id: int
    symbol: str
    side: str
    quantity: float
    price: float
    total_amount: float
    timestamp: datetime

    class Config:
        from_attributes = True

class PositionResponse(BaseModel):
    symbol: str
    quantity: float
    avg_price: float
    current_price: Optional[float] = None
    pnl: Optional[float] = None

    class Config:
        from_attributes = True

class PriceData(BaseModel):
    GOLD: float
    SILVER: float
    timestamp: str

class APIResponse(BaseModel):
    success: bool
    message: str
    data: Optional[dict] = None

class ErrorResponse(BaseModel):
    success: bool = False
    message: str
    detail: Optional[str] = None
