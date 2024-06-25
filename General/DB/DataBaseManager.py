'''
MongoDB DB Implementation
'''

# Imports
from .InterfaceDBManager import IDBManager
from typing import Dict, List, Any
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import UpdateOne
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
    
    async def get_documents(self, collection: str, filter: Dict[str, Any], returnID: bool = False) -> Dict[str, Any]:
        """
        Retrieve a single document based on a filter.
        
        Optionally includes the document's ID.
        """
        documents = await self.db[collection].find(filter).to_list(length=100)
        for document in documents:
            print(document)
            if document and not returnID:
                document.pop("_id", None)
        return documents

    async def get_document_ids(self, collection: str, filter: Dict[str, Any]) -> List[Any]:
        """
        Retrieve IDs of documents based on a filter.
        """
        cursor = self.db[collection].find(filter, {"_id": 1})
        return [doc["_id"] for doc in await cursor.to_list(length=100)]

    async def insert_documents(self, collection: str, newdoc: list[dict], session=None) -> List[Any]:
        """
        Insert new documents and return their IDs. Updates duplicates if they exist.
        """
        if not newdoc:
            print("No documents to insert or update (empty list)")
            return []
        
        id_list = []
        for doc in newdoc:
            id = doc["_id"]
            id_list.append(id)
            
        updateResults = self.db[collection].find({
            "_id" : {"$in" : id_list}
        },session=session)

        duplicteIds = await updateResults.distinct("_id")

        ids_to_remove = set(duplicteIds)
        newdoc_filtered = [d for d in newdoc if d['_id'] not in ids_to_remove]
        newdoc_updates = [d for d in newdoc if d['_id'] in ids_to_remove]

        inserted_ids = []
        try:
            if newdoc_filtered:
                result = await self.db[collection].insert_many(newdoc_filtered, session=session)
                inserted_ids = result.inserted_ids
                print(f"{len(result.inserted_ids)} documents inserted.")
            else:
                print("No new docs to insert")

            updates_count = 0
            for doc in newdoc_updates:
                filter = {'_id' : doc['_id']}
                new_values = {'$set': doc}
                await self.db[collection].update_one(filter, new_values, session=session)
                updates_count += 1
            print(f"{updates_count} documents updated.")

        except TypeError as te:
            print(f"TypeError: {te}. Ensure docs are a non-empty list")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

        return inserted_ids