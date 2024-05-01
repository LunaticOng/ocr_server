from flask import Flask
import firebase_admin
from firebase_admin import credentials, firestore

app = Flask(__name__)

# Initialize Firebase Admin SDK
cred = credentials.Certificate("path/to/your/firebase/credentials.json")
firebase_admin.initialize_app(cred)



@app.route('/')
def hello_world():
    return 'Hello, World!'

db = firestore.client()

# Example route to fetch data from Firestore
@app.route('/data')
def get_data():
    data = db.collection('your_collection').get()
    # Process data as needed
    return jsonify(data)