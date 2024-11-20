import paho.mqtt.client as mqtt
from time import sleep, time
import firebase_admin
from firebase_admin import credentials, storage, firestore
import threading

curr_temp = None
curr_humidity = None
last_temp = None
last_humidity = None
update_interval = 5  # Interval in seconds for writing to Firebase

# Initialize Firebase SDK
try:
    cred = credentials.Certificate("project-7603294209459337285-firebase-adminsdk-dhg12-1b3b39aec2.json")
    firebase_app = firebase_admin.initialize_app(cred)
    db = firestore.client()
except Exception as e:
    print(f"Error initializing Firebase: {str(e)}")
    exit(1)

# Function to periodically write to Firebase
def periodic_update():
    global last_temp, last_humidity
    threading.Timer(update_interval, periodic_update).start()  # Schedule the next call

    # Check if either value has changed
    if curr_temp != last_temp or curr_humidity != last_humidity:
        try:
            col_ref = db.collection('tnh')
            col_ref.document().set({
                "Temperature": curr_temp,
                "Humidity": curr_humidity,
                "Timestamp": firestore.SERVER_TIMESTAMP
            })
            print("Updated Firestore with Temperature and Humidity")
            last_temp, last_humidity = curr_temp, curr_humidity  # Update last known values
        except Exception as e:
            print(f"Error writing to Firestore: {str(e)}")

# MQTT Callbacks
def on_connect(client, userdata, flags, rc):
    print("Connected with result code: " + str(rc))
    client.subscribe("message/temp")
    client.subscribe("message/humidity")

def on_message(client, userdata, message):
    global curr_temp, curr_humidity
    payload = message.payload.decode('utf-8')
    print("Received message: " + payload)
    
    try:
        string_arr = payload.split()
        if message.topic == "message/temp" and "Temperature:" in string_arr:
            index = string_arr.index("Temperature:")
            temp_str = string_arr[index + 1].rstrip("°C")  
            curr_temp = float(temp_str)  # Convert to float, then to int
            print("Updated Temperature: " + str(curr_temp))
        elif message.topic == "message/humidity" and "Humidity:" in string_arr:
            index = string_arr.index("Humidity:")
            curr_humidity = float(string_arr[index + 1][:-1])
            print("Updated Humidity: " + str(curr_humidity))
    except Exception as e:
        print(f"Error processing message: {str(e)}")

# Start periodic updates
periodic_update()

# MQTT Client setup
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect("13.229.116.98", 1883, 60)
client.loop_forever()
