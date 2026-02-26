import os
import sys
from flask import Flask, jsonify
from flask_cors import CORS
from database.db import db, ma
from config import Config

# Import Blueprints
from routes.predict import predict_bp
from routes.fraud import fraud_bp
from routes.ocr import ocr_bp
from routes.assessments import assessments_bp

# Ensure ML modules are importable
sys.path.append(os.path.join(os.path.dirname(__file__), 'ml'))

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize Plugins
    db.init_app(app)
    ma.init_app(app)
    CORS(app)
    
    # Register Blueprints
    app.register_blueprint(predict_bp, url_prefix='/api')
    app.register_blueprint(fraud_bp, url_prefix='/api')
    app.register_blueprint(ocr_bp, url_prefix='/api')
    app.register_blueprint(assessments_bp, url_prefix='/api')
    
    # Error Handling
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({"error": "Resource not found"}), 404
        
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({"error": "Internal server error"}), 500
        
    # Database Initialization & Model Check
    with app.app_context():
        db.create_all()
        
        # Check if model exists, if not, train it
        if not os.path.exists(app.config['MODEL_PATH']):
            print("ML Model not found. Training initial model on synthetic data...")
            from ml.train import train_models
            try:
                train_models()
                print("Initial model training complete.")
            except Exception as e:
                print(f"Failed to train initial model: {e}")
                
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5000)
