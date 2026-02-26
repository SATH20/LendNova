from datetime import datetime
from .db import db

class Assessment(db.Model):
    __tablename__ = 'assessments'

    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Input Data
    income = db.Column(db.Float, nullable=False)
    expenses = db.Column(db.Float, nullable=False)
    employment_type = db.Column(db.String(50), nullable=False)
    job_tenure = db.Column(db.Float, nullable=False)
    
    # Prediction Results
    credit_score = db.Column(db.Integer, nullable=False)
    approval_probability = db.Column(db.Float, nullable=False)
    fraud_probability = db.Column(db.Float, nullable=False)
    risk_band = db.Column(db.String(20), nullable=False)
    model_used = db.Column(db.String(50), nullable=False)
    confidence_score = db.Column(db.Float, nullable=False)
    
    # Relationship
    documents = db.relationship('Document', backref='assessment', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'timestamp': self.timestamp.isoformat(),
            'credit_score': self.credit_score,
            'approval_probability': self.approval_probability,
            'risk_band': self.risk_band,
            'model_used': self.model_used
        }

class Document(db.Model):
    __tablename__ = 'documents'

    id = db.Column(db.Integer, primary_key=True)
    assessment_id = db.Column(db.Integer, db.ForeignKey('assessments.id'), nullable=True) # Can be uploaded before assessment
    document_type = db.Column(db.String(50), nullable=False) # 'payslip', 'id_card', etc.
    extracted_text = db.Column(db.Text, nullable=True) # Masked sensitive data
    fraud_flags = db.Column(db.Text, nullable=True) # JSON string or comma-separated
    upload_time = db.Column(db.DateTime, default=datetime.utcnow)
