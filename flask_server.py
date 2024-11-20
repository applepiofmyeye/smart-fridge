from flask import Flask, request, jsonify
import firebase_admin
from firebase_admin import credentials, storage, firestore
import os
import uuid
import pkg_resources
from dotenv import load_dotenv
import os

load_dotenv()  # This line brings all environment variables from .env into os.environ

app = Flask(__name__)

classes = ["Red Apple", "Rotten Red Apple", "Green Apple", "Rotten Green Apple", "Cucumber", "Rotten Cucumber", "Banana", "Rotten Banana"]


fruits = ["Red Apple", "Green Apple", "Cucumber", "Banana"]

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

    # # Initialize Firestore document
    # doc_ref = db.collection("fruits").document("apple")
    # doc_ref.set({"name": "Apple", "plural_name": "Apples", "quantity": 0})
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

@app.route('/upload-image', methods=['POST'])
def upload_image():
    print("Uploading image...")
    
    try:
        file_path = ""
        if request.method == "POST": #if we make a post request to the endpoint, look for the image in the request body
            image_raw_bytes = request.get_data()  #get the whole body

            save_location = (os.path.join(app.root_path, "test.jpg")) #save to the same folder as the flask app live in 
            
            file_path = save_location

            f = open(save_location, 'wb') # wb for write byte data in the file instead of string
            f.write(image_raw_bytes) #write the bytes from the request body to the file
            f.close()

            print("Image saved")

        if len(file_path) == 0 :
            print('empty')
            return "there is no saved image"
        # # print("Image saved")    
        # if 'file' not in request.files:
        #     return jsonify({"error": "No file uploaded"}), 400
    
        # file = request.files['file']
        # if file.filename == '':
        #     return jsonify({"error": "No selected file"}), 400
        
        # Run YOLO prediction
        results = model(file_path)
        
        # Process results
        # Initialize a dictionary to keep track of counts
        fruit_counts = {fruit: {"Quantity": 0, "Total": 0} for fruit in fruits}
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

                # Get the fruit and its condition (fresh/rotten)
                class_name = classes[cls]  # e.g., "Rotten Red Apple"

                # Check if the class name contains "Rotten" and split accordingly
                if "Rotten" in class_name:
                    condition = "Rotten"
                    fruit = class_name.replace("Rotten ", "")  # Remove "Rotten" and get the fruit name
                else:
                    condition = "Fresh"
                    fruit = class_name  # No need to modify if it's not rotten

                # Print the condition and fruit
                print(f"Condition: {condition}, Fruit: {fruit}")

                if condition != "Rotten":
                    fruit_counts[fruit]["Quantity"] += 1  # Count only fresh fruits for "Quantity"

                fruit_counts[fruit]["Total"] += 1  # Count both fresh and rotten for "Total"

        # Update Firestore with the counts
        for fruit, counts in fruit_counts.items():
            print("--------------------------")
            print(fruit, counts)
            col_ref = db.collection(u'fridge')
            doc_refs_generator = col_ref.where("Item", "==", fruit).stream()
            for doc_ref in doc_refs_generator:
                doc = col_ref.document(doc_ref.id)
                doc.set({
                    "Item": fruit,
                    "Quantity": counts["Quantity"],
                    "Total": counts["Total"]
                })

        
        # Clean up
        # if os.path.exists(file_path):
        #     os.remove(file_path)
        
        return jsonify({
            'success': True,
            'predictions': processed_results
        }), 200
        
    except Exception as e:
        # Clean up on error
        # if 'file_path' in locals() and os.path.exists(file_path):
            # os.remove(file_path)
        
        print(f"Error processing image: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    print("Server starting...")
    app.run(debug=True, host='192.168.94.46')
