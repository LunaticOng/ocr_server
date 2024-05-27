from flask import Flask, jsonify, request
import firebase_admin
from firebase_admin import credentials, firestore, storage, initialize_app
from firebase_functions import storage_fn
import easyocr
import io
import pathlib

app = Flask(__name__)

# Initialize Firebase Admin SDK
cred = credentials.Certificate("smartmailbox-secret.json")
firebase_app = firebase_admin.initialize_app(
    cred, {"storageBucket": "smartmailbox-8513f.appspot.com"}
)

db = firestore.client()
initialize_app()


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
@storage_fn.on_object_finalized() # when there's a new file uploaded
def get_photo():
    """Reads text from an image using EasyOCR and stores it in Firestore."""
    bucket = storage.bucket(app=firebase_app)
    image_blob = bucket.blob("images/good_resolution.jpg") # replace with timestamp
    image_data = image_blob.download_as_bytes()

    reader = easyocr.Reader(lang_list=["ch_tra", "en"], gpu=False)
    ocr_results = reader.readtext(image_data)

    ocr_dict = {}
    for idx, result in enumerate(ocr_results, start=1):
        text = result[1]
        ocr_dict[str(idx)] = text

    try:
        db.collection("mailBoxes").document("test").collection("mails").add(ocr_dict)
        return jsonify(ocr_dict)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/notify", methods=["POST"])
def notify():
    data = request.get_json()
    file_path = data.get("filePath")
    download_url = data.get("downloadURL")

    # Handle the notification (e.g., log it, process it, etc.)
    print(f"New file uploaded: {file_path}")
    print(f"Download URL: {download_url}")

    return jsonify({"status": "success"}), 200


if __name__ == "__main__":
    app.run(debug=True)
