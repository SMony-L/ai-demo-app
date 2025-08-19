from flask import Blueprint, jsonify, request

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def hello():
    """Root endpoint that returns a hello message."""
    return jsonify({
        "message": "Hello, World!",
        "status": "success"
    })

@main_bp.route('/health')
def health():
    """Health check endpoint that returns 200 OK."""
    return jsonify({
        "status": "healthy",
        "message": "Service is running"
    }), 200

@main_bp.route('/greet')
def greet():
    """Greet endpoint that takes a name parameter and returns a personalized greeting."""
    name = request.args.get('name', 'World')
    return jsonify({
        "message": f"Hello, {name}!",
        "status": "success"
    })
