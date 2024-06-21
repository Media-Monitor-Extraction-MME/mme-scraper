'''
Interface for DB, in case we ever want to switch from Mongo
'''

# Imports
from abc import ABC, abstractmethod
from typing import Any, Dict, List

class IDBManager(ABC):
    @abstractmethod
    def update_documents(self, collection: str, filter: Dict[str, Any], document: Dict[str, Any]) -> int:
        """
        Update documents in a collection based on a filter.

        Args:
            collection (str): Name of the collection.
            filter (Dict[str, Any]): Criteria for selecting documents to update.
            document (Dict[str, Any]): New values to update.

        Returns:
            int: Number of documents updated.
        """
        pass

    @abstractmethod
    def delete_documents(self, collection: str, filter: Dict[str, Any]) -> int:
        """
        Delete documents from a collection based on a filter.

        Args:
            collection (str): Name of the collection.
            filter (Dict[str, Any]): Criteria for selecting documents to delete.

        Returns:
            int: Number of documents deleted.
        """
        pass

    @abstractmethod
    def get_document(self, collection: str, filter: Dict[str, Any], returnID: bool = False) -> Dict[str, Any]:
        """
        Retrieve a single document from a collection based on a filter.

        Args:
            collection (str): Name of the collection.
            filter (Dict[str, Any]): Criteria for selecting the document.
            returnID (bool): Whether to return the document's ID.

        Returns:
            Dict[str, Any]: The document matching the criteria.
        """
        pass
    @abstractmethod
    def get_documents(self, collection: str, filter: Dict[str, Any], returnID: bool = False) -> List[Dict[str, Any]]:
        """
        Retrieve a single document from a collection based on a filter.

        Args:
            collection (str): Name of the collection.
            filter (Dict[str, Any]): Criteria for selecting the document.
            returnID (bool): Whether to return the document's ID.

        Returns:
            List[Dict[str, Any]]: The document matching the criteria.
        """
        pass
    
    @abstractmethod
    def get_document_ids(self, collection: str, filter: Dict[str, Any]) -> List[Any]:
        """
        Retrieve the IDs of documents from a collection based on a filter.

        Args:
            collection (str): Name of the collection.
            filter (Dict[str, Any]): Criteria for selecting documents.

        Returns:
            List[Any]: A list of document IDs matching the criteria.
        """
        pass

    @abstractmethod
    def insert_documents(self, collection: str, newdoc: List[Dict[str, Any]]) -> List[Any]:
        """
        Insert new documents into a collection.

        Args:
            collection (str): Name of the collection.
            newdoc (List[Dict[str, Any]]): List of documents to insert.

        Returns:
            List[Any]: IDs of the inserted documents.
        """
        pass
