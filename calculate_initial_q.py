import os
import json
from firebase_admin import credentials, firestore
import firebase_admin

# Load Firebase credentials from environment or file
service_account_json = os.getenv('CREDENTIALS')
if service_account_json:
    service_account = json.loads(service_account_json)
    cred = credentials.Certificate(service_account)
else:
    # Alternatively, load the service account from a local JSON file
    cred = credentials.Certificate("project-7603294209459337285-firebase-adminsdk-dhg12-1b3b39aec2.json")

# Initialize Firebase Admin SDK
firebase_admin.initialize_app(cred)

# Initialize Firestore client
db = firestore.client()

def calculate_and_update_average_quantity():
    # Dictionary to hold the sum of fresh quantities and counts for each fruit
    fruit_data = {}
    
    # Retrieve all documents from 'dailyData' collection
    docs = db.collection('dailyData').stream()
    
    for doc in docs:
        data = doc.to_dict()
        
        # Iterate through each fruit in the document
        for fruit, quantities in data.items():
            if isinstance(quantities, list) and len(quantities) == 2:
                fresh_quantity = quantities[0]  # Quantity of fresh fruit (index 0)
                
                # Update the sum and count for each fruit
                if fruit not in fruit_data:
                    fruit_data[fruit] = {"total_fresh_quantity": 0, "count": 0}
                
                fruit_data[fruit]["total_fresh_quantity"] += fresh_quantity
                fruit_data[fruit]["count"] += 1

    # Calculate average and update/create documents in 'initialQuantity' collection
    for fruit, values in fruit_data.items():
        if values["count"] > 0:
            average_quantity = int(values["total_fresh_quantity"] / values["count"])
            
            # Prepare data for the document update
            doc_data = {
                "Item": fruit,
                "Quantity": average_quantity
            }
            
            # Check if a document for the fruit already exists
            query = db.collection('initialQuantity').where("Item", "==", fruit).limit(1).stream()
            doc_found = False
            for existing_doc in query:
                # Update the existing document
                db.collection('initialQuantity').document(existing_doc.id).update({"Quantity": average_quantity})
                print(f"Updated document for {fruit}: {doc_data}")
                doc_found = True
                break

            if not doc_found:
                # Create a new document if no existing document was found
                db.collection('initialQuantity').add(doc_data)
                print(f"Created new document for {fruit}: {doc_data}")

try:
    calculate_and_update_average_quantity()
except Exception as e:
    print(f"Error: {e}")
