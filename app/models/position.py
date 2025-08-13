from sqlalchemy import Column, Integer, String, Float, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from ..core.database import Base

class Position(Base):
    __tablename__ = "positions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    symbol = Column(String(10), nullable=False)
    quantity = Column(Float, nullable=False)
    avg_price = Column(Float, nullable=False)
    
    user = relationship("User", back_populates="positions")

    __table_args__ = (
        UniqueConstraint('user_id', 'symbol', name='uq_user_symbol'),
    )

    def calculate_pnl(self, current_price: float) -> float:
        return (current_price - self.avg_price) * self.quantity

    def __repr__(self):
        return f"<Position(user_id={self.user_id}, symbol={self.symbol}, quantity={self.quantity})>"
