import os
import shutil
import zipfile
import cv2
from flask import Flask, render_template, request, send_file, redirect, url_for, abort

app = Flask(__name__)

# Define paths for folders
UPLOAD_FOLDER = r'D:\Machine_Learning_Deploy\Deployment\static\uploads'
HUMAN_FOLDER = r'D:\Machine_Learning_Deploy\Deployment\static\human'
NON_HUMAN_FOLDER = r'D:\Machine_Learning_Deploy\Deployment\static\non_human'

# Ensure folders exist
for folder in [UPLOAD_FOLDER, HUMAN_FOLDER, NON_HUMAN_FOLDER]:
    os.makedirs(folder, exist_ok=True)

# Load Haar Cascade for face detection
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    if 'files' not in request.files:
        return redirect(request.url)
    
    files = request.files.getlist('files')
    for file in files:
        if file.filename == '':
            continue
        if file:
            file_path = os.path.join(UPLOAD_FOLDER, file.filename)
            file.save(file_path)

            # Process the image
            img = cv2.imread(file_path)
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, scaleFactor=1.4, minNeighbors=5, minSize=(50, 50))
            
            if len(faces) > 0:
                target_folder = HUMAN_FOLDER
            else:
                target_folder = NON_HUMAN_FOLDER
            
            # Move the image to the appropriate folder
            shutil.copy(file_path, os.path.join(target_folder, file.filename))

    # Create zip files after processing
    create_zip_for_category('human')
    create_zip_for_category('non_human')

    return redirect(url_for('result'))

@app.route('/result')
def result():
    return render_template('result.html')

@app.route('/download/<category>')
def download(category):
    if category not in ['human', 'non_human']:
        return "Invalid category", 400

    # Construct the filename and file path
    zip_filename = f'{category}_images.zip'
    zip_filepath = os.path.join(UPLOAD_FOLDER, zip_filename)

    # Check if the file exists
    if not os.path.exists(zip_filepath):
        abort(404, description="File not found")

    # Return the file as an attachment
    return send_file(zip_filepath, as_attachment=True, download_name=zip_filename)

def create_zip_for_category(category):
    if category not in ['human', 'non_human']:
        return "Invalid category", 400

    source_folder = HUMAN_FOLDER if category == 'human' else NON_HUMAN_FOLDER
    zip_filename = f'{category}_images.zip'
    zip_filepath = os.path.join(UPLOAD_FOLDER, zip_filename)

    # Remove existing zip file if it exists
    if os.path.exists(zip_filepath):
        os.remove(zip_filepath)

    # Create a new zip file
    try:
        with zipfile.ZipFile(zip_filepath, 'w') as zipf:
            for root, _, files in os.walk(source_folder):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, source_folder)
                    zipf.write(file_path, arcname=arcname)
        print(f'Zip file created: {zip_filepath}')
    except Exception as e:
        print(f'Error creating zip file: {e}')

    return zip_filepath

if __name__ == '__main__':
    app.run(debug=True)
