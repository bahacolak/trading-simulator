from fastapi import APIRouter
from ..core.schemas import PriceData
from ..services.price_service import price_service

router = APIRouter(prefix="/prices", tags=["Prices"])

@router.get("/current", response_model=PriceData)
async def get_current_prices():
    prices = price_service.get_all_prices()
    return PriceData(**prices)

@router.get("/gold")
async def get_gold_price():
    price = price_service.get_current_price("GOLD")
    return {"symbol": "GOLD", "price": price}

@router.get("/silver")
async def get_silver_price():
    price = price_service.get_current_price("SILVER")
    return {"symbol": "SILVER", "price": price}
