from flask import Flask, jsonify, request
import firebase_admin
from firebase_admin import credentials, firestore, storage
import easyocr

app = Flask(__name__)

# Initialize Firebase Admin SDK
cred = credentials.Certificate("smartmailbox-secret.json")
firebase_app = firebase_admin.initialize_app(
    cred, {"storageBucket": "smartmailbox-8513f.appspot.com"}
)

db = firestore.client()

@app.route("/hw")
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

@app.route("/")
def get_photo():
    bucket = storage.bucket(app=firebase_app)
    blob = bucket.blob("images/good_resolution.jpg")
    
    # Download the image data as bytes
    image_data = blob.download_as_bytes()

    # Use EasyOCR to read the text from the image
    reader = easyocr.Reader(lang_list=["ch_tra", "en"], gpu=False)
    result = reader.readtext(image_data)
    
    # Process the OCR results
    myDict = {}
    for idx, item in enumerate(result):
        text = item[1]
        myDict[idx] = text

    # Write the data to Firebase Firestore
    try:
        db.collection('mailBoxes').document('test').collection('mails').add(myDict)
        return jsonify(myDict)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
