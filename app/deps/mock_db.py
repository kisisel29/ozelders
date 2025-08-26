import json
import os
from typing import Dict, List, Optional, Any
from datetime import datetime

class MockDatabase:
    def __init__(self):
        self.data_file = "mock_data.json"
        self.data = self._load_data()
    
    def _load_data(self) -> Dict[str, Any]:
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        return {
            "classes": {},
            "users": {},
            "assignments": {},
            "submissions": {}
        }
    
    def _save_data(self):
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2, default=str)
    
    def create_document(self, collection: str, data: Dict[str, Any]) -> str:
        """Create a new document and return its ID"""
        if collection not in self.data:
            self.data[collection] = {}
        
        doc_id = f"{collection}_{len(self.data[collection]) + 1}"
        data['id'] = doc_id
        data['created_at'] = datetime.now().isoformat()
        self.data[collection][doc_id] = data
        self._save_data()
        return doc_id
    
    def get_document(self, collection: str, doc_id: str) -> Optional[Dict[str, Any]]:
        """Get a document by ID"""
        return self.data.get(collection, {}).get(doc_id)
    
    def update_document(self, collection: str, doc_id: str, updates: Dict[str, Any]) -> bool:
        """Update a document"""
        if doc_id in self.data.get(collection, {}):
            self.data[collection][doc_id].update(updates)
            self._save_data()
            return True
        return False
    
    def delete_document(self, collection: str, doc_id: str) -> bool:
        """Delete a document"""
        if doc_id in self.data.get(collection, {}):
            del self.data[collection][doc_id]
            self._save_data()
            return True
        return False
    
    def query_documents(self, collection: str, field: str, operator: str, value: Any) -> List[Dict[str, Any]]:
        """Query documents by field"""
        results = []
        for doc_id, doc_data in self.data.get(collection, {}).items():
            if field in doc_data:
                if operator == "==" and doc_data[field] == value:
                    results.append(doc_data)
                elif operator == "array_contains" and value in doc_data.get(field, []):
                    results.append(doc_data)
        return results
    
    def get_all_documents(self, collection: str) -> List[Dict[str, Any]]:
        """Get all documents in a collection"""
        return list(self.data.get(collection, {}).values())

# Global instance
mock_db = MockDatabase()
