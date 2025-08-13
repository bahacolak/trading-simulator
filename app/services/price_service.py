import asyncio
import random
import xml.etree.ElementTree as ET
import csv
import io
from datetime import datetime
from typing import Dict, Optional
import requests
import logging

from ..core.config import settings

logger = logging.getLogger(__name__)

class PriceService:
    
    def __init__(self):
        self.prices = {
            "GOLD": 2000.0,
            "SILVER": 25.0
        }
        self.last_update = datetime.utcnow()
        self._update_task: Optional[asyncio.Task] = None

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

    async def _price_update_loop(self):
        while True:
            try:
                await self._fetch_lbma_data()
                
                for _ in range(15):
                    await asyncio.sleep(settings.price_update_interval)
                    self._apply_micro_fluctuations()
                    
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in price update loop: {e}")
                await asyncio.sleep(10)

    async def _fetch_lbma_data(self):
        try:
            try:
                response = requests.get(settings.lbma_xml_url, timeout=10)
                if response.status_code == 200:
                    self._parse_xml_data(response.text)
                    logger.debug("Successfully fetched LBMA XML data")
                    return
            except Exception as e:
                logger.debug(f"XML feed failed: {e}")
            
            try:
                response = requests.get(settings.lbma_csv_url, timeout=10)
                if response.status_code == 200:
                    self._parse_csv_data(response.text)
                    logger.debug("Successfully fetched LBMA CSV data")
                    return
            except Exception as e:
                logger.debug(f"CSV feed failed: {e}")
                
        except Exception as e:
            logger.warning(f"LBMA feed error: {e}")

    def _parse_xml_data(self, xml_content: str):
        try:
            root = ET.fromstring(xml_content)
            
            gold_elements = (root.findall(".//gold") or 
                           root.findall(".//Gold") or 
                           root.findall(".//GOLD"))
            
            silver_elements = (root.findall(".//silver") or 
                             root.findall(".//Silver") or 
                             root.findall(".//SILVER"))
            
            for elem in gold_elements:
                price_text = elem.text or elem.get('price') or elem.get('value')
                if price_text:
                    try:
                        self.prices["GOLD"] = float(price_text)
                        break
                    except ValueError:
                        continue
            
            for elem in silver_elements:
                price_text = elem.text or elem.get('price') or elem.get('value')
                if price_text:
                    try:
                        self.prices["SILVER"] = float(price_text)
                        break
                    except ValueError:
                        continue
                    
        except Exception as e:
            logger.error(f"XML parse error: {e}")

    def _parse_csv_data(self, csv_content: str):
        try:
            reader = csv.DictReader(io.StringIO(csv_content))
            rows = list(reader)
            
            if not rows:
                return
                
            last_row = rows[-1]
            
            for col_name, value in last_row.items():
                if value and col_name:
                    col_lower = col_name.lower()
                    if 'gold' in col_lower:
                        try:
                            self.prices["GOLD"] = float(value)
                        except ValueError:
                            pass
                    elif 'silver' in col_lower:
                        try:
                            self.prices["SILVER"] = float(value)
                        except ValueError:
                            pass
                        
        except Exception as e:
            logger.error(f"CSV parse error: {e}")

    def _apply_micro_fluctuations(self):
        for symbol in list(self.prices.keys()):
            if symbol not in ["timestamp"]:
                change_percent = random.uniform(-0.1, 0.1)
                self.prices[symbol] *= (1 + change_percent / 100)
                self.prices[symbol] = round(self.prices[symbol], 2)
        
        self.last_update = datetime.utcnow()

price_service = PriceService()
