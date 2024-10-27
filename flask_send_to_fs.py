from flask import Flask, request, jsonify
import firebase_admin
from firebase_admin import credentials, storage, firestore
import os
import uuid
import cv2
import numpy as np
import torch
import pkg_resources
from dotenv import load_dotenv
import os

load_dotenv()  # This line brings all environment variables from .env into os.environ

app = Flask(__name__)

classes = ["fresh apple", "rotten apple", "fresh banana", "rotten banana", "fresh cucumber", "rotten cucumber", "fresh orange", "rotten orange", "fresh potato", "rotten potato", "fresh tomato", "rotten tomato"]

# Check ultralytics version
try:
    ultralytics_version = pkg_resources.get_distribution('ultralytics').version
    print(f"Ultralytics version: {ultralytics_version}")
    from ultralytics import YOLO
except Exception as e:
    print(f"Error checking ultralytics version: {str(e)}")
    exit(1)

# Initialize Firebase SDK
try:
    cred = credentials.Certificate(os.environ['CREDENTIALS'])
    firebase_app = firebase_admin.initialize_app(cred)
    db = firestore.client()

    # Initialize Firestore document
    doc_ref = db.collection("fruits").document("apple")
    doc_ref.set({"name": "Apple", "plural_name": "Apples", "quantity": 0})
except Exception as e:
    print(f"Error initializing Firebase: {str(e)}")
    exit(1)

# Load YOLO model
try:
    if not os.path.exists("./models/best.pt"):
        print("Error: Model file './models/best.pt' not found!")
        exit(1)
    
    model = YOLO("./models/best.pt")
    print("Model loaded successfully")
except Exception as e:
    print(f"Error loading YOLO model: {str(e)}")
    exit(1)

# Ensure uploads directory exists
os.makedirs('uploads', exist_ok=True)

@app.route('/upload', methods=['POST'])
def upload_image():
    print("Uploading image...")
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    try:
        # Save the image temporarily
        image_name = str(uuid.uuid4()) + ".jpg"
        file_path = os.path.join('uploads', image_name)
        file.save(file_path)
        
        # Run YOLO prediction
        results = model(file_path)
        
        # Process results
        processed_results = []
        for r in results:
            boxes = r.boxes
            for box in boxes:
                b = box.xyxy[0].tolist()  # get box coordinates in (top, left, bottom, right) format
                conf = float(box.conf[0])
                cls = int(box.cls[0])
                
                processed_results.append({
                    'bbox': b,
                    'confidence': conf,
                    'class_id': cls
                })
        
        # Update Firestore if needed
        if processed_results:
            # Update the count in Firestore
            doc_ref = db.collection("fruits").document(classes[cls])
            doc_ref.set({"quantity": 1 if doc_ref.get().to_dict() is None else int(doc_ref.get().to_dict().get("quantity"))  + 1})
        
        # Clean up
        if os.path.exists(file_path):
            os.remove(file_path)
        
        return jsonify({
            'success': True,
            'predictions': processed_results
        }), 200
        
    except Exception as e:
        # Clean up on error
        if 'file_path' in locals() and os.path.exists(file_path):
            os.remove(file_path)
        
        print(f"Error processing image: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    print("Server starting...")
    app.run(debug=True, host='192.168.1.59')