from flask import Flask, jsonify
import firebase_admin
from firebase_admin import credentials, firestore

app = Flask(__name__)

# Initialize Firebase Admin SDK
cred = credentials.Certificate(
    "smartmailbox-8513f-firebase-adminsdk-gqlfr-9a1519f74f.json"
)
firebase_admin.initialize_app(cred)

db = firestore.client()


@app.route("/")
def main_page():
    return "Hello, World!"

# Example route to fetch data from Firestore
@app.route("/data")
def get_data():
    data = db.collection("mails").get()
    # Process data as needed
    serialized_data = []
    for doc in data:
        serialized_data.append(doc.to_dict())
    return jsonify(serialized_data)