import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

class DatabaseManager:

    def __init__(self):
        cred = credentials.Certificate("./../data/database_cred.json")
        firebase_admin.initialize_app(cred)
        self.db = firestore.client()

    def add_new_webpage(self, ref, data):
        doc_ref = self.db.collection('pages').document(ref)
        if doc_ref.get().exists:
            return doc_ref
        else:
            return doc_ref.set(data)

    def get_webpage(self, ref):
        return self.db.collection('pages').document(ref).get()

    def update_web_page(self, ref, data):
        if self.db.collection('pages').document(ref).get().exists:
            self.db.collection('pages').document(ref).update(data)

    def delete_web_page(self, ref):
        if  self.db.collection('pages').document(ref).get().exists:
            self.db.collection('pages').document(ref).delete()

if __name__ == '__main__':
    db = DatabaseManager()
    ref = db.add_new_webpage('firstpage', {
        'home_url': 'https://www.firstpage.com',
        'login_url': 'https://www.firestpage.com/login',
        'register_url': 'https://www.firstpage.com/register',
        'register_data': {
            'user_name': 'cookiehunter',
            'email': 'cookiehunterproject+firstpage@gmail.com',
            'password': 'passwordRandom123!',
            'name': 'Janssen'
        },
        'registered': False,
        'able_to_fill_register': False,
        'able_to_fill_login': False,
        'activated': False,
        'captcha': False
    })
