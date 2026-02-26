from flask import Blueprint, jsonify, request
from database.models import Assessment
from database.schemas import AssessmentOutputSchema

assessments_bp = Blueprint('assessments', __name__)
output_schema = AssessmentOutputSchema(many=True)

@assessments_bp.route('/assessments', methods=['GET'])
def get_assessments():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    pagination = Assessment.query.order_by(Assessment.timestamp.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    result = output_schema.dump(pagination.items)
    
    return jsonify({
        'assessments': result,
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': page
    }), 200
