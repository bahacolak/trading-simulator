from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    database_url: str = "mysql+pymysql://root:password@localhost/trading_simulator"
    
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    api_v1_str: str = "/api/v1"
    project_name: str = "Trading Simulator"
    
    backend_cors_origins: list[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]
    
    lbma_xml_url: str = "https://www.lbma.org.uk/prices"
    lbma_csv_url: str = "https://www.lbma.org.uk/downloads/gold-price.csv"
    price_update_interval: int = 2
    
    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()
