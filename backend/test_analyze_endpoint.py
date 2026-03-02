"""
Test Suite for Unified /api/analyze Endpoint
Tests complete pipeline integration with SHAP explainability
"""

import os
import sys
import json
import pytest

# Add backend to path
sys.path.insert(0, os.path.dirname(__file__))

from app import create_app
from database.db import db


@pytest.fixture
def client():
    """Create test client"""
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client


def test_analyze_without_documents(client):
    """Test analyze endpoint with form data only (no documents)"""
    data = {
        'income': 5000,
        'expenses': 2000,
        'employment_type': 'Full-time',
        'job_tenure': 3.5,
        'name': 'John Doe',
        'employer': 'Tech Corp',
        'mobile': '+1234567890'
    }
    
    response = client.post('/api/analyze', data=data)
    assert response.status_code == 200
    
    result = response.get_json()
    
    # Check required fields
    assert 'credit_score' in result
    assert 'risk_band' in result
    assert 'decision' in result
    assert 'approval_probability' in result
    
    # Check verification structure
    assert 'verification' in result
    assert 'status' in result['verification']
    assert 'trust_score' in result['verification']
    assert 'flags' in result['verification']
    assert isinstance(result['verification']['flags'], list)
    
    # Check fraud structure
    assert 'fraud' in result
    assert 'fraud_probability' in result['fraud']
    assert 'flags' in result['fraud']
    assert isinstance(result['fraud']['flags'], list)
    
    # Check explainability structure
    assert 'explainability' in result
    assert 'positive_factors' in result['explainability']
    assert 'risk_factors' in result['explainability']
    assert isinstance(result['explainability']['positive_factors'], list)
    assert isinstance(result['explainability']['risk_factors'], list)
    
    # Check processing summary
    assert 'processing_summary' in result
    assert 'ocr_completed' in result['processing_summary']
    assert 'verification_completed' in result['processing_summary']
    assert 'fraud_checked' in result['processing_summary']
    
    # Verify numeric fields are not null
    assert result['credit_score'] is not None
    assert result['approval_probability'] is not None
    assert result['verification']['trust_score'] is not None
    assert result['fraud']['fraud_probability'] is not None
    
    print("\n✓ Test 1 PASSED: Analyze without documents")
    print(f"  Credit Score: {result['credit_score']}")
    print(f"  Risk Band: {result['risk_band']}")
    print(f"  Decision: {result['decision']}")
    print(f"  Approval Probability: {result['approval_probability']:.2%}")
    print(f"  Positive Factors: {len(result['explainability']['positive_factors'])}")
    print(f"  Risk Factors: {len(result['explainability']['risk_factors'])}")


def test_analyze_high_income_applicant(client):
    """Test high-income applicant"""
    data = {
        'income': 12000,
        'expenses': 3000,
        'employment_type': 'Full-time',
        'job_tenure': 5.0,
        'name': 'Jane Smith',
        'employer': 'Finance Inc',
        'mobile': '+1987654321'
    }
    
    response = client.post('/api/analyze', data=data)
    assert response.status_code == 200
    
    result = response.get_json()
    
    # High income should result in better scores
    assert result['credit_score'] >= 600
    assert result['approval_probability'] >= 0.5
    
    # Should have positive factors
    assert len(result['explainability']['positive_factors']) > 0
    
    print("\n✓ Test 2 PASSED: High-income applicant")
    print(f"  Credit Score: {result['credit_score']}")
    print(f"  Decision: {result['decision']}")


def test_analyze_risky_applicant(client):
    """Test risky applicant profile"""
    data = {
        'income': 1500,
        'expenses': 1400,
        'employment_type': 'Part-time',
        'job_tenure': 0.5,
        'name': 'Bob Johnson',
        'employer': 'Retail Store',
        'mobile': '+1122334455'
    }
    
    response = client.post('/api/analyze', data=data)
    assert response.status_code == 200
    
    result = response.get_json()
    
    # Risky profile should have lower scores
    assert result['credit_score'] < 700
    assert result['risk_band'] in ['Medium', 'High']
    
    # Should have risk factors
    assert len(result['explainability']['risk_factors']) > 0
    
    print("\n✓ Test 3 PASSED: Risky applicant")
    print(f"  Credit Score: {result['credit_score']}")
    print(f"  Risk Band: {result['risk_band']}")
    print(f"  Decision: {result['decision']}")


def test_analyze_student_applicant(client):
    """Test student applicant"""
    data = {
        'income': 800,
        'expenses': 600,
        'employment_type': 'Student',
        'job_tenure': 0.0,
        'name': 'Alice Brown',
        'employer': '',
        'mobile': '+1555666777'
    }
    
    response = client.post('/api/analyze', data=data)
    assert response.status_code == 200
    
    result = response.get_json()
    
    # Student should have special handling
    assert result['verification']['status'] in ['PENDING', 'PARTIAL', 'INCOMPLETE']
    
    print("\n✓ Test 4 PASSED: Student applicant")
    print(f"  Credit Score: {result['credit_score']}")
    print(f"  Verification Status: {result['verification']['status']}")


def test_analyze_validation_errors(client):
    """Test validation errors"""
    # Missing required field
    data = {
        'income': 5000,
        'expenses': 2000,
        # Missing employment_type
        'job_tenure': 3.0
    }
    
    response = client.post('/api/analyze', data=data)
    assert response.status_code == 400
    
    print("\n✓ Test 5 PASSED: Validation errors handled correctly")


def test_analyze_response_consistency(client):
    """Test that multiple calls with same data produce consistent results"""
    data = {
        'income': 6000,
        'expenses': 2500,
        'employment_type': 'Full-time',
        'job_tenure': 2.0,
        'name': 'Test User',
        'employer': 'Test Corp',
        'mobile': '+1000000000'
    }
    
    # Make two identical requests
    response1 = client.post('/api/analyze', data=data)
    response2 = client.post('/api/analyze', data=data)
    
    assert response1.status_code == 200
    assert response2.status_code == 200
    
    result1 = response1.get_json()
    result2 = response2.get_json()
    
    # Core scores should be consistent (allowing for minor floating point differences)
    assert abs(result1['credit_score'] - result2['credit_score']) <= 1
    assert result1['risk_band'] == result2['risk_band']
    assert abs(result1['approval_probability'] - result2['approval_probability']) < 0.01
    
    print("\n✓ Test 6 PASSED: Response consistency verified")
    print(f"  Credit Score: {result1['credit_score']} vs {result2['credit_score']}")


def test_explainability_structure(client):
    """Test SHAP explainability output structure"""
    data = {
        'income': 7000,
        'expenses': 3000,
        'employment_type': 'Full-time',
        'job_tenure': 4.0,
        'name': 'Test User',
        'employer': 'Test Corp',
        'mobile': '+1111111111'
    }
    
    response = client.post('/api/analyze', data=data)
    assert response.status_code == 200
    
    result = response.get_json()
    explainability = result['explainability']
    
    # Check positive factors structure
    for factor in explainability['positive_factors']:
        assert 'feature' in factor
        assert 'impact' in factor
        assert isinstance(factor['feature'], str)
        assert isinstance(factor['impact'], (int, float))
        assert factor['impact'] >= 0
    
    # Check risk factors structure
    for factor in explainability['risk_factors']:
        assert 'feature' in factor
        assert 'impact' in factor
        assert isinstance(factor['feature'], str)
        assert isinstance(factor['impact'], (int, float))
        assert factor['impact'] >= 0  # Risk factors should have positive impact values
    
    # Should have at most 3 factors each
    assert len(explainability['positive_factors']) <= 3
    assert len(explainability['risk_factors']) <= 3
    
    print("\n✓ Test 7 PASSED: Explainability structure validated")
    print(f"  Positive Factors: {explainability['positive_factors']}")
    print(f"  Risk Factors: {explainability['risk_factors']}")


if __name__ == '__main__':
    # Run tests
    print("=" * 60)
    print("UNIFIED ANALYZE ENDPOINT TEST SUITE")
    print("=" * 60)
    
    pytest.main([__file__, '-v', '--tb=short'])
