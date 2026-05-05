import pdfplumber
import pytesseract
from pdf2image import convert_from_path
import re
import json
import os
import cv2
import numpy as np

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
POPPLER_PATH = r'C:\Users\Shree\Downloads\Release-25.12.0-0\poppler-25.12.0\Library\bin'


# ---------- TEXT CLEAN ----------
def clean_text(text):
    text = re.sub(r'[^\x00-\x7F]+', ' ', text)   # remove weird unicode
    text = re.sub(r'[\*\|\"\'`]', '', text)      # remove garbage symbols
    text = re.sub(r'\s+', ' ', text)             # normalize spaces
    return text


# ---------- IMAGE PREPROCESS ----------
def preprocess_image(image):
    img = np.array(image)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)
    return thresh


# ---------- PDFPLUMBER ----------
def extract_with_pdfplumber(pdf_path):
    full_text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                full_text += text + "\n"
    return full_text


# ---------- OCR ----------
def extract_with_ocr(pdf_path):
    print("OCR प्रोसेस सुरू होत आहे...")
    full_text = ""
    try:
        images = convert_from_path(pdf_path, poppler_path=POPPLER_PATH)
        for image in images:
            processed = preprocess_image(image)
            full_text += pytesseract.image_to_string(processed, lang='eng', config='--psm 6') + "\n"
    except Exception as e:
        return f"OCR एरर: {str(e)}"
    return full_text


# ---------- MAIN ----------
def smart_extract(pdf_path):
    if not os.path.exists(pdf_path):
        return json.dumps({"error": "फाईल सापडली नाही!"})

    text = extract_with_pdfplumber(pdf_path)

    # OCR fallback
    if not text or len(text.strip()) < 200:
        text = extract_with_ocr(pdf_path)

    text = clean_text(text)

    # DEBUG
    print("\n--- DEBUG TEXT ---")
    print(text[:500])
    print("------------------\n")

    # प्रश्न split
    questions = re.split(r'(?m)\s*(\d{1,3})[\.\)\s]+', text)

    all_data = []

    for i in range(1, len(questions), 2):
        if i + 1 < len(questions):

            q_num = questions[i]
            content = questions[i+1].strip()

            # lines split
            lines = re.split(r'(?=[(]?[a-dA-D][\)])', content)

            options = []
            question_text = ""

            for l in lines:
                l = l.strip()

                if not l:
                    continue

                # skip answer line
                if "answer" in l.lower():
                    continue

                # option detect
                elif re.match(r'^\(?[a-dA-D][\)]', l):
                    options.append(l)

                else:
                    question_text += " " + l

            question_text = question_text.strip()

            if len(options) >= 2:
                all_data.append({
                    "id": q_num,
                    "question": question_text,
                    "options": options
                })

    return json.dumps(all_data, indent=4, ensure_ascii=False)


# ---------- RUN ----------
if __name__ == "__main__":
    result = smart_extract("Unit_II_Management_MCQs_Part2.pdf")
    print(result)