from typing import Dict, Any, Optional

import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore


class DatabaseManager:
    collection_name = 'alexa_test'

    def __init__(self):
        if not firebase_admin._apps:
            cred = credentials.Certificate("./../data/database_cred.json")
            firebase_admin.initialize_app(cred)
        self.db = firestore.client()

    def add_new_webpage(self, ref: str, data: Dict[str, Any]) -> Any:
        doc_ref = self.db.collection(self.collection_name).document(ref)
        if doc_ref.get().exists:
            return doc_ref
        else:
            return doc_ref.set(data)

    def get_webpage(self, ref: str) -> Optional[Dict[str, Any]]:
        if self.db.collection(self.collection_name).document(ref).get().exists:
            return self.db.collection(self.collection_name).document(ref).get().to_dict()
        else:
            return None

    def update_web_page(self, ref: str, data: Dict[str, any]) -> None:
        if self.db.collection(self.collection_name).document(ref).get().exists:
            self.db.collection(self.collection_name).document(ref).update(data)

    def delete_web_page(self, ref: str) -> None:
        if self.db.collection(self.collection_name).document(ref).get().exists:
            self.db.collection(self.collection_name).document(ref).delete()
