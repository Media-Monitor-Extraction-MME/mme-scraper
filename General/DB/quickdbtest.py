# Imports
from InterfaceDBManager import IDBManager
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

    async def insert_documents(self, collection: str, newdoc: List[Dict[str, Any]]) -> List[Any]:
        """
        Insert new documents and return their IDs.
        """
        result = await self.db[collection].insert_many(newdoc)
        return result.inserted_ids

# Example usage
async def main():
    manager = DBManager(db_name='testsamples')
    
    # Insert documents
    new_docs = [
        {"name": "Alice", "age": 25},
        {"name": "Bob", "age": 30}
    ]
    inserted_ids = await manager.insert_documents("testsamplesTwitter", new_docs)
    print(f"Inserted IDs: {inserted_ids}")

    '''
    # Get document by a filter
    document = await manager.get_document("users", {"name": "Alice"})
    print(f"Fetched Document: {document}")

    # Update documents
    updated_count = await manager.update_documents("users", {"name": "Alice"}, {"$set": {"age": 26}})
    print(f"Documents Updated: {updated_count}")

    # Get document IDs by a filter
    document_ids = await manager.get_document_ids("users", {"age": {"$gte": 20}})
    print(f"Document IDs: {document_ids}")

    # Delete documents
    deleted_count = await manager.delete_documents("users", {"age": {"$gte": 20}})
    print(f"Documents Deleted: {deleted_count}")
    '''

import asyncio
asyncio.run(main())
