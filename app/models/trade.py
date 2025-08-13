from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from datetime import datetime
from ..core.database import Base

class Trade(Base):
    __tablename__ = "trades"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    symbol = Column(String(10), nullable=False)
    side = Column(String(4), nullable=False)
    quantity = Column(Float, nullable=False)
    price = Column(Float, nullable=False)
    total_amount = Column(Float, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    
    user = relationship("User", back_populates="trades")

    __table_args__ = (
        Index('idx_user_symbol', 'user_id', 'symbol'),
        Index('idx_user_timestamp', 'user_id', 'timestamp'),
    )

    def __repr__(self):
        return f"<Trade(user_id={self.user_id}, symbol={self.symbol}, side={self.side}, quantity={self.quantity})>"
