"""
Simple test for /api/analyze endpoint
"""

import os
import sys
sys.path.insert(0, os.path.dirname(__file__))

from app import create_app
from database.db import db


def test_analyze_endpoint():
    """Test the unified analyze endpoint"""
    app = create_app()
    app.config['TESTING'] = True
    
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        
        print("\n" + "=" * 60)
        print("TESTING UNIFIED /api/analyze ENDPOINT")
        print("=" * 60)
        
        # Test 1: Basic request without documents
        print("\n[Test 1] Basic request without documents...")
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
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.get_json()
            
            print(f"\n✓ SUCCESS - Response Structure:")
            print(f"  Credit Score: {result.get('credit_score')}")
            print(f"  Risk Band: {result.get('risk_band')}")
            print(f"  Decision: {result.get('decision')}")
            print(f"  Approval Probability: {result.get('approval_probability'):.2%}")
            
            print(f"\n  Verification:")
            print(f"    Status: {result.get('verification', {}).get('status')}")
            print(f"    Trust Score: {result.get('verification', {}).get('trust_score')}")
            print(f"    Flags: {result.get('verification', {}).get('flags')}")
            
            print(f"\n  Fraud:")
            print(f"    Probability: {result.get('fraud', {}).get('fraud_probability')}")
            print(f"    Flags: {result.get('fraud', {}).get('flags')}")
            
            print(f"\n  Explainability:")
            positive = result.get('explainability', {}).get('positive_factors', [])
            risk = result.get('explainability', {}).get('risk_factors', [])
            print(f"    Positive Factors ({len(positive)}):")
            for factor in positive:
                print(f"      - {factor.get('feature')}: {factor.get('impact'):.3f}")
            print(f"    Risk Factors ({len(risk)}):")
            for factor in risk:
                print(f"      - {factor.get('feature')}: {factor.get('impact'):.3f}")
            
            print(f"\n  Processing Summary:")
            summary = result.get('processing_summary', {})
            print(f"    OCR Completed: {summary.get('ocr_completed')}")
            print(f"    Verification Completed: {summary.get('verification_completed')}")
            print(f"    Fraud Checked: {summary.get('fraud_checked')}")
            
            # Validate structure
            assert 'credit_score' in result
            assert 'risk_band' in result
            assert 'decision' in result
            assert 'approval_probability' in result
            assert 'verification' in result
            assert 'fraud' in result
            assert 'explainability' in result
            assert 'processing_summary' in result
            
            print("\n✓ All required fields present")
            
        else:
            print(f"✗ FAILED - {response.get_json()}")
            return False
        
        # Test 2: High-income applicant
        print("\n[Test 2] High-income applicant...")
        data2 = {
            'income': 12000,
            'expenses': 3000,
            'employment_type': 'Full-time',
            'job_tenure': 5.0,
            'name': 'Jane Smith',
            'employer': 'Finance Inc',
            'mobile': '+1987654321'
        }
        
        response2 = client.post('/api/analyze', data=data2)
        if response2.status_code == 200:
            result2 = response2.get_json()
            print(f"✓ Credit Score: {result2.get('credit_score')}")
            print(f"  Decision: {result2.get('decision')}")
            print(f"  Risk Band: {result2.get('risk_band')}")
        else:
            print(f"✗ FAILED")
        
        # Test 3: Risky applicant
        print("\n[Test 3] Risky applicant...")
        data3 = {
            'income': 1500,
            'expenses': 1400,
            'employment_type': 'Part-time',
            'job_tenure': 0.5,
            'name': 'Bob Johnson',
            'employer': 'Retail Store',
            'mobile': '+1122334455'
        }
        
        response3 = client.post('/api/analyze', data=data3)
        if response3.status_code == 200:
            result3 = response3.get_json()
            print(f"✓ Credit Score: {result3.get('credit_score')}")
            print(f"  Decision: {result3.get('decision')}")
            print(f"  Risk Band: {result3.get('risk_band')}")
        else:
            print(f"✗ FAILED")
        
        print("\n" + "=" * 60)
        print("ALL TESTS COMPLETED SUCCESSFULLY")
        print("=" * 60)
        return True


if __name__ == '__main__':
    try:
        success = test_analyze_endpoint()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n✗ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
