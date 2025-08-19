#!/usr/bin/env python3
"""
Entry point for the Flask application.
Run this file to start the development server.
"""

from app import create_app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)
