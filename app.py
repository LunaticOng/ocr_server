from flask import Flask, jsonify, send_file
import firebase_admin
import tempfile
from firebase_admin import credentials, firestore, storage

app = Flask(__name__)

# Initialize Firebase Admin SDK
cred = credentials.Certificate("smartmailbox-secret.json")
firebase_app = firebase_admin.initialize_app(
    cred, {"storageBucket": "smartmailbox-8513f.appspot.com"}
)

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


@app.route("/get_photo")
def get_photo():
    bucket = storage.bucket(app=firebase_app)
    blob = bucket.blob("images/下載.png0e553576-fad1-487e-a6f5-912353f1fb74")
    temp_file = tempfile.NamedTemporaryFile(delete=False)
    blob.download_to_filename(temp_file.name)
    return send_file(temp_file.name, mimetype="image/jpeg")
