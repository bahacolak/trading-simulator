from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from ..models import User, Trade, Position
from ..core.schemas import TradeCreate, TradeSide
from .price_service import PriceService

class TradingService:
    
    def __init__(self, db: Session):
        self.db = db
        self.price_service = PriceService()

    def execute_trade(self, user: User, trade_data: TradeCreate) -> Trade:
        current_price = self.price_service.get_current_price(trade_data.symbol.value)
        if not current_price:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Price not available for {trade_data.symbol.value}"
            )

        total_amount = trade_data.quantity * current_price

        if trade_data.side == TradeSide.BUY:
            return self._execute_buy(user, trade_data, current_price, total_amount)
        else:
            return self._execute_sell(user, trade_data, current_price, total_amount)

    def _execute_buy(self, user: User, trade_data: TradeCreate, price: float, total_amount: float) -> Trade:
        if user.balance < total_amount:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Insufficient balance"
            )

        user.balance -= total_amount

        trade = Trade(
            user_id=user.id,
            symbol=trade_data.symbol.value,
            side=trade_data.side.value,
            quantity=trade_data.quantity,
            price=price,
            total_amount=total_amount
        )
        self.db.add(trade)

        position = self.db.query(Position).filter(
            Position.user_id == user.id,
            Position.symbol == trade_data.symbol.value
        ).first()

        if position:
            total_quantity = position.quantity + trade_data.quantity
            total_value = (position.avg_price * position.quantity) + total_amount
            position.avg_price = total_value / total_quantity
            position.quantity = total_quantity
        else:
            position = Position(
                user_id=user.id,
                symbol=trade_data.symbol.value,
                quantity=trade_data.quantity,
                avg_price=price
            )
            self.db.add(position)

        self.db.commit()
        return trade

    def _execute_sell(self, user: User, trade_data: TradeCreate, price: float, total_amount: float) -> Trade:
        position = self.db.query(Position).filter(
            Position.user_id == user.id,
            Position.symbol == trade_data.symbol.value
        ).first()

        if not position or position.quantity < trade_data.quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Insufficient position to sell"
            )

        user.balance += total_amount

        trade = Trade(
            user_id=user.id,
            symbol=trade_data.symbol.value,
            side=trade_data.side.value,
            quantity=trade_data.quantity,
            price=price,
            total_amount=total_amount
        )
        self.db.add(trade)

        position.quantity -= trade_data.quantity
        if position.quantity == 0:
            self.db.delete(position)

        self.db.commit()
        return trade

    def get_user_positions(self, user: User) -> List[Position]:
        return self.db.query(Position).filter(Position.user_id == user.id).all()

    def get_user_trades(self, user: User, limit: int = 50) -> List[Trade]:
        return (
            self.db.query(Trade)
            .filter(Trade.user_id == user.id)
            .order_by(Trade.timestamp.desc())
            .limit(limit)
            .all()
        )
