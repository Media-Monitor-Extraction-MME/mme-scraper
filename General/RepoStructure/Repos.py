'''
Contains all different repo patterns for the repo structure
'''
#Imports
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ..DB.InterfaceDBManager import IDBManager
from .IRepos import *

from typing import Any

class CommentRepo(ICommentRepository):    
    def __init__(self, db: IDBManager, collection: str):
        self.db = db
        self.collection = collection

    #Methods
    async def add_comment(self, document: dict) -> Any:
        return await self.db.insert_documents(self.collection, [document])

    async def remove_comment(self, filter: dict) -> Any:
        return await self.db.delete_documents(self.collection, filter)

    async def update_comment(self, filter: dict, document: dict) -> Any:
        return await self.db.update_documents(self.collection, filter, document)

    async def search_comment(self, filter):
        return await self.db.get_document(self.collection, filter)


class PostRepo(IPostRepository):        
    def __init__(self, db: IDBManager, collection: str):
        self.db = db
        self.collection = collection
        
    #Methods
    async def add_post(self, document: dict) -> Any:
        return await self.db.insert_documents(self.collection, [document])

    async def remove_post(self, filter: dict) -> Any:
        return await self.db.delete_documents(self.collection, filter)

    async def update_post(self, filter: dict, document: dict) -> Any:
        return await self.db.update_documents(self.collection, filter, document)

    async def search_post(self, filter):
        return await self.db.get_document(self.collection, filter)