from flask import Flask, jsonify, request
import firebase_admin
from firebase_admin import credentials, firestore, storage
import easyocr
import json

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
    myDict = dict()
    for idx, item in enumerate(result):
        myDict[str(idx)] = str(item[1])

    db.collection("mailBoxes").document("test").collection("mails").add(myDict)

    return jsonify(myDict)


"""
output:
{
    "0": "國泰人壽",
    "1": "M",
    "2": "10633 臺北市仁愛路四段 296號",
    "3": "國",
    "4": "內",
    "5": "免費服務菴話:0800-036-599",
    "6": "鄰資已 付",
    "7": "絹",
    "8": "址:wWw.cathayholdings.comlife",
    "9": "台北郅局許可.",
    "10": "台北字常1ll1芫",
    "11": "國 內 邽 商",
    "12": "云法扭遼訪遲口原貞",
    "13": "701033",
    "14": "重要文件請先拆閱",
    "15": "台南市東區崇德十九街120巷31號",
    "16": "詹秀如",
    "17": "君啟",
    "18": "352627",
    "19": "NIX",
    "20": "Papo[",
    "21": "5-11-[+71",
    "22": "[巳_1",
    "23": "{",
    "24": "FSC",
    "25": "FsC` C157544"
}
"""


if __name__ == "__main__":
    app.run(debug=True)
