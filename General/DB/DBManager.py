'''
MongoDB DB Implementation
'''

#Imports
from typing import Dict, List
from InterfaceDBManager import *
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient
import os
import certifi

load_dotenv()
MONGODB_URI = os.getenv('MONGODB_URI')
ca_path = certifi.where()

class DBManager(IDBManager):
    client = None
    db = None

    def __init__(self, uri=MONGODB_URI, db_name='testdb'):
        self.client = AsyncIOMotorClient(uri, tlsCAFile=ca_path) #tlsCAFile used because i couldn't connect otherwise
        self.db = self.client[db_name]

    async def update_documents(self, collection: str, filter: Dict[str, Any], document: Dict[str, Any]) -> int:
        return super().update_documents(collection, filter, document)
    
    async def delete_documents(self, collection: str, filter: Dict[str, os.Any]) -> int:
        return super().delete_documents(collection, filter)
    
    async def get_document(self, collection: str, filter: Dict[str, os.Any], returnID: bool = False) -> Dict[str, os.Any]:
        return super().get_document(collection, filter, returnID)
    
    async def get_document_ids(self, collection: str, filter: Dict[str, os.Any]) -> List[Any]:
        return super().get_document_ids(collection, filter)
    
    async def insert_documents(self, collection: str, newdoc: List[Dict[str, os.Any]]) -> List[os.Any]:
        return super().insert_documents(collection, newdoc)