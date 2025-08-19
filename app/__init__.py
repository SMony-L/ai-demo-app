from flask import Flask

def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__)
    
    # Import and register blueprints
    from app.main import main_bp
    app.register_blueprint(main_bp)
    
    return app
