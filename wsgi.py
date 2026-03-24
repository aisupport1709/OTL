"""Entry point for Gunicorn: gunicorn --bind 0.0.0.0:$PORT --workers 2 wsgi:app"""
from app import create_app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True, port=5002)
