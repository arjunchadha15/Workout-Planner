"""
Minimal Flask app to test the plan generation endpoint.
Run this to start the API server, then run interactive_test.py in another terminal.
"""
from flask import Flask
from flask_cors import CORS
from plan_routes import plan_routes

app = Flask(__name__)
CORS(app)  # Enable CORS for iOS app

# Register the plan generation blueprint
app.register_blueprint(plan_routes)

@app.route('/')
def home():
    return {
        'status': 'online',
        'service': 'Repple AI Plan Generation API',
        'endpoints': {
            'generate': 'POST /plans/generate',
            'health': 'GET /plans/health'
        }
    }

if __name__ == '__main__':
    print("🚀 Starting Repple API server...")
    print("📍 API will be available at: http://localhost:8000")
    print("📍 Plan generation endpoint: POST http://localhost:8000/plans/generate")
    print("📍 Health check: GET http://localhost:8000/plans/health")
    print("\n⚠️  Make sure you have:")
    print("   - Installed dependencies: pip install -r requirements.txt")
    print("   - Set OPENAI_API_KEY in .env file")
    print("   - Database with exercise data available")
    print("\n✨ Press Ctrl+C to stop the server\n")
    
    app.run(
        host='0.0.0.0',
        port=8000,
        debug=True
    )
