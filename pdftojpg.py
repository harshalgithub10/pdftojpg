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
    <title>Upload PDF</title>
    <h1>Upload PDF to Convert to JPG</h1>
    <form method="POST" action="/" enctype="multipart/form-data">
        <input type="file" name="file" accept=".pdf">
        <input type="submit" value="Upload">
    </form>
    '''

# Route to handle file upload and conversion
@app.route('/', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return 'No file part in the request'

    file = request.files['file']
    if file.filename == '':
        return 'No file selected for uploading'

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        pdf_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(pdf_path)

        # Convert PDF to images using pdf2image
        try:
            pages = convert_from_path(pdf_path, dpi=300, poppler_path=r"C:\Users\V. Mathia\Downloads\Release-24.08.0-0\poppler-24.08.0\Library\bin")
        except Exception as e:
            return f"Error during PDF conversion: {str(e)}"

        # Save each page as a JPG image
        image_paths = []
        for i, page in enumerate(pages):
            image_filename = f"{filename.rsplit('.', 1)[0]}_page_{i + 1}.jpg"
            image_path = os.path.join(app.config['OUTPUT_FOLDER'], image_filename)
            page.save(image_path, 'JPEG')
            image_paths.append(image_filename)

        # Provide links to download the images
        image_links = ''.join(
            [f'<a href="/download/{img}">{img}</a><br>' for img in image_paths]
        )
        return f"<h1>Conversion Complete!</h1><p>{image_links}</p>"

    return 'File type not allowed'

# Route to download the images
@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(app.config['OUTPUT_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True, port=6000)
