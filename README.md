# Getting Started
## Project Structure
```
|_ flask_server.py: Flask Server hosting YOLO model, upload data to Firebase
|_ mqtt_firebase.py: Python script reading from MQTT, uploading temperature and humidity info to Firebase
|_ calculate_initial_q.py: Python script to calculate the 'dailyData' in Firestore, update the new initial quantity
```



## Flask Server
1. Request for Firebase Admin Credentials JSON file and .env file from me! (Note: if you want to use your own Firebase Credentials, go to [Using Your Own Firestore Database](https://github.com/applepiofmyeye/smart-fridge/main/README.md)
2. Make sure you have these installed: `flask`, `firebase_admin` and `dotenv`
3. In your terminal, run: `ifconfig` (on Mac), `ipconfig` (Linux / Windows)
4. Find your local host's IP address.
5. Edit `flask_send_to_fs.py` in the last line:
```
app.run(debug=True, host='<Your IP>') 
```
6. Save the file.
7. In your terminal, run:
```
python flask_server.py
```

## Script Uploading MQTT data to Firebase
To read the MQTT data and use it to update Firebase.

1. Retrieve the .json file from me or go to Using Your Own Firestore Database.
2. Run the following file:
```
python mqtt_firebase.py
```

## Generating Data 
In our report, we wished to simulate 2 months of data, where we simulated taking the stock of fridge items every day. This was done through the following steps:

1. Generate data by running the following file:
```
generate_data.js
```
2. The data will now be stored in `data.json`. The format of this file is:

```
[
  {
    "<fruit>": [int, int] // 0th index: fresh qty; 1st index: total qty (fresh + rotten)
  }
]
```

## Calculate New Initial Quantity
This calculates the new optimal initial quantity of the fridge, based on what users on average maintain in their fridge without them going bad.
```
python calculate_initial_q.py
```

## Using Your Own Firestore Database
1. Create a .env file
2. Insert the following line:
```
CREDENTIALS='</path/to/file/.json>'
```

