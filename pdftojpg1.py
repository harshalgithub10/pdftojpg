from flask import Flask, request, send_from_directory
from werkzeug.utils import secure_filename
from pdf2image import convert_from_path
import os

app = Flask(__name__)

# Configuration
UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'output_images'
ALLOWED_EXTENSIONS = {'pdf'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER

# Create necessary folders
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Function to check allowed file extensions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Route to render upload form
@app.route('/')
def upload_form():
    return '''
    <!doctype html>
    <title>Upload PDFs</title>
    <h1>Upload PDFs to Convert to JPG</h1>
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

    image_links = ""
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

            # Save each page as a JPG image
            for i, page in enumerate(pages):
                image_filename = f"{filename.rsplit('.', 1)[0]}_page_{i + 1}.jpg"
                image_path = os.path.join(app.config['OUTPUT_FOLDER'], image_filename)
                page.save(image_path, 'JPEG')
                image_links += f'<a href="/download/{image_filename}">{image_filename}</a><br>'

    return f"<h1>Conversion Complete!</h1><p>{image_links}</p>"

# Route to download the images
@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(app.config['OUTPUT_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True, port=22001)
