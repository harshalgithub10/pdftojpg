from flask import Flask, request, send_from_directory
from werkzeug.utils import secure_filename
from pdf2image import convert_from_path
import pytesseract
import os
import json

app = Flask(__name__)

# Configuration
UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'output_images'
JSON_OUTPUT_FOLDER = 'output_json'
TEXT_OUTPUT_FOLDER = 'output_text'
ALLOWED_EXTENSIONS = {'pdf'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER
app.config['JSON_OUTPUT_FOLDER'] = JSON_OUTPUT_FOLDER
app.config['TEXT_OUTPUT_FOLDER'] = TEXT_OUTPUT_FOLDER

# Create necessary folders
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)
os.makedirs(JSON_OUTPUT_FOLDER, exist_ok=True)
os.makedirs(TEXT_OUTPUT_FOLDER, exist_ok=True)

# Function to check allowed file extensions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Route to render upload form
@app.route('/')
def upload_form():
    return '''
    <!doctype html>
    <title>Upload PDFs</title>
    <h1>Upload PDFs to Convert to JPG, JSON, and Text</h1>
    <form method="POST" action="/" enctype="multipart/form-data">
        <input type="file" name="files" multiple accept=".pdf">
        <input type="submit" value="Upload">
    </form>
    '''

# Route to handle file upload and conversion
@app.route('/', methods=['POST'])
def upload_files():
    if 'files' not in request.files:
        return 'No files part in the request'

    files = request.files.getlist('files')
    if not files:
        return 'No files selected for uploading'

    result_links = ""
    for file in files:
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(pdf_path)

            # Convert PDF to images
            try:
                pages = convert_from_path(pdf_path, dpi=300, poppler_path=r"C:\Users\V. Mathia\Downloads\Release-24.08.0-0\poppler-24.08.0\Library\bin")
            except Exception as e:
                return f"Error during PDF conversion: {str(e)}"

            # Process each page
            for i, page in enumerate(pages):
                # Save as JPG
                image_filename = f"{filename.rsplit('.', 1)[0]}_page_{i + 1}.jpg"
                image_path = os.path.join(app.config['OUTPUT_FOLDER'], image_filename)
                page.save(image_path, 'JPEG')

                # Extract text with Tesseract
                extracted_text = pytesseract.image_to_string(image_path)

                # Save text to JSON
                json_filename = f"{filename.rsplit('.', 1)[0]}_page_{i + 1}.json"
                json_path = os.path.join(app.config['JSON_OUTPUT_FOLDER'], json_filename)
                with open(json_path, 'w', encoding='utf-8') as json_file:
                    json.dump({"text": extracted_text}, json_file, ensure_ascii=False, indent=4)

                # Save text to TEXT file
                text_filename = f"{filename.rsplit('.', 1)[0]}_page_{i + 1}.txt"
                text_path = os.path.join(app.config['TEXT_OUTPUT_FOLDER'], text_filename)
                with open(text_path, 'w', encoding='utf-8') as text_file:
                    text_file.write(extracted_text)

                # Add links to results
                result_links += f'<a href="/download_image/{image_filename}">{image_filename}</a> (Image)<br>'
                result_links += f'<a href="/download_json/{json_filename}">{json_filename}</a> (JSON)<br>'
                result_links += f'<a href="/download_text/{text_filename}">{text_filename}</a> (Text)<br><br>'

    return f"<h1>Processing Complete!</h1><p>{result_links}</p>"

# Route to download the images
@app.route('/download_image/<filename>')
def download_image(filename):
    return send_from_directory(app.config['OUTPUT_FOLDER'], filename)

# Route to download the JSON files
@app.route('/download_json/<filename>')
def download_json(filename):
    return send_from_directory(app.config['JSON_OUTPUT_FOLDER'], filename)

# Route to download the TEXT files
@app.route('/download_text/<filename>')
def download_text(filename):
    return send_from_directory(app.config['TEXT_OUTPUT_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True, port=6002)

