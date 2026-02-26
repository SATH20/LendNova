from flask import Blueprint, request, jsonify, current_app
import os
from werkzeug.utils import secure_filename
from services.ocr_service import extract_text_from_image

ocr_bp = Blueprint('ocr', __name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@ocr_bp.route('/ocr-extract', methods=['POST'])
def ocr_extract():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
        
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
        
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        upload_folder = current_app.config['UPLOAD_FOLDER']
        
        # Ensure upload folder exists
        os.makedirs(upload_folder, exist_ok=True)
        
        file_path = os.path.join(upload_folder, filename)
        file.save(file_path)
        
        # Extract Text
        # Pass config for Tesseract CMD
        extracted_data = extract_text_from_image(file_path, current_app.config)
        
        if extracted_data is None:
             return jsonify({"error": "OCR failed"}), 500
             
        # Cleanup (Optional)
        # os.remove(file_path)
        
        return jsonify(extracted_data), 200
        
    return jsonify({"error": "File type not allowed"}), 400
