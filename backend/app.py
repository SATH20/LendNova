import os
import sys
from flask import Flask, jsonify
from flask_cors import CORS
from database.db import db, ma
from config import Config
from routes.predict import predict_bp
from routes.fraud import fraud_bp
from routes.ocr import ocr_bp
from routes.assessments import assessments_bp

sys.path.append(os.path.join(os.path.dirname(__file__), "ml"))

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    ma.init_app(app)
    CORS(app)

    app.register_blueprint(predict_bp, url_prefix="/api")
    app.register_blueprint(fraud_bp, url_prefix="/api")
    app.register_blueprint(ocr_bp, url_prefix="/api")
    app.register_blueprint(assessments_bp, url_prefix="/api")

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({"error": "Resource not found"}), 404

    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({"error": "Internal server error"}), 500

    with app.app_context():
        db.create_all()

        model_path = app.config["MODEL_PATH"]
        pipeline_path = app.config["PIPELINE_PATH"]
        stats_path = app.config["FEATURE_STATS_PATH"]

        if not (os.path.exists(model_path) and os.path.exists(pipeline_path) and os.path.exists(stats_path)):
            from ml.train import train_models
            train_models()

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5000)
