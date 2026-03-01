from marshmallow import Schema, fields, validate

class AssessmentInputSchema(Schema):
    income = fields.Float(required=True, validate=validate.Range(min=0))
    expenses = fields.Float(required=True, validate=validate.Range(min=0))
    employment_type = fields.Str(required=True, validate=validate.OneOf(['Full-time', 'Part-time', 'Self-employed', 'Unemployed', 'Student']))
    job_tenure = fields.Float(required=True, validate=validate.Range(min=0))

class AssessmentOutputSchema(Schema):
    id = fields.Int()
    timestamp = fields.DateTime()
    credit_score = fields.Int()
    approval_probability = fields.Float()
    fraud_probability = fields.Float(allow_none=True)
    assessment_status = fields.Str()
    verification_status = fields.Str()
    risk_band = fields.Str()
    model_used = fields.Str()
    confidence_score = fields.Float()
    top_factors = fields.List(fields.Dict())

class OcrResultSchema(Schema):
    name = fields.Str()
    income = fields.Float(allow_none=True)
    employer = fields.Str(allow_none=True)
    extracted_text = fields.Str()

class FraudCheckInputSchema(Schema):
    ocr_data = fields.Nested(OcrResultSchema, required=True)
    form_data = fields.Nested(AssessmentInputSchema, required=True)
    assessment_id = fields.Int(required=False, allow_none=True)
