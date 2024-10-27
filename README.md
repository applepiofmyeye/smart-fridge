# Getting Started

1. Request for Firebase Admin Credentials JSON file and .env file from me!
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
python flask_send_to_fs.py
```
