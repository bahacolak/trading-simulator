import asyncio
import random
import json
from datetime import datetime
from typing import Dict, Optional
import requests
import logging

from ..core.config import settings

logger = logging.getLogger(__name__)

class PriceService:
    
    def __init__(self):
        self.prices = {}
        self.last_update = datetime.utcnow()
        self._update_task: Optional[asyncio.Task] = None
        
        self._fetch_initial_prices()

    def get_current_price(self, symbol: str) -> Optional[float]:
        return self.prices.get(symbol.upper())

    def get_all_prices(self) -> Dict[str, float]:
        return {
            **self.prices,
            "timestamp": datetime.utcnow().isoformat()
        }

    async def start_price_updates(self):
        if self._update_task and not self._update_task.done():
            return
        
        self._update_task = asyncio.create_task(self._price_update_loop())
        logger.info("Price update service started")

    async def stop_price_updates(self):
        if self._update_task:
            self._update_task.cancel()
            try:
                await self._update_task
            except asyncio.CancelledError:
                pass
            logger.info("Price update service stopped")

    def _fetch_initial_prices(self):
        try:
            self._fetch_real_prices()
            logger.info("Initial real prices fetched successfully")
        except Exception as e:
            logger.warning(f"Failed to fetch initial prices: {e}")
            self.prices = {
                "GOLD": 2650.00,
                "SILVER": 32.00
            }
            logger.info("Using fallback prices")

    async def _price_update_loop(self):
        while True:
            try:
                await self._fetch_real_prices_async()
                
                for _ in range(15):
                    await asyncio.sleep(settings.price_update_interval)
                    self._apply_micro_fluctuations()
                    
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in price update loop: {e}")
                await asyncio.sleep(10)

    def _fetch_real_prices(self):
        try:
            self._fetch_gold_price()
            self._fetch_silver_price()
            
            self.last_update = datetime.utcnow()
            logger.info(f"Real prices updated - Gold: ${self.prices.get('GOLD')}, Silver: ${self.prices.get('SILVER')}")
                
        except Exception as e:
            logger.error(f"Error fetching real prices: {e}")
            raise

    def _fetch_gold_price(self):
        try:
            url = f"{settings.coingecko_api_url}?ids={settings.gold_coin_id}&vs_currencies=usd"
            
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                
                if settings.gold_coin_id in data:
                    gold_price = data[settings.gold_coin_id]['usd']
                    self.prices["GOLD"] = round(float(gold_price), 2)
                    logger.debug(f"Gold price updated from {settings.gold_coin_id}: ${gold_price}")
                else:
                    raise Exception(f"Gold coin ID {settings.gold_coin_id} not found in response")
            else:
                logger.warning(f"CoinGecko API returned status: {response.status_code}")
                raise Exception(f"Gold API call failed with status {response.status_code}")
                
        except Exception as e:
            logger.error(f"Error fetching gold price: {e}")
            raise

    def _fetch_silver_price(self):
        for silver_id in settings.silver_coin_ids:
            try:
                url = f"{settings.coingecko_api_url}?ids={silver_id}&vs_currencies=usd"
                
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    
                    if silver_id in data:
                        silver_price = data[silver_id]['usd']
                        if silver_price >= 5:
                            self.prices["SILVER"] = round(float(silver_price), 2)
                            logger.debug(f"Silver price updated from {silver_id}: ${silver_price}")
                            return
                        else:
                            logger.debug(f"Silver price from {silver_id} too low (${silver_price}), trying next token")
                    else:
                        logger.debug(f"Silver coin ID {silver_id} not found in response")
                        
            except Exception as e:
                logger.debug(f"Error fetching silver price from {silver_id}: {e}")
                continue
        
        if "GOLD" in self.prices:
            silver_ratio = random.uniform(75, 85)
            silver_price = self.prices["GOLD"] / silver_ratio
            self.prices["SILVER"] = round(float(silver_price), 2)
            logger.info(f"Silver price calculated from gold ratio: ${silver_price} (ratio: {silver_ratio:.1f})")
        else:
            raise Exception("Cannot fetch silver price from API and no gold price available for ratio calculation")

    async def _fetch_real_prices_async(self):
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, self._fetch_real_prices)

    def _apply_micro_fluctuations(self):
        for symbol in list(self.prices.keys()):
            if symbol not in ["timestamp"]:
                change_percent = random.uniform(-0.2, 0.2)
                self.prices[symbol] *= (1 + change_percent / 100)
                self.prices[symbol] = round(self.prices[symbol], 2)
        
        self.last_update = datetime.utcnow()

price_service = PriceService()
