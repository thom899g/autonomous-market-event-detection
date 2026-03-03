"""
Configuration management for Autonomous Market Event Detection System.
Centralizes environment variables, Firebase credentials, and system parameters.
"""

import os
from typing import Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class MarketDataSource(Enum):
    """Supported market data sources"""
    COINBASE = "coinbase"
    BINANCE = "binance"
    KRAKEN = "kraken"
    BYBIT = "bybit"
    DERIBIT = "deribit"

class AnomalyType(Enum):
    """Classification of detected anomalies"""
    VOLATILITY_SPIKE = "volatility_spike"
    LIQUIDITY_CRISIS = "liquidity_crisis"
    FLASH_CRASH = "flash_crash"
    PUMP_DUMP = "pump_dump"
    STRUCTURAL_BREAK = "structural_break"
    SYBIL_ATTACK = "sybil_attack"

@dataclass
class FirebaseConfig:
    """Firebase configuration container"""
    project_id: str
    credentials_path: str
    database_url: str
    collection_prefix: str = "market_events"
    
    @classmethod
    def from_env(cls) -> 'FirebaseConfig':
        """Initialize from environment variables"""
        creds_path = os.getenv("FIREBASE_CREDENTIALS_PATH", "./firebase-credentials.json")
        if not os.path.exists(creds_path):
            raise FileNotFoundError(f"Firebase credentials not found at {creds_path}")
        
        return cls(
            project_id=os.getenv("FIREBASE_PROJECT_ID", "autonomous-market-detection"),
            credentials_path=creds_path,
            database_url=os.getenv("FIREBASE_DATABASE_URL", "https://autonomous-market-detection.firebaseio.com")
        )

@dataclass
class PredictionConfig:
    """Predictive synthesis engine configuration"""
    forecast_horizon_minutes: int = 60
    lookback_window_hours: int = 168  # 7 days
    probability_threshold: float = 0.85
    confidence_interval: float = 0.95
    resample_frequency: str = "5min"
    
class SystemConfig:
    """Main system configuration"""
    
    def __init__(self):
        self.firebase = FirebaseConfig.from_env()
        self.prediction = PredictionConfig()
        
        # Data sources
        self.data_sources = [
            MarketDataSource.COINBASE,
            MarketDataSource.BINANCE,
            MarketDataSource.KRAKEN
        ]
        
        # Symbols to monitor
        self.symbols = [
            "BTC/USDT",
            "ETH/USDT",
            "SOL/USDT",
            "BNB/USDT"
        ]
        
        # System parameters
        self.polling_interval_seconds = 300  # 5 minutes
        self.max_retries = 3
        self.retry_delay = 5
        
        # Logging
        self.log_level = os.getenv("LOG_LEVEL", "INFO").upper()
        
    def validate(self) -> bool:
        """Validate configuration"""
        errors = []
        
        if not self.symbols:
            errors.append("No symbols configured for monitoring")
        
        if self.prediction.probability_threshold > 1.0 or self.prediction.probability_threshold < 0.5:
            errors.append("Probability threshold must be between 0.5 and 1.0")
            
        if errors:
            logging.error(f"Configuration validation failed: {errors}")
            return False
            
        return True

# Global configuration instance
config = SystemConfig()