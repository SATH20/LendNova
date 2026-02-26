import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev_secret_key_change_in_production")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///lendnova.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # ML Models Paths
    MODEL_PATH = os.path.join(os.path.dirname(__file__), "models", "ml_model.pkl")
    PIPELINE_PATH = os.path.join(os.path.dirname(__file__), "models", "preprocess_pipeline.pkl")
    
    # Uploads
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "uploads")
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf'}

    # Tesseract Path (Windows example, override in .env for production/linux)
    TESSERACT_CMD = os.getenv("TESSERACT_CMD", r"C:\Program Files\Tesseract-OCR\tesseract.exe")
