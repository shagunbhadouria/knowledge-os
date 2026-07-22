"""ASGI entry point for OmniRAG."""

from app.main import create_app

app = create_app()
