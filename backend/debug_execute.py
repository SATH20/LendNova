import traceback

try:
    with open('routes/analyze.py', 'r') as f:
        code = f.read()
    exec(code)
    print("File executed successfully")
    print("analyze_bp exists:", 'analyze_bp' in dir())
except Exception as e:
    print("EXECUTION FAILED:")
    traceback.print_exc()
