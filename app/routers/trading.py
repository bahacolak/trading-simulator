from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..core.database import get_db
from ..core.auth import get_current_user
from ..core.schemas import TradeCreate, TradeResponse, PositionResponse, APIResponse
from ..models import User
from ..services.trading_service import TradingService
from ..services.price_service import price_service

router = APIRouter(prefix="/trading", tags=["Trading"])

@router.post("/trade", response_model=APIResponse)
async def execute_trade(
    trade_data: TradeCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        trading_service = TradingService(db)
        trade = trading_service.execute_trade(current_user, trade_data)
        
        return APIResponse(
            success=True,
            message="Trade executed successfully",
            data={
                "trade_id": trade.id,
                "symbol": trade.symbol,
                "side": trade.side,
                "quantity": trade.quantity,
                "price": trade.price,
                "total_amount": trade.total_amount
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Trade execution failed: {str(e)}"
        )

@router.get("/positions", response_model=List[PositionResponse])
async def get_positions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    trading_service = TradingService(db)
    positions = trading_service.get_user_positions(current_user)
    
    result = []
    for position in positions:
        current_price = price_service.get_current_price(position.symbol)
        pnl = position.calculate_pnl(current_price) if current_price else 0
        
        result.append(PositionResponse(
            symbol=position.symbol,
            quantity=position.quantity,
            avg_price=position.avg_price,
            current_price=current_price,
            pnl=pnl
        ))
    
    return result

@router.get("/trades", response_model=List[TradeResponse])
async def get_trade_history(
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if limit > 100:
        limit = 100
    
    trading_service = TradingService(db)
    trades = trading_service.get_user_trades(current_user, limit)
    
    return [TradeResponse.from_orm(trade) for trade in trades]

@router.get("/balance")
async def get_balance(current_user: User = Depends(get_current_user)):
    return {
        "balance": current_user.balance,
        "username": current_user.username
    }
