"""WSGI entry point for production deployment."""
import os
from app import create_app

# Create application instance
application = create_app()
app = application  # Alias for compatibility

if __name__ == '__main__':
    # For Railway/Render: use PORT env variable
    port = int(os.environ.get("PORT", 8000))
    application.run(host='0.0.0.0', port=port)
