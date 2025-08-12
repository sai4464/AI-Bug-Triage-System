from app import app
import os

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))  # Use PORT env var or default to 8080
    print(f"Starting Flask app on port {port}")
    app.run(host='0.0.0.0', port=port, debug=True)