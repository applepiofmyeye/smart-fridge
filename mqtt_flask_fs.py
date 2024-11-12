import firebase_admin
from firebase_admin import credentials, storage, firestore
import os

# Initialize Firebase SDK
try:
    cred = credentials.Certificate(os.environ['CREDENTIALS'])
    firebase_app = firebase_admin.initialize_app(cred)
    db = firestore.client()

    # # Initialize Firestore document
    # doc_ref = db.collection("fruits").document("apple")
    # doc_ref.set({"name": "Apple", "plural_name": "Apples", "quantity": 0})
except Exception as e:
    print(f"Error initializing Firebase: {str(e)}")
    exit(1)