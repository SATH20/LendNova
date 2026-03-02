from datetime import datetime
import json
from .db import db

class Assessment(db.Model):
    __tablename__ = 'assessments'

    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Input Data
    income = db.Column(db.Float, nullable=False)  # declared_income
    expenses = db.Column(db.Float, nullable=False)  # declared_expense
    employment_type = db.Column(db.String(50), nullable=False)
    job_tenure = db.Column(db.Float, nullable=False)
    
    # Verified Financial Data
    declared_income = db.Column(db.Float, nullable=True)
    verified_income = db.Column(db.Float, nullable=True)
    declared_expense = db.Column(db.Float, nullable=True)
    verified_expense = db.Column(db.Float, nullable=True)
    verification_method = db.Column(db.String(50), nullable=True)
    
    # Prediction Results
    credit_score = db.Column(db.Integer, nullable=False)
    approval_probability = db.Column(db.Float, nullable=False)
    fraud_probability = db.Column(db.Float, nullable=True)
    risk_band = db.Column(db.String(20), nullable=False)
    decision = db.Column(db.String(20), nullable=True)  # APPROVED, REVIEW, REJECTED
    model_used = db.Column(db.String(50), nullable=False)
    confidence_score = db.Column(db.Float, nullable=False)
    assessment_status = db.Column(db.String(20), nullable=False, default="PRELIMINARY")
    assessment_stage = db.Column(db.String(20), nullable=False, default="PRELIMINARY")
    verification_status = db.Column(db.String(20), nullable=False, default="PENDING")
    trust_score = db.Column(db.Float, nullable=True)
    identity_status = db.Column(db.String(20), nullable=True)
    verification_reasons = db.Column(db.Text, nullable=True)
    verification_flags = db.Column(db.Text, nullable=True)
    identity_hash = db.Column(db.String(128), nullable=True)
    
    # Stability Scores
    income_stability_score = db.Column(db.Float, nullable=True)
    expense_pattern_score = db.Column(db.Float, nullable=True)
    
    # Relationship
    documents = db.relationship('Document', backref='assessment', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'timestamp': self.timestamp.isoformat(),
            'credit_score': self.credit_score,
            'approval_probability': self.approval_probability,
            'fraud_probability': self.fraud_probability,
            'risk_band': self.risk_band,
            'decision': self.decision,
            'model_used': self.model_used,
            'assessment_status': self.assessment_status,
            'assessment_stage': self.assessment_stage,
            'verification_status': self.verification_status,
            'trust_score': self.trust_score,
            'identity_status': self.identity_status,
            'verification_reasons': json.loads(self.verification_reasons) if self.verification_reasons else [],
            'verification_flags': json.loads(self.verification_flags) if self.verification_flags else [],
            'declared_income': self.declared_income,
            'verified_income': self.verified_income,
            'declared_expense': self.declared_expense,
            'verified_expense': self.verified_expense,
            'verification_method': self.verification_method,
            'income_stability_score': self.income_stability_score,
            'expense_pattern_score': self.expense_pattern_score,
        }

class Document(db.Model):
    __tablename__ = 'documents'

    id = db.Column(db.Integer, primary_key=True)
    assessment_id = db.Column(db.Integer, db.ForeignKey('assessments.id'), nullable=True) # Can be uploaded before assessment
    document_type = db.Column(db.String(50), nullable=False) # 'payslip', 'id_card', etc.
    extracted_text = db.Column(db.Text, nullable=True) # Masked sensitive data
    fraud_flags = db.Column(db.Text, nullable=True) # JSON string or comma-separated
    upload_time = db.Column(db.DateTime, default=datetime.utcnow)
