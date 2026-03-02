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
from routes.analyze import analyze_bp

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
    app.register_blueprint(analyze_bp, url_prefix="/api")

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({"error": "Resource not found"}), 404

    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({"error": "Internal server error"}), 500

    with app.app_context():
        db.create_all()
        _ensure_assessments_schema()

        model_path = app.config["MODEL_PATH"]
        pipeline_path = app.config["PIPELINE_PATH"]
        stats_path = app.config["FEATURE_STATS_PATH"]

        if not (os.path.exists(model_path) and os.path.exists(pipeline_path) and os.path.exists(stats_path)):
            from ml.train import train_models
            train_models()

    return app

def _ensure_assessments_schema():
    if db.engine.dialect.name != "sqlite":
        return
    with db.engine.begin() as connection:
        table_info = connection.exec_driver_sql("PRAGMA table_info(assessments)").fetchall()
        if not table_info:
            return
        existing_cols = {row[1] for row in table_info}
        required_cols = {
            "id",
            "timestamp",
            "income",
            "expenses",
            "employment_type",
            "job_tenure",
            "credit_score",
            "approval_probability",
            "fraud_probability",
            "risk_band",
            "decision",
            "model_used",
            "confidence_score",
            "assessment_status",
            "assessment_stage",
            "verification_status",
            "trust_score",
            "identity_status",
            "verification_reasons",
            "verification_flags",
            "identity_hash",
            "declared_income",
            "verified_income",
            "declared_expense",
            "verified_expense",
            "verification_method",
            "income_stability_score",
            "expense_pattern_score",
        }
        if required_cols.issubset(existing_cols):
            return
        connection.exec_driver_sql("PRAGMA foreign_keys=off")
        connection.exec_driver_sql("ALTER TABLE assessments RENAME TO assessments_old")
        connection.exec_driver_sql(
            """
            CREATE TABLE assessments (
                id INTEGER PRIMARY KEY,
                timestamp DATETIME,
                income FLOAT NOT NULL,
                expenses FLOAT NOT NULL,
                employment_type VARCHAR(50) NOT NULL,
                job_tenure FLOAT NOT NULL,
                declared_income FLOAT,
                verified_income FLOAT,
                declared_expense FLOAT,
                verified_expense FLOAT,
                verification_method VARCHAR(50),
                credit_score INTEGER NOT NULL,
                approval_probability FLOAT NOT NULL,
                fraud_probability FLOAT,
                risk_band VARCHAR(20) NOT NULL,
                decision VARCHAR(20),
                model_used VARCHAR(50) NOT NULL,
                confidence_score FLOAT NOT NULL,
                assessment_status VARCHAR(20) NOT NULL,
                assessment_stage VARCHAR(20) NOT NULL,
                verification_status VARCHAR(20) NOT NULL,
                trust_score FLOAT,
                identity_status VARCHAR(20),
                verification_reasons TEXT,
                verification_flags TEXT,
                identity_hash VARCHAR(128),
                income_stability_score FLOAT,
                expense_pattern_score FLOAT
            )
            """
        )
        connection.exec_driver_sql(
            """
            INSERT INTO assessments (
                id,
                timestamp,
                income,
                expenses,
                employment_type,
                job_tenure,
                credit_score,
                approval_probability,
                fraud_probability,
                risk_band,
                decision,
                model_used,
                confidence_score,
                assessment_status,
                assessment_stage,
                verification_status,
                trust_score,
                identity_status,
                verification_reasons,
                verification_flags,
                identity_hash,
                declared_income,
                verified_income,
                declared_expense,
                verified_expense,
                verification_method,
                income_stability_score,
                expense_pattern_score
            )
            SELECT
                id,
                timestamp,
                income,
                expenses,
                employment_type,
                job_tenure,
                credit_score,
                approval_probability,
                fraud_probability,
                risk_band,
                'REVIEW',
                model_used,
                confidence_score,
                'PRELIMINARY',
                'PRELIMINARY',
                'PENDING',
                NULL,
                NULL,
                NULL,
                NULL,
                NULL,
                income,
                NULL,
                expenses,
                NULL,
                NULL,
                NULL,
                NULL
            FROM assessments_old
            """
        )
        connection.exec_driver_sql("DROP TABLE assessments_old")
        connection.exec_driver_sql("PRAGMA foreign_keys=on")

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5000)
