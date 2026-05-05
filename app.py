

# app.py
from flask import Flask, request, jsonify
from flask_cors import CORS
from parser import smart_extract
import os

app = Flask(__name__)
CORS(app)

# PDF अपलोड करण्यासाठी एक फोल्डर
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/upload-quiz', methods=['POST'])
def upload_quiz():
    if 'file' not in request.files:
        return jsonify({"error": "फाईल मिळाली नाही"}), 400
    
    file = request.files['file']
    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(file_path)

    print("FILE RECEIVED:", file.filename)

    # PDF मधून प्रश्न काढणे
    quiz_data = smart_extract(file_path)

    print("QUIZ DATA:", quiz_data)  # 🔥 IMPORTANT

    return quiz_data# हे थेट JSON फ्रंटएंडला पाठवेल

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)