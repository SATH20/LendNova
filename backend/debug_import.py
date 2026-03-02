import traceback
import sys

sys.path.insert(0, '.')

try:
    from routes.analyze import analyze_bp
    print("SUCCESS:", analyze_bp)
except Exception as e:
    print("FAILED TO IMPORT:")
    traceback.print_exc()
