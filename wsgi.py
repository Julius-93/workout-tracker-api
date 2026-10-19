"""Entry point for both the Flask CLI and a production WSGI server."""
from app import create_app

app = create_app()
