'''
MongoDB DB Implementation
'''

# Imports
from typing import Dict, List, Any
#from InterfaceDBManager import IDBManager
from .InterfaceDBManager import IDBManager
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient
import certifi
import os

load_dotenv()
MONGODB_URI = os.getenv('MONGODB_URI')
ca_path = certifi.where()

class DBManager(IDBManager):
    client = None
    db = None

    def __init__(self, uri=MONGODB_URI, db_name='testdb'):
        self.client = AsyncIOMotorClient(uri, tlsCAFile=ca_path)
        self.db = self.client[db_name]

    async def update_documents(self, collection: str, filter: Dict[str, Any], document: Dict[str, Any]) -> int:
        """
        Update documents based on a filter.
        
        Returns the number of documents updated.
        """
        result = await self.db[collection].update_many(filter, document)
        return result.modified_count

    async def delete_documents(self, collection: str, filter: Dict[str, Any]) -> int:
        """
        Delete documents based on a filter.

        Returns the number of documents deleted.
        """
        result = await self.db[collection].delete_many(filter)
        return result.deleted_count

    async def get_document(self, collection: str, filter: Dict[str, Any], returnID: bool = False) -> Dict[str, Any]:
        """
        Retrieve a single document based on a filter.
        
        Optionally includes the document's ID.
        """
        document = await self.db[collection].find_one(filter)
        if document and not returnID:
            document.pop("_id", None)
        return document

    async def get_document_ids(self, collection: str, filter: Dict[str, Any]) -> List[Any]:
        """
        Retrieve IDs of documents based on a filter.
        """
        cursor = self.db[collection].find(filter, {"_id": 1})
        return [doc["_id"] for doc in await cursor.to_list(length=100)]

    async def insert_documents(self, collection: str, newdoc: list[dict], session=None) -> List[Any]:
        """
        Insert new documents and return their IDs.
        """
        result = await self.db[collection].insert_many(newdoc, session=session)
        print(f"{len(result.inserted_ids)} documents inserted.")
        return result.inserted_ids