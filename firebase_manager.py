"""
Firebase state management and real-time data synchronization.
Handles all Firestore operations with robust error handling and connection pooling.
"""

import firebase_admin
from firebase_admin import credentials, firestore, db
from google.cloud.firestore_v1 import Client as FirestoreClient
from google.cloud.firestore_v1.base_query import FieldFilter
from typing import Dict, Any, List, Optional, Callback
import logging
import json
from datetime import datetime, timedelta
import asyncio
from concurrent.futures import ThreadPoolExecutor
import threading

logger = logging.getLogger(__name__)

class FirebaseManager:
    """Manages Firebase connections and operations with connection pooling"""
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls, config):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
            return cls._instance
    
    def __init__(self, config):
        if not hasattr(self, 'initialized'):
            self.config = config
            self.app = None
            self.db_firestore: Optional[FirestoreClient] = None
            self.db_realtime = None
            self.initialized = False
            self._init_firebase()
            
    def _init_firebase(self):
        """Initialize Firebase connection with error handling"""
        try:
            if not firebase_admin._apps:
                cred = credentials.Certificate(self.config.firebase.credentials_path)
                self.app = firebase_admin.initialize_app(
                    cred,
                    {
                        'projectId': self.config.firebase.project_id,
                        'databaseURL': self.config.firebase.database_url
                    }
                )
                logger.info("Firebase Admin SDK initialized successfully")
            else:
                self.app = firebase_admin.get_app()
                logger.info("Using existing Firebase app")
                
            # Initialize Firestore
            self.db_firestore = firestore.client(app=self.app)
            
            # Initialize Realtime Database (optional)
            self.db_realtime = db.reference('/', app=self.app)
            
            self.initialized = True
            logger.info(f"Connected to Firebase project: {self.config.firebase.project_id}")
            
        except FileNotFoundError as e:
            logger.error(f"Firebase credentials file not found: {e}")
            raise
        except ValueError as e:
            logger.error(f"Invalid Firebase configuration: {e}")
            raise
        except Exception as e:
            logger.error(f"Failed to initialize Firebase: {e}")
            raise
    
    def save_market_state(self, 
                         symbol: str, 
                         data: Dict[str, Any],
                         source: str,
                         timestamp: Optional[datetime] = None) -> bool:
        """
        Save market state to Firestore