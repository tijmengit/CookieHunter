import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
#collection_name = 'pages'
collection_name = 'alexa_test'
class DatabaseManager:

    def __init__(self):
        if not firebase_admin._apps:
            cred = credentials.Certificate("../data/database_cred.json")
            firebase_admin.initialize_app(cred)
        self.db = firestore.client()

    def add_new_webpage(self, ref, data):
        doc_ref = self.db.collection(collection_name).document(ref)
        if doc_ref.get().exists:
            return doc_ref
        else:
            return doc_ref.set(data)

    def get_webpage(self, ref):
        if self.db.collection(collection_name).document(ref).get().exists:
            return self.db.collection(collection_name).document(ref).get().to_dict()
        else:
            return None

    def update_web_page(self, ref, data):
        if self.db.collection(collection_name).document(ref).get().exists:
            self.db.collection(collection_name).document(ref).update(data)

    def delete_web_page(self, ref):
        if self.db.collection(collection_name).document(ref).get().exists:
            self.db.collection(collection_name).document(ref).delete()
