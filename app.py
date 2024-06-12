from flask import Flask, jsonify, request
import firebase_admin
from firebase_admin import credentials, firestore, storage, initialize_app
import easyocr
import re
import json
import google.generativeai as genai

app = Flask(__name__)
API_KEY = ""
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")
chat = model.start_chat(history=[])

# Initialize Firebase Admin SDK
cred = credentials.Certificate("smartmailbox-secret.json")
firebase_app = firebase_admin.initialize_app(
    cred, {"storageBucket": "smartmailbox-8513f.appspot.com"}
)

# Initialize Firestore Database
db = firestore.client()


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
    """Reads text from an image using EasyOCR and stores it in Firestore."""
    bucket = storage.bucket(app=firebase_app)
    image_blob = bucket.blob(
        "test/images/no_personal_info.jpeg"
    )  # replace with timestamp
    image_data = image_blob.download_as_bytes()

    reader = easyocr.Reader(lang_list=["ch_tra", "en"], gpu=False)
    ocr_results = reader.readtext(image_data)
    ocr_res = [res[1] for res in ocr_results]
    ask_prompt = "\n".join(ocr_res)
    ask_prompt = (
        "請告訴我這封信的內容，收件人(receiver)、寄件人(sender)、收件人地址(receiverAddress)、寄件人地址(senderAddress)、分類(type)、分爲高中低的緊急性(urgency)、如果有時間限制(timeLimit)可以告訴我詳細的時間，最後再給這封信一個合適的標題(title)，如果有任何未知的訊息，請以'未知'回覆，以Json格式回傳，並且key要用英文"
        + "\n"
        + ask_prompt
    )

    response = chat.send_message(ask_prompt)

    try:
        val = response.text
        matcch = re.search(r"\{([^}]+)\}", val)
        matcch = json.loads("{" + matcch.group(1) + "}")

        db.collection("mailBoxes").document("test").collection("mails").add(matcch)
        return jsonify(matcch)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)
