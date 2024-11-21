import os
import json
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, firestore

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

# Function to convert ISO 8601 date string to a Python datetime object
def convert_to_datetime(date_str):
    return datetime.fromisoformat(date_str.replace('Z', '+00:00'))

# Read data from data.json
with open('data.json', 'r') as file:
    data = json.load(file)

# Process each record and upload to Firestore
for record in data:
    try:
        # Check if 'Date' exists and convert it to a datetime object
        if 'Date' in record:
            record['Date'] = convert_to_datetime(record['Date'])

        # Add record to the 'dailyData' collection with an auto-generated document ID
        db.collection('dailyData').add(record)
        print('Document successfully written:', record)
    except Exception as e:
        print('Error writing document:', e)